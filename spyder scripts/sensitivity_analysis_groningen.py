# -*- coding: utf-8 -*-
"""
Created on Tue Mar 26 13:59:42 2024

@author: Anne-Fleur
"""

import numpy as np
from scipy.spatial import distance
from scipy.optimize import linear_sum_assignment
import matplotlib.pyplot as plt
import networkx as nx
import copy

### LOAD INPUT
import load_instance_groningen

year = 2022
MAX_DIST_NODES = 200
G, n, K, K_i, betas, alpha, C, b, c, B, w = load_instance_groningen.MIP_input(year, MAX_DIST_NODES, random_wind = False)


#%%

def compare_runs(filenames, labels, fixed_index, sensitive_areas = False, alphas = []):
    runs = []

    for filename in filenames:
        groningen_filename = 'output_groningen/'+filename
        with open(groningen_filename) as f:
            run = f.readlines()
        run = [eval(line.strip()) for line in run]
        runs += [run]
    
    mean_distances = np.zeros((len(runs)-1, len(runs[1])-1))
    max_distances = np.zeros((len(runs)-1, len(runs[1])-1))
    flow_differences = np.zeros((len(runs)-1, len(runs[1])-1))
    flow_differences_new_situation = np.zeros((len(runs)-1, len(runs[1])-1))

    flow_total = np.zeros((len(runs)-1, len(runs[1])-1))
    flow_sensitive_area = np.zeros((len(runs)-1, len(runs[1])-1))
    flow_total_fixed = np.zeros(len(runs[1])-1)
    flow_sensitive_fixed = np.zeros(len(runs[1])-1)

    list_index = 0
    for i, run in enumerate(runs):
        if i != fixed_index:
            for j, budget in enumerate(run[1:]):
                locations_i = [list(system[-1]) for system in budget[-1]]
                locations_fixed = [list(system[-1]) for system in runs[fixed_index][j+1][-1]]
    
                pairwise_distances = distance.cdist(locations_i, locations_fixed)
                row_ind, col_ind = linear_sum_assignment(pairwise_distances)
    
                # choose one of three to report
                total_distance = pairwise_distances[row_ind, col_ind].sum()
                mean_distance = (pairwise_distances[row_ind, col_ind].sum())/len(locations_i)
                max_distance = np.max(pairwise_distances[row_ind, col_ind])
    
                mean_distances[list_index, j] = mean_distance
                max_distances[list_index, j] = max_distance
                flow_differences[list_index,j] = budget[4]-runs[fixed_index][j+1][3] #4th entry of each run with different budget is the flow_caught with same fixed solution from base case
                flow_differences_new_situation[list_index,j] = budget[4]-budget[3]
                flow_sensitive_area[list_index, j] = budget[5]
                flow_total[list_index, j] = budget[3]
            list_index += 1
        else:
            for j, budget in enumerate(run[1:]):
                flow_total_fixed[j] = budget[3]
                flow_sensitive_fixed[j] = budget[5]

    budgets = [row[0] for row in runs[1][1:]]
    plot_labels = labels[:fixed_index] + labels[fixed_index+1:]
    
    if sensitive_areas == False:
    
        fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize = (18, 5))
        # ax.title("Sensitivity analysis of wind directions compared to 2022")
        
        ax1.grid()
        ax1.set_xlabel('budget')
        ax1.set_ylabel('maximum distance between solutions')
    
        # ax1a = ax1.twinx()
    
        ax2.set_xlabel('budget')
        ax2.set_ylabel('difference flow caught compared to base situation')
        
        ax2.grid()
        ax2.axhline(y = 0, linewidth = 0.5, color = 'k')
        for i in range(len(plot_labels)):
            ax1.plot(budgets, max_distances[i], label = plot_labels[i])
    
            ax2.plot(budgets, flow_differences[i], label = plot_labels[i])
        ax1.set_prop_cycle(None)
    
        # ax2a = ax2.twinx()
        ax3.grid()
        ax3.set_xlabel('budget')
        ax3.set_ylabel('difference flow caught compared to optimum of new situation')
    
        # ax2.ticklabel_format(style='plain')
        # ax3.ticklabel_format(style='plain')
    
    
        for i in range(len(plot_labels)):
            ax1.plot(budgets, mean_distances[i], 'x')#, label = plot_labels[i] + ' mean distance solutions')
            ax3.plot(budgets, flow_differences_new_situation[i], '--')
        # ax1.legend()
        ax2.legend()
        # ax3.legend()

    else:
        fig, axs = plt.subplots(2, 2)
        for i in range(len(plot_labels)):
            axs[0,0].plot(budgets, max_distances[i], label = plot_labels[i])
        axs[0,0].set_prop_cycle(None)
        for i in range(len(plot_labels)):
            axs[0,0].plot(budgets, mean_distances[i], 'x')
        axs[0,0].legend()
        axs[0,0].set_ylabel("Distance between solution and alpha = 0")
            
            
        # for i in range(len(runs[1])-9):
        for j in range(1,5):
            i = j*5-1
            axs[0,1].plot(np.append([0], alphas), np.append(flow_total_fixed[i], flow_total[:,i]), '-o', label = 'B='+str(round(budgets[i], 1)))
            axs[1,0].plot(np.append([0], alphas), np.append(flow_sensitive_fixed[i], flow_sensitive_area[:,i]), '-o')
            axs[1,1].plot(alphas, (flow_total[:,i]-flow_total_fixed[i])/(flow_sensitive_area[:,i]-flow_sensitive_fixed[i]), '-o')
        axs[0,1].legend()
        axs[0,1].set_ylabel("Total flow caught in optimum")
        axs[1,0].set_ylabel("Total flow in sensitive area in optimum")
        axs[1,1].set_ylabel(r"$ \Delta $ total flow caught / $ \Delta $ flow in sensitive area")
        axs[0,1].set_xlabel(r"$ \alpha $")
        axs[1,0].set_xlabel(r"$ \alpha $")
        axs[1,1].set_xlabel(r"$ \alpha $")


