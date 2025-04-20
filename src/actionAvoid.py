import networkx as nx
def extract_action_patterns(graphs, harmful_edges, max_hops=3):
    patterns = []
    
    for g in graphs:
        for edge in harmful_edges:
            if g.has_edge(*edge):
                src, dst = edge
                added = False
                for target in g.nodes():
                    if target != src:
                        try:
                            path = nx.shortest_path(g, source=src, target=target)
                            if len(path) <= max_hops + 1:
                                edge_in_path = any((path[i], path[i+1]) == edge or (path[i+1], path[i]) == edge 
                                                   for i in range(len(path)-1))
                                if edge_in_path:
                                    patterns.append(path)
                                    added = True
                        except nx.NetworkXNoPath:
                            continue
                # if the edge wasn't added in a path, include it directly
                if not added:
                    patterns.append([src, dst])

    # Remove duplicates and return
    unique_patterns = [list(x) for x in set(tuple(p) for p in patterns)]
    return unique_patterns