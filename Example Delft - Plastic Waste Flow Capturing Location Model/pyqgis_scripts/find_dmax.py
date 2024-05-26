import geopandas as gpd
import numpy as np
import os

def myround(x, base=5):
    return base * round(x/base)

def find_dmax():
    max_gurobi_nodes = 400 # check this!
    
    dirname = os.path.dirname(__file__)
    layers_folder = os.path.normpath(os.path.join(dirname, '../'))
    waterways_layer_path = layers_folder + "\\waterways_simplified.geojson"
    corner_nodes_layer_path = layers_folder + "\\corner_nodes.geojson"
# gdf = gpd.read_file("C:/Users/Anne-Fleur/OneDrive - Noria/Documents - Noria Internship/Anne Fleur/1. Working Folder/3. GIS/Network FCLM/waterway_canal_delft_exploded_fewnodes.geojson")
# gdf2 = gpd.read_file("C:/Users/Anne-Fleur/OneDrive - Noria/Documents - Noria Internship/Anne Fleur/1. Working Folder/3. GIS/Network FCLM/corner_vertices_delft.geojson")

    gdf = gpd.read_file(waterways_layer_path)
    gdf2 = gpd.read_file(corner_nodes_layer_path)

    lengths = np.array(gdf.length)
    corner_nodes = len(gdf2)

    d1 = 2*sum(lengths)/(max_gurobi_nodes - corner_nodes + 2*len(gdf)-2)
    d2 = 2*sum(lengths)/(max_gurobi_nodes - corner_nodes)

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
    
    return test_d