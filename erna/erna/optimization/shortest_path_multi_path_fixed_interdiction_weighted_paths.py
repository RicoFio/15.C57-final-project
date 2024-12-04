from gurobipy import Model, GRB, quicksum
from erna.toy_data.toy_graph_1 import toy_graph_1

nodes = toy_graph_1.nodes
edges = toy_graph_1.edges
od_pairs = toy_graph_1.od_pairs
interdiction_delay = 10
interdictions = {e: 0 for e in toy_graph_1.edges}
interdictions[1, 2] = 2
fortifications = {e: 1 for e in toy_graph_1.edges}


def fixed_interdiction():
    path_weighting = {}
    for (o, d) in od_pairs:
        tg_b = toy_graph_1.get_neighborhood_people_count_per_group(o)
        tg_s = toy_graph_1.get_neighborhood_mhhi(o)
        path_weighting[o, d] = sum([s / b for s, b in zip(tg_s, tg_b)])

    # path_weighting = {k: v/sum(path_weighting.values()) for k, v in path_weighting.items()}
    path_weighting = {(0, 3): 1, (1, 2): 1000}
    print("Path Weighting", path_weighting)

    M = 1000

    # Create a new model
    model = Model('ShortestPathMultiOD')
    # Suppress stdout
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

    # Successful interdiction variable
    z_vars = model.addVars(edges, obj=edges, name='z', vtype=GRB.BINARY)

    # Objective: minimize the total cost of the path
    model.modelSense = GRB.MINIMIZE
    model.setObjective(quicksum(
            path_weighting[p] * (edges[a] * w_vars[p, a] + interdiction_delay * q_vars[p, a]) for p in od_pairs for a in edges)
    )

    # Constraints
    # Flow
    for p in od_pairs:
        origin, destination = p
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
    for a in edges:
        # Big M
        model.addConstrs((interdictions[a] - fortifications[a] <= M * z_vars[a] for a in edges), 'big_m_trick_UB')
        model.addConstrs((interdictions[a] - fortifications[a] >= -M * (1 - z_vars[a]) for a in edges), 'big_m_trick_LB')

    # Optimize the model
    model.optimize()
    # print(z_vars)
    # Print solution
    if model.status == GRB.OPTIMAL:
        print(f'Shortest paths (multi-path approach) (toy_graph_1, ODs: {od_pairs}):')
        for p in od_pairs:
            print(f'\tFor OD pair {p}')
            for a in edges:
                # Edge is in the shortest path
                if w_vars[p, a].X == 1.0:
                    print(f"\t\tEdge from {a[0]} to {a[1]} with cost {edges[a]}")
    else:
        print("No solution found")

if __name__=="__main__":
    fixed_interdiction()