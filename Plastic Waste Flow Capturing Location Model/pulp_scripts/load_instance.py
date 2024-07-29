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
import copy

from scipy.spatial import distance
from scipy.optimize import linear_sum_assignment

import matplotlib.pyplot as plt

import transition_probabilities_wind
import MDP_exact
import MDP_heuristic

import yaml

import os
dirname = os.path.dirname(__file__)
layers_folder = os.path.normpath(os.path.join(dirname, '../'))+"\\QGIS_layers"

import sys
sys.path.insert(1, os.path.normpath(os.path.join(dirname, '../')) + "\\pyqgis_scripts")
import find_dmax

with open('MILP_parameters.yaml', 'r') as file:
    data = yaml.safe_load(file)

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
    catching_systems_accuracy = data['accuracy']
    betas = np.stack((catching_systems_accuracy[0]*catching, catching_systems_accuracy[1]*catching)).T

    no_system = no_catching_system()
    ### later proberen met sets K_i
    K_i = {}
    for node in G.nodes():
        if node in no_system:
            K_i[G.nodes[node]['label']] = {}
        else:
            K_i[G.nodes[node]['label']] = {1, 2}


    w = data['weight_costs'] #0.1% should be caught per unit cost
    c = data['costs']
    B = data['budget']

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
    alpha_catching_early = data['impact_factor_catching_early']
    alpha_sensitive_area = data['impact_factor_sensitive_areas']
    alpha = np.array(n*[alpha_catching_early]) + alpha_sensitive_area*np.array([G.nodes[node]['impact_factor'] for node in G.nodes()])

    return G, n, K, K_i, betas, alpha, C, b, c, B, w


#%%

def write_outputs(G, n, K, K_i, betas, alpha, C, b, c, B, w, show_impact_flow = True):

    label_to_position = {value: key for key, value in nx.get_node_attributes(G, 'label').items()}
    
    output = [['budget', 'runtime', 'objective_value', 'flow_caught_optimal', 'flow_impact_area', 'flow_total_area', ['solution']]]

    start = time.time()
    prob, G, solution, flow_caught, flow_impact_area, flow_total_area, _ = MDP_exact.solve_MDP(G, n, K, K_i, betas, alpha, C, b, c, B, w, show_impact_flow, [], warm_start = False, without_gurobi=False, time_limit = 3600)
    end = time.time()

    output += [[B, end-start, value(prob.objective), flow_caught, flow_impact_area, flow_total_area, [[system[0], system[1], label_to_position[system[0]]]+system[2:] for system in solution]]]


    with open('solution.txt', 'w+') as f:
        # write elements of list
        for items in output:
            f.write('%s\n' %items)
        print("File written successfully")
    f.close()


def write_outputs_warm_heuristic(G, n, K, K_i, betas, alpha, C, b, c, B, w, show_impact_flow = True):

    label_to_position = {value: key for key, value in nx.get_node_attributes(G, 'label').items()}
    
    output = [['budget', 'runtime', 'objective_value', 'flow_caught_optimal', 'flow_impact_area', 'flow_total_area', ['solution']]]

    x_heur, objective, solution = MDP_heuristic.MDP_heuristic(n, K, K_i, betas, alpha, C, b, c, B, w)
    start = time.time()
    prob, G, solution, flow_caught, flow_impact_area, flow_total_area, _ = MDP_exact.solve_MDP(G, n, K, K_i, betas, alpha, C, b, c, B, w, show_impact_flow, x_heur, warm_start = True)
    end = time.time()

    output += [[B, end-start, value(prob.objective), flow_caught, flow_impact_area, flow_total_area, [[system[0], system[1], label_to_position[system[0]]]+system[2:] for system in solution]]]

    with open('solution.txt', 'w+') as f:
        # write elements of list
        for items in output:
            f.write('%s\n' %items)
        print("File written successfully")
    f.close()


def write_outputs_heuristic(G, n, K, K_i, betas, alpha, C, b, c, B, w):
    label_to_position = {value: key for key, value in nx.get_node_attributes(G, 'label').items()}
    
    output = [['budget', 'runtime', 'objective_value', 'flow_caught_optimal', 'flow_impact_area', 'flow_total_area', ['solution']]]
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

#%% plot impact factor

