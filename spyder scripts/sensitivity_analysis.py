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
import load_instance

year = 2022
MAX_DIST_NODES = 100
G, n, K, K_i, betas, alpha, C, b, c, B, w = load_instance.MIP_input(year, MAX_DIST_NODES, random_wind = False)


#%%

def compare_runs(filenames, labels, fixed_index, sensitive_areas = False):
    runs = []
    for filename in filenames:
        with open(filename) as f:
            run = f.readlines()
        run = [eval(line.strip()) for line in run]
        runs += [run]
    
    mean_distances = np.zeros((len(runs)-1, len(runs[1])-1))
    max_distances = np.zeros((len(runs)-1, len(runs[1])-1))
    flow_differences = np.zeros((len(runs)-1, len(runs[1])-1))
    flow_differences_new_situation = np.zeros((len(runs)-1, len(runs[1])-1))

    flow_total = np.zeros((len(runs)-1, len(runs[1])-1))
    flow_sensitive_area = np.zeros((len(runs)-1, len(runs[1])-1))

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
                flow_total[list_index, j] = budget[4]
            list_index += 1
    
    budgets = [row[0] for row in runs[1][1:]]
    plot_labels = labels[:fixed_index] + labels[fixed_index+1:]

    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize = (18, 5))
    # ax.title("Sensitivity analysis of wind directions compared to 2022")
    
    ax1.grid()
    ax1.set_xlabel('budget')
    ax1.set_ylabel('maximum distance between solutions')

    # ax1a = ax1.twinx()

    ax2.set_xlabel('budget')
    ax2.set_ylabel('difference in proportion of flow caught compared to base situation')
    
    ax2.grid()
    ax2.axhline(y = 0, linewidth = 0.5, color = 'k')
    for i in range(len(plot_labels)):
        ax1.plot(budgets, max_distances[i], label = plot_labels[i])

        ax2.plot(budgets, flow_differences[i], label = plot_labels[i])
    ax1.set_prop_cycle(None)

    # ax2a = ax2.twinx()
    ax3.grid()
    ax3.set_ylabel('difference in proportion of flow caught compared to optimum of new situation')

    # ax2.ticklabel_format(style='plain')
    # ax3.ticklabel_format(style='plain')


    for i in range(len(plot_labels)):
        ax1.plot(budgets, mean_distances[i], 'x', label = plot_labels[i] + ' mean distance solutions')
        ax3.plot(budgets, flow_differences_new_situation[i], '--')
    ax1.legend()
    ax2.legend()
    ax3.legend()

    if sensitive_areas == True:
        fig, (ax1, ax2) = plt.subplots(1, 2)
        for i in range(len(plot_labels)):
            ax1.plot(budgets, flow_sensitive_area[i]/flow_total[i], label = plot_labels[i])
            # ax2.plot(budgets, flow_total[i], label = plot_labels[i])
        ax1.legend()


#%%


### CREATE PERTURBATIONS

def change_n_nodes():
    year = 2022
    # node_dists = [50, 70, 120, 150]

    # for dist in node_dists:
    #     G, n, K, K_i, betas, alpha, C, b, c, B, w = load_instance.MIP_input(year, dist, random_wind = False)
    #     load_instance.write_outputs(G, n, K, K_i, betas, alpha, C, b, c, B, w, str(n)+'nodes.txt')


    # filenames = ['308nodes.txt', 'init_prob_uniform10_308nodes.txt', 'init_prob_choice10_308nodes.txt', 'init_prob_uniform20_308nodes.txt', 'init_prob_choice20_308nodes.txt','init_prob_uniform_308nodes.txt']
    # labels = ['estimated', 'estimated+-10percent uniform', 'estimated+-10percent choice', 'estimated+-20percent uniform', 'estimated+-20percent choice','uniform init prob']
    filenames = ['308nodes.txt', '198nodes.txt', '250nodes.txt', '444nodes.txt', '622nodes.txt']
    labels = ['d=100', 'd=50', 'd=70', 'd=120', 'd=150']

    fixed_index = 0

    compare_runs(filenames, labels, fixed_index)
    plt.suptitle("Sensitivity analysis of number of nodes")

change_n_nodes()

