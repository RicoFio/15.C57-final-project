from gurobipy import Model, GRB, quicksum
from erna.toy_data.toy_graph_1 import toy_graph_1
import numpy as np

# Define nodes, edges, and costs
nodes = toy_graph_1.nodes
edges = toy_graph_1.edges
od_pairs = toy_graph_1.od_pairs
interdiction_delay = 10
interdiction_budget = 2

# Create a new model
model = Model('ShortestPathDualMultiPathInterdiction')
# Suppress stdout
model.setParam('OutputFlag', 0)
# Suppress stdout
model.setParam('OutputFlag', 0)

# Add variables for edges
pi_vars = model.addVars(len(od_pairs), len(nodes), name='pi', vtype=GRB.CONTINUOUS)
x_vars = model.addVars(edges, obj=edges, name='x', vtype=GRB.BINARY)

# Add constraints
# For each edge, ensure that the nodes follow the constraints of the dual variables
for p_i, (o, d) in enumerate(od_pairs):
    for (i, j) in edges:
        # The difference of the out minus the in node's dual variable pi is smaller or equal to the cost of the edge
        model.addConstr(pi_vars[p_i, j] - pi_vars[p_i, i] - x_vars[(i, j)] * interdiction_delay <= edges[(i, j)], f"dual_flow_{i}_{j}")

# Exactly one edge leaving the start node and entering the end node
for p_i, (o, d) in enumerate(od_pairs):
    model.addConstr(pi_vars[p_i, o] == 0, 'source_node_zero')

# Objective: maximize the difference of the sink pi - the source pi
model.setObjective(quicksum(pi_vars[p_i, d] - pi_vars[p_i, o] for p_i, (o, d) in enumerate(od_pairs)), GRB.MAXIMIZE)

# Only up to budget_x interdictions
model.addConstr(quicksum(x_vars) <= interdiction_budget)

# Optimize the model
model.optimize()

# Print solution
if model.status == GRB.OPTIMAL:
    print(f'Shortest path (dual formulation | multi-path) (toy_graph_1, ODs: {od_pairs}):')
    # print(pi_vars)
    paths = []
    for p_i, (o, d) in enumerate(od_pairs):
        print(f'\tFor OD pair {(o, d)}')
        path = [o]
        while path[-1] != d:
            next_node = None
            path_cost = np.inf
            for (i, j) in [e for e in edges if e[0] == path[-1]]:
                # Edge is in the shortest path
                print(f"for node i: {pi_vars[p_i, i].X}, node j: {pi_vars[p_i, j].X}")
                if o == i:
                    if pi_vars[p_i, i].X == 0.0 and 0.0 < pi_vars[p_i, j].X:
                        if pi_vars[p_i, j].X < path_cost:
                            path_cost = pi_vars[p_i, j].X
                            next_node = j
                        # print(f"Edge from {i} to {j} with cost {edges[(i, j)]}")
                else:
                    if pi_vars[p_i, i].X > 0.0 and pi_vars[p_i, j].X > 0.0:
                        if pi_vars[p_i, j].X < path_cost:
                            path_cost = pi_vars[p_i, j].X
                            next_node = j
                        # print(f"Edge from {i} to {j} with cost {edges[(i, j)]}")
            path.append(next_node)
        paths.append(path)
        print(path, 'travel time:', quicksum([edges[(path[i - 1], path[i])] for i in range(1, len(path))]))
else:
    print("No solution found")
