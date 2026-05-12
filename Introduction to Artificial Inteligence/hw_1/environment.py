class Environment:
    def __init__(self, vertices=None, edges=None, agents=None):
        self.vertices = vertices if vertices is not None else {}
        self.edges = edges if edges is not None else {}
        self.agents = agents if agents is not None else []

    def total_people_remaining(self):
        return sum(vertex.people_to_rescue for vertex in self.vertices.values())
