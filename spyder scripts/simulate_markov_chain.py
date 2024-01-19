# -*- coding: utf-8 -*-
"""
Created on Fri Nov 17 16:41:00 2023

@author: Anne-Fleur
"""
import networkx as nx
import numpy as np
import matplotlib.pyplot as plt

import network_creation
import transition_probabilities_wind
import init_probability

np.random.seed(0)

# import the networkx graph from network_creation.py, get transition probabilities and initial probabilities
G = network_creation.create_network()
transition_probabilities_wind.get_transition_probabilities(G)
init_probability.get_initial_probabilities(G)

# b = np.random.random(len(G))
# b = b/np.sum(b)
b = [G.nodes[node]['init_probability'] for node in G.nodes()]

A = nx.adjacency_matrix(G, nodelist = G.nodes(), weight = 'transition_probability').toarray()
# C = np.random.random(np.shape(A))*A
# row_sums = C.sum(axis=1)
# C = C / row_sums[:, np.newaxis]

def simulate_markov_chain(initial_distribution, transition_matrix, num_steps, num_paths):
    if len(initial_distribution) != transition_matrix.shape[0]:
        raise ValueError("Initial distribution size must match the number of states in the transition matrix")
    
    num_states = len(initial_distribution)
    paths = np.zeros((num_paths, num_steps), dtype=int)
    
    for path in range(num_paths):
        current_state = np.random.choice(np.arange(1,num_states+1), p=initial_distribution)
        for step in range(num_steps):
            paths[path, step] = current_state
            current_state = np.random.choice(np.arange(1,num_states+1), p=transition_matrix[current_state-1])

    return paths

num_steps = 20
num_paths = 5
simulation = simulate_markov_chain(b, A, num_steps, num_paths)

### add attributes label and position so they can not get lost
attrs = {}
for index, node in enumerate(G.nodes()):
    attrs[node] = {'label': index, 'position' : node}
nx.set_node_attributes(G, attrs)

mapping = {key: index+1 for index, key in enumerate(G.nodes.keys())}
inv_map = {v: k for k, v in mapping.items()}

G = nx.relabel_nodes(G, mapping)
positions = {n: [G.nodes[n]['position'][0], G.nodes[n]['position'][1]] for n in G.nodes()}


### plot paths with labels and color in graph
for path in simulation:
    ### generate labels and colored edges for each simulated path
    attrs = {}
    for edge in G.edges():
        attrs[edge] = {'color' : 'k'}
    for i in range(num_steps-1):
        attrs[(path[i], path[i+1])] = {'color' : 'r'}
    nx.set_edge_attributes(G, attrs)

    colors = [G[u][v]['color'] for u, v in G.edges()]
    partial_mapping = {key: index+1 for index, key in enumerate(G.nodes.keys()) if index+1 in path}

    # plt.figure()
    # plt.title(str(path))
    # nx.draw(G, positions, node_size=5, edge_color = colors)
    # nx.draw_networkx_labels(G, positions, partial_mapping)

    P = nx.DiGraph()
    node_attrs = {}
    for node in path:
        P.add_node(node)
        node_attrs[node] = G.nodes[node]
    nx.set_node_attributes(P, node_attrs)

    edge_attrs = {}
    for i in range(num_steps-1):
        P.add_edge(path[i], path[i+1])
        edge_attrs[(path[i], path[i+1])] = {'color' : 'r'}
    nx.set_edge_attributes(P, edge_attrs)

    positionsP = {n: [P.nodes[n]['position'][0], P.nodes[n]['position'][1]] for n in P.nodes()}
    colorsP = [P[u][v]['color'] for u, v in P.edges()]

    # Plot graph and path next to each other
    f, ax = plt.subplots(1, 2, figsize=(12, 6), sharex=True, sharey=True)
    plt.title(str(path))
    nx.draw(G, positions, ax=ax[0], node_size=5, edge_color = colors)
    nx.draw_networkx_labels(G, positions, partial_mapping, ax = ax[0])

    nx.draw(P, positions, ax=ax[1], node_size=5, edge_color = colorsP)
    nx.draw_networkx_labels(P, positionsP, ax = ax[1])

    # break