#%%


### CREATE PERTURBATIONS

def change_n_nodes():
    # year = 2022
    # node_dists = [50, 75, 125, 150]
    # node_dists = [75, 50]

    # for dist in node_dists:
    #     G, n, K, K_i, betas, alpha, C, b, c, B, w = load_instance.MIP_input(year, dist, random_wind = False)
    #     load_instance.write_outputs(G, n, K, K_i, betas, alpha, C, b, c, B, w, str(n)+'nodes_B3.txt')


    filenames = ['308nodes.txt', '622nodes_B2.txt', '412nodes_B2.txt', '198nodes.txt', '244nodes.txt']
    labels = ['d=100', 'd=50', 'd=70', 'd=150', 'd=125']

    fixed_index = 0

    compare_runs(filenames, labels, fixed_index)
    plt.suptitle("Sensitivity analysis of number of nodes")

# change_n_nodes()

def change_init_prob(G, n, K, K_i, betas, alpha, C, b, c, B, w):
    # run for different perturbations of b, save to output files

    # b_new = b*np.random.choice([0.9, 1.1], n)
    # b_new = b_new/np.sum(b_new)
    # load_instance_groningen.write_outputs(G, n, K, K_i, betas, alpha, C, b_new, c, B, w, 'init_prob_choice10_'+str(n)+'nodes.txt')

    # b_new = b*np.random.choice([0.8, 1.2], n)
    # b_new = b_new/np.sum(b_new)
    # load_instance_groningen.write_outputs(G, n, K, K_i, betas, alpha, C, b_new, c, B, w, 'init_prob_choice20_'+str(n)+'nodes.txt')


    # b_new = b*np.random.choice([0.7, 1.3], n)
    # b_new = b_new/np.sum(b_new)
    # load_instance_groningen.write_outputs(G, n, K, K_i, betas, alpha, C, b_new, c, B, w, 'init_prob_choice30_'+str(n)+'nodes.txt')

    # b_new = np.ones(n)/n
    # load_instance_groningen.write_outputs(G, n, K, K_i, betas, alpha, C, b_new, c, B, w, 'init_prob_uniform_'+str(n)+'nodes.txt')

    # plot differences in solution and flow caught
    filenames = ['291nodes.txt', 'init_prob_choice10_291nodes.txt', 'init_prob_choice20_291nodes.txt', 'init_prob_choice30_291nodes.txt', 'init_prob_uniform_291nodes.txt']
    labels = ['estimated', 'estimated+-10percent choice', 'estimated+-20percent choice','estimated+-30percent choice', 'uniform init prob']
    fixed_index = 0

    compare_runs(filenames, labels, fixed_index)
    plt.suptitle("Sensitivity analysis of initial distribution")


