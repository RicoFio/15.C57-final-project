from eraft.optimization.wait_and_see_e_raft import wait_and_see_e_raft
from eraft.utility_profiles.base import base_utility_profile_function
from eraft.toy_data import toy_graph_1, toy_graph_2
import logging

logging.basicConfig()
logger = logging.getLogger(__file__)
logger.setLevel(logging.INFO)


if __name__ == '__main__':
    g = toy_graph_2
    planning_budget = 3
    wait_and_see_obj = wait_and_see_e_raft(
        g=g,
        planning_budget=planning_budget,
        utility_profile_function=base_utility_profile_function,
        verbose=False, big_m=1_000,
    )
    logger.info(wait_and_see_obj)
