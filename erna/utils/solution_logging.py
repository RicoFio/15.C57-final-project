from erna.data.graph import Graph
import gurobipy as grb
import numpy as np
import logging
from typing import  Union

logging.basicConfig()
logger = logging.getLogger('erna_logging')
logger.setLevel(logging.INFO)


def log_smpd_solution(status: grb.GRB.Status, graph: Graph, od_pairs: list[tuple[int, int]],
                      pi_vars: dict[tuple[int, int], grb.Var]):

    if not status == grb.GRB.OPTIMAL:
        logger.error("No solution found")

    edges = graph.edges

    paths = []
    for p_i, (o, d) in enumerate(od_pairs):
        logger.info(f'\tFor OD pair {(o, d)}')
        path = [o]
        while path[-1] != d:
            next_node = None
            path_cost = np.inf
            for (i, j) in [e for e in edges if e[0] == path[-1]]:
                # Edge is in the shortest path
                # logger.info(f"for node i: {pi_vars[p_i, i].X}, node j: {pi_vars[p_i, j].X}")
                if o == i:
                    if pi_vars[p_i, i].X == 0.0 and 0.0 < pi_vars[p_i, j].X:
                        if pi_vars[p_i, j].X < path_cost:
                            path_cost = pi_vars[p_i, j].X
                            next_node = j
                        # logger.info(f"Edge from {i} to {j} with cost {edges[(i, j)]}")
                else:
                    if pi_vars[p_i, i].X > 0.0 and pi_vars[p_i, j].X > 0.0:
                        if pi_vars[p_i, j].X < path_cost:
                            path_cost = pi_vars[p_i, j].X
                            next_node = j
                        # logger.info(f"Edge from {i} to {j} with cost {edges[(i, j)]}")
            path.append(next_node)
        paths.append(path)
        path_tt = str(grb.quicksum([edges[(path[i - 1], path[i])] for i in range(1, len(path))]))
        logger.info(f'\t\t{path}: Travel Time: {path_tt}')
