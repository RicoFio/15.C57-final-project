from ._base_e_raft import base_e_raft
from ..data_structures.graph import Graph
from ..utility_profiles.base import base_utility_profile_function
import logging

logging.basicConfig()
logger = logging.getLogger(__file__)
logger.setLevel(logging.WARNING)


def deterministic_e_raft(g: Graph, planning_budget: int,
                        utility_profile_function: callable = base_utility_profile_function,
                        verbose: bool = False, big_m: int = 1_000) -> float:

    if verbose:
        logger.setLevel(logging.INFO)

    scenarios = g.scenarios

    ev_model = base_e_raft(
        g=g,
        planning_budget=planning_budget,
        utility_profile_function=utility_profile_function,
        verbose=False, big_m=big_m, use_mean_scenario=True,
        fixed_adaptation_decisions=None
    )

    adaptations_ev = {e: ev_model.getVarByName(f'x[{e[0]},{e[1]}]').X for e in g.edges.keys()}
    logger.info(f"EV E-RAFT adaptations: {adaptations_ev}")

    expected_objective = 0

    for i, s in enumerate(scenarios):
        scenario_model = base_e_raft(
            g=g,
            planning_budget=planning_budget,
            utility_profile_function=utility_profile_function,
            verbose=False, big_m=big_m, use_mean_scenario=False,
            use_single_scenario=i, fixed_adaptation_decisions=adaptations_ev
        )

        scenario_obj_value = scenario_model.getObjective().getValue()
        logger.info(f"Value for scenario {i}: {scenario_obj_value}")
        expected_objective += s.probability * scenario_obj_value

    return expected_objective
