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

import os
dirname = os.path.dirname(__file__)
layers_folder = os.path.normpath(os.path.join(dirname, '../'))+ '\\pyqgis_scripts\\QGIS_layers'

import MDP_exact
import MDP_heuristic


def no_catching_system():
    gdf = gpd.read_file(layers_folder + '\\corner_vertices_delft.geojson')

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

        stuck_prob = row['stuck_probability']
        impact_factor = row['impact_factor']

        # Extract the coordinates of the vertex
        coordinates = point.coords[0]

        # Add attribute to node
        attrs[coordinates] = {'init_probability': init_prob, 'catching_probability': catching_prob, \
                              'dead_ends_prob': dead_ends_prob, 'sharp_corners_prob': sharp_corners_prob, \
                              'shore_boats_prob': shore_boats_prob, 'shore_veg_prob': shore_veg_prob, \
                              'water_veg_prob': water_veg_prob, 'stuck_probability': stuck_prob, \
                              'impact_factor': impact_factor}

    nx.set_node_attributes(G, attrs)


def create_network(line_layer_path):
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

    attrs = {}
    for index, node in enumerate(G.nodes()):
        attrs[node] = {'label': index+1, 'position' : node}
    nx.set_node_attributes(G, attrs)

    return G



def MIP_input(year, max_dist_nodes, random_wind = False, version_alpha = '25maxbeta'):
    line_layer_path = layers_folder + '\\delft_final_network_exploded_d'+ str(max_dist_nodes)+'.geojson'
    nodes_layer_path = layers_folder + '\\final_network_nodes_attributes_d'+ str(max_dist_nodes)+'.geojson'

    # import the networkx graph from network_creation.py, get transition probabilities and initial probabilities
    G = create_network(line_layer_path)

    if random_wind == False:
        transition_probabilities_wind.get_transition_probabilities(G, year)
    else:
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


    w = 0.005 #0.5% should be caught per unit cost
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

    if version_alpha == '25maxbeta':
        alpha = n * [0.25*np.max((betas*M2)[(betas*M2) > 0])]

    else:
        alpha = n * [np.min((betas*M2)[(betas*M2) > 0])]

    return G, n, K, K_i, betas, alpha, C, b, c, B, w


#%%

def write_outputs(G, n, K, K_i, betas, alpha, C, b, c, Bmax, w, filename, show_impact_flow = False):

    # with open('308nodes_solutions.txt') as f:
    with open('522nodes_solutions.txt') as f:
        fixed_solutions = f.readlines()
    fixed_solutions = [eval(line.strip()) for line in fixed_solutions]

    # only necessary for fixed flow of base situation in new situation with different amount of nodes

    # if n != 308:
    #     with open('308nodes.txt') as f:
    if n != 522:
        with open('522nodes_B2.txt') as f:
            fixed_solutions = f.readlines()
        fixed_solutions_types = [[system[1] for system in eval(line.strip())[-1]] for line in fixed_solutions[1:]]
        fixed_solutions = [[[system[2][0], system[2][1]] for system in eval(line.strip())[-1]] for line in fixed_solutions[1:]]

        no_catching_location = no_catching_system()
        new_node_locations = [[node[0], node[1]] if node not in no_catching_location else [0, 0] for node in G.nodes()]

    label_to_position = {value: key for key, value in nx.get_node_attributes(G, 'label').items()}
    
    output = [['budget', 'runtime', 'objective_value', 'flow_caught_optimal', 'flow_caught_fixed_solution', 'flow_impact_area', ['solution']]]
    output2 = []
    j = 0
    old_solution = np.zeros((n, K))#n*[K*[0]]
    for B in np.arange(0.2, Bmax+0.2, 0.2):
        start = time.time()
        prob, G, solution, flow_caught, flow_impact_area, old_solution = MDP_exact.solve_MDP(G, n, K, K_i, betas, alpha, C, b, c, B, w, show_impact_flow, old_solution, warm_start = True, without_gurobi=False, time_limit = 3600)
        end = time.time()

        if end-start > 3600:
            break
        # if n == 308:
        if n == 522:
        # if n == 622:
            x_fixed = np.array(fixed_solutions[j])
            flow_caught_fixed_solution = MDP_heuristic.flow_caught(x_fixed, n, betas, alpha, C, b)
        else:
            locations_solution = fixed_solutions[j]
            pairwise_distances = distance.cdist(locations_solution, new_node_locations)
            row_ind, col_ind = linear_sum_assignment(pairwise_distances)
            x_fixed = np.zeros((n, K))
            for col, row in zip(col_ind, row_ind):
                x_fixed[col][fixed_solutions_types[j][row]-1] = 1
            flow_caught_fixed_solution = MDP_heuristic.flow_caught(x_fixed, n, betas, alpha, C, b)
            print("flow caught fixed solution: ", flow_caught_fixed_solution)
            output2 += [[new_node_locations[i] for i in col_ind]]
        j+= 1


        output += [[B, end-start, value(prob.objective), flow_caught, flow_caught_fixed_solution, flow_impact_area, [[system[0], system[1], label_to_position[system[0]]] for system in solution]]]


    with open(filename, 'w+') as f:
        # write elements of list
        for items in output:
            f.write('%s\n' %items)
        print("File written successfully")
    f.close()

    # if n != 308:
        # with open(str(n)+'nodes_fixed_solutions.txt', 'w+') as f:
    if n != 522:
        with open(str(n)+'nodes_fixed_solutions_d60.txt', 'w+') as f:
            for items in output2:
                f.write('%s\n' %items)
            print("File written successfully")
        f.close()