# change_init_prob(G, n, K, K_i, betas, alpha, C, b, c, B, w)


def change_transition_prob():
    ### only run when files do not exist yet or when input has changed
    # for year in [2020, 2021, 2023]:
    #     G, n, K, K_i, betas, alpha, C, b, c, B, w = load_instance_groningen.MIP_input(year, MAX_DIST_NODES, random_wind = False)
    #     load_instance_groningen.write_outputs(G, n, K, K_i, betas, alpha, C, b, c, B, w, 'wind_year'+str(year)+'_'+str(n)+'nodes.txt')

    G, n, K, K_i, betas, alpha, C, b, c, B, w = load_instance_groningen.MIP_input(year, MAX_DIST_NODES, random_wind = True)
    load_instance_groningen.write_outputs(G, n, K, K_i, betas, alpha, C, b, c, B, w, 'transition_prob_uniform_'+ str(n)+'nodes.txt')

    filenames = ['wind_year2020_291nodes.txt', 'wind_year2021_291nodes.txt', '291nodes.txt', 'wind_year2023_291nodes.txt', 'transition_prob_uniform_291nodes.txt']
    labels = ['2020', '2021', '2022', '2023', 'turbulent']
    fixed_index = 2

    compare_runs(filenames, labels, fixed_index)
    plt.suptitle("Sensitivity analysis of transition probabilities due to wind")

change_transition_prob()

