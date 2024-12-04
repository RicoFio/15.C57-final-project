from ..data.graph import Graph
from ..data.graph import Neighborhood, Demographic


toy_graph_1 = Graph(
    nodes=[0, 1, 2, 3],
    edges={
        (0, 1): 2,
        (0, 2): 3,
        (1, 2): 10,
        (1, 3): 1,
        (2, 3): 5,
        (3, 2): 1,
    },
    od_pairs=[(0, 3), (1, 2)],
    neighborhoods=[
        Neighborhood(node=0, census=[
            Demographic(group="A", num_inhabitants=100, median_hhi=10_000.0),
            Demographic(group="B", num_inhabitants=20, median_hhi=50_000.0),
        ]),
        Neighborhood(node=1, census=[
            Demographic(group="A", num_inhabitants=20, median_hhi=10_000.0),
            Demographic(group="B", num_inhabitants=100, median_hhi=50_000.0),
        ])
    ]
)
