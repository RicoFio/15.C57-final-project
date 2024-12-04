from gurobipy import Model, GRB, quicksum
from erna.toy_data.toy_graph_1 import toy_graph_1
import numpy as np
import random
import logging
import argparse

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Set up argument parser
parser = argparse.ArgumentParser(description='input params')
parser.add_argument('--seed', type=int, default=0, help='Random seed')
parser.add_argument('--stage', type=int, required=True, help='Stage number')

# Parse arguments
args = parser.parse_args()

if args.stage == 1:
    stage = 1
else:
    stage = 2

##############################################################
# SETUP
##############################################################
logger.info("Starting setup of stochastic optimization")

nodes = toy_graph_1.nodes
edges = toy_graph_1.edges
od_pairs = toy_graph_1.od_pairs
interdiction_delay = 10

path_weighting = {}
for (o, d) in od_pairs:
    tg_b = toy_graph_1.get_neighborhood_people_count_per_group(o)
    tg_s = toy_graph_1.get_neighborhood_mhhi(o)
    path_weighting[o, d] = sum([b/s for s, b in zip(tg_s, tg_b)])

# path_weighting = {k: v/sum(path_weighting.values()) for k, v in path_weighting.items()}
# path_weighting = {(0, 3): 1, (1, 2): 1000}

# Fortification
Budget_x = 100
random.seed(0)

# Extreme weather data ######### looks like we are sampling from the distribution for each scenario and then run the n scenarios
num_scenarios = 2
alpha = [1/num_scenarios]*num_scenarios

# S = ["No Rain", "Rain", "Storm", "Thunderstorm", "Flooding"]
weather_probs = [0.4, 0.25, 0.2, 0.1, 0.05]
interdiction_extent = [0, 1, 3, 7, 11]
interdiction_uncertainty = [0.5, 1, 2, 3, 4]

scenario_sample = np.random.choice(list(range(len(weather_probs))), p=weather_probs, size=num_scenarios)
scenario_ies = [interdiction_extent[i] for i in scenario_sample]
scenario_ius = [interdiction_uncertainty[i] for i in scenario_sample]

print(scenario_ies)
print(scenario_ius)
interdiction_sample = {}
for s in range(num_scenarios):
    for a in edges:
        interdiction_sample[s, a] = np.floor(np.random.normal(scenario_ies[s], scenario_ius[s], 1)[0])
        # No negative interdiction
        interdiction_sample[s, a] = 0 if interdiction_sample[s, a] < 0 else interdiction_sample[s, a]
print(interdiction_sample)
# Big M trick
M = 1_000

##############################################################
# Optimization
##############################################################
logger.info("Setting up optimization model")

model = Model('StochasticShortestMultiPathInterdictionDET')
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

##############################################################
# STAGE 1
##############################################################
if stage == 1:
    # Fortification planning
    x_vars = model.addVars(edges, obj=edges, name='x', vtype=GRB.BINARY)

    # Objective: minimize the total cost of the path
    model.modelSense = GRB.MINIMIZE
    model.setObjective(
        quicksum(
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
    for s in range(num_scenarios):
        for a in edges:
            # Big M
            model.addConstrs((quicksum(alpha[s] * (interdiction_sample[s, a]) for s in range(num_scenarios)) - x_vars[a] <= M * z_vars[a] for a in edges), 'big_m_trick_UB')
            model.addConstrs((quicksum(alpha[s] * (interdiction_sample[s, a]) for s in range(num_scenarios)) - x_vars[a] >= -M * (1 - z_vars[a]) for a in edges), 'big_m_trick_LB')

##############################################################
# STAGE 2
##############################################################
else:
    # Fortification planning
    # read previously saved xzs
    x_vars = np.load(f"../toy_data/x_vars_1_{args.seed}_det.npy", allow_pickle=True).item()

    # Objective: minimize the total cost of the path
    model.modelSense = GRB.MINIMIZE
    model.setObjective(
        quicksum(alpha[s] * quicksum(
            path_weighting[p] * (edges[a] * w_vars[p, a] + interdiction_delay * q_vars[p, a]) for p in od_pairs for a in edges)
        for s in range(num_scenarios))
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
    for s in range(num_scenarios):
        for a in edges:
            # Big M
            model.addConstrs((interdiction_sample[s, a] - x_vars[a] <= M * z_vars[a] for a in edges), 'big_m_trick_UB')
            model.addConstrs((interdiction_sample[s, a] - x_vars[a] >= -M * (1 - z_vars[a]) for a in edges), 'big_m_trick_LB')

# Budget constraint
model.addConstr(quicksum(x_vars[a] for a in edges) <= Budget_x, 'fortification_budget_constraint')

# Optimize the model
model.optimize()

print("DETERMINISTIC")
# Print solution
xzs = {x: x_vars[x].X for x in x_vars}
qzs = {q: q_vars[q].X for q in q_vars}

# save the results
np.save(f"../toy_data/x_vars_{args.stage}_{args.seed}_det.npy", xzs)

logger.info(f"x_vars: {xzs}")
logger.info(f"q_vars: {qzs}")

if model.status == GRB.OPTIMAL:
    logger.info(f"Used budget: {sum(x_vars[a].X for a in edges)}")
    print(f"Optimal objective value: {model.objVal}")
    for s in range(num_scenarios):
        for a in edges:
            # Big M
            logger.info(f"{interdiction_sample[s, a] - x_vars[a].X} of {z_vars[a].X}")
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
                print(f"\t\tEdge from {a[0]} to {a[1]} with cost {edges[a]}")
else:
    print("No solution found")
