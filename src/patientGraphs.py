import pandas as pd
import networkx as nx

def build_patient_graphs(df):
    R_class1 = []
    R_class2 = []

    # Group by subject_id
    for subject_id, group in df.groupby('subject_id'):
        group = group.sort_values('sequence_num')  # ensure correct order
        mortality_label = group['mortality'].iloc[0]

        # initialize a new graph for this patient
        G = nx.Graph()
        codes = group['icd_code'].tolist()
        
        # create sequential edges between ICD codes
        for i in range(len(codes) - 1):
            src = codes[i]
            tgt = codes[i+1]
            if G.has_edge(src, tgt):
                G[src][tgt]['weight'] += 1
            else:
                G.add_edge(src, tgt, weight=1)

        if mortality_label == 0:
            R_class1.append(G)
        else:
            R_class2.append(G)

    return R_class1, R_class2