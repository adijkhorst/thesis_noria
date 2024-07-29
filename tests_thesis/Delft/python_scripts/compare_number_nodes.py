# -*- coding: utf-8 -*-
"""
Created on Sun May  5 11:14:30 2024

@author: Anne-Fleur
"""

import numpy as np
import networkx as nx
import geopandas as gpd
import matplotlib.pyplot as plt

from scipy.spatial import distance
from scipy.optimize import linear_sum_assignment

import MDP_exact
import MDP_heuristic

import load_instance


import os
dirname = os.path.dirname(__file__)
layers_folder = os.path.normpath(os.path.join(dirname, '../'))+'\\pyqgis_scripts\\QGIS_layers'
# layers_folder_groningen = os.path.normpath(os.path.join(dirname, '../../../')) + '\\Static model\\Static Model Groningen Leeuwarden'

import sys
sys.path.insert(1, os.path.normpath(os.path.join(dirname, '../../'))+'\\Groningen\\python_scripts')
import load_instance_groningen


year = 2022

def no_catching_system():
    gdf = gpd.read_file(layers_folder + '\\corner_vertices_delft.geojson')
    # gdf = gpd.read_file(layers_folder_groningen + '\\no_catching_systems_groningen.geojson')

    no_system = []
    # Iterate through the GeoDataFrame
    for idx, row in gdf.iterrows():
        point = row['geometry']

        # Extract the coordinates of the vertex
        no_system += [point.coords[0]]

    return no_system

# def compare_fixed_solutions():

### Delft
# n_nodes = [198, 244, 308, 412, 622]
# dists = [150, 125, 100, 75, 50]

n_nodes = [308, 338, 390, 444, 522, 622, 784, 1054]
dists = [100, 90, 80, 70, 60, 50, 40, 30]

# n_nodes = [392, 464, 586, 650, 732, 782, 838, 976, 1166, 1458, 1946]
# dists = [150, 125, 100, 90, 80, 75, 70, 60, 50, 40, 30]

### Groningen
# n_nodes = [586, 650, 732, 838, 976, 1166, 1458, 1946]
# dists = [100, 90, 80, 70, 60, 50, 40, 30]

# Bmax_div2 = 10 #for plot with 150, 125, 100, 75, 50 Delft, otherwise use n_cols = min(len(run)-1, len(fixed_solutions))

for index_fixed, n in enumerate(n_nodes):
    index_fixed = 4; n = 522;
    # index_fixed = 2; n = 308;
