def evaluate_accuracy(subgraphs, positive_graphs, negative_graphs):
    if not positive_graphs and not negative_graphs:
        return 0.0

    correct_pos = 0
    for g in positive_graphs:
        for sub in subgraphs:
            if all(g.has_edge(*e) for e in sub.edges()):
                correct_pos += 1
                break

    correct_neg = 0
    for g in negative_graphs:
        for sub in subgraphs:
            if not all(g.has_edge(*e) for e in sub.edges()):
                correct_neg += 1
                break

    total = len(positive_graphs) + len(negative_graphs)
    return (correct_pos + correct_neg) / total