def change_init_prob(G, n, K, K_i, betas, alpha, C, b, c, B, w):
    # run for different perturbations of b, save to output files

    # b_new = b*np.random.choice([0.9, 1.1], n)
    # b_new = b_new/np.sum(b_new)
    # load_instance.write_outputs(G, n, K, K_i, betas, alpha, C, b_new, c, B, w, 'init_prob_choice10_'+str(n)+'nodes.txt')

    # b_new = b*np.random.choice([0.8, 1.2], n)
    # b_new = b_new/np.sum(b_new)
    # load_instance.write_outputs(G, n, K, K_i, betas, alpha, C, b_new, c, B, w, 'init_prob_choice20_'+str(n)+'nodes.txt')


    # b_new = b*np.random.choice([0.7, 1.3], n)
    # b_new = b_new/np.sum(b_new)
    # load_instance.write_outputs(G, n, K, K_i, betas, alpha, C, b_new, c, B, w, 'init_prob_choice30_'+str(n)+'nodes.txt')

    # b_new = np.ones(n)/n
    # load_instance.write_outputs(G, n, K, K_i, betas, alpha, C, b_new, c, B, w, 'init_prob_uniform_'+str(n)+'nodes.txt')

    # plot differences in solution and flow caught
    filenames = ['308nodes.txt', 'init_prob_choice10_308nodes.txt', 'init_prob_choice20_308nodes.txt', 'init_prob_choice30_308nodes.txt', 'init_prob_uniform_308nodes.txt']
    labels = ['estimated', 'estimated+-10percent choice', 'estimated+-20percent choice','estimated+-30percent choice', 'uniform init prob']
    fixed_index = 0

    compare_runs(filenames, labels, fixed_index)
    plt.suptitle("Sensitivity analysis of initial distribution")


change_init_prob(G, n, K, K_i, betas, alpha, C, b, c, B, w)


def change_transition_prob():
    ### only run when files do not exist yet or when input has changed
    # for year in [2020, 2021, 2023]:
    #     G, n, K, K_i, betas, alpha, C, b, c, B, w = load_instance.MIP_input(year, MAX_DIST_NODES, random_wind = False)
    #     load_instance.write_outputs(G, n, K, K_i, betas, alpha, C, b, c, B, w, 'wind_year'+str(year)+'_'+str(n)+'nodes.txt')

    # G, n, K, K_i, betas, alpha, C, b, c, B, w = load_instance.MIP_input(year, MAX_DIST_NODES, random_wind = True)
    # load_instance.write_outputs(G, n, K, K_i, betas, alpha, C, b, c, B, w, 'transition_prob_uniform_'+ str(n)+'nodes.txt')

    filenames = ['wind_year2020_308nodes.txt', 'wind_year2021_308nodes.txt', '308nodes.txt', 'wind_year2023_308nodes.txt', 'transition_prob_uniform_308nodes.txt']
    labels = ['2020', '2021', '2022', '2023', 'turbulent']
    fixed_index = 2

    compare_runs(filenames, labels, fixed_index)
    plt.suptitle("Sensitivity analysis of transition probabilities due to wind")

change_transition_prob()