def write_outputs_warm_heuristic(G, n, K, K_i, betas, alpha, C, b, c, B, w, filename, show_impact_flow = False):

    with open('308nodes_solutions.txt') as f:
        fixed_solutions = f.readlines()
    fixed_solutions = [eval(line.strip()) for line in fixed_solutions]

    # only necessary for fixed flow of base situation in new situation with different amount of nodes

    if n != 308:
        with open('308nodes.txt') as f:
            fixed_solutions = f.readlines()
        fixed_solutions_types = [[system[1] for system in eval(line.strip())[-1]] for line in fixed_solutions[1:]]
        fixed_solutions = [[[system[2][0], system[2][1]] for system in eval(line.strip())[-1]] for line in fixed_solutions[1:]]

        no_catching_location = no_catching_system()
        new_node_locations = [[node[0], node[1]] if node not in no_catching_location else [0, 0] for node in G.nodes()]

    label_to_position = {value: key for key, value in nx.get_node_attributes(G, 'label').items()}
    
    output = [['budget', 'runtime', 'objective_value', 'flow_caught_optimal', 'flow_caught_fixed_solution', 'flow_impact_area', ['solution']]]
    output2 = []
    j = 0
    for B in np.arange(0.2, 2.2, 0.2):
        x_heur, objective, solution = MDP_heuristic.MDP_heuristic(n, K, K_i, betas, alpha, C, b, c, B, w)
        start = time.time()
        prob, G, solution, flow_caught, flow_impact_area, old_solution = MDP_exact.solve_MDP(G, n, K, K_i, betas, alpha, C, b, c, B, w, show_impact_flow, x_heur, warm_start = True)
        end = time.time()

        if n == 308:
            x_fixed = np.array(fixed_solutions[j])
            flow_caught_fixed_solution = MDP_heuristic.flow_caught(x_fixed, n, betas, alpha, C, b)
        else:
            locations_solution = fixed_solutions[j]
            pairwise_distances = distance.cdist(locations_solution, new_node_locations)
            row_ind, col_ind = linear_sum_assignment(pairwise_distances)
            x_fixed = np.zeros((n, K))
            for col, row in zip(col_ind, row_ind):
                x_fixed[col][fixed_solutions_types[j][row]-1] = 1
            flow_caught_fixed_solution = MDP_heuristic.flow_caught(x_fixed, n, betas, alpha, C, b)
            print("flow caught fixed solution: ", flow_caught_fixed_solution)
            output2 += [[new_node_locations[i] for i in col_ind]]
        j+= 1

        if end-start > 3600:
            break

        output += [[B, end-start, value(prob.objective), flow_caught, flow_caught_fixed_solution, flow_impact_area, [[system[0], system[1], label_to_position[system[0]]] for system in solution]]]

    with open(filename, 'w+') as f:
        for items in output:
            f.write('%s\n' %items)
        print("File written successfully")
    f.close()

    if n != 308:
        with open(str(n)+'nodes_fixed_solutions.txt', 'w+') as f:
            for items in output2:
                f.write('%s\n' %items)
            print("File written successfully")
        f.close()