def change_stuck_prob(vary_factor, G, n, K, K_i, betas, alpha, C, b, c, B, w):


    if vary_factor == 1:
        # old_attrs = nx.get_node_attributes(G, 'dead_ends_prob')
        # for perc in [-0.2, -0.1, 0.1, 0.2]:
        #     for node in G.nodes():
        #         new_dead_ends_prob =  old_attrs[node]*(1+perc)
        #         nx.set_node_attributes(G, {node: {'dead_ends_prob': new_dead_ends_prob}})
        #         probs = np.array([G.nodes[node]['dead_ends_prob'], G.nodes[node]['sharp_corners_prob'], G.nodes[node]['shore_boats_prob'], G.nodes[node]['shore_veg_prob'], G.nodes[node]['water_veg_prob']])
        #         nx.set_node_attributes(G, {node: {'stuck_probability': (1-np.prod(1-probs))}})

        #     stuck = [G.nodes[node]['stuck_probability'] for node in G.nodes()]
        #     stuck_matrix = np.repeat([stuck], len(stuck), axis = 0).T

        #     A = nx.adjacency_matrix(G, nodelist = G.nodes(), weight = 'transition_probability').toarray()
        #     C_new = (1-stuck_matrix) * A
        #     load_instance_groningen.write_outputs(G, n, K, K_i, betas, alpha, C_new, b, c, B, w, 'dead_ends_'+str(int(perc*100))+'percent_'+str(n)+'nodes.txt')
        filenames = ['308nodes.txt', 'dead_ends_-20percent_308nodes.txt', 'dead_ends_-10percent_308nodes.txt', 'dead_ends_10percent_308nodes.txt', 'dead_ends_20percent_308nodes.txt']
        # labels = ['estimated', 'estimated-20percent', 'estimated-10percent', 'estimated+10percent', 'estimated+20percent']
        # fixed_index = 0

        # compare_runs(filenames, labels, fixed_index)
        # plt.suptitle("Sensitivity analysis of dead ends in stuck probability")

    elif vary_factor == 2:
        # for perc in [-0.2, -0.1, 0.1, 0.2]:
        #     old_attrs = nx.get_node_attributes(G, 'sharp_corners_prob')
        #     for node in G.nodes():
        #         new_sharp_corners_prob =  old_attrs[node]*(1+perc)
        #         nx.set_node_attributes(G, {node: {'sharp_corners_prob': new_sharp_corners_prob}})
        #         probs = np.array([G.nodes[node]['dead_ends_prob'], G.nodes[node]['sharp_corners_prob'], G.nodes[node]['shore_boats_prob'], G.nodes[node]['shore_veg_prob'], G.nodes[node]['water_veg_prob']])
        #         nx.set_node_attributes(G, {node: {'stuck_probability': (1-np.prod(1-probs))}})

        #     stuck = [G.nodes[node]['stuck_probability'] for node in G.nodes()]
        #     stuck_matrix = np.repeat([stuck], len(stuck), axis = 0).T

        #     A = nx.adjacency_matrix(G, nodelist = G.nodes(), weight = 'transition_probability').toarray()
        #     C_new = (1-stuck_matrix) * A
        #     load_instance_groningen.write_outputs(G, n, K, K_i, betas, alpha, C_new, b, c, B, w, 'sharp_corners_'+str(int(perc*100))+'percent_'+str(n)+'nodes.txt')

        filenames = ['308nodes.txt', 'sharp_corners_-20percent_308nodes.txt', 'sharp_corners_-10percent_308nodes.txt', 'sharp_corners_10percent_308nodes.txt', 'sharp_corners_20percent_308nodes.txt']
        # labels = ['estimated', 'estimated-20percent', 'estimated-10percent', 'estimated+10percent', 'estimated+20percent']
        # fixed_index = 0

        # compare_runs(filenames, labels, fixed_index)
        # plt.suptitle("Sensitivity analysis of sharp corners in stuck probability")


    elif vary_factor == 3:
        # old_attrs = nx.get_node_attributes(G, 'shore_boats_prob')
        # for perc in [0.1, 0.2, 0.4, 0.5]:
        #     for node in G.nodes():
        #         new_shore_boats_prob =  perc if old_attrs[node] > 0 else 0
        #         nx.set_node_attributes(G, {node: {'shore_boats_prob': new_shore_boats_prob}})
        #         probs = np.array([G.nodes[node]['dead_ends_prob'], G.nodes[node]['sharp_corners_prob'], G.nodes[node]['shore_boats_prob'], G.nodes[node]['shore_veg_prob'], G.nodes[node]['water_veg_prob']])
        #         nx.set_node_attributes(G, {node: {'stuck_probability': (1-np.prod(1-probs))}})

        #     stuck = [G.nodes[node]['stuck_probability'] for node in G.nodes()]
        #     stuck_matrix = np.repeat([stuck], len(stuck), axis = 0).T

        #     A = nx.adjacency_matrix(G, nodelist = G.nodes(), weight = 'transition_probability').toarray()
        #     C_new = (1-stuck_matrix) * A
        #     load_instance_groningen.write_outputs(G, n, K, K_i, betas, alpha, C_new, b, c, B, w, 'shore_boats_'+str(int(perc*100))+'percent_'+str(n)+'nodes.txt')

        filenames = ['291nodes.txt', 'shore_boats_10percent_291nodes.txt', 'shore_boats_20percent_291nodes.txt', 'shore_boats_40percent_291nodes.txt', 'shore_boats_50percent_291nodes.txt']
        labels = ['estimated', 'boat_prob = 0.1', 'boat_prob = 0.2', 'boat_prob = 0.4', 'boat_prob = 0.5']
        fixed_index = 0

        compare_runs(filenames, labels, fixed_index)
        plt.suptitle("Sensitivity analysis of docked boats in stuck probability")


    elif vary_factor == 4:
        old_attrs = nx.get_node_attributes(G, 'shore_veg_prob')
        for perc in [0.1, 0.2, 0.4, 0.5]:
            for node in G.nodes():
                new_shore_veg_prob = perc if old_attrs[node] > 0 else 0
                nx.set_node_attributes(G, {node: {'shore_veg_prob': new_shore_veg_prob}})
                probs = np.array([G.nodes[node]['dead_ends_prob'], G.nodes[node]['sharp_corners_prob'], G.nodes[node]['shore_boats_prob'], G.nodes[node]['shore_veg_prob'], G.nodes[node]['water_veg_prob']])
                nx.set_node_attributes(G, {node: {'stuck_probability': (1-np.prod(1-probs))}})

            stuck = [G.nodes[node]['stuck_probability'] for node in G.nodes()]
            stuck_matrix = np.repeat([stuck], len(stuck), axis = 0).T

            A = nx.adjacency_matrix(G, nodelist = G.nodes(), weight = 'transition_probability').toarray()
            C_new = (1-stuck_matrix) * A
            load_instance_groningen.write_outputs(G, n, K, K_i, betas, alpha, C_new, b, c, B, w, 'shore_veg_'+str(int(perc*100))+'percent_'+str(n)+'nodes.txt')

        filenames = ['291nodes.txt', 'shore_veg_10percent_291nodes.txt', 'shore_veg_20percent_291nodes.txt', 'shore_veg_40percent_291nodes.txt', 'shore_veg_50percent_291nodes.txt']
        labels = ['estimated', 'shore_veg_prob = 0.1', 'shore_veg_prob = 0.2', 'shore_veg_prob = 0.4', 'shore_veg_prob = 0.5']
        fixed_index = 0

        compare_runs(filenames, labels, fixed_index)
        plt.suptitle("Sensitivity analysis of shore vegetation in stuck probability")

    elif vary_factor == 5:
        old_attrs = nx.get_node_attributes(G, 'water_veg_prob')
        # # for perc in [0, 0.3, 0.6, 0.9]:
        # for perc in [0]:
        #     for node in G.nodes():
        #         new_water_veg_prob =  perc if old_attrs[node] > 0 else 0
        #         nx.set_node_attributes(G, {node: {'water_veg_prob': new_water_veg_prob}})
        #         probs = np.array([G.nodes[node]['dead_ends_prob'], G.nodes[node]['sharp_corners_prob'], G.nodes[node]['shore_boats_prob'], G.nodes[node]['shore_veg_prob'], G.nodes[node]['water_veg_prob']])
        #         nx.set_node_attributes(G, {node: {'stuck_probability': (1-np.prod(1-probs))}})

        #     stuck = [G.nodes[node]['stuck_probability'] for node in G.nodes()]
        #     stuck_matrix = np.repeat([stuck], len(stuck), axis = 0).T

        #     A = nx.adjacency_matrix(G, nodelist = G.nodes(), weight = 'transition_probability').toarray()
        #     C_new = (1-stuck_matrix) * A
        #     load_instance_groningen.write_outputs(G, n, K, K_i, betas, alpha, C_new, b, c, B, w, 'water_veg_'+str(int(perc*100))+'percent_'+str(n)+'nodes.txt')

        # filenames = ['308nodes.txt', 'water_veg_0percent_308nodes.txt', 'water_veg_30percent_308nodes.txt', 'water_veg_60percent_308nodes.txt', 'water_veg_90percent_308nodes.txt']
        # labels = ['estimated', 'water_veg_prob = 0', 'water_veg_prob = 0.3', 'water_veg_prob = 0.6', 'water_veg_prob = 0.9']
        # fixed_index = 0

        # compare_runs(filenames, labels, fixed_index)
        # plt.suptitle("Sensitivity analysis of water vegetation in stuck probability")

