"""Graph module containing Vertex, Edge, and Graph classes."""

from typing import Dict, Any


class Vertex:
    """Represents a vertex in the graph."""

    def __init__(
        self,
        v_id,
    ):
        self.v_id = v_id
        self.edges = {}


class Edge:
    """Represents an edge in the graph."""

    def __init__(
        self, edge_id, source: Vertex, target: Vertex, weight: int, flooded_prob: float
    ):
        self.edge_id = edge_id
        self.vertex_set = {source, target}
        self.weight = weight
        self.flood_prob = flooded_prob

    def get_other_vertex(self, v: Vertex):
        return (self.vertex_set - {v}).pop()


class Graph:
    """Graph data structure with algorithms."""

    def __init__(self, vertices: Dict[Any, Vertex], edges: Dict[Any, Edge]):
        self._vertices = vertices
        self._edges = edges
        self.add_edges_to_vertices()

    def get_vertices(self):
        return self._vertices

    def get_edges(self):
        return self._edges

    def add_edges_to_vertices(self):
        for e_id, e in self._edges.items():
            for v_id in e.vertex_set:
                v = self._vertices[v_id]
                if e_id not in v.edges:
                    v.edges[e_id] = e

    @classmethod
    def from_config(cls, graph_cfg):
        num_vertices = graph_cfg.num_vertices
        edges_data = graph_cfg.edges_data

        vertices = {
            v_id: Vertex(
                v_id,
            )
            for v_id in range(1, num_vertices + 1)
        }
        edges = {e_id: Edge(**edge_data) for e_id, edge_data in edges_data.items()}
        return cls(vertices, edges)
