# -*- coding: utf-8 -*-
"""
Created on Fri Nov 17 15:09:03 2023

@author: Anne-Fleur
"""

import wind_data
import numpy as np
import networkx as nx

def get_transition_probabilities(G):
    ### Calculate transition probabilities and put as attribute on edges
    attrs = {}
    wind_directions = wind_data.get_wind_directions()
    for node in G.nodes():
        neighbors = [neighbor for neighbor in G.neighbors(node)]
        num_neighbors = len(neighbors)
        transition_probabilities = np.zeros(num_neighbors)
        edge_angles = [G[node][neighbor]["weight"] for neighbor in neighbors]
    
        threshold = 0.1 # np.cos(5/180*np.pi) #if less than 5 degrees difference
    
        for direction in wind_directions:
            # print(direction)
            innerproducts = np.cos((edge_angles-direction)/180*np.pi)
            # print(innerproducts)
            index, value = np.argmax(innerproducts), np.max(innerproducts)
            innerproducts[index] -= value
            second_index, second_value = np.argmax(innerproducts), np.max(innerproducts)
            transition_probabilities[index] += 1
            if value-second_value < threshold:
                transition_probabilities[second_index] += 1
    
        # print(forward, backward)
        transition_probabilities /= np.sum(transition_probabilities)
        # print(transition_probabilities)
        # break
        # print(transition_probabilities/total)
        for index, neighbor in enumerate(neighbors):
            attrs[(node, neighbor)] = {"transition_probability": transition_probabilities[index]}
    
    nx.set_edge_attributes(G, attrs)