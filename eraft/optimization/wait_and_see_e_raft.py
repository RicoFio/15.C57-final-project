from ._base_e_raft import base_e_raft
from ..data_structures.graph import Graph
from ..utility_profiles.base import base_utility_profile_function
import logging

logging.basicConfig()
logger = logging.getLogger(__file__)
logger.setLevel(logging.WARNING)


def wait_and_see_e_raft(g: Graph, planning_budget: int,
                        utility_profile_function: callable = base_utility_profile_function,
                        verbose: bool = False, big_m: int = 1_000) -> float:

    if verbose:
        logger.setLevel(logging.INFO)

    expected_objective = 0
    adaptation_choices = []

    for i, scenario in enumerate(g.scenarios):

        scenario_model = base_e_raft(
            g=g,
            planning_budget=planning_budget,
            utility_profile_function=utility_profile_function,
            verbose=verbose, big_m=big_m, use_mean_scenario=False,
            use_single_scenario=i
        )

        scenario_obj_value = scenario_model.getObjective().getValue()
        logger.info(f"Value for scenario {i}: {scenario_obj_value}")
        expected_objective += scenario.probability * scenario_obj_value
        adaptation_choices.append({e: scenario_model.getVarByName(f'x[{e[0]},{e[1]}]').X for e in g.edges.keys()})


    return expected_objective, adaptation_choices
