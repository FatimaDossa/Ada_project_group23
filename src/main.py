import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from sklearn.metrics import confusion_matrix, precision_score, recall_score

from fsm import fsm
from sube import subE
from graph import Graph, find_subgraphs
from discgraph import find_discriminative_graph
from accuracy import evaluate_accuracy
from harmfulEdges import find_harmful_edges
from actionAvoid import extract_action_patterns

# ========== DATA LOAD ==========
df = pd.read_csv("../data/data.csv", dtype=str)
print("CSV Columns:", df.columns.tolist())

# ========== BASIC CONNECTIVITY TEST ==========
grouped = df.sort_values(["subject_id", "phase", "sequence_num"]).groupby(["subject_id", "phase"])
all_edges = []
for _, group in grouped:
    diags = list(group["icd_code"])
    all_edges.extend([(diags[i], diags[i + 1]) for i in range(len(diags) - 1)])

connectivity_graph = nx.DiGraph()
connectivity_graph.add_edges_from(all_edges)
plt.figure(figsize=(10, 6))
nx.draw_kamada_kawai(connectivity_graph, node_size=20, edge_color='gray', alpha=0.5)
plt.title("Basic ICD Code Connectivity Graph")
plt.savefig("basic_connectivity.png")
plt.clf()

# ========== FSM AND SUBE ==========
τ_values = [1, 2, 3]
fsm_by_tau = {}
def convert_to_nx_graph(custom_graph):
    G = nx.DiGraph()
    G.add_nodes_from(custom_graph.nodes)
    for u in custom_graph.edges:
        for v in custom_graph.edges[u]:
            G.add_edge(u, v)
    return G

for tau in τ_values:
    print(f"\nRunning FSM with τ={tau}")
    G = []
    for _, group in grouped:
        diags = list(group["icd_code"])
        edges = [(diags[i], diags[i + 1]) for i in range(len(diags) - 1)]
        G.append(edges)
    fsm_result = fsm(G, tau)
    fsm_by_tau[tau] = fsm_result
    result_sube = set()
    for edge in fsm_result:
        result_sube.update(subE(edge, G, tau, fsm_result))

    sg = Graph(set([n for e in fsm_result for n in e]))
    for u, v in fsm_result:
        sg.add_edge(u, v)
    nx.draw_networkx(convert_to_nx_graph(sg))
    plt.title(f"FSM Patterns (τ={tau})")
    plt.savefig(f"fsm_tau_{tau}.png")
    plt.clf()

# ========== CLASS-SPECIFIC GRAPHS ==========
R_urgent, R_nonurgent, R_chronic, R_alive, R_dead = [], [], [], [], []

for subj_id, group in grouped:
    diags = list(group["icd_code"])
    edges = [(diags[i], diags[i + 1]) for i in range(len(diags) - 1)]
    if not edges: continue
    g = nx.DiGraph()
    g.add_edges_from(edges)
    if int(group["mortality"].iloc[0]) == 0:
        R_alive.append(g)
    else:
        R_dead.append(g)
    label = int(group["label"].iloc[0])
    if label == 1: R_urgent.append(g)
    elif label == 0: R_nonurgent.append(g)
    elif label == 2: R_chronic.append(g)

print(f"# Urgent: {len(R_urgent)}, Chronic: {len(R_chronic)}, Non-Urgent: {len(R_nonurgent)}")

# ========== TEST: DISCRIMINATIVE PATTERNS ==========
pairs = [("Urgent", R_urgent, R_chronic), ("Urgent", R_urgent, R_nonurgent), ("Chronic", R_chronic, R_nonurgent)]
for name1, g1, g2 in pairs:
    dg, _ = find_discriminative_graph(g1, g2)
    print(f"\nDiscriminative edges for {name1} vs other:", list(dg.edges()))
# ========== PHASE-WISE ANALYSIS & METRICS ==========
recommendations = []
y_true, y_pred = [], []

