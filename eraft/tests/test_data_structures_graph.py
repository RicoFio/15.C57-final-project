import pytest
from dataclasses import dataclass
from eraft.data_structures.graph import Graph, Scenario


def test_get_mean_scenario():
    # Sample edges and their travel time impacts in different scenarios
    edge_impact_matrix_1 = { (1, 2): 10, (2, 3): 20, (3, 4): 20 }
    edge_impact_matrix_2 = { (1, 2): 15, (2, 3): 25, (3, 4): 30 }

    severity_matrix_1 = { (1, 2): 1, (2, 3): 2, (3, 4): 20}
    severity_matrix_2 = { (1, 2): 2, (2, 3): 3, (3, 4): 4 }

    # Create scenarios
    scenario1 = Scenario(probability=0.5, edge_impact_matrix=edge_impact_matrix_1, severity_matrix=severity_matrix_1)
    scenario2 = Scenario(probability=0.5, edge_impact_matrix=edge_impact_matrix_2, severity_matrix=severity_matrix_2)

    # Create a Graph with these scenarios
    graph = Graph(
        nodes=[1, 2, 3, 4],
        edges={ (1, 2): 1, (2, 3): 1, (3, 4): 1 },
        od_pairs=[],
        scenarios=[scenario1, scenario2]
    )

    # Get the mean scenario
    mean_scenario = graph.get_mean_scenario()

    # Expected mean edge impact and severity matrices
    expected_edge_impact = {
        (1, 2): (10 + 15) / 2,
        (2, 3): (20 + 25) / 2,
        (3, 4): (20 + 30) / 2
    }
    expected_severity = {
        (1, 2): (1 + 2) / 2,
        (2, 3): (2 + 3) / 2,
        (3, 4): (20 + 4) / 2  # Only in scenario2
    }

    # Assertions
    assert mean_scenario.edge_impact_matrix == expected_edge_impact, "Edge impact matrix does not match expected values"
    assert mean_scenario.severity_matrix == expected_severity, "Severity matrix does not match expected values"
    assert mean_scenario.probability == 1, "Mean scenario probability should be 1"
