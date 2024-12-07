from gurobipy import Model, GRB, quicksum
import logging
from ..data.graph import Graph
from ..utility_profiles.base import base_utility_profile_function

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def stochastic_model(g: Graph, planning_budget: int, utility_profile_function: callable = base_utility_profile_function,
                     verbose: bool = False, big_m: int = 1_000) -> Model:
    ##############################################################
    # SETUP
    ##############################################################
    logger.info("Starting setup of stochastic optimization")

    nodes = g.nodes
    edges = g.edges
    od_pairs = g.od_pairs
    scenarios = g.scenarios

    path_weighting = {}

    # Compute utility profile for each OD pair
    for p in od_pairs:
        path_weighting[p] = utility_profile_function(g, p)

    # Fortification
    Budget_x = planning_budget

    ##############################################################
    # Optimization
    ##############################################################
    logger.info("Setting up optimization model")

    model = Model('StochasticE-RAFT')

    if not verbose:
        model.setParam('OutputFlag', 0)

    # Decision Variables
    # Edge flow variables
    w_vars = {}
    # Decision variable representing non-linearity
    q_vars = {}
    for p in od_pairs:
        for a in edges:
            w_vars[p, a] = model.addVar(name=f'w_{a}', vtype=GRB.BINARY)
            # Variable introduced to represent the non-linearity
            q_vars[p, a] = model.addVar(name=f'q_{a}', vtype=GRB.BINARY)

    # Decision variables representing adaptation measures on the edges
    x_vars = model.addVars(edges, obj=edges, name='x', vtype=GRB.BINARY)
    # Decision variables representing successful interdiction of edges
    z_vars = model.addVars(edges, obj=edges, name='z', vtype=GRB.BINARY)

    # Objective: minimize the total cost of the path stochastically over all scenarios
    model.modelSense = GRB.MINIMIZE
    model.setObjective(
        quicksum(s.probability *
            quicksum(
                path_weighting[p] * (edges[a] * w_vars[p, a] + s.get_tt_impact(a) * q_vars[p, a])
            for p in od_pairs for a in edges)
        for s in scenarios)
    )

    # Constraints
    # Flow
    for p in od_pairs:
        origin, destination = p.origin_node, p.destination_node
        for node in nodes:
            if node != origin and node != destination:
                model.addConstr(quicksum(w_vars[p, (i, j)] for i, j in edges if j == node) ==
                                quicksum(w_vars[p, (j, i)] for j, i in edges if j == node), f"flow")

        # McCormick
        for a in edges:
            model.addConstr(q_vars[p, a] <= z_vars[a])
            model.addConstr(q_vars[p, a] <= w_vars[p, a])
            model.addConstr(q_vars[p, a] >= z_vars[a] + w_vars[p, a] - 1)

        # Exactly one edge leaving the start node and entering the end node
        model.addConstr(quicksum(w_vars[p, (origin, j)] for j in nodes if (origin, j) in edges) == 1, 'p_outward_edge')
        model.addConstr(quicksum(w_vars[p, (i, destination)] for i in nodes if (i, destination) in edges) == 1,
                        'p_inward_edge')

    # For each scenario
    for s in scenarios:
        for a in edges:
            # Big M
            model.addConstrs((s.get_severity(a) - x_vars[a] <= big_m * z_vars[a] for a in edges), 'big_m_trick_UB')
            model.addConstrs((s.get_severity(a) - x_vars[a] >= -big_m * (1 - z_vars[a]) for a in edges), 'big_m_trick_LB')

    # Budget constraint
    model.addConstr(quicksum(x_vars[a] for a in edges) <= Budget_x, 'fortification_budget_constraint')

    # Optimize the model
    model.optimize()

    # Print solution
    xzs = {x: x_vars[x].X for x in x_vars}
    qzs = {q: q_vars[q].X for q in q_vars}

    if model.status == GRB.OPTIMAL:
        logger.info(f"Used budget for: {[a for a in edges if x_vars[a].X > 0]}")
        logger.info(f"Total used budget: {sum(x_vars[a].X for a in edges)}")
        for s in scenarios:
            for a in edges:
                logger.info(f"{s.get_severity(a) - x_vars[a].X} of {z_vars[a].X}")

    else:
        print("No solution found")

    print(q_vars)

    if model.status == GRB.OPTIMAL:
        print(f'Shortest paths (multi-path approach) (toy_graph_1, ODs: {od_pairs}):')
        for p in od_pairs:
            print(f'\tFor OD pair {p}')
            for a in edges:
                # Edge is in the shortest path
                if w_vars[p, a].X == 1.0:
                    exp_tt = sum(s.probability * (edges[a] + s.get_tt_impact(a)) for s in scenarios)
                    print(f"\t\tEdge from {a[0]} to {a[1]} with expected travel time {exp_tt}")
    else:
        print("No solution found")

    return model
