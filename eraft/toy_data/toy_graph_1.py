from ..data_structures.graph import Graph
from ..data_structures.graph import (
    Neighborhood,
    Demographic,
    DemographicGroup,
    ODPair,
    Scenario
)


toy_graph_1 = Graph(
    nodes=[0, 1, 2, 3],
    edges={
        (0, 1): 2,
        (0, 2): 3,
        # (1, 2): 10,
        (1, 3): 1,
        (2, 3): 5,
        (3, 2): 1,
    },
    od_pairs=[
        ODPair(0, 3, 100, DemographicGroup("A")),
        ODPair(0, 2,  10, DemographicGroup("B")),
        # ODPair(1, 2, 20, DemographicGroup("A")),
        # ODPair(1, 2, 100, DemographicGroup("B")),
    ],
    neighborhoods=[
        Neighborhood(node=0, census=[
            Demographic(group=DemographicGroup("A"), num_inhabitants=100, median_hhi=10_000.0),
            Demographic(group=DemographicGroup("B"), num_inhabitants=20, median_hhi=50_000.0),
        ]),
        # Neighborhood(node=1, census=[
        #     Demographic(group=DemographicGroup("A"), num_inhabitants=20, median_hhi=10_000.0),
        #     Demographic(group=DemographicGroup("B"), num_inhabitants=100, median_hhi=50_000.0),
        # ])
    ],
    scenarios=[
        Scenario(
            probability=0.2,
            edge_impact_matrix={
                (0, 1): 90.0,
                # (0, 2): 90.0,
            },
            severity_matrix={
                (0, 1): 1.0,
                # (0, 2): 1.0,
            }
        ),
        Scenario(
            probability=0.5,
            edge_impact_matrix={
                # (0, 1): 90.0,
                (1, 3): 90.0,
            },
            severity_matrix={
                # (0, 1): 1.0,
                (1, 3): 1.0,
            }
        ),
        Scenario(
            probability=0.3,
            edge_impact_matrix={
                # (0, 1): 90.0,
                (2, 3): 90.0,
            },
            severity_matrix={
                # (0, 1): 1.0,
                (2, 3): 1.0,
            }
        )
    ]
)
