"""Configuration parsing and example configurations."""


def parse_config_string(config_string):
    """
    Parse the configuration string for the Hurricane Evacuation problem.
    Returns: num_vertices, deadline, params, vertices_data, edges_data
    """
    lines = config_string.strip().split("\n")
    num_vertices = 0
    deadline = 100 

    params = {"unequip_time": 1, "equip_time": 1, "flood_penalty": 1}  # #U  # #Q  # #P

    vertices_data, edges_data = {}, {}
    kit_counter = 0

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

        if tag == "#N":
            num_vertices = int(tokens[1])
        elif tag == "#D":
            deadline = int(tokens[1])*2
        elif tag == "#U":
            params["unequip_time"] = int(tokens[1])
        elif tag == "#Q":
            params["equip_time"] = int(tokens[1])
        elif tag == "#P":
            params["flood_penalty"] = int(tokens[1])

        elif tag.startswith("#V"):
            vertex_id = f"V{tag[2:]}"
            people = 0
            kits = []

            for part in tokens[1:]:
                if part.startswith("P"):
                    people = int(part[1:])
                elif part == "K":
                    kit_id = f"K{kit_counter}"
                    kits.append(kit_id)
                    kit_counter += 1

            vertices_data[vertex_id] = {
                "people": people,
                "kits": kits, 
            }

        elif tag.startswith("#E"):
            source_id, target_id = f"V{tokens[1]}", f"V{tokens[2]}"
            weight = 0
            flooded = False

            for part in tokens[3:]:
                if part.startswith("W"):
                    weight = int(part[1:])
                elif part == "F":
                    flooded = True

            edges_data[tag] = (source_id, target_id, weight, flooded)

    return num_vertices, deadline, params, vertices_data, edges_data


config_flooded = """
#N 6
#D 40
#U 1
#Q 2
#P 3
#V1 K
#V2
#V3 P2
#V4 K
#V5 P7
#V6 P1

#E1 1 2 W1
#E2 2 3 W1 F
#E3 3 6 W1
#E4 2 4 W1 F
#E5 4 5 W1
#E6 2 5 W1
"""