# change_stuck_prob(1, G, n, K, K_i, betas, alpha, C, b, c, B, w)
# change_stuck_prob(2, G, n, K, K_i, betas, alpha, C, b, c, B, w)
# change_stuck_prob(3, G, n, K, K_i, betas, alpha, C, b, c, B, w)
change_stuck_prob(4, G, n, K, K_i, betas, alpha, C, b, c, B, w)
# change_stuck_prob(5, G, n, K, K_i, betas, alpha, C, b, c, B, w)
# change_transition_prob()


def change_catching_prob(G, n, K, K_i, betas, alpha, C, b, c, B, w):
    old_attrs = nx.get_node_attributes(G, 'catching_probability')
    for perc in [-0.2, -0.1, 0.1, 0.2]:
        for node in G.nodes():
            new_catching_prob =  old_attrs[node]*(1+perc)
            nx.set_node_attributes(G, {node: {'catching_probability': new_catching_prob}})

        catching = np.array([G.nodes[node]['catching_probability'] for node in G.nodes()])
        new_betas = np.stack((0.98*catching, 0.85*catching)).T


        load_instance_groningen.write_outputs(G, n, K, K_i, new_betas, alpha, C, b, c, B, w, 'catching_'+str(int(perc*100))+'percent_'+str(n)+'nodes.txt')

    # filenames = ['308nodes.txt', 'catching_-20percent_308nodes.txt', 'catching_-10percent_308nodes.txt', 'catching_10percent_308nodes.txt', 'catching_20percent_308nodes.txt']
    # labels = ['estimated', 'estimated-20percent', 'estimated-10percent', 'estimated+10percent', 'estimated+20percent']
    # fixed_index = 0

    # compare_runs(filenames, labels, fixed_index)
    # plt.suptitle("Sensitivity analysis of catching probability")

