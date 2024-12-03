from dataclasses import dataclass, asdict
from typing import Optional

import networkx as nx
from igraph import Graph as IGraph
import logging

from jinja2 import TemplateRuntimeError

logging.basicConfig()
logger = logging.getLogger(__file__)
logger.setLevel(logging.INFO)


@dataclass(frozen=True)
class DemographicGroup:
    name: str


@dataclass(frozen=True)
class Demographic:
    group: DemographicGroup
    num_inhabitants: int
    median_hhi: float

    def to_dict(self):
        return {
            "group": self.group.name,
            "num_inhabitants": self.num_inhabitants,
            "median_hhi": self.median_hhi
        }


@dataclass(frozen=True)
class Neighborhood:
    node: int
    census: list[Demographic]


@dataclass(frozen=True)
class ODPair:
    origin_node: int
    destination_node: int
    demand: int
    demographic_group: DemographicGroup


@dataclass(frozen=True)
class Scenario:
    probability: float
    edge_impact_matrix: dict[tuple[int, int],float]
    severity_matrix: Optional[dict[tuple[int, int],float]] = None

    def get_tt_impact(self, edge: tuple[int, int]) -> float:
        return self.edge_impact_matrix.get(edge, 0.0)

    def get_severity(self, edge: tuple[int, int]) -> float:
        if self.severity_matrix:
            return self.severity_matrix.get(edge, 0.0)
        return 0.0


@dataclass(frozen=True)
class Graph:
    nodes: list[int]
    edges: dict[tuple[int, int], dict[str, float]]
    od_pairs: list[ODPair]
    neighborhoods: Optional[list[Neighborhood]] = None
    scenarios: Optional[list[Scenario]] = None

    def __post_init__(self):
        # Verify neighborhoods when Graph is instantiated
        if self.neighborhoods and not self._verify_neighborhoods():
            raise ValueError("Invalid neighborhoods: some nodes are not in the graph.")
        if self.scenarios:
            if not self._verify_scenarios_adj_matrices():
                raise ValueError(
                    "Invalid scenarios: all adjacency matrices have to be of the same size and relate to the"
                    "graph.")
            if not self._verify_scenarios_in_graph():
                raise ValueError("Invalid scenarios: all nodes in the adjacency matrices have to be in the graph.")
            if not self._verify_scenarios_probabilities():
                raise ValueError("Invalid scenarios: the sum of all probabilities has to be 1.")
        if self.od_pairs:
            if not self._verify_od_pairs():
                raise ValueError("Invalid OD pairs: some nodes are not in the graph.")
            if not self._verify_od_pairs_demographic_groups():
                raise ValueError("Invalid OD pairs: demographics in the od pairs don't match up with the demographics "
                                 "in the graph.")

    def _verify_od_pairs(self) -> bool:
        return all(od.origin_node in self.nodes and od.destination_node in self.nodes for od in self.od_pairs)

    def _verify_od_pairs_demographic_groups(self) -> bool:
        for od in self.od_pairs:
            if od.origin_node not in self.nodes or od.destination_node not in self.nodes:
                return False
            if od.demographic_group not in {d.group for neighborhood in self.neighborhoods for d in neighborhood.census
                                            if od.origin_node == neighborhood.node}:
                return False
            o_inhabitants = [
                d for neighborhood in self.neighborhoods for d in neighborhood.census if
                od.origin_node == neighborhood.node and
                d.group == od.demographic_group
            ]
            if len(o_inhabitants) > 1:
                logger.warning("More than one demographic group found for the same origin node in the od pair.")
            o_inhabitants = o_inhabitants[0].num_inhabitants
            if od.demand < 0 or od.demand > o_inhabitants:
                return False
            # Return False if there is more than one OD-pair with the same demographic group and the same origin and destination
            uniqueness_check = [
                odp for odp in self.od_pairs if
                odp.origin_node == od.origin_node and
                odp.destination_node == od.destination_node and
                odp.demographic_group == od.demographic_group
            ]
            if len(uniqueness_check) > 1:
                return False
        return True

    def _verify_scenarios_adj_matrices(self) -> bool:
        edge_impact_matrix = {len(scenario.edge_impact_matrix) for scenario in self.scenarios}
        return all(sl < len(list(self.edges.keys())) for sl in edge_impact_matrix)

    def _verify_scenarios_in_graph(self) -> bool:
        for scenario in self.scenarios:
            for (node1, node2), tt_impact in scenario.edge_impact_matrix.items():
                if node1 not in self.nodes or node2 not in self.nodes:
                    return False
                if (node1, node2) not in self.edges:
                    return False
        return True

    def _verify_scenarios_probabilities(self) -> bool:
        probabilities = [scenario.probability for scenario in self.scenarios]
        return sum(probabilities) == 1

    def _verify_neighborhoods(self) -> bool:
        # Check if each neighborhood's node is in the graph's nodes
        nnodes = [neighborhood.node for neighborhood in self.neighborhoods]
        return all(nn in self.nodes for nn in nnodes) and len(set(nnodes)) == len(nnodes)

    def get_neighborhood_groups(self, node: int) -> list:
        return [c.group for n in self.neighborhoods for c in n.census if n.node == node]

    def get_neighborhood_people_count_per_group(self, node: int) -> list:
        return [c.num_inhabitants for n in self.neighborhoods for c in n.census if n.node == node]

    def get_neighborhood_mhhi(self, node: int, group: Optional[DemographicGroup] = None) -> list:
        if group:
            return [c.median_hhi for n in self.neighborhoods for c in n.census if n.node == node and c.group == group]
        return [c.median_hhi for n in self.neighborhoods for c in n.census if n.node == node]

    def to_networkx_graph(self):
        # Create a NetworkX graph
        G = nx.MultiDiGraph()

        # Add nodes
        for node in self.nodes:
            G.add_node(node)
            # Add neighborhood attributes if available
            if self.neighborhoods:
                neighborhood = next((n for n in self.neighborhoods if n.node == node), None)
                if neighborhood:
                    G.nodes[node]['census'] = [asdict(c) for c in neighborhood.census]

        # Add edges
        if not isinstance(self.edges, dict):
            raise TypeError("Edges should be a dictionary with keys as tuple pairs and values as attributes.")

        for (node1, node2), attributes in self.edges.items():
            if not isinstance(attributes, dict):
                # Automatically wrap non-dict attributes into a dictionary
                attributes = {"attribute": attributes}
            if node1 not in self.nodes or node2 not in self.nodes:
                raise ValueError(f"Edge ({node1}, {node2}) refers to nodes not present in the graph.")
            G.add_edge(node1, node2, **attributes)

        return G

    def to_igraph(self):
        # Create an igraph graph
        g = IGraph(directed=True)

        # Add nodes
        g.add_vertices(self.nodes)

        # Add neighborhood attributes if available
        if self.neighborhoods:
            # Create a dictionary mapping nodes to their census data
            node_census = {
                neighborhood.node: [asdict(c) for c in neighborhood.census]
                for neighborhood in self.neighborhoods
            }
            # Attach census data as vertex attributes
            g.vs['census'] = [node_census.get(node, None) for node in self.nodes]

        # Add edges
        if not isinstance(self.edges, dict):
            raise TypeError("Edges should be a dictionary with keys as tuple pairs and values as attributes.")

        edges = list(self.edges.keys())
        g.add_edges(edges)

        # Add edge attributes
        for edge, attributes in self.edges.items():
            if not isinstance(attributes, dict):
                attributes = {"attribute": attributes}
            for key, value in attributes.items():
                g.es[g.get_eid(*edge)][key] = value

        return g