def change_stuck_prob(vary_factor, G, n, K, K_i, betas, alpha, C, b, c, B, w):


    if vary_factor == 1:
        # for perc in [-0.2, -0.1, 0.1, 0.2]:
        #     for node in G.nodes():
        #         new_dead_ends_prob =  G.nodes[node]['dead_ends_prob']*(1+perc)
        #         nx.set_node_attributes(G, {node: {'dead_ends_prob': new_dead_ends_prob}})
        #         probs = np.array([G.nodes[node]['dead_ends_prob'], G.nodes[node]['sharp_corners_prob'], G.nodes[node]['shore_boats_prob'], G.nodes[node]['shore_veg_prob'], G.nodes[node]['water_veg_prob']])
        #         nx.set_node_attributes(G, {node: {'stuck_probability': (1-np.prod(1-probs))}})

        #     stuck = [G.nodes[node]['stuck_probability'] for node in G.nodes()]
        #     stuck_matrix = np.repeat([stuck], len(stuck), axis = 0).T

        #     A = nx.adjacency_matrix(G, nodelist = G.nodes(), weight = 'transition_probability').toarray()
        #     C_new = (1-stuck_matrix) * A
        #     load_instance.write_outputs(G, n, K, K_i, betas, alpha, C_new, b, c, B, w, 'dead_ends_'+str(int(perc*100))+'percent_'+str(n)+'nodes.txt')

        filenames = ['308nodes.txt', 'dead_ends_-20percent_308nodes.txt', 'dead_ends_-10percent_308nodes.txt', 'dead_ends_10percent_308nodes.txt', 'dead_ends_20percent_308nodes.txt']
        labels = ['estimated', 'estimated-20percent', 'estimated-10percent', 'estimated+10percent', 'estimated+20percent']
        fixed_index = 0

        compare_runs(filenames, labels, fixed_index)
        plt.suptitle("Sensitivity analysis of dead ends in stuck probability")

    elif vary_factor == 2:
        # for perc in [-0.2, -0.1, 0.1, 0.2]:
        #     for node in G.nodes():
        #         new_sharp_corners_prob =  G.nodes[node]['sharp_corners_prob']*(1+perc)
        #         nx.set_node_attributes(G, {node: {'sharp_corners_prob': new_sharp_corners_prob}})
        #         probs = np.array([G.nodes[node]['dead_ends_prob'], G.nodes[node]['sharp_corners_prob'], G.nodes[node]['shore_boats_prob'], G.nodes[node]['shore_veg_prob'], G.nodes[node]['water_veg_prob']])
        #         nx.set_node_attributes(G, {node: {'stuck_probability': (1-np.prod(1-probs))}})

        #     stuck = [G.nodes[node]['stuck_probability'] for node in G.nodes()]
        #     stuck_matrix = np.repeat([stuck], len(stuck), axis = 0).T

        #     A = nx.adjacency_matrix(G, nodelist = G.nodes(), weight = 'transition_probability').toarray()
        #     C_new = (1-stuck_matrix) * A
        #     load_instance.write_outputs(G, n, K, K_i, betas, alpha, C_new, b, c, B, w, 'sharp_corners_'+str(int(perc*100))+'percent_'+str(n)+'nodes.txt')

        filenames = ['308nodes.txt', 'sharp_corners_-20percent_308nodes.txt', 'sharp_corners_-10percent_308nodes.txt', 'sharp_corners_10percent_308nodes.txt', 'sharp_corners_20percent_308nodes.txt']
        labels = ['estimated', 'estimated-20percent', 'estimated-10percent', 'estimated+10percent', 'estimated+20percent']
        fixed_index = 0

        compare_runs(filenames, labels, fixed_index)
        plt.suptitle("Sensitivity analysis of sharp corners in stuck probability")


    elif vary_factor == 3:
        # for perc in [0.1, 0.2, 0.4, 0.5]:
        #     for node in G.nodes():
        #         new_shore_boats_prob =  perc if G.nodes[node]['shore_boats_prob'] > 0.1 else 0
        #         nx.set_node_attributes(G, {node: {'shore_boats_prob': new_shore_boats_prob}})
        #         probs = np.array([G.nodes[node]['dead_ends_prob'], G.nodes[node]['sharp_corners_prob'], G.nodes[node]['shore_boats_prob'], G.nodes[node]['shore_veg_prob'], G.nodes[node]['water_veg_prob']])
        #         nx.set_node_attributes(G, {node: {'stuck_probability': (1-np.prod(1-probs))}})

        #     stuck = [G.nodes[node]['stuck_probability'] for node in G.nodes()]
        #     stuck_matrix = np.repeat([stuck], len(stuck), axis = 0).T

        #     A = nx.adjacency_matrix(G, nodelist = G.nodes(), weight = 'transition_probability').toarray()
        #     C_new = (1-stuck_matrix) * A
        #     load_instance.write_outputs(G, n, K, K_i, betas, alpha, C_new, b, c, B, w, 'shore_boats_'+str(int(perc*100))+'percent_'+str(n)+'nodes.txt')

        filenames = ['308nodes.txt', 'shore_boats_10percent_308nodes.txt', 'shore_boats_20percent_308nodes.txt', 'shore_boats_40percent_308nodes.txt', 'shore_boats_50percent_308nodes.txt']
        labels = ['estimated', 'boat_prob = 0.1', 'boat_prob = 0.2', 'boat_prob = 0.4', 'boat_prob = 0.5']
        fixed_index = 0

        compare_runs(filenames, labels, fixed_index)
        plt.suptitle("Sensitivity analysis of docked boats in stuck probability")


    elif vary_factor == 4:
        # for perc in [0.1, 0.2, 0.4, 0.5]:
        #     for node in G.nodes():
        #         new_shore_veg_prob =  perc if G.nodes[node]['shore_veg_prob'] > 0.1 else 0
        #         nx.set_node_attributes(G, {node: {'shore_veg_prob': new_shore_veg_prob}})
        #         probs = np.array([G.nodes[node]['dead_ends_prob'], G.nodes[node]['sharp_corners_prob'], G.nodes[node]['shore_boats_prob'], G.nodes[node]['shore_veg_prob'], G.nodes[node]['water_veg_prob']])
        #         nx.set_node_attributes(G, {node: {'stuck_probability': (1-np.prod(1-probs))}})

        #     stuck = [G.nodes[node]['stuck_probability'] for node in G.nodes()]
        #     stuck_matrix = np.repeat([stuck], len(stuck), axis = 0).T

        #     A = nx.adjacency_matrix(G, nodelist = G.nodes(), weight = 'transition_probability').toarray()
        #     C_new = (1-stuck_matrix) * A
        #     load_instance.write_outputs(G, n, K, K_i, betas, alpha, C_new, b, c, B, w, 'shore_veg_'+str(int(perc*100))+'percent_'+str(n)+'nodes.txt')

        filenames = ['308nodes.txt', 'shore_veg_10percent_308nodes.txt', 'shore_veg_20percent_308nodes.txt', 'shore_veg_40percent_308nodes.txt', 'shore_veg_50percent_308nodes.txt']
        labels = ['estimated', 'shore_veg_prob = 0.1', 'shore_veg_prob = 0.2', 'shore_veg_prob = 0.4', 'shore_veg_prob = 0.5']
        fixed_index = 0

        compare_runs(filenames, labels, fixed_index)
        plt.suptitle("Sensitivity analysis of shore vegetation in stuck probability")

    elif vary_factor == 5:
        # for perc in [0, 0.3, 0.6, 0.9]:
        #     for node in G.nodes():
        #         new_water_veg_prob =  perc if G.nodes[node]['water_veg_prob'] > 0.1 else 0
        #         nx.set_node_attributes(G, {node: {'water_veg_prob': new_water_veg_prob}})
        #         probs = np.array([G.nodes[node]['dead_ends_prob'], G.nodes[node]['sharp_corners_prob'], G.nodes[node]['shore_boats_prob'], G.nodes[node]['shore_veg_prob'], G.nodes[node]['water_veg_prob']])
        #         nx.set_node_attributes(G, {node: {'stuck_probability': (1-np.prod(1-probs))}})

        #     stuck = [G.nodes[node]['stuck_probability'] for node in G.nodes()]
        #     stuck_matrix = np.repeat([stuck], len(stuck), axis = 0).T

        #     A = nx.adjacency_matrix(G, nodelist = G.nodes(), weight = 'transition_probability').toarray()
        #     C_new = (1-stuck_matrix) * A
        #     load_instance.write_outputs(G, n, K, K_i, betas, alpha, C_new, b, c, B, w, 'water_veg_'+str(int(perc*100))+'percent_'+str(n)+'nodes.txt')

        filenames = ['308nodes.txt', 'water_veg_0percent_308nodes.txt', 'water_veg_30percent_308nodes.txt', 'water_veg_60percent_308nodes.txt', 'water_veg_90percent_308nodes.txt']
        labels = ['estimated', 'water_veg_prob = 0', 'shore_veg_prob = 0.3', 'shore_veg_prob = 0.6', 'shore_veg_prob = 0.9']
        fixed_index = 0

        compare_runs(filenames, labels, fixed_index)
        plt.suptitle("Sensitivity analysis of water vegetation in stuck probability")

