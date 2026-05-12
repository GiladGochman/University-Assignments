import solver
import queries
from itertools import product

def answer_q1(bn):
    print("1. What is the probability that each of the vertices contains evacuees?")
    probs = queries.calculate_evacuees_probabilities(bn)
    for v, p in probs.items():
        print(f"  Vertex {v}: {p:.4f}")

def answer_q2(bn):
    print("\n2. What is the probability that each of the edges is flooded?")
    probs = queries.calculate_flooded_probabilities(bn)
    for e, p in probs.items():
        print(f"  Edge {e}: {p:.4f}")

def answer_q3(bn):
    print("\n3. What is the distribution of the weather variable?")
    dist = solver.enumeration_ask("Weather", bn.evidence, bn)
    for w, p in dist.items():
        print(f"  P({w}) = {p:.4f}")

def answer_q4(bn, path_edge_ids):
    print(f"\n4. Probability path {path_edge_ids} is free from flooding:")
    for eid in path_edge_ids:
        if not bn.has_edge(eid):
            print(f"  Edge {eid} does not exist in the graph.")
            return
        
    prob = queries.calculate_path_free_prob(bn, path_edge_ids)
    print(f"  P(Free) = {prob:.4f}")

def answer_q5(bn, start, end):
    print(f"\n5. Path from {start} to {end} with highest probability of being free:")
    if not bn.has_vertex(start):
        print(f"  Start vertex {start} does not exist in the graph.")
        return
    if not bn.has_vertex(end):
        print(f"  End vertex {end} does not exist in the graph.")
        return
    
    try:
        path, prob = queries.find_best_path(bn, start, end)
        if path is None:
            print("  No path found.")
        else:
            print(f"  Best Path (Edges): {path}")
            print(f"  Probability: {prob:.4f}")
    except Exception as e:
        print(f"  Could not calculate best path: {e}")

def show_info(bn):
    """
    Displays the structure and CPTs of the Bayesian Network.
    """
    print("Bayesian Network Information:")
    print(f"  Number of Variables: {len(bn.variables)}")
    print("  Variables:")
    
    weather_node = bn.node_map["Weather"]
    for value in weather_node.domain:
        print(f"    P({value}) = {weather_node.cpt[value]:.4f}")
    
    for edge_id in bn.graph_cfg.edges_data:
        print(f"  EDGE {edge_id}:")
        for value in weather_node.domain:
            flooded_node = bn.node_map[f"Flooded_{edge_id}"]
            prob = flooded_node.cpt.get((value,), {}).get(True, 0.0)
            print(f"    P(flooded|{value}) = {prob:.2f}")
            
    for vertex_id in bn.graph.get_vertices():
        print(f"  VERTEX {vertex_id}:")
        evac_node = bn.node_map[f"Evacuees_{vertex_id}"]
        parent_names = evac_node.parents
        
        for parent_vals in product([True, False], repeat=len(parent_names)):
            prob = evac_node.cpt[parent_vals][True]
            
            conditions = []
            for i, val in enumerate(parent_vals):
                edge_id = parent_names[i].split('_')[1]
                status = "flooded" if val else "not flooded"
                conditions.append(f"{status} {edge_id}")
            
            parent_str = ", ".join(conditions)
            print(f"    P(Evacuees|{parent_str}) = {prob:.2f}")