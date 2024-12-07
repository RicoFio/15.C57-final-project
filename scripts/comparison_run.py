from eraft.optimization.stochastic_e_raft import stochastic_e_raft
from eraft.optimization.wait_and_see_e_raft import wait_and_see_e_raft
from eraft.optimization.deterministic_e_raft import deterministic_e_raft
from eraft.utility_profiles.base import base_utility_profile_function
from eraft.toy_data import toy_graph_1, toy_graph_2
import logging

logging.basicConfig()
logger = logging.getLogger(__file__)
logger.setLevel(logging.INFO)


if __name__ == '__main__':
    g = toy_graph_2
    planning_budget = 2

    # Stochastic run
    stochastic_obj_value = stochastic_e_raft(
        g=g,
        planning_budget=planning_budget,
        utility_profile_function=base_utility_profile_function,
        verbose=False, big_m=1_000
    )

    # Wait and see run
    wait_and_see_obj_value = wait_and_see_e_raft(
        g=g,
        planning_budget=planning_budget,
        utility_profile_function=base_utility_profile_function,
        verbose=False, big_m=1_000,
    )

    # Deterministic run
    deterministic_obj_value = deterministic_e_raft(
        g=g,
        planning_budget=planning_budget,
        utility_profile_function=base_utility_profile_function,
        verbose=False, big_m=1_000,
    )

    logger.info(f"Stochastic objective value: {stochastic_obj_value}")
    logger.info(f"Wait and see objective value: {wait_and_see_obj_value}")
    logger.info(f"Deterministic objective value: {deterministic_obj_value}")
