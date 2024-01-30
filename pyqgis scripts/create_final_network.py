### input: geojson with simplified waterlines
### output: layer with extra nodes and edges for directed network
## new attribute: angle of water segment

from math import *
import numpy as np
import shutil

MAX_DIST_NODES = 100


original_layer_path = "C:/Users/Anne-Fleur/OneDrive - Noria/Documents - Noria Internship/Anne Fleur/1. Working Folder/3. GIS/Network FCLM/waterway_canal_delft_exploded_fewnodes.geojson"
new_layer_path = "C:/Users/Anne-Fleur/OneDrive - Noria/Documents - Noria Internship/Anne Fleur/1. Working Folder/3. GIS/Network FCLM/delft_final_network.geojson"

shutil.copy(original_layer_path, new_layer_path) 
def add_nodes(original_layer, extra_nodes_layer):
    pass

def make_directed(extra_nodes_layer, final_network_layer):
    pass