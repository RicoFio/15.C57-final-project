from gurobipy import Model, GRB, quicksum
from erna.toy_data.toy_graph_1 import toy_graph_1
import numpy as np

# Define nodes, edges, and costs
nodes = toy_graph_1.nodes
edges = toy_graph_1.edges
start_node, end_node = toy_graph_1.od_pairs[0]
interdiction_delay = 10
interdiction_budget = 1

tg_b = toy_graph_1.get_neighborhood_people_count_per_group(start_node)
tg_s = toy_graph_1.get_neighborhood_mhhi(start_node)
path_weighting = quicksum([s/b for s, b in zip(tg_s, tg_b)])
# Create a new model
model = Model('ShortestPathDualInterdiction')
# Suppress stdout
model.setParam('OutputFlag', 0)

# Add variables for edges
pi_vars = model.addVars(nodes, obj=nodes, name='pi')
x_vars = model.addVars(edges, obj=edges, name='x', vtype=GRB.BINARY)

# Add constraints
# For each edge, ensure that the nodes follow the constraints of the dual variables
for (i, j) in edges:
    # The difference of the out minus the in node's dual variable pi is smaller or equal to the cost of the edge
    model.addConstr(path_weighting*(pi_vars[j] - pi_vars[i]) - x_vars[(i, j)] * interdiction_delay <= edges[(i, j)], f"dual_flow_{i}_{j}")

# Exactly one edge leaving the start node and entering the end node
model.addConstr(pi_vars[start_node] == 0, 'source_node_zero')

# Only up to budget_x interdictions
model.addConstr(quicksum(x_vars) <= interdiction_budget)

# Objective: maximize the difference of the sink pi - the source pi
model.setObjective(pi_vars[end_node] - pi_vars[start_node], GRB.MAXIMIZE)

# Optimize the model
model.optimize()

# Print solution
if model.status == GRB.OPTIMAL:
    print(f'Shortest path (dual formulation) (toy_graph_1, ODs: {(start_node, end_node)}):')
    # print(pi_vars)
    print(f'For OD: {(start_node, end_node)}')
    path = [start_node]
    while path[-1] != end_node:
        next_node = None
        path_cost = np.inf
        for (i, j) in [e for e in edges if e[0] == path[-1]]:
            # Edge is in the shortest path
            # print(f"for node i: {pi_vars[i].X}, node j: {pi_vars[j].X}")
            if start_node == i:
                if pi_vars[i].X == 0.0 and 0.0 < pi_vars[j].X:
                    if pi_vars[j].X < path_cost:
                        path_cost = pi_vars[j].X
                        next_node = j
                    # print(f"Edge from {i} to {j} with cost {edges[(i, j)]}")
            else:
                if pi_vars[i].X > 0.0 and pi_vars[j].X > 0.0:
                    if pi_vars[j].X < path_cost:
                        path_cost = pi_vars[j].X
                        next_node = j
                    # print(f"Edge from {i} to {j} with cost {edges[(i, j)]}")
        path.append(next_node)
    print(path, 'travel time:', quicksum([edges[(path[i-1], path[i])] for i in range(1, len(path))]))
    print('Interdictions:', {k: v.X for k, v in x_vars.items()})
else:
    print("No solution found")