change_stuck_prob(1, G, n, K, K_i, betas, alpha, C, b, c, B, w)
change_stuck_prob(2, G, n, K, K_i, betas, alpha, C, b, c, B, w)
change_stuck_prob(3, G, n, K, K_i, betas, alpha, C, b, c, B, w)
change_stuck_prob(4, G, n, K, K_i, betas, alpha, C, b, c, B, w)
change_stuck_prob(5, G, n, K, K_i, betas, alpha, C, b, c, B, w)


def change_catching_prob(G, n, K, K_i, betas, alpha, C, b, c, B, w):
    # for perc in [-0.2, -0.1, 0.1, 0.2]:
    #     for node in G.nodes():
    #         new_catching_prob =  G.nodes[node]['catching_probability']*(1+perc)
    #         nx.set_node_attributes(G, {node: {'catching_probability': new_catching_prob}})

    #     catching = np.array([G.nodes[node]['catching_probability'] for node in G.nodes()])
    #     new_betas = np.stack((0.98*catching, 0.85*catching)).T


    #     load_instance.write_outputs(G, n, K, K_i, new_betas, alpha, C, b, c, B, w, 'catching_'+str(int(perc*100))+'percent_'+str(n)+'nodes.txt')

    filenames = ['308nodes.txt', 'catching_-20percent_308nodes.txt', 'catching_-10percent_308nodes.txt', 'catching_10percent_308nodes.txt', 'catching_20percent_308nodes.txt']
    labels = ['estimated', 'estimated-20percent', 'estimated-10percent', 'estimated+10percent', 'estimated+20percent']
    fixed_index = 0

    compare_runs(filenames, labels, fixed_index)
    plt.suptitle("Sensitivity analysis of catching probability")

