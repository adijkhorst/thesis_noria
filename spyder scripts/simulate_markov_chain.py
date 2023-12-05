# -*- coding: utf-8 -*-
"""
Created on Fri Nov 17 16:41:00 2023

@author: Anne-Fleur
"""
import networkx as nx
import numpy as np

# import the networkx graph from network_creation.py!
G = nx.Graph()

b = np.random.random(len(G))
b = b/np.sum(b)

A = nx.adjacency_matrix(G, weight = None).toarray()
C = np.random.random(np.shape(A))*A
row_sums = C.sum(axis=1)
C = C / row_sums[:, np.newaxis]

def simulate_markov_chain(initial_distribution, transition_matrix, num_steps, num_paths):
    if len(initial_distribution) != transition_matrix.shape[0]:
        raise ValueError("Initial distribution size must match the number of states in the transition matrix")
    
    num_states = len(initial_distribution)
    paths = np.zeros((num_paths, num_steps), dtype=int)
    
    for path in range(num_paths):
        current_state = np.random.choice(num_states, p=initial_distribution)
        for step in range(num_steps):
            paths[path, step] = current_state
            current_state = np.random.choice(num_states, p=transition_matrix[current_state])

    return paths

simulation = simulate_markov_chain(b, C, 10, 5)