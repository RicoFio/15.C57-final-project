import numpy as np
from gurobipy import Model, GRB, quicksum
from erna.toy_data.toy_graph_1 import toy_graph_1
from erna.data.graph import Graph
import logging
from matplotlib import pyplot as plt

logging.basicConfig()
logger = logging.getLogger('erna_logging')
logger.setLevel(logging.INFO)


def fixed_interdiction(graph: Graph, interdictions: dict[tuple[int, int], int],
                       fortifications: dict[tuple[int, int], int], interdiction_delay: float,
                       path_weightings: dict[tuple[int, int], int] = None):
    nodes = graph.nodes
    edges = graph.edges
    od_pairs = graph.od_pairs

    path_weights = {}
    for (o, d) in od_pairs:
        tg_b = toy_graph_1.get_neighborhood_people_count_per_group(o)
        tg_s = toy_graph_1.get_neighborhood_mhhi(o)
        path_weights[o, d] = sum([b / s for s, b in zip(tg_s, tg_b)])

    # path_weighting = {k: v/sum(path_weighting.values()) for k, v in path_weighting.items()}
    path_weights = path_weightings if path_weightings is not None else path_weights
    logger.info(f"Path Weighting: {path_weights}")

    M = 1000

    # Create a new model
    model = Model('FullProblemFormulation')
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
        path_weights[p] * quicksum(
            edges[a] * w_vars[p, a] + interdiction_delay * q_vars[p, a] for a in edges
        ) for p in od_pairs)
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
        # Big M trick
        model.addConstr(interdictions[a] - fortifications[a] <= M * z_vars[a], 'big_m_trick_UB')
        model.addConstr(interdictions[a] - fortifications[a] >= -M * (1 - z_vars[a]), 'big_m_trick_LB')

    # Optimize the model
    model.optimize()
    # print(z_vars)
    # Print solution
    shortest_paths = {}
    travel_times = {}

    if model.status == GRB.OPTIMAL:
        logger.debug('Shortest paths (multi-path approach):')
        for p in od_pairs:
            logger.debug(f'\tFor OD pair {p}')
            shortest_paths[p] = [p[0]]
            travel_times[p] = 0
            for a in filter(lambda x: x[0] == shortest_paths[p][-1], edges):
                # Edge is in the shortest path
                if round(w_vars[p, a].X) == 1.0:
                    logger.debug(f"\t\tEdge from {a[0]} to {a[1]} with cost {edges[a]}")
                    shortest_paths[p].append(a[1])
                    travel_times[p] += edges[a]
        return shortest_paths, travel_times, model.ObjVal
    else:
        raise RuntimeError("No solution found")


def get_text_color(value, threshold=0.2):
    """
    Return 'white' or 'black' depending on the brightness of the background color.
    """
    return 'white' if value < threshold else 'black'


if __name__ == "__main__":
    graph = toy_graph_1

    interdictions = []
    fortifications = []

    for a in graph.edges:
        fortifications.append({e: 1 for e in toy_graph_1.edges})
        interdictions.append({e: 2 if a==e else 0 for e in graph.edges})

    shortest_paths = []
    travel_times = []
    model_objs = []

    for fort, inter in zip(fortifications, interdictions):
        res = fixed_interdiction(toy_graph_1, inter, fort, 10)
        shortest_paths.append(res[0])
        travel_times.append(list(res[1].values()))
        model_objs.append(res[2])

    arr = np.array(travel_times).T
    arr = np.append(arr, np.array(model_objs).reshape(1, -1), axis=0)

    # Create the plot
    fig, ax = plt.subplots(figsize=(8, 8))
    heatmap = ax.imshow(arr, cmap='viridis', interpolation='nearest')

    # Add text annotations (numbers) on each cell
    for i in range(arr.shape[0]):
        for j in range(arr.shape[1]):
            color = get_text_color(arr[i, j], arr.mean())
            text = ax.text(j, i, str(arr[i, j]),
                            ha="center", va="center", color=color, fontsize=14)

    # plt.colorbar(heatmap)
    ax.set_xticks(np.arange(len(graph.edges)))
    ax.set_xticklabels([str(s) for s in list(graph.edges)], fontsize=14)
    ax.set_xlabel('Interdictions', fontsize=18, labelpad=20)

    ax.set_yticks([0, 1, 2])
    ax.set_yticklabels([f'TT {graph.od_pairs[0]}', f'TT {graph.od_pairs[1]}', 'OBJ'], fontsize=14)

    # ax.set_title("Hello")

    # Show the plot
    # plt.show()
    # plt.savefig('./evaluation_matrix.png', dpi=300, bbox_inches='tight')