def write_outputs_heuristic(G, n, K, K_i, betas, alpha, C, b, c, Bmax, w, filename):

    with open('runs_different_n/compared_n308d100/308nodes_solutions.txt') as f:
        fixed_solutions = f.readlines()
    fixed_solutions = [eval(line.strip()) for line in fixed_solutions]

    # only necessary for fixed flow of base situation in new situation with different amount of nodes

    if n != 308:
        with open('runs_different_n/compared_n308d100/308nodes.txt') as f:
            fixed_solutions = f.readlines()
        fixed_solutions_types = [[system[1] for system in eval(line.strip())[-1]] for line in fixed_solutions[1:]]
        fixed_solutions = [[[system[2][0], system[2][1]] for system in eval(line.strip())[-1]] for line in fixed_solutions[1:]]

        no_catching_location = no_catching_system()
        new_node_locations = [[node[0], node[1]] if node not in no_catching_location else [0, 0] for node in G.nodes()]

    label_to_position = {value: key for key, value in nx.get_node_attributes(G, 'label').items()}
    
    output = [['budget', 'runtime', 'objective_value', 'flow_caught_optimal', 'flow_caught_fixed_solution', 'flow_impact_area', ['solution']]]
    output2 = []
    j = 0
    for B in np.arange(0.2, Bmax+0.2, 0.2):
        start = time.time()
        x, objective, solution = MDP_heuristic.MDP_heuristic(n, K, K_i, betas, alpha, C, b, c, B, w)
        end = time.time()
        flow_caught = MDP_heuristic.flow_caught(x, n, betas, alpha, C, b)
        flow_caught_impact_area = 0
        
        if n == 308:
            x_fixed = np.array(fixed_solutions[j])
            flow_caught_fixed_solution = MDP_heuristic.flow_caught(x_fixed, n, betas, alpha, C, b)
        else:
            locations_solution = fixed_solutions[j]
            pairwise_distances = distance.cdist(locations_solution, new_node_locations)
            row_ind, col_ind = linear_sum_assignment(pairwise_distances)
            x_fixed = np.zeros((n, K))
            for col, row in zip(col_ind, row_ind):
                x_fixed[col][fixed_solutions_types[j][row]-1] = 1
            flow_caught_fixed_solution = MDP_heuristic.flow_caught(x_fixed, n, betas, alpha, C, b)
            print("flow caught fixed solution: ", flow_caught_fixed_solution)
            output2 += [[new_node_locations[i] for i in col_ind]]
        j+= 1

        if end-start > 3600:
            break
        output += [[B, end-start, objective, flow_caught, flow_caught_fixed_solution, flow_caught_impact_area, [[system[0], system[1], label_to_position[system[0]]] for system in solution]]]

    with open('heuristic_v2_'+filename, 'w+') as f:
        for items in output:
            f.write('%s\n' %items)
        print("File written successfully")
    f.close()

#%%

if __name__ == '__main__':

    year = 2022
    MAX_DIST_NODES = 60
    Bmax = 2
    G, n, K, K_i, betas, alpha, C, b, c, B, w = MIP_input(year, MAX_DIST_NODES)
    # write_outputs(G, n, K, K_i, betas, alpha, C, b, c, Bmax, w, str(n)+'nodes.txt', show_impact_flow = True)

    # start = time.time()
    # prob, G, solution, folow_caught = solve_MDP(G, n, K, K_i, betas, alpha, C, b, c, B, w)
    # end = time.time()


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

