# -*- coding: utf-8 -*-
"""
Created on Sun Mar 17 17:31:42 2024

@author: Anne-Fleur
"""

from pulp import *
import numpy as np
import networkx as nx
import geopandas as gpd
import time

from scipy.spatial import distance
from scipy.optimize import linear_sum_assignment

import transition_probabilities_wind
import MDP_exact
import MDP_heuristic

import os
dirname = os.path.dirname(__file__)
layers_folder = os.path.normpath(os.path.join(dirname, '../'))

import sys
sys.path.insert(1, layers_folder + "\\pyqgis_scripts")
import find_dmax


def no_catching_system():
    gdf = gpd.read_file(layers_folder + '\\intersection_nodes.geojson')

    no_system = []
    # Iterate through the GeoDataFrame
    for idx, row in gdf.iterrows():
        point = row['geometry']

        # Extract the coordinates of the vertex
        no_system += [point.coords[0]]

    return no_system

def get_probabilities(G, nodes_layer_path):
    # Read shapefile
    gdf = gpd.read_file(nodes_layer_path)

    attrs = {}
    # Iterate through the GeoDataFrame
    for idx, row in gdf.iterrows():
        point = row['geometry']
        init_prob = row['init_probability']
        catching_prob = row['catching_probability']


        dead_ends_prob = row["dead_ends"]
        sharp_corners_prob = row["sharp_corners"]
        shore_boats_prob = row["shore_boats"]
        shore_veg_prob = row["shore_vegetation"]
        water_veg_prob = row["water_vegetation"]
        stuck_prob = row["stuck_probability"]
        # stuck_prob = 1 - np.prod(1-np.array([dead_ends_prob, sharp_corners_prob, shore_boats_prob, shore_veg_prob, water_veg_prob]))


        stuck_prob = row['stuck_probability']
        impact_factor = row['impact_factor']
        #YES OR NO CATCHING SYSTEMS

        # Extract the coordinates of the vertex
        coordinates = point.coords[0]

        # Add attribute to node
        attrs[coordinates] = {'init_probability': init_prob, 'catching_probability': catching_prob, \
                              'dead_ends_prob': dead_ends_prob, 'sharp_corners_prob': sharp_corners_prob, \
                              'shore_boats_prob': shore_boats_prob, 'shore_veg_prob': shore_veg_prob, \
                              'water_veg_prob': water_veg_prob, 'stuck_probability': stuck_prob, \
                              'impact_factor': impact_factor} #ALSO IMPACT FACTOR AND YES OR NO CATCHING SYSTEMS

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
    # positions = {n: [n[0], n[1]] for n in list(G.nodes)}

    attrs = {}
    for index, node in enumerate(G.nodes()):
        attrs[node] = {'label': index+1, 'position' : node}
    nx.set_node_attributes(G, attrs)

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


    return G



def MIP_input(year, max_dist_nodes):
    line_layer_path = layers_folder + '\\final_network_exploded_d'+ str(max_dist_nodes)+'.geojson'
    nodes_layer_path = layers_folder + '\\final_network_nodes_attributes_d'+ str(max_dist_nodes)+'.geojson'

    # import the networkx graph from network_creation.py, get transition probabilities and initial probabilities
    G = create_network(line_layer_path)

    transition_probabilities_wind.random_transition_probabilities(G)

    get_probabilities(G, nodes_layer_path)

    n = len(G.nodes())
    K = 2

    b = np.array([G.nodes[node]['init_probability'] for node in G.nodes()])


    stuck = [G.nodes[node]['stuck_probability'] for node in G.nodes()]
    stuck_matrix = np.repeat([stuck], len(stuck), axis = 0).T

    A = nx.adjacency_matrix(G, nodelist = G.nodes(), weight = 'transition_probability').toarray()
    C = (1-stuck_matrix) * A

    catching = np.array([G.nodes[node]['catching_probability'] for node in G.nodes()])
    betas = np.stack((0.98*catching, 0.85*catching)).T

    no_system = no_catching_system()
    ### later proberen met sets K_i
    K_i = {}
    for node in G.nodes():
        if node in no_system:
            K_i[G.nodes[node]['label']] = {}
        else:
            K_i[G.nodes[node]['label']] = {1, 2}


    w = 0.0001 #0.1% should be caught per unit cost
    c = [1, 0.2]
    B = 1

    alpha = [G.nodes[node]['impact_factor'] for node in G.nodes()]

    ### examine M1 and M2 for values of alpha
    
    # M1 = b.T @ np.linalg.inv(np.eye(n)-C)
    M2 = np.zeros((n,K))
    for i in range(n):
        for k in range(K):
            diagB = np.eye(n)
            diagB[i,i] = 1 - betas[i,k]
            M2[i,k] = (b.T @ np.linalg.inv(np.eye(n)- diagB @ C))[i]


### choose the alpha!
    alpha = n * [0.25*np.max((betas*M2)[(betas*M2) > 0])]
    # alpha = n * [np.min((betas*M2)[(betas*M2) > 0])]

    return G, n, K, K_i, betas, alpha, C, b, c, B, w


