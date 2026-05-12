class GraphConfigs:
    def __init__(
        self, num_vertices, people_dist_hypererparam, weather_distribution, edges_data
    ):
        self.num_vertices = num_vertices
        self.people_dist_hypererparam = people_dist_hypererparam
        self.weather_distribution = weather_distribution
        self.edges_data = edges_data

    def __repr__(self):
        return f"GraphConfigs(num_vertices={self.num_vertices}, people_dist_hypererparam={self.people_dist_hypererparam}, weather_distribution={self.weather_distribution}, edges_data={self.edges_data})"


def parse_config_string(config_string):
    lines = config_string.strip().split("\n")
    num_vertices = 0
    weather_distribution = []
    edges_data = {}
    P1 = 0

    for line in lines:
        line = line.strip()
        if ";" in line:
            line = line.split(";")[0].strip()

        if not line or line.startswith("# "):
            continue

        tokens = line.split()
        if not tokens:
            continue

        tag = tokens[0]
        if tag == "#V":
            num_vertices = int(tokens[1])
        elif tag == "#P1":
            P1 = float(tokens[1])
        elif tag == "#W":
            weather_distribution = [float(x) for x in tokens[1:]]

        elif tag.startswith("#E"):
            edge_id = int(tag.replace("#E", ""))
            source_id = int(tokens[1])
            target_id = int(tokens[2])
            weight = int(tokens[3][1:]) if tokens[3].startswith("W") else 0
            flooded_prob = float(tokens[5])

            edges_data[edge_id] = {
                "edge_id": edge_id,
                "source": source_id,
                "target": target_id,
                "weight": weight,
                "flooded_prob": flooded_prob,
            }
    graph_cfg = GraphConfigs(num_vertices, P1, weather_distribution, edges_data)
    return graph_cfg
