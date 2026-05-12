def parse_config_string(config_string):
    vertices_config = {}
    edges_config = {}
    kits_config = set()
    params = {"EC": 0, "UC": 0, "FF": 1}
    start = None
    target = None

    lines = config_string.strip().split("\n")
    for line in lines:
        line = line.strip()
        if not line or line.startswith(";"):
            continue
        if ";" in line:
            line = line.split(";")[0].strip()

        tokens = line.split()
        if not tokens:
            continue
        tag = tokens[0]

        if tag == "#V":
            N = int(tokens[1])
            for i in range(N):
                vertices_config[f"V{i+1}"] = 0
        elif tag == "#Start":
            start = f"V{tokens[1]}"
        elif tag == "#Target":
            target = f"V{tokens[1]}"
        elif tag == "#EC":
            params["EC"] = int(tokens[1])
        elif tag == "#UC":
            params["UC"] = int(tokens[1])
        elif tag == "#FF":
            params["FF"] = int(tokens[1])
        elif tag.startswith("#K"):
            kits_config.add(f"V{tokens[1]}")
        elif tag.startswith("#E"):
            e_id = tag[2:]

            u, v = tokens[1], tokens[2]
            w = 0
            prob = 0.0

            idx = 3
            while idx < len(tokens):
                t = tokens[idx]
                if t.startswith("W"):
                    w = int(t[1:])
                elif t == "F":
                    if idx + 1 < len(tokens):
                        try:
                            prob = float(tokens[idx + 1])
                            idx += 1
                        except ValueError:
                            prob = 1.0
                    else:
                        prob = 1.0
                idx += 1

            edges_config[e_id] = (f"V{u}", f"V{v}", w, prob)

    return vertices_config, edges_config, kits_config, params, start, target