#%%

def write_outputs(G, n, K, K_i, betas, alpha, C, b, c, B, w, show_impact_flow = True):

    label_to_position = {value: key for key, value in nx.get_node_attributes(G, 'label').items()}
    
    output = [['budget', 'runtime', 'objective_value', 'flow_caught_optimal', 'flow_impact_area', ['solution']]]

    start = time.time()
    prob, G, solution, flow_caught, flow_impact_area, _ = MDP_exact.solve_MDP(G, n, K, K_i, betas, alpha, C, b, c, B, w, show_impact_flow, [], warm_start = False, without_gurobi=False, time_limit = 3600)
    end = time.time()

    output += [[B, end-start, value(prob.objective), flow_caught, flow_impact_area, [[system[0], system[1], label_to_position[system[0]]]+system[2:] for system in solution]]]


    with open('solution.txt', 'w+') as f:
        # write elements of list
        for items in output:
            f.write('%s\n' %items)
        print("File written successfully")
    f.close()


def write_outputs_warm_heuristic(G, n, K, K_i, betas, alpha, C, b, c, B, w, show_impact_flow = True):

    label_to_position = {value: key for key, value in nx.get_node_attributes(G, 'label').items()}
    
    output = [['budget', 'runtime', 'objective_value', 'flow_caught_optimal', 'flow_impact_area', ['solution']]]

    x_heur, objective, solution = MDP_heuristic.MDP_heuristic(n, K, K_i, betas, alpha, C, b, c, B, w)
    start = time.time()
    prob, G, solution, flow_caught, flow_impact_area, _ = MDP_exact.solve_MDP(G, n, K, K_i, betas, alpha, C, b, c, B, w, show_impact_flow, x_heur, warm_start = True)
    end = time.time()

    output += [[B, end-start, value(prob.objective), flow_caught, flow_impact_area, [[system[0], system[1], label_to_position[system[0]]]+system[2:] for system in solution]]]

    with open('solution.txt', 'w+') as f:
        # write elements of list
        for items in output:
            f.write('%s\n' %items)
        print("File written successfully")
    f.close()


def write_outputs_heuristic(G, n, K, K_i, betas, alpha, C, b, c, B, w):
    label_to_position = {value: key for key, value in nx.get_node_attributes(G, 'label').items()}
    
    output = [['budget', 'runtime', 'objective_value', 'flow_caught_optimal', 'flow_impact_area', ['solution']]]
    start = time.time()
    x, objective, solution = MDP_heuristic.MDP_heuristic(n, K, K_i, betas, alpha, C, b, c, B, w)
    end = time.time()
    flow_caught = MDP_heuristic.flow_caught(x, n, betas, alpha, C, b)
    flow_caught_impact_area = 0 #NOG FIXEN

    output += [[B, end-start, objective, flow_caught, flow_caught_impact_area, [[system[0], system[1], label_to_position[system[0]]] for system in solution]]]

    with open('heuristic_solution.txt', 'w+') as f:
        # write elements of list
        for items in output:
            f.write('%s\n' %items)
        print("File written successfully")
    f.close()

#%%

if __name__ == '__main__':

    year = 2022
    MAX_DIST_NODES = find_dmax.find_dmax()
    G, n, K, K_i, betas, alpha, C, b, c, B, w = MIP_input(year, MAX_DIST_NODES)
    B = 0.6
    write_outputs(G, n, K, K_i, betas, alpha, C, b, c, B, w, show_impact_flow = True)

    nx.write_gml(G, 'solution.gml')


#%% first version, n = 308 as fixed situation
    ### write output file with all fixed solutions that will be used to compare sensitivity analysis
    # G, n, K, K_i, betas, alpha, C, b, c, B, w = load_instance.MIP_input(2022, 100, random_wind = False)

    # output = []
    # for B in np.arange(0.2, 4.2, 0.2):
    #     start = time.time()
    #     _, _, _, _, _, x_fixed = MDP_exact.solve_MDP(G, n, K, K_i, betas, alpha, C, b, c, B, w)
    #     end = time.time()
    #     output += [x_fixed]

    # with open('308nodes_solutions.txt', 'w+') as f:
    # # with open('without_gurobi'+str(n)+'nodes.txt', 'w+') as f:
    #     # write elements of list
    #     for items in output:
    #         f.write('%s\n' %items)
    #     print("File written successfully")
    # f.close()