def test_impact_factor(G, n, K, K_i, betas, alpha, C, b, c, B, w):

    if data['tests_catching_early'] != []:
        M2 = np.zeros((n,K))
        for i in range(n):
            for k in range(K):
                diagB = np.eye(n)
                diagB[i,i] = 1 - betas[i,k]
                M2[i,k] = (b.T @ np.linalg.inv(np.eye(n)- diagB @ C))[i]
    
        ### catching early
        plot_number = 0
        for i in range(2):
    
            if plot_number == 0:
                alphas_catching_early = [1e-10, np.min((betas*M2)[(betas*M2) > 0]), np.mean((betas*M2)[(betas*M2) > 0]), 0.25*np.max((betas*M2)[(betas*M2) > 0]), 0.5*np.max((betas*M2)[(betas*M2) > 0]), 0.75*np.max((betas*M2)[(betas*M2) > 0]), 1*np.max((betas*M2)[(betas*M2) > 0])]
                label = 'alpha = 0, alpha = min(beta*M2)='+str(round(alphas_catching_early[1],5))+' alpha = mean(beta*M2)='+str(round(alphas_catching_early[2],5))+' alpha = 0.25*max(beta*M2)='+str(round(alphas_catching_early[3],5))+'\n'+' alpha = 0.5*max(beta*M2)='+str(round(alphas_catching_early[4],5))+' alpha = 0.75*max(beta*M2)='+str(round(alphas_catching_early[5],5))+' alpha = max(beta*M2)='+str(round(alphas_catching_early[6],5))
            else:
                alphas_catching_early = [1e-10] + data['tests_catching_early']
                label = alphas_catching_early
            flow_caught_catching_early = []
            flow_leftover_sensitive_area_catching_early = []
            for test in alphas_catching_early:
                alpha_new = n*[test]
                G_new = copy.deepcopy(G)
                for index, node in enumerate(G_new.nodes()):
                    nx.set_node_attributes(G_new, {node: {'impact_factor': alpha_new[index]}})
                prob, G_new, solution, flow_caught, flow_impact_area, flow_total_area, _ = MDP_exact.solve_MDP(G_new, n, K, K_i, betas, alpha_new, C, b, c, B, w, True, [], warm_start = False, without_gurobi=False, time_limit = 3600)
                flow_caught_catching_early += [flow_caught]
                flow_leftover_sensitive_area_catching_early += [flow_total_area]
        
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize = (14, 6))
            ax1.plot(alphas_catching_early, flow_caught_catching_early, '-o')
            ax2.plot(alphas_catching_early, flow_leftover_sensitive_area_catching_early, '-o')
            ax1.set_ylabel("Total flow caught")
            ax1.set_title("Total flow caught in optimum")
            ax2.set_ylabel("Total flow leftover")
            ax2.set_title("Total leftover flow in optimum")
            ax1.set_xlabel(r"$ \alpha $")
            ax2.set_xlabel(r"$ \alpha $")
            if plot_number == 0:
                fig.suptitle(r"$\bf{Default \: test \:} :$"+r"$ \alpha = $"+ str(label))
            else:
                fig.suptitle(r"$\bf{Tests \: catching \: early \: }$"+r"$ \alpha = $"+str(alphas_catching_early))
            plot_number += 1



    ### sensitive area
    if data['tests_sensitive_area'] != []:
        alphas_sensitive_area = [1e-10]+data['tests_sensitive_area']
        flow_caught_sensitive_area = []
        flow_leftover_sensitive_area = []
        for test in alphas_sensitive_area:
            alpha_new = test*np.array([G.nodes[node]['impact_factor'] for node in G.nodes()])
            G_new = copy.deepcopy(G)
            for index, node in enumerate(G_new.nodes()):
                nx.set_node_attributes(G_new, {node: {'impact_factor': alpha_new[index]}})
            prob, G_new, solution, flow_caught, flow_impact_area, flow_total_area, _ = MDP_exact.solve_MDP(G_new, n, K, K_i, betas, alpha_new, C, b, c, B, w, True, [], warm_start = False, without_gurobi=False, time_limit = 3600)
            flow_caught_sensitive_area += [flow_caught]
            flow_leftover_sensitive_area += [flow_impact_area]
    
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize = (14, 6))
        ax1.plot(alphas_sensitive_area, flow_caught_sensitive_area, '-o')
        ax2.plot(alphas_sensitive_area, flow_leftover_sensitive_area, '-o')
        ax1.set_ylabel("Total flow caught")
        ax1.set_title("Total flow caught in optimum")
        ax2.set_ylabel("Total flow leftover")
        ax2.set_title("Total leftover flow in sensitive area in optimum")
        ax1.set_xlabel(r"$ \alpha $")
        ax2.set_xlabel(r"$ \alpha $")
        fig.suptitle(r"$\bf{Tests \: sensitive \: area \:}$"+r"$ \alpha = $"+str(alphas_sensitive_area))



if __name__ == '__main__':
    year = data['wind_year']
    MAX_DIST_NODES = find_dmax.find_dmax()
    G, n, K, K_i, betas, alpha, C, b, c, B, w = MIP_input(year, MAX_DIST_NODES)

    test_impact_factor(G, n, K, K_i, betas, alpha, C, b, c, B, w)

    write_outputs(G, n, K, K_i, betas, alpha, C, b, c, B, w, show_impact_flow = True)

    nx.write_gml(G, 'solution.gml')