change_catching_prob(G, n, K, K_i, betas, alpha, C, b, c, B, w)

def change_impact_factor(G, n, K, K_i, betas, alpha, C, b, c, B, w):
    ### 1. impact factor the same value everywhere, higher lower etc
    ### impact factor = 0
    alpha_new = n * [0]
    # load_instance.write_outputs(G, n, K, K_i, betas, alpha_new, C, b, c, B, w, 'impact_factor_0_'+str(n)+'nodes.txt')

    ### examine M1 and M2 for values of alpha
    
    # M1 = b.T @ np.linalg.inv(np.eye(n)-C)
    M2 = np.zeros((n,K))
    for i in range(n):
        for k in range(K):
            diagB = np.eye(n)
            diagB[i,i] = 1 - betas[i,k]
            M2[i,k] = (b.T @ np.linalg.inv(np.eye(n)- diagB @ C))[i]
    
    
    # alpha_new = n * [np.mean((betas*M2)[(betas*M2) > 0])]
    # load_instance.write_outputs(G, n, K, K_i, betas, alpha_new, C, b, c, B, w, 'impact_factor_meanbetaM2_'+str(n)+'nodes.txt')

    # alpha_new = n * [np.max((betas*M2)[(betas*M2) > 0])]
    # load_instance.write_outputs(G, n, K, K_i, betas, alpha_new, C, b, c, B, w, 'impact_factor_maxbetaM2_'+str(n)+'nodes.txt')

    filenames = ['308nodes.txt', 'impact_factor_0_308nodes.txt', 'impact_factor_meanbetaM2_308nodes.txt', 'impact_factor_maxbetaM2_308nodes.txt']
    labels = ['estimated', 'alpha = 0', 'alpha = mean(beta*M2)', 'alpha = max(beta*M2)']
    fixed_index = 0

    compare_runs(filenames, labels, fixed_index)
    plt.suptitle("Sensitivity analysis of impact factor")


    ### 2. impact factor zero with value for area, higher lower
    ### impact factor value everywhere and extra value for area, higher and lower
    ## plot amount of flow caught in total vs amount of flow in area
    # alpha_new = copy.copy(alpha)
    # alpha_new2 = copy.copy(alpha)
    # alpha_new4 = copy.copy(alpha)
    # alpha_new6 = copy.copy(alpha)
    # for index, node in enumerate(G.nodes()):
    #     alpha_new[index] += G.nodes[node]['impact_factor']
    #     alpha_new2[index] += G.nodes[node]['impact_factor']*2
    #     alpha_new4[index] += G.nodes[node]['impact_factor']*4
    #     alpha_new6[index] += G.nodes[node]['impact_factor']*6
    # load_instance.write_outputs(G, n, K, K_i, betas, alpha_new, C, b, c, B, w, 'impact_factor_area0.1_'+str(n)+'nodes.txt', show_impact_flow = True)
    # load_instance.write_outputs(G, n, K, K_i, betas, alpha_new2, C, b, c, B, w, 'impact_factor_area0.2_'+str(n)+'nodes.txt', show_impact_flow = True)
    # load_instance.write_outputs(G, n, K, K_i, betas, alpha_new4, C, b, c, B, w, 'impact_factor_area0.4_'+str(n)+'nodes.txt', show_impact_flow = True)
    # load_instance.write_outputs(G, n, K, K_i, betas, alpha_new6, C, b, c, B, w, 'impact_factor_area0.6_'+str(n)+'nodes.txt', show_impact_flow = True)

    filenames = ['308nodes.txt', 'impact_factor_area0.1_308nodes.txt', 'impact_factor_area0.2_308nodes.txt', 'impact_factor_area0.4_308nodes.txt', 'impact_factor_area0.6_308nodes.txt']
    labels = ['estimated', 'alpha = 0.1', 'alpha = 0.2', 'alpha = 0.4', 'alpha = 0.6']
    fixed_index = 0



    ### 3. impact factor zero and value for edge, higher lower
    ### impact factor value everywhere and extra for edge, higher and lower
    ## plot amount of flow caught in total vs amount of flow in area




