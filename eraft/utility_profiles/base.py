from ..data_structures.graph import Graph, ODPair


def base_utility_profile_function(g: Graph, p: ODPair) -> float:
    tg_b = p.demand
    tg_s = g.get_neighborhood_mhhi(p.origin_node, p.demographic_group)[0]
    return tg_b / tg_s
