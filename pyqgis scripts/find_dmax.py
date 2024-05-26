# -*- coding: utf-8 -*-
"""
Created on Mon May 13 10:12:46 2024

@author: Anne-Fleur
"""

import geopandas as gpd
import numpy as np

gdf = gpd.read_file("C:/Users/Anne-Fleur/OneDrive - Noria/Documents - Noria Internship/Anne Fleur/1. Working Folder/3. GIS/Network FCLM/waterway_canal_delft_exploded_fewnodes.geojson")
gdf2 = gpd.read_file("C:/Users/Anne-Fleur/OneDrive - Noria/Documents - Noria Internship/Anne Fleur/1. Working Folder/3. GIS/Network FCLM/corner_vertices_delft.geojson")

gdf = gpd.read_file("C:/Users/Anne-Fleur/OneDrive - Noria/Documents - Noria Internship/Anne Fleur/1. Working Folder/3. GIS/Static model/Static Model Groningen Leeuwarden/waterways_groningen_final2.geojson")
gdf2 = gpd.read_file("C:/Users/Anne-Fleur/OneDrive - Noria/Documents - Noria Internship/Anne Fleur/1. Working Folder/3. GIS/Static model/Static Model Groningen Leeuwarden/corner_vertices_groningen.geojson")

lengths = np.array(gdf.length)
corner_nodes = len(gdf2)

max_gurobi_nodes = 400 # check this!


d1 = 2*sum(lengths)/(max_gurobi_nodes - corner_nodes + 2*len(gdf)-2)
d2 = 2*sum(lengths)/(max_gurobi_nodes - corner_nodes)

def myround(x, base=5):
    return base * round(x/base)

test_d = (d1+d2)/2
test_d = myround(d1)-5

done = False

while done == False:
    test_d += 5
    nodes_count = 0
    for edge in lengths:
        nodes_count += 2*(edge//test_d)
    if nodes_count <= max_gurobi_nodes:
        done = True