# change_catching_prob(G, n, K, K_i, betas, alpha, C, b, c, B, w)

def change_impact_factor(G, n, K, K_i, betas, alpha, C, b, c, B, w):
    ### 1. impact factor the same value everywhere, higher lower etc
    ### impact factor = 0
    # alpha_new = n * [1e-10]
    # for index, node in enumerate(G.nodes()):
    #     nx.set_node_attributes(G, {node: {'impact_factor': alpha_new[index]}})
    # load_instance_groningen.write_outputs(G, n, K, K_i, betas, alpha_new, C, b, c, B, w, 'impact_factor_0_'+str(n)+'nodes.txt', show_impact_flow = True)

    ### examine M1 and M2 for values of alpha
    
    # M1 = b.T @ np.linalg.inv(np.eye(n)-C)
    M2 = np.zeros((n,K))
    for i in range(n):
        for k in range(K):
            diagB = np.eye(n)
            diagB[i,i] = 1 - betas[i,k]
            M2[i,k] = (b.T @ np.linalg.inv(np.eye(n)- diagB @ C))[i]
    
    
    # alpha_new = n * [np.mean((betas*M2)[(betas*M2) > 0])]
    # for index, node in enumerate(G.nodes()):
    #     nx.set_node_attributes(G, {node: {'impact_factor': alpha_new[index]}})
    # load_instance_groningen.write_outputs(G, n, K, K_i, betas, alpha_new, C, b, c, B, w, 'impact_factor_meanbetaM2_'+str(n)+'nodes.txt', show_impact_flow = True)

    alpha_new = n * [np.max((betas*M2)[(betas*M2) > 0])]
    for index, node in enumerate(G.nodes()):
        nx.set_node_attributes(G, {node: {'impact_factor': alpha_new[index]}})
    load_instance_groningen.write_outputs(G, n, K, K_i, betas, alpha_new, C, b, c, B, w, 'impact_factor_maxbetaM2_'+str(n)+'nodes.txt', show_impact_flow = True)

    # filenames = ['impact_factor_0_308nodes.txt', '308nodes.txt', 'impact_factor_meanbetaM2_308nodes.txt', 'impact_factor_maxbetaM2_308nodes.txt']
    # labels = ['alpha = 0', 'alpha = min(beta*M2)', 'alpha = mean(beta*M2)', 'alpha = max(beta*M2)']
    # fixed_index = 0
    
    

    # compare_runs(filenames, labels, fixed_index)
    # plt.suptitle("Sensitivity analysis of impact factor")


    ### 2. impact factor zero with value for area, higher lower
    ### impact factor value everywhere and extra value for area, higher and lower
    ## plot amount of flow caught in total vs amount of flow in area
    # alpha_new5 = np.zeros(n)
    # alpha_new7 = np.zeros(n)
    # alpha_new9 = np.zeros(n)
    # for index, node in enumerate(G.nodes()):
    #     alpha_new5[index] += G.nodes[node]['impact_factor']*5
    #     alpha_new7[index] += G.nodes[node]['impact_factor']*7
    #     alpha_new9[index] += G.nodes[node]['impact_factor']*9
    # load_instance_groningen.write_outputs(G, n, K, K_i, betas, n*[0], C, b, c, B, w, 'impact_factor_area0_'+str(n)+'nodes.txt', show_impact_flow = True)
    # load_instance_groningen.write_outputs(G, n, K, K_i, betas, alpha_new5, C, b, c, B, w, 'impact_factor_area05_'+str(n)+'nodes.txt', show_impact_flow = True)
    # load_instance_groningen.write_outputs(G, n, K, K_i, betas, alpha_new7, C, b, c, B, w, 'impact_factor_area07_'+str(n)+'nodes.txt', show_impact_flow = True)
    # load_instance_groningen.write_outputs(G, n, K, K_i, betas, alpha_new9, C, b, c, B, w, 'impact_factor_area09_'+str(n)+'nodes.txt', show_impact_flow = True)


    # filenames = ['impact_factor_area0_308nodes.txt', 'impact_factor_area05_308nodes.txt', 'impact_factor_area07_308nodes.txt', 'impact_factor_area09_308nodes.txt']
    # labels = ['alpha = 0', 'alpha = 0.5', 'alpha = 0.7', 'alpha = 0.9']
    # fixed_index = 0

    # compare_runs(filenames, labels, fixed_index, sensitive_areas = True, alphas = [0.5, 0.7, 0.9])
    # plt.suptitle("Sensitive area in city center")

    ### 3. impact factor zero and value for edge, higher lower
    ### impact factor value everywhere and extra for edge, higher and lower
    ## plot amount of flow caught in total vs amount of flow in area

    # tests = [1e-10, 1,2,3]
    # node_label = 122
    # for impact in tests:
    #     for index, node in enumerate(G.nodes()):
    #         nx.set_node_attributes(G, {node: {'impact_factor': 0}})
    #         if index == node_label -1:
    #             nx.set_node_attributes(G, {node: {'impact_factor': impact}})
    #     alpha_new = [G.nodes[node]['impact_factor'] for node in G.nodes()]
    #     load_instance_groningen.write_outputs(G, n, K, K_i, betas, alpha_new, C, b, c, B, w, 'impact_factor_edge'+str(round(impact))+'_'+str(n)+'nodes.txt', show_impact_flow = True)


    # filenames = ['impact_factor_edge0_308nodes.txt', 'impact_factor_edge1_308nodes.txt', 'impact_factor_edge2_308nodes.txt', 'impact_factor_edge3_308nodes.txt']
    # labels = ['alpha = 0', 'alpha = 1', 'alpha = 2' , 'alpha = 3']
    # fixed_index = 0

    # compare_runs(filenames, labels, fixed_index, sensitive_areas = True, alphas = [1, 2, 3])
    # plt.suptitle("Sensitive area at edge node")

