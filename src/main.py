import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from fsm import fsm
from sube import subE
from graph import Graph, find_subgraphs
from discgraph import find_discriminative_graph
from accuracy import evaluate_accuracy
from harmfulEdges import find_harmful_edges, find_frequent_edges 
from actionAvoid import extract_action_patterns

# load the diagnosis data
df = pd.read_csv("../data/data.csv", dtype=str)
print("CSV Columns:", df.columns.tolist())
#print(df.columns)

# group diagnoses by subject_id and sort by admission_id to preserve order
grouped = df.sort_values(["subject_id", "phase", "sequence_num"]).groupby(["subject_id", "phase"])
# build diagnosis transition edges per patient
G = []
for _, group in grouped:
    diags = list(group["icd_code"])
    edges = [(diags[i], diags[i + 1]) for i in range(len(diags) - 1)]
    G.append(edges)

# now run FSM on this graph data
τ = 2  # frequency threshold, tweak as you like
result_fsm = fsm(G, τ)

# now extend the subgraphs using subE
result_sube = set()
for edge in result_fsm:
    result_sube.update(subE(edge, G, τ, result_fsm))

# print("FSM results:")
# print(result_fsm)
# print("\nExtended Subgraphs:")
# for i, subgraph in enumerate(result_sube):
#     if subgraph:  # skip empty sets
#         print(f"Subgraph {i+1}: {subgraph}")


# collect all unique nodes
all_nodes = set()
for u, v in result_fsm:
    all_nodes.add(u)
    all_nodes.add(v)
    
graph = Graph(all_nodes)

for u, v in result_fsm:
    graph.add_edge(u, v)

graphs = [graph] 

subgraphs = find_subgraphs(graphs)

# for i, sg in enumerate(subgraphs):
#     print(f"Subgraph {i + 1}: {sg}")

# Check the subjects for each label
urgent_subjects = df[df['label'] == 1]['subject_id'].unique()
chronic_subjects = df[df['label'] == 2]['subject_id'].unique()
non_urgent_subjects = df[df['label'] == 0]['subject_id'].unique()

# create lists to hold graphs for each class
R_urgent = []
R_nonurgent = []
R_chronic = []
R_alive = []
R_dead = []


# loop through subject-wise groups
for subj_id, group in grouped:
    diags = list(group["icd_code"])
    edges = [(diags[i], diags[i + 1]) for i in range(len(diags) - 1)]
    if len(edges) < 1:
        continue
    g = nx.DiGraph()
    g.add_edges_from(edges)
    if pd.notna(group["mortality"].iloc[0]):
        mortality = int(group["mortality"].iloc[0])
    if mortality == 0:
        R_alive.append(g)
    else:
        R_dead.append(g)
    label = int(group["label"].iloc[0])  # convert from string to int 
    if label == 1:
        R_urgent.append(g)
    elif label == 0:
        R_nonurgent.append(g)
    elif label == 2:
        R_chronic.append(g)

# print the number of graphs in each class
print(f"# Urgent graphs: {len(R_urgent)}")
print(f"# Chronic graphs: {len(R_chronic)}")
print(f"# Non-Urgent graphs: {len(R_nonurgent)}")

# compare urgent vs chronic
# disc_graph = find_discriminative_graph(R_urgent, R_chronic)
# print("Discriminative Edges (Urgent VS Chronic):", list(disc_graph.edges()))
# # or urgent vs non-urgent
# disc_graph = find_discriminative_graph(R_urgent, R_nonurgent)
# print("Discriminative Edges (Urgent VS Non-Urgent):", list(disc_graph.edges()))
# # or chronic vs non-urgent
# disc_graph = find_discriminative_graph(R_chronic, R_nonurgent)
# print("Discriminative Edges (Non-urgent VS Chronic):", list(disc_graph.edges()))

# print("Discriminative Subgraph Edges (Urgent vs Non-Urgent):", list(discriminative_graph.edges()))
accuracies = []
recommendations = []
for phase in ["early", "middle", "late"]:
    R_alive_phase = []
    R_dead_phase = []

    for (subj_id, p), group in grouped:
        if p!= phase:
            continue
        diags = list(group["icd_code"])
        edges = [(diags[i], diags[i + 1]) for i in range(len(diags) - 1)]
        if len(edges) < 1:
            continue
        g = nx.DiGraph()
        g.add_edges_from(edges)
        if int(group["mortality"].iloc[0]) == 0:
            R_alive_phase.append(g)
        else:
            R_dead_phase.append(g)

    print(f"\n--- Phase {phase} ---")
    print(f"# Alive graphs: {len(R_alive_phase)}")
    print(f"# Dead graphs: {len(R_dead_phase)}")

    disc_graph, avoid_graph = find_discriminative_graph(R_alive_phase, R_dead_phase)
    # print(f"Discriminative Subgraph (Alive vs Dead) for Phase {phase}:")
    # print(list(disc_graph.edges()))
    print("Recovery-promoting actions:")
    for edge in disc_graph.edges():
        print("  ", edge)

    # print("\nActions to avoid:")
    # for edge in avoid_graph.edges():
    #     print("  ", edge)
        
    # find harmful edges and extract avoidable patterns
    harmful_edges = find_harmful_edges(R_dead_phase, R_alive_phase)
    print("Harmful edges (from R_class2 - To Avoid):", len(harmful_edges))

    if harmful_edges:
        print("Actions to avoid:")
        warning_patterns = extract_action_patterns(R_dead_phase, harmful_edges)
        for pattern in warning_patterns:
            print("  ->", " -> ".join(pattern))
    else:
        print("No harmful edges found for actions to avoid.")
        
    accuracy = evaluate_accuracy([disc_graph], R_alive_phase, R_dead_phase)
    print(f"Phase {phase} Accuracy: {accuracy:.2%}")
    
    for edge in disc_graph.edges():
        recommendations.append({"phase": phase, "type": "do", "edge": edge})
    
    for edge in avoid_graph.edges():
        recommendations.append({"phase": phase, "type": "avoid", "edge": edge})
        
    nx.draw_networkx(disc_graph)
    plt.title(f"Recovery actions - {phase}")
    plt.savefig(f"recovery_{phase}.png")
    plt.clf()

    nx.draw_networkx(avoid_graph)
    plt.title(f"Avoid actions - {phase}")
    plt.savefig(f"avoid_{phase}.png")
    plt.clf()

    
rec_df = pd.DataFrame(recommendations)
rec_df.to_csv("phasewise_recommendations.csv", index=False)
