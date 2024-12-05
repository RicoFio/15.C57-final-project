from gurobipy import Model, GRB, quicksum

from erna.toy_data.toy_graph_2 import toy_graph_2
import numpy as np
import random
import logging

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

##############################################################
# SETUP
##############################################################
logger.info("Starting setup of stochastic optimization")

nodes = toy_graph_2.nodes
edges = toy_graph_2.edges
od_pairs = toy_graph_2.od_pairs
scenarios = toy_graph_2.scenarios

path_weighting = {}
for p in od_pairs:
    tg_b = p.demand
    tg_s = toy_graph_2.get_neighborhood_mhhi(p.origin_node, p.demographic_group)[0]
    path_weighting[p] = tg_b/tg_s

# path_weighting = {k: v/sum(path_weighting.values()) for k, v in path_weighting.items()}
# path_weighting = {(0, 3): 1, (1, 2): 1000}

# Fortification
Budget_x = 3
random.seed(0)

# Big M trick
M = 1_000

##############################################################
# Optimization
##############################################################
logger.info("Setting up optimization model")

model = Model('StochasticShortestMultiPathInterdiction')
# Suppress stdout
model.setParam('OutputFlag', 0)
# Wait-and-see costs and solutions
ws_costs = []  # Store objective values for each scenario
ws_results = {}  # Store decision variables for each scenario

for s in scenarios:
    logger.info(f"Starting wait-and-see optimization for scenario {s}")
    
    # Create a new model for this scenario
    ws_model = Model(f'WaitAndSee_Scenario_{s}')
    ws_model.setParam('OutputFlag', 0)
    
    # Decision Variables
    w_vars = {}
    q_vars = {}
    for p in od_pairs:
        for a in edges:
            w_vars[p, a] = ws_model.addVar(name=f'w_{a}', vtype=GRB.BINARY)
            q_vars[p, a] = ws_model.addVar(name=f'q_{a}', vtype=GRB.BINARY)
    
    x_vars = ws_model.addVars(edges, name='x', vtype=GRB.BINARY)
    z_vars = ws_model.addVars(edges, name='z', vtype=GRB.BINARY)
    
    # Objective: Minimize total cost for this scenario
    ws_model.setObjective(
        quicksum(
            path_weighting[p] * (edges[a] * w_vars[p, a] + s.get_tt_impact(a) * q_vars[p, a]) 
            for p in od_pairs for a in edges
        ), GRB.MINIMIZE
    )
    
    # Constraints
    for p in od_pairs:
        origin, destination = p.origin_node, p.destination_node
        
        # Flow constraints
        for node in nodes:
            if node != origin and node != destination:
                ws_model.addConstr(
                    quicksum(w_vars[p, (i, j)] for i, j in edges if j == node) ==
                    quicksum(w_vars[p, (j, i)] for j, i in edges if j == node),
                    f"flow_{node}_{p}"
                )
        
        # McCormick relaxation for q_vars
        for a in edges:
            ws_model.addConstr(q_vars[p, a] <= z_vars[a])
            ws_model.addConstr(q_vars[p, a] <= w_vars[p, a])
            ws_model.addConstr(q_vars[p, a] >= z_vars[a] + w_vars[p, a] - 1)
        
        # Path constraints
        ws_model.addConstr(
            quicksum(w_vars[p, (origin, j)] for j in nodes if (origin, j) in edges) == 1,
            f'p_outward_edge_{p}'
        )
        ws_model.addConstr(
            quicksum(w_vars[p, (i, destination)] for i in nodes if (i, destination) in edges) == 1,
            f'p_inward_edge_{p}'
        )
    
    # Big-M constraints for this scenario
    for a in edges:
        ws_model.addConstr(s.get_severity(a) - x_vars[a] <= M * z_vars[a], f'big_m_ub_{a}')
        ws_model.addConstr(s.get_severity(a) - x_vars[a] >= -M * (1 - z_vars[a]), f'big_m_lb_{a}')
    
    # Budget constraint
    ws_model.addConstr(quicksum(x_vars[a] for a in edges) <= Budget_x, 'fortification_budget')
    
    # Solve the model
    ws_model.optimize()
    
    # Store results
    if ws_model.status == GRB.OPTIMAL:
        ws_costs.append(ws_model.objVal)
        logger.info(f"Used budget for: {[a for a in edges if x_vars[a].X > 0]}")
        logger.info(f"Optimal cost for scenario {s}: {ws_model.objVal}")
        for p in od_pairs:
            print(f'\tFor OD pair {p}')
            for a in edges:
                # Edge is in the shortest path
                if w_vars[p, a].X == 1.0:
                    exp_tt = sum(s.probability * (edges[a] + s.get_tt_impact(a)) for s in scenarios)
                    print(f"\t\tEdge from {a[0]} to {a[1]} with expected travel time {exp_tt}")
    else:
        logger.warning(f"No optimal solution found for scenario {s}")

# Calculate expected cost
expected_ws_cost = np.mean(ws_costs)
print(f"Expected wait-and-see cost: {expected_ws_cost}")