# change_impact_factor(G, n, K, K_i, betas, alpha, C, b, c, B, w)

#%% test accuracy of catching systems
def change_accuracy_types(G, n, K, K_i, betas, alpha, C, b, c, B, w):
    # catching = np.array([G.nodes[node]['catching_probability'] for node in G.nodes()])
    # for acc in [0.1, 0.2, 0.4, 0.6]:
    #     new_betas = np.stack((0.98*catching, acc*catching)).T
    #     load_instance_groningen.write_outputs(G, n, K, K_i, new_betas, alpha, C, b, c, B, w, 'catching_accuracy_k2_'+str(int(acc*100))+'percent_'+str(n)+'nodes.txt')

    filenames = ['308nodes.txt', 'accuracyk2_10percent_308nodes.txt', 'accuracyk2_20percent_308nodes.txt', 'accuracyk2_40percent_308nodes.txt', 'accuracyk2_60percent_308nodes.txt']
    labels = ['estimated', 'estimated-20percent', 'estimated-10percent', 'estimated+10percent', 'estimated+20percent']
    fixed_index = 0

    # compare_runs(filenames, labels, fixed_index)
    # plt.suptitle("Sensitivity analysis of catching probability")

# change_accuracy_types(G, n, K, K_i, betas, alpha, C, b, c, B, w)


#%%
### TESTS

