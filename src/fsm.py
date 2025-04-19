from collections import defaultdict

def fsm(G, τ):
    freq = defaultdict(int)

    # count frequency of each edge
    for graph in G:
        for edge in graph:
            edge = (str(edge[0]), str(edge[1]))  # Ensure each edge is a tuple of strings
            freq[edge] += 1

    # keep only frequent edges
    fEdges = set()
    for edge, count in freq.items():
        if count >= τ:
            fEdges.add(edge)

    return fEdges