### for each number of nodes, compare optimum solution with optimum in other situations
    # with open('runs_different_n/compared_n308d100/'+str(n)+'nodes.txt') as f:
    with open('results_n308_oldalpha/'+str(n)+'nodes.txt') as f:
    # with open('output_groningen/'+str(n)+'nodes.txt') as f:
        file_contents = f.readlines()
        fixed_solutions_types = [[system[1] for system in eval(line.strip())[-1]] for line in file_contents[1:]]
        fixed_solutions = [[[system[2][0], system[2][1]] for system in eval(line.strip())[-1]] for line in file_contents[1:]]
        # flow_caught = [eval(line.strip())[3] for line in file_contents[1:]]
    
    
    ### make figure for the fixed n, plot one line each time we compare to new situation
    # fig, (ax1, ax3) = plt.subplots(1, 2, figsize = (14, 6))
    fig, ax3 = plt.subplots(figsize = (8,6))
    prop_cycle = plt.rcParams['axes.prop_cycle']
    colors = prop_cycle.by_key()['color']

    compared_to = n_nodes[:index_fixed] + n_nodes[index_fixed+1:]
    compared_dists = dists[:index_fixed] + dists[index_fixed+1:]
    plot_labels = [r'$d_{max}=$'+str(dist) for dist in compared_dists]
    
    for index, n_compared in enumerate(compared_to): #308 is being compared
        G, n, K, K_i, betas, alpha, C, b, c, B, w = load_instance.MIP_input(year, compared_dists[index], random_wind = False, version_alpha='')
        # G, n, K, K_i, betas, alpha, C, b, c, B, w = load_instance_groningen.MIP_input(year, compared_dists[index], random_wind = False, wind_groningen = True)
    
        no_catching_location = no_catching_system()
        new_node_locations = [[node[0], node[1]] if node not in no_catching_location else [0, 0] for node in G.nodes()]
        # with open('runs_different_n/compared_n308d100/'+str(n_compared)+'nodes.txt') as f:
        with open('results_n308_oldalpha/'+str(n_compared)+'nodes.txt') as f:
        # with open('output_groningen/'+str(n_compared)+'nodes.txt') as f:
            run = f.readlines()
        run = [eval(line.strip()) for line in run]

        compared_solutions = [[[system[2][0], system[2][1]] for system in line[-1]] for line in run[1:]]
        flow_caught_new_optimum = [line[3] for line in run[1:]]
    
        n_rows = len(compared_to) #rows are the number of different scenarios that we are comparing
        # n_cols = Bmax_div2 #columns are the different budgets, we have at most 10 because for many nodes this is only possible
        n_cols = min(len(run)-1, len(fixed_solutions))
        mean_distances = np.zeros(n_cols)
        max_distances = np.zeros(n_cols)
        flow_differences_optimum = np.zeros(n_cols) # difference between caught flow with fixed solution and caught flow with optimal solution in new scenario (compared to having perfect knowledge)
    
    
    
        # for i in range(Bmax_div2):
        for i in range(n_cols):
            ### calculate distance
            locations_fixed_i = fixed_solutions[i]
            locations_compared_i = compared_solutions[i]
            pairwise_distances = distance.cdist(locations_fixed_i, locations_compared_i)
            row_ind, col_ind = linear_sum_assignment(pairwise_distances)
    
            # choose one of three to report
            total_distance = pairwise_distances[row_ind, col_ind].sum()
            mean_distance = (pairwise_distances[row_ind, col_ind].sum())/len(locations_fixed_i)
            max_distance = np.max(pairwise_distances[row_ind, col_ind])
        
            mean_distances[i] = mean_distance
            max_distances[i] = max_distance
    
            ### calculate difference in flow caught
    
            ### calculate fixed solution with new number of nodes:
            pairwise_distances = distance.cdist(locations_fixed_i, new_node_locations)
            row_ind, col_ind = linear_sum_assignment(pairwise_distances)
            x_fixed = np.zeros((n_compared, K))
            for col, row in zip(col_ind, row_ind):
                x_fixed[col][fixed_solutions_types[i][row]-1] = 1 # check if indices are correct!!!
            flow_caught_fixed_solution = MDP_heuristic.flow_caught(x_fixed, n_compared, betas, alpha, C, b)
    
            flow_differences_optimum[i] = (flow_caught_fixed_solution - flow_caught_new_optimum[i])/flow_caught_new_optimum[i]
            
        budgets = 0.2*np.arange(n_cols)+0.2 #0.2*np.arange(Bmax_div2)+0.2
        # ax1.plot(budgets, max_distances, label = plot_labels[index])
        # ax1.plot(budgets, mean_distances, 'x', color = colors[index])
        ax3.plot(budgets, flow_differences_optimum, label = plot_labels[index])

        ### only for manual graph for comparison with groningen!!!
        # ax1.plot(budgets, flow_differences_optimum, label = plot_labels[index])
    
    # ax1.grid()
    # ax1.set_title('Maximum and mean distance between new optimal \n solution and base scenario')
    # ax1.set_xlabel('budget')
    # ax1.set_ylabel('distance between solutions')
    # ax1.set_ylim(bottom = -100, top = 2800)
    # ax1.set_ylim(bottom = 0, top = 5100)
    ax3.grid()
    ax3.set_title('Relative difference of flow caught with fixed base scenario \n solution compared to optimum of new situation')
    ax3.set_xlabel('budget')
    ax3.set_ylabel('relative difference flow caught')
    ax3.set_ylim(bottom = -0.6, top = 0.05)
    # ax3.set_ylim(bottom = -0.15, top = 0.005)

    # # ax2.ticklabel_format(style='plain')
    # # ax3.ticklabel_format(style='plain')
    
    # ax1.legend()
    # ax2.legend()
    ax3.legend()

    ### only for manual graph for comparison with groningen!!!
    # ax1.grid()
    # ax1.set_title('Relative difference of flow caught with fixed base scenario \n solution compared to optimum of new situation')
    # ax1.set_xlabel('budget')
    # ax1.set_ylabel('relative difference flow caught')
    # ax1.set_ylim(bottom = -0.6, top = 0.05)
    # ax1.legend()


    # compare_fixed_solutions()
    break

