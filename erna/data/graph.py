from dataclasses import dataclass
from typing import Optional
import networkx as nx


@dataclass
class Demographic:
    group: str
    num_inhabitants: int
    median_hhi: float


@dataclass
class Neighborhood:
    node: int
    census: list[Demographic]


@dataclass
class Graph:
    nodes: list[int]
    edges: dict[tuple[int, int]:dict[str, float]]
    od_pairs: list[tuple[int, int]]
    neighborhoods: Optional[list[Neighborhood]] = None

    def __post_init__(self):
        # Verify neighborhoods when Graph is instantiated
        if self.neighborhoods and not self.verify_neighborhoods():
            raise ValueError("Invalid neighborhoods: some nodes are not in the graph.")

    def verify_neighborhoods(self) -> bool:
        # Check if each neighborhood's node is in the graph's nodes
        nnodes = [neighborhood.node for neighborhood in self.neighborhoods]
        return all(nn in self.nodes for nn in nnodes) and len(set(nnodes)) == len(nnodes)

    def get_neighborhood_groups(self, node: int) -> list:
        return [c.group for n in self.neighborhoods for c in n.census if n.node == node]

    def get_neighborhood_people_count_per_group(self, node: int) -> list:
        return [c.num_inhabitants for n in self.neighborhoods for c in n.census if n.node == node]

    def get_neighborhood_mhhi(self, node: int):
        return [c.median_hhi for n in self.neighborhoods for c in n.census if n.node == node]

    def to_networkx_graph(self):
        # Create a NetworkX graph
        G = nx.Graph()

        # Add nodes
        for node in self.nodes:
            G.add_node(node)
            # Add neighborhood attributes if available
            if self.neighborhoods:
                neighborhood = next((n for n in self.neighborhoods if n.node == node), None)
                if neighborhood:
                    G.nodes[node]['census'] = neighborhood.census

        # Add edges
        for (node1, node2), attributes in self.edges.items():
            G.add_edge(node1, node2, **attributes)

        return G