#%% second version, d = 60, n = 522 as fixed situation, third with d=50 as fixed situation to check
    ## write output file with all fixed solutions that will be used to compare sensitivity analysis
    # G, n, K, K_i, betas, alpha, C, b, c, B, w = MIP_input(2022, 60, random_wind = False)
    # # G, n, K, K_i, betas, alpha, C, b, c, B, w = MIP_input(2022, 50, random_wind = False)

    # output = []
    # for B in np.arange(0.2, 2.2, 0.2):
    #     start = time.time()
    #     _, _, _, _, _, x_fixed = MDP_exact.solve_MDP(G, n, K, K_i, betas, alpha, C, b, c, B, w)
    #     end = time.time()
    #     output += [x_fixed]

    # with open('522nodes_solutions.txt', 'w+') as f:
    # # with open('without_gurobi'+str(n)+'nodes.txt', 'w+') as f:
    #     # write elements of list
    #     for items in output:
    #         f.write('%s\n' %items)
    #     print("File written successfully")
    # f.close()

#%% test runtime without gurobi
    # year = 2022
    # MAX_DIST_NODES = 50
    # G, n, K, K_i, betas, alpha, C, b, c, B, w = MIP_input(year, MAX_DIST_NODES, random_wind = False)

    # B = 2
    # label_to_position = {value: key for key, value in nx.get_node_attributes(G, 'label').items()}
    
    # prob, G, solution, flow_caught, flow_impact_area, old_solution = MDP_exact.solve_MDP(G, n, K, K_i, betas, alpha, C, b, c, B, w, show_impact_flow = False, init_solution = [], warm_start = False, without_gurobi = True)
    
    
    # output = [['budget', 'runtime', 'objective_value', 'flow_caught_optimal', 'flow_impact_area', ['solution']]]
    # output += [B, prob.solutionTime, value(prob.objective), flow_caught, flow_impact_area, [[system[0], system[1], label_to_position[system[0]]] for system in solution]]
    # with open('withoutGurobi'+str(n)+'nodes_B'+str(B)+'.txt', 'w+') as f:
    # # with open('without_gurobi'+str(n)+'nodes.txt', 'w+') as f:
    #     # write elements of list
    #     for items in output:
    #         f.write('%s\n' %items)
    #     print("File written successfully")
    # f.close()

    #%% test runtime of exact, heuristic and exact with warm start using heuristic WITHOUT GUROBI
    # year = 2022
    # MAX_DIST_NODES = 100
    # G, n, K, K_i, betas, alpha, C, b, c, B, w = MIP_input(year, MAX_DIST_NODES)
    # B = 2

    # start_exact = time.time()
    # prob, G, solution, flow_caught, flow_impact_area, old_solution = MDP_exact.solve_MDP(G, n, K, K_i, betas, alpha, C, b, c, B, w, False, [], False, without_gurobi = True)
    # end_exact = time.time()
    # print('runtime exact: ', end_exact-start_exact)

    # start_heur = time.time()
    # x, objective, solution = MDP_heuristic.MDP_heuristic(n, K, K_i, betas, alpha, C, b, c, B, w)
    # end_heur = time.time()
    # print('runtime heuristic: ', end_heur-start_heur)

    # start_warm_exact = time.time()
    # prob, G, solution, flow_caught, flow_impact_area, old_solution = MDP_exact.solve_MDP(G, n, K, K_i, betas, alpha, C, b, c, B, w, False, x, warm_start = True, without_gurobi = True)
    # end_warm_exact = time.time()
    # print('runtime warm exact: ', end_warm_exact - start_warm_exact)

    #%% test runtime of exact, heuristic and exact with warm start using heuristic WITH GUROBI
    # year = 2022
    # MAX_DIST_NODES = 50
    # G, n, K, K_i, betas, alpha, C, b, c, B, w = MIP_input(year, MAX_DIST_NODES)
    # B = 2.6

    # start_exact = time.time()
    # prob, G, solution, flow_caught, flow_impact_area, old_solution = MDP_exact.solve_MDP(G, n, K, K_i, betas, alpha, C, b, c, B, w)
    # print(prob.solutionTime)
    # end_exact = time.time()
    # print('runtime exact: ', end_exact-start_exact)

    # start_heur = time.time()
    # x, objective, solution = MDP_heuristic.MDP_heuristic(n, K, K_i, betas, alpha, C, b, c, B, w)
    # end_heur = time.time()
    # print('runtime heuristic: ', end_heur-start_heur)

    # start_warm_exact = time.time()
    # prob, G, solution, flow_caught, flow_impact_area, old_solution = MDP_exact.solve_MDP(G, n, K, K_i, betas, alpha, C, b, c, B, w, False, x, warm_start = True)
    # end_warm_exact = time.time()
    # print('runtime warm exact: ', end_warm_exact - start_warm_exact)



#%% write file with heuristic solutions


# output = [['budget', 'runtime', ['solution']]]
# for B in range(1,5):
#     start = time.time()
#     x, objective, solution = MDP_heuristic.MDP_heuristic(n, K, K_i, betas, alpha, C, b, c, B, w)
#     end = time.time()
#     # print('runtime for ', B, ' catching systems', end-start)
#     output += [[B, end-start, solution]]

# # open file
# with open('heuristic'+str(n)+'nodes.txt', 'w+') as f:
     
#     # write elements of list
#     for items in output:
#         f.write('%s\n' %items)
     
#     print("File written successfully")
 
 
# # close the file
# f.close()

