from eraft.optimization.stochastic_e_raft import stochastic_e_raft
from eraft.utility_profiles.base import base_utility_profile_function
from eraft.toy_data import toy_graph_2
import logging

logging.basicConfig()
logger = logging.getLogger(__file__)
logger.setLevel(logging.INFO)


if __name__ == '__main__':
    g = toy_graph_2
    planning_budget = 3
    stochastic_obj_value = stochastic_e_raft(
        g=g,
        planning_budget=planning_budget,
        utility_profile_function=base_utility_profile_function,
        verbose=False, big_m=1_000,
    )
    logger.info(f"Final objective value: {stochastic_obj_value}")
