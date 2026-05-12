import math
from itertools import product
from graph import Graph
from bayesian_node import BayesianNode


class BayesianNetwork:
    def __init__(self, graph_cfg):
        self.graph_cfg = graph_cfg
        self.graph = Graph.from_config(graph_cfg)
        self.people_dist_hyperparam = graph_cfg.people_dist_hypererparam
        self.nodes = []
        self.evidence = {}

        self._build_weather_node(graph_cfg.weather_distribution)
        self._build_flooded_nodes(graph_cfg.edges_data)
        self._build_evacuees_nodes()

        self.variables = [node.name for node in self.nodes]
        self.node_map = {node.name: node for node in self.nodes}

    def _build_weather_node(self, dist):
        node = BayesianNode(
            name="Weather",
            domain=["mild", "stormy", "extreme"],
            parents=[],
            cpt={"mild": dist[0], "stormy": dist[1], "extreme": dist[2]},
        )
        self.nodes.append(node)

    def _build_flooded_nodes(self, edges_data):
        for edge_id, edge_info in edges_data.items():
            prob_mild = edge_info["flooded_prob"]
            prob_stormy = min(1.0, prob_mild * 2)
            prob_extreme = min(1.0, prob_mild * 3)

            cpt = {
                ("mild",): {True: prob_mild, False: 1 - prob_mild},
                ("stormy",): {True: prob_stormy, False: 1 - prob_stormy},
                ("extreme",): {True: prob_extreme, False: 1 - prob_extreme},
            }
            self.nodes.append(
                BayesianNode(
                    name=f"Flooded_{edge_id}",
                    domain=[True, False],
                    parents=["Weather"],
                    cpt=cpt,
                )
            )

    def _build_evacuees_nodes(self):
        for vertex_id, vertex_obj in self.graph.get_vertices().items():
            connected_edges = list(vertex_obj.edges.values())
            parent_names = [f"Flooded_{e.edge_id}" for e in connected_edges]
            cpt = {}

            for parent_vals in product([True, False], repeat=len(parent_names)):
                flooded_indices = [
                    i for i, val in enumerate(parent_vals) if val is True
                ]

                if not flooded_indices:
                    prob_evac = 0.0
                else:
                    active_edges = [connected_edges[i] for i in flooded_indices]
                    qi_prod = math.prod(
                        [
                            min(1, self.people_dist_hyperparam / e.weight)
                            for e in active_edges
                        ]
                    )
                    prob_evac = 1.0 - qi_prod

                cpt[parent_vals] = {True: prob_evac, False: 1.0 - prob_evac}

            self.nodes.append(
                BayesianNode(
                    name=f"Evacuees_{vertex_id}",
                    domain=[True, False],
                    parents=parent_names,
                    cpt=cpt,
                )
            )
    def add_evidence(self, var_name, value):
        self.evidence[var_name] = value

    def reset_evidence(self):
        self.evidence = {}



    def has_vertex(self, vertex_id):
        return vertex_id in self.graph.get_vertices()

    def has_edge(self, edge_id):
        return edge_id in self.graph.get_edges()

