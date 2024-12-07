from gurobipy import Model
from eraft.data_structures.graph import Scenario


def compute_evpi(exp_obj_stochastic: float, exp_obj_deterministic: float) -> float:
    return (exp_obj_stochastic - exp_obj_deterministic) / exp_obj_stochastic


def compute_vss(exp_obj_expected_value: float, exp_obj_stochastic: float) -> float:
    return (exp_obj_expected_value - exp_obj_stochastic) / exp_obj_expected_value


def compute_expected_objective_value(scenarios: [Scenario], model: Model) -> float:
    return sum([s.probability * model.getObjective() for s in scenarios])
