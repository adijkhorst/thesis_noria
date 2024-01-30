# -*- coding: utf-8 -*-
"""
Created on Mon Dec 11 13:15:51 2023

@author: Anne-Fleur
"""
import networkx as nx
import geopandas as gpd

def get_initial_probabilities(G):
    # Read shapefile
    gdf = gpd.read_file('C:/Users/Anne-Fleur/OneDrive - Noria/Documents - Noria Internship/Anne Fleur/1. Working Folder/3. GIS/Network FCLM/initial_probabilities.geojson')

    attrs = {}
    # Iterate through the GeoDataFrame
    for idx, row in gdf.iterrows():
        point = row['geometry']
        init_prob = row['init_probability']
    
        # Extract the coordinates of the vertex
        coordinates = point.coords[0]

        # Add attribute to node
        attrs[coordinates] = init_prob

    ### CHECK IF ALL NODES NOW HAVE THE ATTRIBUTE, OTHERWISE SET SOME TO ZERO?

    nx.set_node_attributes(G, attrs, 'init_probability')

    # return G


def get_stuck_probabilities(G):
    # Read shapefile
    gdf = gpd.read_file('C:/Users/Anne-Fleur/OneDrive - Noria/Documents - Noria Internship/Anne Fleur/1. Working Folder/3. GIS/Network FCLM/stuck_probabilities.geojson')

    attrs = {}
    # Iterate through the GeoDataFrame
    for idx, row in gdf.iterrows():
        point = row['geometry']
        stuck_prob = row['stuck_probability']
    
        # Extract the coordinates of the vertex
        coordinates = point.coords[0]

        # Add attribute to node
        attrs[coordinates] = stuck_prob

    ### CHECK IF ALL NODES NOW HAVE THE ATTRIBUTE, OTHERWISE SET SOME TO ZERO?

    nx.set_node_attributes(G, attrs, 'stuck_probability')

    # return G

def no_catching_system():
    gdf = gpd.read_file('C:/Users/Anne-Fleur/OneDrive - Noria/Documents - Noria Internship/Anne Fleur/1. Working Folder/3. GIS/Network FCLM/corner_vertices_delft.geojson')

    no_system = []
    # Iterate through the GeoDataFrame
    for idx, row in gdf.iterrows():
        point = row['geometry']
    
        # Extract the coordinates of the vertex
        no_system += [point.coords[0]]

    return no_system