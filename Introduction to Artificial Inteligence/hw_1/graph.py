from dataclasses import dataclass


@dataclass
class Node:
    node_id: int
    amphibian_kits: int
    people_to_rescue: int


@dataclass
class Edge:
    edge_id: int
    from_node: int
    to_node: int
    weight: float
    is_flooded: bool

    @staticmethod
    def get_edge_label(from_node, to_node):
        smallest_id = min(from_node, to_node)
        largest_id = max(from_node, to_node)
        return f"E{smallest_id}_{largest_id}"
