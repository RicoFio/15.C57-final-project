from gurobipy import Model, GRB, quicksum
from erna.toy_data.toy_graph_1 import toy_graph_1

nodes = toy_graph_1.nodes
edges = toy_graph_1.edges
start_node, end_node = toy_graph_1.od_pairs[0]

# Create a new model
model = Model('ShortestPath')
# Suppress stdout
model.setParam('OutputFlag', 0)

# Add variables for edges
w = model.addVars(edges, obj=edges, name='edge', vtype=GRB.BINARY)

# Add constraints
# Each node (except start and end) should have equal inflow and outflow
for node in nodes:
    if node != start_node and node != end_node:
        model.addConstr(quicksum(w[i, j] for i, j in edges if j == node) == 
                        quicksum(w[j, i] for j, i in edges if j == node), f"flow")

# Exactly one edge leaving the start node and entering the end node
model.addConstr(quicksum(w[start_node, j] for j in nodes if (start_node, j) in edges) == 1, 'outward_edge')
model.addConstr(quicksum(w[i, end_node] for i in nodes if (i, end_node) in edges) == 1, 'inward_edge')

# Objective: minimize the total cost of the path
model.setObjective(quicksum(w[e] * edges[e]for e in edges), GRB.MINIMIZE)

# Optimize the model
model.optimize()

# Print solution
if model.status == GRB.OPTIMAL:
    print(f'Shortest path (toy_graph_1, OD: {(start_node, end_node)}):')
    for edge in edges:
        # Edge is in the shortest path
        if w[edge].X > 0.0:
            print(f"Edge from {edge[0]} to {edge[1]} with cost {edges[edge]}")
else:
    print("No solution found")
