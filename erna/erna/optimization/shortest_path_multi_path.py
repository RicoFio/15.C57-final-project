from gurobipy import Model, GRB, quicksum
from erna.toy_data.toy_graph_1 import toy_graph_1

nodes = toy_graph_1.nodes
edges = toy_graph_1.edges
od_pairs = toy_graph_1.od_pairs

# Create a new model
model = Model('ShortestPathMultiOD')
# Suppress stdout
model.setParam('OutputFlag', 0)

# Add variables for edges
p_edge_vars = {k: None for k in od_pairs}

for p in p_edge_vars:
    p_edge_vars[p] = model.addVars(edges, obj=edges, name='edge', vtype=GRB.BINARY)

# Add constraints
# Each node (except start and end) should have equal inflow and outflow
for p in od_pairs:
    origin, destination = p
    for node in nodes:
        if node != origin and node != destination:
            model.addConstr(quicksum(p_edge_vars[p][i, j] for i, j in edges if j == node) ==
                            quicksum(p_edge_vars[p][j, i] for j, i in edges if j == node), f"flow")

    # Exactly one edge leaving the start node and entering the end node
    model.addConstr(quicksum(p_edge_vars[p][origin, j] for j in nodes if (origin, j) in edges) == 1, 'p_outward_edge')
    model.addConstr(quicksum(p_edge_vars[p][i, destination] for i in nodes if (i, destination) in edges) == 1, 'p_inward_edge')

# Objective: minimize the total cost of the path
model.setObjective(quicksum(p_edge_vars[p][e] * edges[e] for p in p_edge_vars for e in edges), GRB.MINIMIZE)

# Optimize the model
model.optimize()

# Print solution
if model.status == GRB.OPTIMAL:
    print(f'Shortest paths (multi-path approach) (toy_graph_1, ODs: {od_pairs}):')
    for p in od_pairs:
        print(f'\tFor OD pair {p}')
        for edge in edges:
            # Edge is in the shortest path
            if p_edge_vars[p][edge].X == 1.0:
                print(f"\t\tEdge from {edge[0]} to {edge[1]} with cost {edges[edge]}")
else:
    print("No solution found")
