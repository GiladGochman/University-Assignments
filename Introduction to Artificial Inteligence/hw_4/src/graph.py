class Edge:
    def __init__(self, e_id, v1, v2, w, prob):
        self.id = e_id
        self.v1 = v1
        self.v2 = v2
        self.w = w
        self.prob = prob

    def get_other_vertex(self, v):
        return self.v2 if v.id == self.v1.id else self.v1


class Vertex:
    def __init__(self, v_id, has_kit=False):
        self.id = v_id
        self.edges = {}
        self.has_kit = has_kit


class Graph:
    def __init__(self, vertices_cfg, edges_cfg, kits_cfg):
        self.vertices = {}
        self.edges = {}

        for v_id in vertices_cfg:
            self.vertices[v_id] = Vertex(v_id, has_kit=(v_id in kits_cfg))

        for e_id, (v1_id, v2_id, w, prob) in edges_cfg.items():
            v1 = self.vertices[v1_id]
            v2 = self.vertices[v2_id]
            edge = Edge(e_id, v1, v2, w, prob)
            self.edges[e_id] = edge
            v1.edges[e_id] = edge
            v2.edges[e_id] = edge
