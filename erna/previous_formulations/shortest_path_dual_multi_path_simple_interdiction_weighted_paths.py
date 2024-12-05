from gurobipy import Model, GRB, quicksum
from erna.toy_data.toy_graph_1 import toy_graph_1
import numpy as np

# Define nodes, edges, and costs
nodes = toy_graph_1.nodes
edges = toy_graph_1.edges
od_pairs = toy_graph_1.od_pairs
interdiction_delay = 10
interdiction_budget = 1

path_weighting = {}
for (o, d) in od_pairs:
    tg_b = toy_graph_1.get_neighborhood_people_count_per_group(o)
    tg_s = toy_graph_1.get_neighborhood_mhhi(o)
    path_weighting[o, d] = sum([s/b for s, b in zip(tg_s, tg_b)])

# path_weighting = {k: v/sum(path_weighting.values()) for k, v in path_weighting.items()}
path_weighting = {(0, 3): 10000, (1, 2): 1}
print("Path Weighting", path_weighting)

# Create a new model
model = Model('ShortestPathDualMultiPathInterdiction')
# Suppress stdout
model.setParam('OutputFlag', 0)

# Add variables for edges
pi_vars = {}
for p in od_pairs:
    for n in nodes:
        pi_vars[p, n] = model.addVar(name=f'pi_{p}_{n}', vtype=GRB.CONTINUOUS)

x_vars = model.addVars(edges, obj=edges, name='x', vtype=GRB.BINARY)

# Add constraints
# For each edge, ensure that the nodes follow the constraints of the dual variables
for p in od_pairs:
    for (i, j) in edges:
        # The difference of the out minus the in node's dual variable pi is smaller or equal to the cost of the edge
        model.addConstr(pi_vars[p, j] - pi_vars[p, i] - x_vars[(i, j)] * interdiction_delay <= edges[(i, j)], f"dual_flow_{i}_{j}")

# Exactly one edge leaving the start node and entering the end node
for p in od_pairs:
    model.addConstr(pi_vars[p, p[0]] == 0, 'source_node_zero')

# Only up to budget_x interdictions
model.addConstr(quicksum(x_vars) <= interdiction_budget)

# Objective: maximize the difference of the sink pi - the source pi
model.setObjective(quicksum(path_weighting[p]*(pi_vars[p, p[1]] - pi_vars[p, p[0]]) for p in od_pairs), GRB.MAXIMIZE)

# Optimize the model
model.optimize()

# Print solution
if model.status == GRB.OPTIMAL:
    print(f'Shortest path (dual formulation | multi-path) (toy_graph_1, ODs: {od_pairs}):')
    # print(pi_vars)
    paths = []
    for p in od_pairs:
        print(f'\tFor OD pair {p}')
        print(f'\t\tInterdicted: {[inter for inter in x_vars if round(x_vars[inter].X) == 1]}')
        path = [p[0]]
        while path[-1] != p[1]:
            next_node = None
            path_cost = np.inf
            for (i, j) in [e for e in edges if e[0] == path[-1]]:
                # Edge is in the shortest path
                # print(f"for node i: {pi_vars[p, i].X}, node j: {pi_vars[p, j].X}")
                if p[0] == i:
                    if pi_vars[p, i].X == 0.0 and 0.0 < pi_vars[p, j].X:
                        if pi_vars[p, j].X < path_cost:
                            path_cost = pi_vars[p, j].X
                            next_node = j
                        # print(f"Edge from {i} to {j} with cost {edges[(i, j)]}")
                else:
                    if pi_vars[p, i].X > 0.0 and pi_vars[p, j].X > 0.0:
                        if pi_vars[p, j].X < path_cost:
                            path_cost = pi_vars[p, j].X
                            next_node = j
                        # print(f"Edge from {i} to {j} with cost {edges[(i, j)]}")
            path.append(next_node)
        paths.append(path)
        print('\t\t', path, 'travel time:', quicksum([edges[(path[i - 1], path[i])] for i in range(1, len(path))]))
    print('Interdictions:', {k: v.X for k, v in x_vars.items()})
else:
    print("No solution found")
