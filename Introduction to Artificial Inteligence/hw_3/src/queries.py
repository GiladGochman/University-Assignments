import solver


def calculate_evacuees_probabilities(bn):
    results = {}
    for vertex_id in bn.graph.get_vertices():
        var_name = f"Evacuees_{vertex_id}"
        dist = solver.enumeration_ask(var_name, bn.evidence, bn)
        results[vertex_id] = dist[True]
    return results


def calculate_flooded_probabilities(bn):
    results = {}
    for edge_id in bn.graph_cfg.edges_data:
        var_name = f"Flooded_{edge_id}"
        dist = solver.enumeration_ask(var_name, bn.evidence, bn)
        results[edge_id] = dist[True]
    return results


def calculate_path_free_prob(bn, edge_ids):
    prob_evidence = solver.enumerate_all(bn.variables, bn.evidence, bn)

    extended_evidence = bn.evidence.copy()
    possible = True
    for eid in edge_ids:
        var_name = f"Flooded_{eid}"
        if var_name in extended_evidence and extended_evidence[var_name] is True:
            possible = False
            break
        extended_evidence[var_name] = False  

    if not possible:
        return 0.0

    prob_path_and_evidence = solver.enumerate_all(bn.variables, extended_evidence, bn)

    if prob_evidence == 0:
        return 0.0

    return prob_path_and_evidence / prob_evidence


def find_best_path(bn, start_vertex_id, goal_vertex_id):
    all_paths = []
    stack = [(start_vertex_id, [start_vertex_id], [])]

    while stack:
        curr_id, v_path, e_path = stack.pop()

        if curr_id == goal_vertex_id:
            all_paths.append(e_path)
            continue

        curr_vertex = bn.graph.get_vertices()[curr_id]
        for edge in curr_vertex.edges.values():
            neighbor_id = edge.get_other_vertex(curr_id)
            if neighbor_id not in v_path:
                new_v_path = v_path + [neighbor_id]
                new_e_path = e_path + [edge.edge_id]
                stack.append((neighbor_id, new_v_path, new_e_path))

    if not all_paths:
        return None, 0.0

    best_prob = -1.0
    best_path = None
    for path_edges in all_paths:
        prob = calculate_path_free_prob(bn, path_edges)
        if prob > best_prob:
            best_prob = prob
            best_path = path_edges

    return best_path, best_prob
