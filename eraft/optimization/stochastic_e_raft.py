from ._base_e_raft import base_e_raft
from ..data_structures.graph import Graph
from ..utility_profiles.base import base_utility_profile_function
import logging

logging.basicConfig()
logger = logging.getLogger(__file__)
logger.setLevel(logging.WARNING)


def stochastic_e_raft(g: Graph, planning_budget: int,
                        utility_profile_function: callable = base_utility_profile_function,
                        verbose: bool = False, big_m: int = 1_000) -> float:

    if verbose:
        logger.setLevel(logging.INFO)

    stochastic_model = base_e_raft(
        g=g,
        planning_budget=planning_budget,
        utility_profile_function=utility_profile_function,
        verbose=verbose, big_m=big_m
    )

    adaptation_choice = {e: stochastic_model.getVarByName(f'x[{e[0]},{e[1]}]').X for e in g.edges.keys()}

    return stochastic_model.getObjective().getValue(), adaptation_choice
