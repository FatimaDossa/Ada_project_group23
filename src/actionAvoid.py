import networkx as nx

def extract_action_patterns(graphs, harmful_edges, max_hops=2):
    patterns = []
    for g in graphs:
        for edge in harmful_edges:
            if g.has_edge(*edge):
                # use BFS to extract surrounding path around harmful edge
                src, dst = edge
                paths = []

                # Try both directions
                for node in edge:
                    for target in g.nodes():
                        if node != target:
                            try:
                                path = nx.shortest_path(g, source=node, target=target)
                                if edge[0] in path and edge[1] in path and len(path) <= max_hops + 1:
                                    paths.append(path)
                            except nx.NetworkXNoPath:
                                continue

                patterns.extend(paths)

    # Remove duplicates and return
    unique_patterns = [list(x) for x in set(tuple(p) for p in patterns)]
    return unique_patterns