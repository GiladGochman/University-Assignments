"""Graph module containing Vertex, Edge, and Graph classes."""

import sys
from math import sin, cos, pi
from typing import Dict, Any, List
import os
import matplotlib.pyplot as plt


class Vertex:
    """Represents a vertex in the graph."""

    def __init__(
        self,
        v_id,
        n_people: int,
        initial_kits: List[str] = None,
        pos_x: float = None,
        pos_y: float = None,
    ):
        self.v_id = v_id
        self.n_people = n_people
        self.initial_kits = initial_kits if initial_kits else []
        self.visited = False
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.edges = {}
        self.init = ""

    def __str__(self):
        return self.v_id


class Edge:
    """Represents an edge in the graph."""

    def __init__(
        self, e_id, vertex_1: Vertex, vertex_2: Vertex, w: int, flooded: bool = False
    ):
        self.e_id = e_id
        self.vertex_set = {vertex_1, vertex_2}
        self.w = w
        self.flooded = flooded
        self.blocked = False

    def __str__(self):
        return self.e_id + (" (flooded)" if self.flooded else "")

    def __eq__(self, other):
        return self.e_id == other.e_id

    def __hash__(self):
        return hash(self.e_id)

    def __lt__(self, other):
        return (self.w, self.e_id) < (other.w, other.e_id)

    def get_other_vertex(self, v: Vertex):
        return (self.vertex_set - {v}).pop()


class Graph:
    """Graph data structure with algorithms."""

    def __init__(self, vertices: Dict[Any, Vertex], edges: Dict[Any, Edge]):
        self._vertices = vertices
        self._edges = edges

    def get_vertices(self):
        return self._vertices

    def get_edges(self):
        return self._edges

    @staticmethod
    def add_edges_to_vertices(edges):
        for e_id, e in edges.items():
            for v in e.vertex_set:
                if e_id not in v.edges:
                    v.edges[e_id] = e

    @classmethod
    def from_config(
        cls, vertices_config: Dict[str, dict], edges_config: Dict[str, tuple]
    ):
        n = len(vertices_config)
        vertices = {
            v_id: Vertex(
                v_id,
                cfg["people"],
                cfg["kits"],
                cos(2 * pi * i / n),
                sin(2 * pi * i / n),
            )
            for i, (v_id, cfg) in enumerate(vertices_config.items())
        }
        edges = {
            e_id: Edge(e_id, vertices[tup[0]], vertices[tup[1]], tup[2], tup[3])
            for e_id, tup in edges_config.items()
        }
        Graph.add_edges_to_vertices(edges)
        return cls(vertices, edges)

    def save_plot(self, filename="graph_plot.png"):
        """Visualize the graph and save to output folder."""
        V_x, V_y, V_x_people, V_y_people, V_x_kit, V_y_kit = [], [], [], [], [], []
        fig, ax = plt.subplots(dpi=100)

        for v in self._vertices.values():
            target = (
                (V_x_kit, V_y_kit)
                if len(v.initial_kits) > 0
                else (V_x_people, V_y_people) if v.n_people > 0 else (V_x, V_y)
            )
            target[0].append(v.pos_x)
            target[1].append(v.pos_y)

            label_parts = [str(v.v_id)]
            if v.n_people > 0:
                label_parts.append(f"P:{v.n_people}")
            if len(v.initial_kits) > 0:
                label_parts.append(f"K:{len(v.initial_kits)}")
            if v.init:
                label_parts.append(str(v.init))
            ax.annotate(text=", ".join(label_parts), xy=(v.pos_x, v.pos_y))

        ax.scatter(V_x, V_y, color="b", label="empty", s=200)
        ax.scatter(V_x_people, V_y_people, color="r", label="people", s=200)
        ax.scatter(V_x_kit, V_y_kit, color="g", label="kit", s=200)

        for e in self._edges.values():
            xs, ys = zip(*[(v.pos_x, v.pos_y) for v in e.vertex_set])
            color, ls = ("cyan", "--") if e.flooded else ("b", "-")
            ax.plot(
                xs, ys, color=color, linewidth=2 if e.flooded else 0.3, linestyle=ls
            )
            label = f"{e.w}{' (F)' if e.flooded else ''}"
            plt.text(sum(xs) / 2, sum(ys) / 2, label)

        ax.tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)
        plt.axis("equal")
        plt.tight_layout()

        output_dir = "output"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        save_path = os.path.join(output_dir, filename)
        plt.savefig(save_path)
        plt.close()
