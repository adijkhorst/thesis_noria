# -*- coding: utf-8 -*-
"""
Created on Sun Mar 17 17:31:42 2024

@author: Anne-Fleur
"""

from pulp import *
import numpy as np
import networkx as nx
import geopandas as gpd

import transition_probabilities_wind

def no_catching_system():
    gdf = gpd.read_file('C:/Users/Anne-Fleur/OneDrive - Noria/Documents - Noria Internship/Anne Fleur/1. Working Folder/3. GIS/Network FCLM/corner_vertices_delft.geojson')

    no_system = []
    # Iterate through the GeoDataFrame
    for idx, row in gdf.iterrows():
        point = row['geometry']
    
        # Extract the coordinates of the vertex
        no_system += [point.coords[0]]

    return no_system

def get_probabilities(G):
    # Read shapefile
    gdf = gpd.read_file('C:/Users/Anne-Fleur/OneDrive - Noria/Documents - Noria Internship/Anne Fleur/1. Working Folder/3. GIS/Network FCLM/final_network_nodes_attributes.geojson')

    attrs = {}
    # Iterate through the GeoDataFrame
    for idx, row in gdf.iterrows():
        point = row['geometry']
        init_prob = row['init_probability']
        catching_prob = row['catching_probability']
        stuck_prob = row['stuck_probability']
        #ALSO IMPACT FACTOR AND YES OR NO CATCHING SYSTEMS

        # Extract the coordinates of the vertex
        coordinates = point.coords[0]

        # Add attribute to node
        attrs[coordinates] = {'init_probability': init_prob, 'catching_probability': catching_prob, 'stuck_probability': stuck_prob} #ALSO IMPACT FACTOR AND YES OR NO CATCHING SYSTEMS

    nx.set_node_attributes(G, attrs)


def create_network(line_layer_path, plot = 0):
    # Read shapefile
    gdf = gpd.read_file(line_layer_path)

    # Create a new NetworkX graph
    G = nx.DiGraph()

    # Iterate through the GeoDataFrame
    for idx, row in gdf.iterrows():
        line = row['geometry']
        angle = row['angle']
    
        # Extract the coordinates of the LineString
        coordinates = list(line.coords)
    
        # Add nodes to the graph
        for coord in coordinates:
            G.add_node(coord)
    
        # Add edges to the graph
        for i in range(1, len(coordinates)):
            node_from = coordinates[i - 1]
            node_to = coordinates[i]
            G.add_edge(node_from, node_to, weight = angle)
    
    # G.remove_edges_from(nx.selfloop_edges(G))
    positions = {n: [n[0], n[1]] for n in list(G.nodes)}
    
    # mapping = {key: index for index, key in enumerate(G.nodes.keys())}
    # G = nx.relabel_nodes(G, mapping)
    
    # Plot
    if plot == 1:
        f, ax = plt.subplots(1, 2, figsize=(12, 6), sharex=True, sharey=True)
        gdf.plot(color="k", ax=ax[0])
        for i, facet in enumerate(ax):
            facet.set_title(("Rivers", "Graph")[i])
            facet.axis("off")
        nx.draw(G, positions, ax=ax[1], node_size=5)
    # nx.draw_networkx_labels(G, positions, mapping, ax=ax[1]) #, node_size=5)
    
    # nx.set_node_attributes(G, positions, "coordinates")
    # G = nx.convert_node_labels_to_integers(G, first_label=1)
    
    
    
    transition_probabilities_wind.get_transition_probabilities(G)

    return G

### TEST DELFT
np.random.seed(0)

line_layer_path = 'C:/Users/Anne-Fleur/OneDrive - Noria/Documents - Noria Internship/Anne Fleur/1. Working Folder/3. GIS/Network FCLM/delft_final_network.geojson'

# import the networkx graph from network_creation.py, get transition probabilities and initial probabilities
G = create_network(line_layer_path)
transition_probabilities_wind.get_transition_probabilities(G)
get_probabilities(G)

b = np.array([G.nodes[node]['init_probability'] for node in G.nodes()])

n = len(G.nodes())
K = 2

stuck = [G.nodes[node]['stuck_probability'] for node in G.nodes()]
# stuck = np.random.uniform(0.0, 0.6, n)
stuck_matrix = np.repeat([stuck], len(stuck), axis = 0).T

A = nx.adjacency_matrix(G, nodelist = G.nodes(), weight = 'transition_probability').toarray()
C = (1-stuck_matrix) * A

catching = np.array([G.nodes[node]['catching_probability'] for node in G.nodes()])
# catching = np.repeat([catching], 2, axis = 0).T
catching = np.stack((catching, 0.9*catching)).T
# impact = [G.nodes[node]['impact_factor'] for node in G.nodes()]

attrs = {}
for index, node in enumerate(G.nodes()):
    attrs[node] = {'label': index+1, 'position' : node}
nx.set_node_attributes(G, attrs)

### instance parameters

no_system = no_catching_system()
### later proberen met sets K_i
K_i = {}
for node in G.nodes():
    if node in no_system:
        K_i[G.nodes[node]['label']] = {}
    else:
        K_i[G.nodes[node]['label']] = {1, 2}


betas = np.random.uniform(0.1, 0.8, (n, K))
betas = catching

w = 0.0001 #0.1% should be caught per unit cost
c = [1, 0.6]
B = 7.5

alpha = np.random.uniform(0.0001, 0.01, n)
alpha = np.ones(n)*0.001
# alpha = impact


#%%

sys.path.insert(1, "C:/Users/Anne-Fleur/OneDrive - Noria/Documents - Noria Internship/Anne Fleur/1. Working Folder/3. GIS/Network FCLM/thesis_noria/spyder scripts/pulp")
import MDP_exact
import time

output = [['budget', 'runtime', ['solution']]]
for B in range(1,5):
    start = time.time()
    prob, G, solution = MDP_exact.solve_MDP(G, n, K, K_i, betas, alpha, C, b, c, B, w)
    end = time.time()
    # print('runtime for ', B, ' catching systems', end-start)
    output += [[B, end-start, solution]]

# open file
with open('without_gurobi'+str(n)+'nodes.txt', 'w+') as f:
     
    # write elements of list
    for items in output:
        f.write('%s\n' %items)
     
    print("File written successfully")
 
 
# close the file
f.close()
