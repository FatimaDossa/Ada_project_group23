def subE(edge, G, τ, fEdges):
    candidates = set()
    subnew = set()

    # Debugging: Print the edge being processed
    # print(f"Processing edge: {edge}")

    for graph in G:
        if edge not in graph:
            continue
        
        # Debugging: Print current graph being processed
        # print(f"Processing graph: {graph}")

        # Try to extend the edge in the graph
        for e in graph:
            if e == edge:
                continue
            
            # Debugging: Check if we can extend the edge
            # print(f"Checking if {str(edge[1])} == {str(e[0])}")

            # Naive extension: if nodes connect, try to build larger subgraph
            if str(edge[1]) == str(e[0]):  # Ensure both are strings
                new_sub = (str(edge[0]), str(edge[1]), str(e[1]))  # A-B-C from A-B and B-C
                candidates.add(new_sub)
                # print(f"Candidate found: {new_sub}")

    # Filter based on frequency
    for cand in candidates:
        count = 0
        for graph in G:
            # Reduce to sequences for easy matching
            if len(graph) > 1:
                seq = [u for u, _ in graph] + [graph[-1][1]]
            else:
                seq = [u for u, _ in graph]  # Handle single edge case

            str_cand = ''.join(cand)
            if str_cand in ''.join(seq):
                count += 1
        if count >= τ:
            subnew.add(cand)

    # Debugging: Print the resulting subgraphs
    # print(f"Subgraphs: {subnew}")
    return subnew