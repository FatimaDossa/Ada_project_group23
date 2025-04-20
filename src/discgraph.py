import networkx as nx
import matplotlib.pyplot as plt

def find_discriminative_graph(R_class1, R_class2, alpha=0.005, beta=0.5):
    """
    alpha = 0.01  # edge appears in at least 1% of graphs 
    beta = 0.3    # edge appears in ≤ 30% of comparison class
    This function finds subgraphs that are frequent in R_class1 (recovery/survival)
    and rare in R_class2 (death), suggesting both what to do and what to avoid
    in order to improve recovery chances.
    
    Parameters:
        R_class1: list of nx.Graph — graphs for the first class (recovery/survival)
        R_class2: list of nx.Graph — graphs for the second class (death)
        alpha: float — frequency threshold for R_class1
        beta: float — rarity threshold for R_class2

    Returns:
        G_discriminative: nx.Graph — subgraph with discriminative edges representing recovery-promoting actions
        G_to_avoid: nx.Graph — subgraph with edges representing harmful actions to avoid
    """
    if len(R_class1) == 0 or len(R_class2) == 0:
        print("One of the classes has no graphs. Cannot compute discriminative subgraph.")
        return nx.Graph(), nx.Graph()

    # count edges in R_class1 (Recovery/Survival Class)
    candidate_edges = {}
    for g in R_class1:
        for edge in g.edges():
            edge = tuple(edge)  # normalize edge direction
            candidate_edges[edge] = candidate_edges.get(edge, 0) + 1

    # select frequent edges in R_class1
    total_class1 = len(R_class1)
    frequent_edges = {
        edge for edge, count in candidate_edges.items()
        if (count / total_class1) >= alpha
    }
    print("Total graphs in class1 (Recovery):", total_class1)
    print("Total unique edges found:", len(candidate_edges))    
    # print("Sample of counted edges (with frequency):")
    # for edge, count in list(candidate_edges.items())[:10]:
    #     print(edge, "→", count)

    # filter out edges that are also common in R_class2 (Death Class)
    rare_edges = set()
    for edge in frequent_edges:
        count = 0
        for g in R_class2:
            if g.has_edge(*edge):
                count += 1
        if (count / len(R_class2)) <= beta:
            rare_edges.add(edge)

    # Now let's find harmful actions or edges directly from R_class2 (Death class)
    death_edge_counts = {}
    for g in R_class2:
        for edge in g.edges():
            edge = tuple(edge)  # normalize edge direction
            death_edge_counts[edge] = death_edge_counts.get(edge, 0) + 1

    # select frequent (harmful) edges in R_class2
    harmful_edges = {
        edge for edge, count in death_edge_counts.items()
        if (count / len(R_class2)) >= beta
    }

    # Create discriminative graph for recovery-promoting actions
    G_discriminative = nx.Graph()
    G_discriminative.add_edges_from(rare_edges)

    # Create graph for harmful actions to avoid
    G_to_avoid = nx.Graph()
    G_to_avoid.add_edges_from(harmful_edges)

    print("Frequent edges (R_class1 - Recovery):", len(frequent_edges))
    print("Rare edges (after filtering R_class2 - Recovery Promoting):", len(rare_edges))
    # print("Harmful edges (from R_class2 - To Avoid):", len(harmful_edges))

    if len(rare_edges) == 0:
        print("No discriminative edges found for recovery-promoting actions — try lowering alpha or increasing beta.")
        
    # if len(harmful_edges) == 0:
    #     print("No harmful edges found for actions to avoid.")

    return G_discriminative, G_to_avoid

