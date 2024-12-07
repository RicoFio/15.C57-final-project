from gurobipy import Model, GRB, quicksum
import logging

from ..data_structures.graph import Graph, Scenario
from ..utility_profiles.base import base_utility_profile_function

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)


def base_e_raft(
        g: Graph, planning_budget: int,
        utility_profile_function: callable = base_utility_profile_function,
        verbose: bool = False, big_m: int = 1_000, use_mean_scenario: bool = False,
        use_single_scenario: int = None,
        fixed_adaptation_decisions: dict = None
) -> Model:

    if verbose:
        logger.setLevel(logging.INFO)

    logger.info("Starting setup of E-RAFT")

    nodes = g.nodes
    edges = g.edges
    od_pairs = g.od_pairs

    if use_mean_scenario and use_single_scenario is not None:
        raise ValueError("Cannot consider both mean and single scenarios.")

    # Select scenarios based on the model type we want to run
    if use_mean_scenario:
        scenarios = [g.get_ev_scenario()]
    elif use_single_scenario is not None:
        scenarios = [Scenario(probability=1.0,
                              edge_impact_matrix=g.scenarios[use_single_scenario].edge_impact_matrix,
                              severity_matrix=g.scenarios[use_single_scenario].severity_matrix)]
    else:
        scenarios = g.scenarios

    # Compute utility profile for each OD pair
    # This weighting is used to determine the importance of each OD pair
    # It is equal across all scenarios
    path_weighting = {}
    for p in od_pairs:
        path_weighting[p] = utility_profile_function(g, p)

    # Adaptation budget
    budget_x = planning_budget

    # Optimization formulation
    logger.info("Setting up optimization model")

    model = Model('E-RAFT')

    if not verbose:
        model.setParam('OutputFlag', 0)

    # Setup of the variables for the optimization problem
    # Decision Variables
    # Edge flow variables
    w_vars = {}
    # Decision variable representing non-linearity
    q_vars = {}
    for s, scenario in enumerate(scenarios):
        for p in od_pairs:
            for a in edges:
                # Variable representing the flow of a specific edge in a scenario
                w_vars[s, p, a] = model.addVar(name=f'w_{s}_{p}_{a}', vtype=GRB.BINARY)
                # Variable introduced to represent the non-linearity
                q_vars[s, p, a] = model.addVar(name=f'q_{s}_{p}_{a}', vtype=GRB.BINARY)

    # Decision variables representing adaptation measures on the edges
    # We can only decide this once across all scenarios
    x_vars = model.addVars(edges, obj=edges, name='x', vtype=GRB.BINARY)

    # Decision variables representing successful interdiction of edges
    # This depends on the scenario but all paths (OD pairs) are equally affected
    z_vars = {}
    for s, scenario in enumerate(scenarios):
        for a in edges:
            z_vars[s, a] = model.addVar(name=f'z_{s}_{a}', vtype=GRB.BINARY)

    # Objective: minimize the total cost of the path stochastically over all scenarios
    model.modelSense = GRB.MINIMIZE
    model.setObjective(
        quicksum(scenario.probability *
            quicksum(
                path_weighting[p] *
                quicksum(
                    edges[a] * w_vars[s, p, a] + scenario.get_tt_impact(a) * q_vars[s, p, a]
                for a in edges)
            for p in od_pairs)
        for s, scenario in enumerate(scenarios))
    )

    # Constraints
    # If X is given:
    if fixed_adaptation_decisions is not None:
        if sum(fixed_adaptation_decisions.values()) > budget_x:
            raise ValueError("The fixed adaptation decisions exceed the budget")
        for a in edges:
            model.addConstr(x_vars[a] == fixed_adaptation_decisions[a])

    # Flow
    for s, scenario in enumerate(scenarios):
        for p in od_pairs:
            origin, destination = p.origin_node, p.destination_node
            for node in nodes:
                if node != origin and node != destination:
                    model.addConstr(quicksum(w_vars[s, p, (i, j)] for i, j in edges if j == node) ==
                                    quicksum(w_vars[s, p, (j, i)] for j, i in edges if j == node), f"flow")

            # McCormick
            for a in edges:
                model.addConstr(q_vars[s, p, a] <= z_vars[s, a])
                model.addConstr(q_vars[s, p, a] <= w_vars[s, p, a])
                model.addConstr(q_vars[s, p, a] >= z_vars[s, a] + w_vars[s, p, a] - 1)

            # Exactly one edge leaving the start node and entering the end node
            model.addConstr(quicksum(w_vars[s, p, (origin, j)] for j in nodes if (origin, j) in edges) == 1, 'p_outward_edge')
            model.addConstr(quicksum(w_vars[s, p, (i, destination)] for i in nodes if (i, destination) in edges) == 1,
                            'p_inward_edge')

        model.addConstrs((scenario.get_severity(a) - x_vars[a] <= big_m * z_vars[s, a] for a in edges), 'big_m_trick_UB')
        model.addConstrs((scenario.get_severity(a) - x_vars[a] >= -big_m * (1 - z_vars[s, a]) for a in edges), 'big_m_trick_LB')

    # Budget constraint
    model.addConstr(quicksum(x_vars[a] for a in edges) <= budget_x, 'adaptation_budget_constraint')

    # Optimize the model
    model.optimize()

    # Log solution
    if model.status == GRB.OPTIMAL:
        logger.info(f"Used budget for: {[a for a in edges if x_vars[a].X > 0]}")
        logger.info(f"Total used budget: {sum(x_vars[a].X for a in edges)}")
        for s, scenario in enumerate(scenarios):
            logger.info(f"Scenario {s}")
            for a in edges:
                logger.info(f"\t Adaptation success {scenario.get_severity(a) - x_vars[a].X} "
                            f"with a {'successful' if z_vars[s, a].X > 0 else 'unsuccesful'} interdiction")

        logger.info(f'Expected shortest path travel time for every OD: {od_pairs}):')
        for p in od_pairs:
            logger.info(f'\tFor OD pair {p}')
            for a in edges:
                exp_tt = sum([scenario.probability * (edges[a] + scenario.get_tt_impact(a) * w_vars[s, p, a]) for s, scenario in enumerate(scenarios)])
                logger.info(f"\t\tEdge from {a[0]} to {a[1]} with expected travel time {exp_tt}")
    else:
        logger.warning("No solution found")

    return model
