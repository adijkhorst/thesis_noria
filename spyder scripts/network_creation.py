# -*- coding: utf-8 -*-
"""
Created on Thu Oct 26 09:59:53 2023

@author: Anne-Fleur
"""

import matplotlib.pyplot as plt
import networkx as nx
import geopandas as gpd
# import momepy
# import os
# import numpy as np
# import wind_data
import transition_probabilities_wind

def create_network():
    # Read shapefile
    gdf = gpd.read_file('C:/Users/Anne-Fleur/OneDrive - Noria/Documents - Noria Internship/Anne Fleur/1. Working Folder/3. GIS/Network FCLM/waterway_canal_delft_directed_doublenodes.geojson')

    # Create a new NetworkX graph
    G = nx.DiGraph()
    plot = 1

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

if __name__ == '__main__':
    create_network()