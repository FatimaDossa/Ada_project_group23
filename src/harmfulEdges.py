from collections import Counter

def find_frequent_edges(graphs, min_support):
    edge_counter = Counter()
    for g in graphs:
        edge_counter.update(g.edges())
    return {e for e, count in edge_counter.items() if count >= min_support}

def find_harmful_edges(dead_graphs, alive_graphs, min_support_dead=10, max_support_alive=2):
    dead_counts = Counter()
    alive_counts = Counter()

    for g in dead_graphs:
        dead_counts.update(tuple(e) for e in g.edges())

    for g in alive_graphs:
        alive_counts.update(tuple(e) for e in g.edges())

    harmful = []
    for edge, dead_freq in dead_counts.items():
        if dead_freq >= min_support_dead and alive_counts[edge] <= max_support_alive:
            harmful.append(edge)

    return harmful