for phase in ["early", "middle", "late"]:
    R_alive_p, R_dead_p = [], []
    for (subj_id, p), group in grouped:
        if p != phase:
            continue
        diags = list(group["icd_code"])
        edges = [(diags[i], diags[i + 1]) for i in range(len(diags) - 1)]
        if not edges:
            continue
        g = nx.DiGraph()
        g.add_edges_from(edges)
        if int(group["mortality"].iloc[0]) == 0:
            R_alive_p.append(g)
        else:
            R_dead_p.append(g)

    disc_graph, avoid_graph = find_discriminative_graph(R_alive_p, R_dead_p)
    acc = evaluate_accuracy([disc_graph], R_alive_p, R_dead_p)
    print(f"\n--- Phase {phase} ---")
    print(f"# Alive: {len(R_alive_p)}, Dead: {len(R_dead_p)}")
    print(f"Accuracy: {acc:.2%}")

    harmful = find_harmful_edges(R_dead_p, R_alive_p)
    print("Harmful Edges Found:", len(harmful))

    # # Find action patterns for avoid actions
    avoid_patterns = extract_action_patterns(R_dead_p, harmful)
    if avoid_patterns:
        print(f"Avoid actions for phase: {phase}")
        for pattern in avoid_patterns:
            print(pattern)
    else:
        print(f"No avoid actions for phase: {phase}")

    # Record recommendations for recovery and avoid actions
    for edge in disc_graph.edges():
        recommendations.append({
            "phase": phase,
            "action_type": "do",  # action type is "do" for recovery actions
            "edge": edge
        })
    if len(avoid_graph.edges) > 0:
        for edge in avoid_graph.edges():
            recommendations.append({
                "phase": phase,
                "action_type": "avoid",  # action type is "avoid" for avoid actions
                "edge": edge
            })

    # simulate confusion matrix
    phase_graphs = R_alive_p + R_dead_p
    phase_labels = [0] * len(R_alive_p) + [1] * len(R_dead_p)
    source = list(disc_graph.nodes())[0] if disc_graph.nodes() else None
    target = list(disc_graph.nodes())[-1] if disc_graph.nodes() else None

    for g, label in zip(phase_graphs, phase_labels):
        y_true.append(label)
        if source in g and target in g:
            y_pred.append(0 if nx.has_path(g, source, target) else 1)
        else:
            # fallback if nodes missing (you can change this logic as needed)
            y_pred.append(1)  # assume mortality if not enough info

    # visualize
    if disc_graph.number_of_edges() > 0:
        nx.draw_networkx(disc_graph)
        plt.title(f"Recovery Actions - {phase}")
        plt.savefig(f"recovery_{phase}.png")
        plt.clf()

    if len(avoid_graph.edges()) > 0:
        nx.draw_networkx(avoid_graph)
        plt.title(f"Avoid Actions - {phase}")
        plt.savefig(f"avoid_{phase}.png")
        plt.clf()
    else:
        print(f"No avoid actions for phase: {phase}")

# ========== FINAL METRICS ==========
print("\n== Predictive Performance Summary ==")
cm = confusion_matrix(y_true, y_pred)
print("Confusion Matrix:\n", cm)

prec_recovery = precision_score(y_true, y_pred, pos_label=0)
recall_recovery = recall_score(y_true, y_pred, pos_label=0)

prec_mortality = precision_score(y_true, y_pred, pos_label=1)
recall_mortality = recall_score(y_true, y_pred, pos_label=1)

print(f"Recovery Precision: {prec_recovery:.2f}, Recall: {recall_recovery:.2f}")
print(f"Mortality Precision: {prec_mortality:.2f}, Recall: {recall_mortality:.2f}")

sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=["Recovered", "Died"], yticklabels=["Recovered", "Died"])
plt.title("Confusion Matrix")
plt.xlabel("Predicted")
plt.ylabel("Actual")
plt.savefig("confusion_matrix.png")
plt.clf()

# ========== EXPORT ==========
rec_df = pd.DataFrame(recommendations)
rec_df.to_csv("phasewise_recommendations.csv", index=False)

'''
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

'''