change_impact_factor(G, n, K, K_i, betas, alpha, C, b, c, B, w)

#%% test w term in obj function


#%%
### TESTS


# with open('308nodes.txt') as f:
#     run1 = f.readlines()
# run1 = [eval(line.strip()) for line in run1]

# with open('338nodes.txt') as f:
#     run2 = f.readlines()
# run2 = [eval(line.strip()) for line in run2]


# distances = np.zeros(len(run1)-1)
# difference_caught_flow = np.zeros(len(run1)-1)
# for budget_index in range(len(run1)-1):
#     locations1 = [list(i[-1]) for i in run1[budget_index + 1][-1]]
#     locations2 = [list(i[-1]) for i in run2[budget_index + 1][-1]]

#     pairwise_distances = distance.cdist(locations1, locations2)
#     row_ind, col_ind = linear_sum_assignment(pairwise_distances)
#     mean_distance = pairwise_distances[row_ind, col_ind].sum()/len(locations1)
#     max_distance = np.max(pairwise_distances[row_ind, col_ind])
#     distances[budget_index] = max_distance
#     # difference_caught_flow[budget_index] = run1[]

#     # caught
# #%%

# filenames = ['wind_year2020_308nodes.txt', 'wind_year2021_308nodes.txt', '308nodes.txt', 'wind_year2023_308nodes.txt', 'transition_prob_uniform_308nodes.txt']
# variations = ['2020', '2021', '2022', '2023', 'turbulent']
# fixed_index = 2

# runs = []
# for filename in filenames:
#     with open(filename) as f:
#         run = f.readlines()
#     run = [eval(line.strip()) for line in run]
#     runs += [run]

# distances = np.zeros((len(runs)-1, len(runs[1])-1))
# flow_differences = np.zeros((len(runs)-1, len(runs[1])-1))

# list_index = 0
# for i, run in enumerate(runs):
#     if i != fixed_index:
#         for j, budget in enumerate(run[1:]):
#             locations_i = [list(system[-1]) for system in budget[-1]]
#             locations_fixed = [list(system[-1]) for system in runs[fixed_index][j+1][-1]]

#             pairwise_distances = distance.cdist(locations_i, locations_fixed)
#             row_ind, col_ind = linear_sum_assignment(pairwise_distances)

#             # choose one of three to report
#             total_distance = pairwise_distances[row_ind, col_ind].sum()
#             mean_distance = pairwise_distances[row_ind, col_ind].sum()/len(locations1)
#             max_distance = np.max(pairwise_distances[row_ind, col_ind])

#             distances[list_index, j] = total_distance
#             flow_differences[list_index,j] = budget[3]-runs[fixed_index][j+1][3]
#         list_index += 1

# budgets = [row[0] for row in runs[0][1:]]
# plot_labels = variations[:fixed_index] + variations[fixed_index+1:]

# #%% two plots

# fig, (ax1, ax2) = plt.subplots(1, 2)
# # ax.title("Sensitivity analysis of wind directions compared to 2022")

# ax1.grid()
# ax1.set_xlabel('budget')
# ax1.set_ylabel('total distance between solutions')
# ax1.legend()

# ax2.set_ylabel('difference in proportion of flow caught')

# ax2.grid()
# ax2.axhline(y = 0, linewidth = 0.5, color = 'k')
# for i in range(len(plot_labels)):
#     ax1.plot(budgets, distances[i], label = plot_labels[i])
#     ax2.plot(budgets, flow_differences[i], label = plot_labels[i])

# ax2.legend()



#%% one plot with double axes

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