### one plot with double axes

# fig, ax1 = plt.subplots()
# plt.title("Sensitivity analysis of wind directions compared to 2022")

# ax1.set_xlabel('budget')
# ax1.set_ylabel('total distance between solutions')

# ax2 = ax1.twinx()
# ax2.set_ylabel('difference in proportion of flow caught')
# for i in range(len(plot_labels)):
#     ax1.plot(budgets, distances[i], label = plot_labels[i])
#     ax2.plot(budgets, flow_differences[i], '--', label = plot_labels[i])

# plt.legend()

#%% tests impact factor

### city center area

# B = 2.5
# plot_flow_caught = []
# plot_flow_impact = []
# objectives = []
# # tests = [0.5, 1, 1.5, 2, 2.5, 3] #te klein, floating point errors?
# # tests = [1, 2, 3, 4, 5] #nog te klein?
# tests = [2, 4, 6, 8, 10]
# tests = [5, 6, 7, 8, 9]
# # tests = [6, 8, 10, 12, 14]
# # tests = [10, 20, 30, 40, 50]
# for mult in tests:
#     # alpha_new = copy.copy(alpha)
#     alpha_new = n*[0]
#     for index, node in enumerate(G.nodes()):
#         alpha_new[index] += G.nodes[node]['impact_factor']*mult
#     prob, G, solution, flow_caught, flow_impact_area = MDP_exact.solve_MDP(G, n, K, K_i, betas, alpha_new, C, b, c, B, w, False, True)
#     plot_flow_caught += [flow_caught]
#     plot_flow_impact += [flow_impact_area]
#     objectives += [value(prob.objective)]
# prob, G, solution, flow_caught, flow_impact_area = MDP_exact.solve_MDP(G, n, K, K_i, betas, n*[0], C, b, c, B, w, False, True)
# fig, (ax1, ax2, ax3) = plt.subplots(1,3)
# ax1.plot(np.array([0]+tests)*0.1, [flow_caught]+plot_flow_caught, '.')
# ax2.plot(np.array([0]+tests)*0.1, [flow_impact_area]+plot_flow_impact, '.')
# plot3 = (np.array(plot_flow_caught)-flow_caught)/(np.array(plot_flow_impact)-flow_impact_area)
# ax3.plot(np.array(tests)*0.1, plot3, '.')


### edge node

# B = 1
# plot_flow_caught = []
# plot_flow_impact = []
# tests = [0.2, 0.4, 0.6, 0.8, 1] #drop tussen 0.4 en 0.6, inzoomen en ook nog iets grotere schaal doen
# tests = [0.4, 0.45, 0.5, 0.55, 0.6]
# tests = [0.425, 0.45, 0.475, 0.5]
# tests = [0.5, 1, 1.5, 2]
# tests = [1, 2, 3, 4, 5]

# tests = [1,2,3]
# node_label = 122
# for impact in tests:
#     for index, node in enumerate(G.nodes()):
#         nx.set_node_attributes(G, {node: {'impact_factor': 0}})
#         if index == node_label -1:
#             nx.set_node_attributes(G, {node: {'impact_factor': impact}})
#     alpha_new = [G.nodes[node]['impact_factor'] for node in G.nodes()]
#     prob, G, solution, flow_caught, flow_impact_area = MDP_exact.solve_MDP(G, n, K, K_i, betas, alpha_new, C, b, c, B, w, False, True)
#     plot_flow_caught += [flow_caught]
#     plot_flow_impact += [flow_impact_area]
# prob, G, solution, flow_caught, flow_impact_area = MDP_exact.solve_MDP(G, n, K, K_i, betas, n*[0], C, b, c, B, w, False, True)
# fig, (ax1, ax2, ax3) = plt.subplots(1,3)
# ax1.plot(np.array([0]+tests), [flow_caught]+plot_flow_caught, '.')
# ax2.plot(np.array([0]+tests), [flow_impact_area]+plot_flow_impact, '.')
# plot3 = (np.array(plot_flow_caught)-flow_caught)/(np.array(plot_flow_impact)-flow_impact_area)
# ax3.plot(np.array(tests), plot3, '.')