# -*- coding: utf-8 -*-
"""
Created on Tue Mar 26 13:59:42 2024

@author: Anne-Fleur
"""

import numpy as np
from scipy.spatial import distance
from scipy.optimize import linear_sum_assignment
# import matplotlib
import matplotlib.pyplot as plt
import networkx as nx
import copy
import time
### LOAD INPUT
import load_instance

import os
dirname = os.path.dirname(__file__)
import sys
sys.path.insert(1, dirname+'\\pulp_scripts')
import MDP_exact



#%% base scenario

year = 2022
MAX_DIST_NODES = 60
G, n, K, K_i, betas, alpha, C, b, c, B, w = load_instance.MIP_input(year, MAX_DIST_NODES, random_wind = False)


#%% first write solutions in array, then write base solutions file

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

# Bmax = 2
# for index, node in enumerate(G.nodes()):
#     nx.set_node_attributes(G, {node: {'impact_factor': alpha[index]}})
# load_instance.write_outputs(G, n, K, K_i, betas, alpha, C, b, c, Bmax, w, str(n)+'nodes.txt', show_impact_flow = True)


#%%
# matplotlib.rcParams.update(matplotlib.rcParamsDefault)
plt.rc('font', size=12)
# matplotlib.rc('text', usetex=True)
# matplotlib.rc('text.latex', preamble=r'\usepackage{amsmath}')
def compare_runs(filenames, labels, fixed_index, sensitive_areas = False, alphas = []):
    runs = []
    for filename in filenames:
        with open(filename) as f:
            run = f.readlines()
        run = [eval(line.strip()) for line in run]
        runs += [run]

    # n_rows = len(runs)-1 #rows are the number of different scenarios that we are comparing
    # n_cols = len(runs[1])-1 #columns are the different budget, we use the number of budgets of the second file in the input filenames
    # mean_distances = np.zeros((n_rows, n_cols))
    # max_distances = np.zeros((n_rows, n_cols))
    # flow_differences = np.zeros((n_rows, n_cols)) # difference between caught flow with fixed solution and expected flow (from base scenario) with fixed solution
    # flow_differences_new_situation = np.zeros((n_rows, n_cols)) # difference between caught flow with fixed solution and caught flow with optimal solution in new scenario (compared to having perfect knowledge)

    # flow_total = np.zeros((n_rows, n_cols))
    # flow_sensitive_area = np.zeros((n_rows, n_cols))
    # flow_total_fixed = np.zeros(n_cols)
    # flow_sensitive_fixed = np.zeros(n_cols)

    mean_distances = [[]]
    max_distances = [[]]
    flow_differences = [[]] # difference between caught flow with fixed solution and expected flow (from base scenario) with fixed solution
    flow_differences_new_situation = [[]] # difference between caught flow with fixed solution and caught flow with optimal solution in new scenario (compared to having perfect knowledge)

    flow_total = [[]]
    flow_sensitive_area = [[]]
    flow_total_fixed = []
    flow_sensitive_fixed = []

    list_index = 0
    for i, run in enumerate(runs):
        if i != fixed_index:
            for j, budget in enumerate(run[1:]):
                # if j < n_cols:
                locations_i = [list(system[-1]) for system in budget[-1]]
                locations_fixed = [list(system[-1]) for system in runs[fixed_index][j+1][-1]]
    
                pairwise_distances = distance.cdist(locations_i, locations_fixed)
                row_ind, col_ind = linear_sum_assignment(pairwise_distances)
    
                # choose one of three to report
                total_distance = pairwise_distances[row_ind, col_ind].sum()
                mean_distance = (pairwise_distances[row_ind, col_ind].sum())/len(locations_i)
                max_distance = np.max(pairwise_distances[row_ind, col_ind])
    
                mean_distances[list_index] += [mean_distance]
                max_distances[list_index] += [max_distance]
                flow_differences[list_index] += [(budget[4]-runs[fixed_index][j+1][3])/runs[fixed_index][j+1][3]] #4th entry of each run with different budget is the flow_caught with same fixed solution from base case
                flow_differences_new_situation[list_index] += [(budget[4]-budget[3])/budget[3]]
                flow_sensitive_area[list_index] += [budget[5]]
                flow_total[list_index] += [budget[3]]
            list_index += 1
            mean_distances += [[]]
            max_distances += [[]]
            flow_differences += [[]] # difference between caught flow with fixed solution and expected flow (from base scenario) with fixed solution
            flow_differences_new_situation += [[]] # difference between caught flow with fixed solution and caught flow with optimal solution in new scenario (compared to having perfect knowledge)

            flow_total += [[]]
            flow_sensitive_area += [[]]
        else:
            for j, budget in enumerate(run[1:]):
                # if j < n_cols:
                flow_total_fixed += [budget[3]]
                flow_sensitive_fixed += [budget[5]]

    budgets = [row[0] for row in runs[1][1:]] # 0.2*np.arange(len(max_distances[i]))+0.2
    plot_labels = labels[:fixed_index] + labels[fixed_index+1:]
    
    if sensitive_areas == False:
    
        # fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize = (18, 5))
        fig, (ax1, ax3) = plt.subplots(1, 2, figsize = (14, 6))
        # ax.title("Sensitivity analysis of wind directions compared to 2022")
        
        ax1.grid()
        ax1.set_title('Maximum and mean distance between new optimal \n solution and base scenario')
        ax1.set_xlabel('budget')
        ax1.set_ylabel('distance between solutions')
        ax1.set_ylim(bottom = -100, top = 2800)
        # ax1.set_ylim(bottom = 0, top = 5100)

        # ax1a = ax1.twinx()
    
        # ax2.set_xlabel('budget')
        # ax2.set_ylabel('relative difference flow caught compared to base situation')
        # ax2.set_ylim(bottom = -0.4, top = 0.2)

        # ax2.grid()
        # ax2.axhline(y = 0, linewidth = 0.5, color = 'k')
        # ax2.plot(budgets, [runs[fixed_index][j+1][3] for j in range(len(runs[1])-1)], '--', label = 'flow caught base situation')
        for i in range(len(plot_labels)):
            # ax1.plot(budgets, max_distances[i], label = plot_labels[i])
            ax1.plot(0.2*np.arange(len(max_distances[i]))+0.2, max_distances[i], label = plot_labels[i])


            # ax2.plot(budgets, flow_differences[i], label = plot_labels[i])
        ax1.set_prop_cycle(None)
    
        # ax2a = ax2.twinx()
        ax3.grid()
        ax3.set_title('Relative difference of flow caught with fixed base scenario \n solution compared to optimum of new scenario')
        ax3.set_xlabel('budget')
        ax3.set_ylabel('relative difference flow caught')
        # ax3.set_ylim(bottom = -0.5, top = 0.005)
        ax3.set_ylim(bottom = -0.6, top = 0.05)

        # ax2.ticklabel_format(style='plain')
        # ax3.ticklabel_format(style='plain')
    
    
        for i in range(len(plot_labels)):
            # ax1.plot(budgets, mean_distances[i], 'x')#, label = plot_labels[i] + ' mean distance solutions')
            ax1.plot(0.2*np.arange(len(mean_distances[i]))+0.2, mean_distances[i], 'x')
            # ax3.plot(budgets, flow_differences_new_situation[i], label = plot_labels[i])
            ax3.plot(0.2*np.arange(len(flow_differences_new_situation[i]))+0.2, flow_differences_new_situation[i], label = plot_labels[i])
        ax1.legend()
        # ax2.legend()
        # ax3.legend()

    else:
        fig, axs = plt.subplots(2, 2, figsize = (14, 10))
        for i in range(len(plot_labels)):
            axs[1,1].plot(budgets, max_distances[i], label = plot_labels[i])
        axs[1,1].set_prop_cycle(None)
        for i in range(len(plot_labels)):
            axs[1,1].plot(budgets, mean_distances[i], 'x')
        axs[1,1].legend()
        axs[1,1].set_ylabel("Distance between solution and alpha = 0")
            
            
        # for i in range(len(runs[1])-9):
        # for j in range(1,3):
            # i = j*5-1
        for i in [1, 3, 5, 7, 9]:
            flow_total_B = np.array([flow_total[j][i] for j in range(len(runs)-1)])
            flow_sensitive_area_B = np.array([flow_sensitive_area[j][i] for j in range(len(runs)-1)])
            if fixed_index == 0: #when testing compared to low alpha
                # DELETE IF FOLLOWING LINE WORKS axs[0,0].plot(alphas, np.append(flow_total_fixed[i], flow_total[:][i]), '-o', label = 'B='+str(round(budgets[i], 1)))
                axs[0,0].plot(alphas, np.append(flow_total_fixed[i], flow_total_B), '-o', label = 'B='+str(round(budgets[i], 1)))
                # DELETE IF FOLLOWING LINE WORKS axs[0,1].plot(alphas, np.append(flow_sensitive_fixed[i], flow_sensitive_area[:,i]), '-o')
                axs[0,1].plot(alphas, np.append(flow_sensitive_fixed[i], flow_sensitive_area_B), '-o')
                # DELETE IF FOLLOWING LINE WORKS axs[1,0].plot(alphas[1:], (flow_total[:][i]-flow_total_fixed[i])/(flow_sensitive_area[:][i]-flow_sensitive_fixed[i]), '-o')
                axs[1,0].plot(alphas[1:], (flow_total_B-flow_total_fixed[i])/(flow_sensitive_area_B-flow_sensitive_fixed[i]), '-o')
            else: #when testing compared to higher alpha
                ### DELETE IF BELOW LINES WORK!
                # axs[0,0].plot(alphas, np.append(flow_total[:][i], flow_total_fixed[i]), '-o', label = 'B='+str(round(budgets[i], 1)))
                # axs[0,1].plot(alphas, np.append(flow_sensitive_area[:][i], flow_sensitive_fixed[i]), '-o')
                # axs[1,0].plot(alphas[:-1], (flow_total[:][i]-flow_total_fixed[i])/(flow_sensitive_area[:][i]-flow_sensitive_fixed[i]), '-o')
                axs[0,0].plot(alphas, np.append(flow_total_B, flow_total_fixed[i]), '-o', label = 'B='+str(round(budgets[i], 1)))
                axs[0,1].plot(alphas, np.append(flow_sensitive_area_B, flow_sensitive_fixed[i]), '-o')
                axs[1,0].plot(alphas[:-1], (flow_total_B-flow_total_fixed[i])/(flow_sensitive_area_B-flow_sensitive_fixed[i]), '-o')

        axs[0,0].legend()
        axs[0,0].set_ylabel("Total flow caught in optimum")
        axs[0,1].set_ylabel("Total flow in sensitive area in optimum")
        axs[1,0].set_ylabel(r"$ \Delta $ total flow caught / $ \Delta $ flow in sensitive area")
        axs[1,1].set_title(r'Compared to solution $\hat{x}$')
        axs[1,0].set_title(r'Compared to solution $\tilde{x}$')
        axs[0,0].set_xlabel(r"$ \alpha $")
        axs[0,1].set_xlabel(r"$ \alpha $")
        axs[1,0].set_xlabel(r"$ \alpha $")
        
        axs[1,0].plot(alphas, alphas, '--')

    # fig.savefig('plots/'+save_filename)
    return fig


def compare_runs_random_init(filenames, labels, fixed_index):
    runs = []
    for filename in filenames:
        with open(filename) as f:
            run = f.readlines()
        run = [eval(line.strip()) for line in run]
        runs += [run]

    n_rows = len(runs)-1 #rows are the number of different scenarios that we are comparing
    n_cols = len(runs[1])-1 #columns are the different budget, we use the number of budgets of the second file in the input filenames
    mean_distances_all = np.zeros((n_rows, n_cols))
    max_distances_all = np.zeros((n_rows, n_cols))
    flow_differences_all = np.zeros((n_rows, n_cols)) # difference between caught flow with fixed solution and expected flow (from base scenario) with fixed solution
    flow_differences_new_situation_all = np.zeros((n_rows, n_cols)) # difference between caught flow with fixed solution and caught flow with optimal solution in new scenario (compared to having perfect knowledge)

    list_index = 0
    for i, run in enumerate(runs):
        if i != fixed_index:
            for j, budget in enumerate(run[1:]):
                if j < n_cols:
                    locations_i = [list(system[-1]) for system in budget[-1]]
                    locations_fixed = [list(system[-1]) for system in runs[fixed_index][j+1][-1]]
        
                    pairwise_distances = distance.cdist(locations_i, locations_fixed)
                    row_ind, col_ind = linear_sum_assignment(pairwise_distances)
        
                    # choose one of three to report
                    total_distance = pairwise_distances[row_ind, col_ind].sum()
                    mean_distance = (pairwise_distances[row_ind, col_ind].sum())/len(locations_i)
                    max_distance = np.max(pairwise_distances[row_ind, col_ind])
        
                    mean_distances_all[list_index, j] = mean_distance
                    max_distances_all[list_index, j] = max_distance
                    flow_differences_all[list_index,j] = (budget[4]-runs[fixed_index][j+1][3])/runs[fixed_index][j+1][3] #4th entry of each run with different budget is the flow_caught with same fixed solution from base case
                    flow_differences_new_situation_all[list_index,j] = (budget[4]-budget[3])/budget[3]
            list_index += 1

    mean_distances = np.stack((np.sum(mean_distances_all[0:10], axis = 0)/10, np.sum(mean_distances_all[10:20], axis = 0)/10, np.sum(mean_distances_all[20:30], axis = 0)/10, mean_distances_all[30]), axis = 0)
    max_distances = np.stack((np.sum(max_distances_all[0:10], axis = 0)/10, np.sum(max_distances_all[10:20], axis = 0)/10, np.sum(max_distances_all[20:30], axis = 0)/10, max_distances_all[30]), axis = 0)
    flow_differences = np.stack((np.sum(flow_differences_all[0:10], axis = 0)/10, np.sum(flow_differences_all[10:20], axis = 0)/10, np.sum(flow_differences_all[20:30], axis = 0)/10,flow_differences_all[30]), axis = 0) # difference between caught flow with fixed solution and expected flow (from base scenario) with fixed solution
    flow_differences_new_situation = np.stack((np.sum(flow_differences_new_situation_all[0:10], axis = 0)/10, np.sum(flow_differences_new_situation_all[10:20], axis = 0)/10, np.sum(flow_differences_new_situation_all[20:30], axis = 0)/10,flow_differences_new_situation_all[30]), axis = 0) # difference between caught flow with fixed solution and caught flow with optimal solution in new scenario (compared to having perfect knowledge)

    # mean_distances = np.stack((np.sum(mean_distances_all[0:2], axis = 0)/2, np.sum(mean_distances_all[2:4], axis = 0)/2, np.sum(mean_distances_all[4:6], axis = 0)/2, mean_distances_all[6]), axis = 0)
    # max_distances = np.stack((np.sum(max_distances_all[0:2], axis = 0)/2, np.sum(max_distances_all[2:4], axis = 0)/2, np.sum(max_distances_all[4:6], axis = 0)/2, max_distances_all[6]), axis = 0)
    # flow_differences = np.stack((np.sum(flow_differences_all[0:2], axis = 0)/2, np.sum(flow_differences_all[2:4], axis = 0)/2, np.sum(flow_differences_all[4:6], axis = 0)/2,flow_differences_all[6]), axis = 0) # difference between caught flow with fixed solution and expected flow (from base scenario) with fixed solution
    # flow_differences_new_situation = np.stack((np.sum(flow_differences_new_situation_all[0:2], axis = 0)/2, np.sum(flow_differences_new_situation_all[2:4], axis = 0)/2, np.sum(flow_differences_new_situation_all[4:6], axis = 0)/2,flow_differences_new_situation_all[6]), axis = 0) # difference between caught flow with fixed solution and caught flow with optimal solution in new scenario (compared to having perfect knowledge)


    budgets = [row[0] for row in runs[1][1:]]
    plot_labels = labels[:fixed_index] + labels[fixed_index+1:]

    # fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize = (18, 5))
    fig, (ax1, ax3) = plt.subplots(1, 2, figsize = (14, 6))
    # ax.title("Sensitivity analysis of wind directions compared to 2022")
    
    ax1.grid()
    ax1.set_title('Maximum and mean distance between new optimal \n solution and base scenario')
    ax1.set_xlabel('budget')
    ax1.set_ylabel('distance between solutions')
    ax1.set_ylim(-100, 2800)
    # ax1.set_ylim(0, 5100)

    # ax1a = ax1.twinx()

    # ax2.set_xlabel('budget')
    # ax2.set_ylabel('relative difference flow caught compared to base situation')
    # ax2.set_ylim(-0.4, 0.2)
    
    # ax2.grid()
    # ax2.axhline(y = 0, linewidth = 0.5, color = 'k')
    # ax2.plot(budgets, [runs[fixed_index][j+1][3] for j in range(len(runs[1])-1)], '--', label = 'flow caught base situation')
    for i in range(len(plot_labels)):
        ax1.plot(budgets, max_distances[i], label = plot_labels[i])

        # ax2.plot(budgets, flow_differences[i], label = plot_labels[i])
    ax1.set_prop_cycle(None)

    # ax2a = ax2.twinx()
    ax3.grid()
    ax3.set_title('Relative difference of flow caught with fixed base scenario \n solution compared to optimum of new scenario')
    ax3.set_xlabel('budget')
    ax3.set_ylabel('relative difference flow caught')
    ax3.set_ylim(-0.6, 0.05)

    # ax2.ticklabel_format(style='plain')
    # ax3.ticklabel_format(style='plain')


    for i in range(len(plot_labels)):
        ax1.plot(budgets, mean_distances[i], 'x')#, label = plot_labels[i] + ' mean distance solutions')
        ax3.plot(budgets, flow_differences_new_situation[i])
    ax1.legend()
    # ax2.legend()
    # ax3.legend()

    # plt.suptitle("Sensitivity analysis of initial distribution")
    fig.tight_layout
    fig.savefig('plots/init_prob.png', bbox_inches='tight', pad_inches=0.05)


def compare_runs_impact_factor(filenames, labels, alphas, budget_indices, delta_calculation = False):
    runs = []
    for filename in filenames:
        with open(filename) as f:
            run = f.readlines()
        run = [eval(line.strip()) for line in run]
        runs += [run]


    n_rows = len(runs)
    n_cols = len(runs[0])-1
    flow_total = np.zeros((n_rows, n_cols))
    flow_sensitive_area = np.zeros((n_rows, n_cols))

    for i, run in enumerate(runs):
            for j, budget in enumerate(run[1:]):
                flow_total[i,j] = budget[3]
                flow_sensitive_area[i,j] = budget[5]

    budgets = [row[0] for row in runs[1][1:]] # 0.2*np.arange(len(max_distances[i]))+0.2
    # plot_labels = labels

    if delta_calculation == True:
        fig, ((ax1, ax2),(ax3, ax4)) = plt.subplots(2, 2, figsize = (14, 10))
    else:
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize = (14, 6))


    # for i in range(len(runs[1])-9):
    # for j in range(1,3):
        # i = j*5-1
    # for i in [1, 3, 5, 7, 9]:
    for i in budget_indices:
        ax1.plot(alphas, flow_total[:,i], '-o', label = 'B='+str(round(budgets[i], 1)))
        ax2.plot(alphas, flow_sensitive_area[:,i], '-o')

        if delta_calculation == True:
            ax3.plot(alphas[1:], (flow_total[1:, i]-flow_total[0, i])/(flow_sensitive_area[1:,i]-flow_sensitive_area[0, i]), '-o')
            ax4.plot(alphas[:-1], (flow_total[:-1, i]-flow_total[-1, i])/(flow_sensitive_area[:-1,i]-flow_sensitive_area[-1, i]), '-o')

    ax1.legend()
    ax1.set_ylabel("Total flow caught")
    ax1.set_title("Total flow caught in optimum")
    ax2.set_ylabel("Total flow in sensitive area")
    ax2.set_title("Total flow in sensitive area in optimum")
    ax1.set_xlabel(r"$ \alpha $")
    ax2.set_xlabel(r"$ \alpha $")

    if delta_calculation == True:
        ax3.set_xlabel(r"$ \alpha $")
        ax4.set_xlabel(r"$ \alpha $")
        ax3.set_ylabel(r"$ \Delta $ total flow caught / $ \Delta $ flow in sensitive area")
        ax4.set_ylabel(r"$ \Delta $ total flow caught / $ \Delta $ flow in sensitive area")
        ax3.plot(alphas, alphas, '--')
        ax3.set_ylim(-0.01, alphas[-1]+0.01)
        ax4.plot(alphas, alphas, '--')
        ax4.set_ylim(-0.01, alphas[-1]+0.01)
        ax3.set_title(r'Compared to solution $x^{+}$')
        ax4.set_title(r'Compared to solution $x^{-}$')

    return fig


#%%

### CREATE PERTURBATIONS

def change_n_nodes():
    year = 2022
    # node_dists = [50, 75, 125, 150]
    # node_dists = [125, 150]
    # node_dists = [50 , 75]
    # node_dists = [70, 60, 40, 30]
    # node_dists = [40, 60, 70, 80, 90]
    # Bmax = 2
    # node_dists = [30]
    # Bmax = 1.8
    # node_dists = [80, 70, 50, 40]
    # for dist in node_dists:
    #     G, n, K, K_i, betas, alpha, C, b, c, B, w = load_instance.MIP_input(year, dist, random_wind = False)
    #     for index, node in enumerate(G.nodes()):
    #         nx.set_node_attributes(G, {node: {'impact_factor': alpha[index]}})
    #     load_instance.write_outputs(G, n, K, K_i, betas, alpha, C, b, c, Bmax, w, str(n)+'nodes_compared_d50.txt', show_impact_flow=True)
        # load_instance.write_outputs_warm_heuristic(G, n, K, K_i, betas, alpha, C, b, c, B, w, str(n)+'nodes_B2.txt', show_impact_flow=True)


    # filenames = ['308nodes.txt', '622nodes_B2.txt', '412nodes_B2.txt', '198nodes.txt', '244nodes.txt']
    # labels = ['d=100', 'd=50', 'd=75', 'd=150', 'd=125']

    # fixed_index = 0

    # fig = compare_runs(filenames, labels, fixed_index)
    # plt.suptitle("Sensitivity analysis of number of nodes compared to d=100, n=308")
    # fig.savefig('plots/nodes_compared_d100.png')

    # # filenames = ['784nodes_B2.txt', '622nodes_B2.txt', '522nodes_B2.txt', '444nodes_B2.txt', '390nodes_B2.txt', '338nodes_B2.txt', '308nodes.txt']
    # # labels = ['d=40', 'd=50', 'd=60', 'd=70', 'd=80', 'd=90', 'd=100']

    # # fixed_index = 2

#     filenames = ['1054nodes_compared_d60.txt', '784nodes_compared_d60.txt', '622nodes_compared_d60.txt', '522nodes_B2.txt', '444nodes_compared_d60.txt', '390nodes_compared_d60.txt']
#     labels = ['d=30', 'd=40', 'd=50', 'd=60', 'd=70', 'd=80']
#     # filenames = ['1054nodes_compared_d50.txt', '784nodes_compared_d50.txt', '622nodes.txt', '522nodes_compared_d50.txt', '444nodes_compared_d50.txt', '390nodes_compared_d50.txt']
#     # labels = ['d=30', 'd=40', 'd=50', 'd=60', 'd=70', 'd=80']

#     fixed_index = 3

#     fig = compare_runs(filenames, labels, fixed_index)
#     plt.suptitle("Sensitivity analysis of number of nodes compared to d=60, n=522")
#     fig.savefig('plots/nodes_compared_d60.png', bbox_inches='tight', pad_inches=0.05)

# change_n_nodes()

def change_init_prob(G, n, K, K_i, betas, alpha, C, b, c, B, w):
    # run for different perturbations of b, save to output files
    Bmax = 2
    np.random.seed(0)

    # for i in range(1,11):
    #     b_new = b*np.random.choice([0.9, 1.1], n)
    #     b_new = b_new/np.sum(b_new)
    #     load_instance.write_outputs(G, n, K, K_i, betas, alpha, C, b_new, c, Bmax, w, 'init_prob_choice10_'+str(i)+'_'+str(n)+'nodes.txt')
    
    #     b_new = b*np.random.choice([0.8, 1.2], n)
    #     b_new = b_new/np.sum(b_new)
    #     load_instance.write_outputs(G, n, K, K_i, betas, alpha, C, b_new, c, Bmax, w, 'init_prob_choice20_'+str(i)+'_'+str(n)+'nodes.txt')
    
    #     b_new = b*np.random.choice([0.7, 1.3], n)
    #     b_new = b_new/np.sum(b_new)
    #     load_instance.write_outputs(G, n, K, K_i, betas, alpha, C, b_new, c, Bmax, w, 'init_prob_choice30_'+str(i)+'_'+str(n)+'nodes.txt')


    # b_new = np.ones(n)/n
    # load_instance.write_outputs(G, n, K, K_i, betas, alpha, C, b_new, c, Bmax, w, 'init_prob_uniform_'+str(n)+'nodes.txt')

    filenames = ['308nodes.txt', 'init_prob_choice10_308nodes.txt', 'init_prob_choice20_308nodes.txt', 'init_prob_choice30_308nodes.txt', 'init_prob_uniform_308nodes.txt']
    labels = ['estimated', 'estimated+-10percent choice', 'estimated+-20percent choice','estimated+-30percent choice', 'uniform init prob']
    labels = [r'$b$', r'$\mathbf{b}\pm 0.1\mathbf{b}$', r'$\mathbf{b}\pm 0.2\mathbf{b}$',r'$\mathbf{b}\pm 0.3\mathbf{b}$', '1/n']
    fixed_index = 0

    filenames = ['308nodes.txt'] + ['init_prob_choice10_'+str(i)+'_308nodes.txt' for i in range(1,11)] +['init_prob_choice20_'+str(i)+'_308nodes.txt' for i in range(1,11)] + ['init_prob_choice30_'+str(i)+'_308nodes.txt' for i in range(1,11)] + ['init_prob_uniform_308nodes.txt']
    filenames = ['522nodes.txt'] + ['init_prob_choice10_'+str(i)+'_522nodes.txt' for i in range(1,11)] +['init_prob_choice20_'+str(i)+'_522nodes.txt' for i in range(1,11)] + ['init_prob_choice30_'+str(i)+'_522nodes.txt' for i in range(1,11)] + ['init_prob_uniform_522nodes.txt']
    # filenames = ['308nodes.txt'] + ['init_prob_choice10_'+str(i)+'_308nodes.txt' for i in range(1,3)] +['init_prob_choice20_'+str(i)+'_308nodes.txt' for i in range(1,3)] + ['init_prob_choice30_'+str(i)+'_308nodes.txt' for i in range(1,3)] + ['init_prob_uniform_308nodes.txt']

    compare_runs_random_init(filenames, labels, fixed_index)

change_init_prob(G, n, K, K_i, betas, alpha, C, b, c, B, w)

#%%


def change_transition_prob():
    Bmax = 2
    ### only run when files do not exist yet or when input has changed
    # for year in [2020, 2021, 2023]:
    #     G_new, n, K, K_i, betas, alpha, C, b, c, B, w = load_instance.MIP_input(year, MAX_DIST_NODES, random_wind = False)
    #     load_instance.write_outputs(G_new, n, K, K_i, betas, alpha, C, b, c, Bmax, w, 'wind_year'+str(year)+'_'+str(n)+'nodes.txt')

    # G_new, n, K, K_i, betas, alpha, C, b, c, B, w = load_instance.MIP_input(year, MAX_DIST_NODES, random_wind = True)
    # load_instance.write_outputs(G_new, n, K, K_i, betas, alpha, C, b, c, Bmax, w, 'transition_prob_uniform_'+ str(n)+'nodes.txt')

    filenames = ['wind_year2020_308nodes.txt', 'wind_year2021_308nodes.txt', '308nodes.txt', 'wind_year2023_308nodes.txt', 'transition_prob_uniform_308nodes.txt']
    filenames = ['wind_year2020_522nodes.txt', 'wind_year2021_522nodes.txt', '522nodes.txt', 'wind_year2023_522nodes.txt', 'transition_prob_uniform_522nodes.txt']
    labels = ['2020', '2021', '2022', '2023', 'turbulent']
    fixed_index = 2

    fig = compare_runs(filenames, labels, fixed_index)
    # plt.suptitle("Sensitivity analysis of transition probabilities due to wind")
    fig.savefig('plots/wind_transition_prob.png', bbox_inches='tight', pad_inches=0.05)

change_transition_prob()

#%%

def change_stuck_prob(vary_factor, G, n, K, K_i, betas, alpha, C, b, c, B, w):
    Bmax = 2

    if vary_factor == 1:
        # old_attrs = nx.get_node_attributes(G, 'dead_ends_prob')
        # G_new = copy.deepcopy(G)
        # for perc in [-0.2, -0.1, 0.1, 0.2]:
        #     for node in G_new.nodes():
        #         new_dead_ends_prob =  old_attrs[node]*(1+perc)
        #         nx.set_node_attributes(G_new, {node: {'dead_ends_prob': new_dead_ends_prob}})
        #         probs = np.array([G_new.nodes[node]['dead_ends_prob'], G_new.nodes[node]['sharp_corners_prob'], G_new.nodes[node]['shore_boats_prob'], G_new.nodes[node]['shore_veg_prob'], G_new.nodes[node]['water_veg_prob']])
        #         nx.set_node_attributes(G_new, {node: {'stuck_probability': (1-np.prod(1-probs))}})

        #     stuck = [G_new.nodes[node]['stuck_probability'] for node in G_new.nodes()]
        #     stuck_matrix = np.repeat([stuck], len(stuck), axis = 0).T

        #     A = nx.adjacency_matrix(G_new, nodelist = G_new.nodes(), weight = 'transition_probability').toarray()
        #     C_new = (1-stuck_matrix) * A
        #     load_instance.write_outputs(G_new, n, K, K_i, betas, alpha, C_new, b, c, Bmax, w, 'dead_ends_'+str(int(perc*100))+'percent_'+str(n)+'nodes.txt')
        filenames = ['308nodes.txt', 'dead_ends_-20percent_308nodes.txt', 'dead_ends_-10percent_308nodes.txt', 'dead_ends_10percent_308nodes.txt', 'dead_ends_20percent_308nodes.txt']
        filenames = ['522nodes.txt', 'dead_ends_-20percent_522nodes.txt', 'dead_ends_-10percent_522nodes.txt', 'dead_ends_10percent_522nodes.txt', 'dead_ends_20percent_522nodes.txt']
        labels = ['estimated', 'estimated-20percent', 'estimated-10percent', 'estimated+10percent', 'estimated+20percent']
        labels = ['base', r'$q_{i0}^d \cdot 0.8$', r'$q_{i0}^d \cdot 0.9$', r'$q_{i0}^d \cdot 1.1$', r'$q_{i0}^d \cdot 1.2$']
        fixed_index = 0

        fig = compare_runs(filenames, labels, fixed_index)
        # plt.suptitle("Sensitivity analysis of dead ends in stuck probability")
        fig.savefig('plots/dead_ends_prob.png', bbox_inches='tight', pad_inches=0.05)

    elif vary_factor == 2:
        # old_attrs = nx.get_node_attributes(G, 'sharp_corners_prob')
        # G_new = copy.deepcopy(G)
        # for perc in [-0.2, -0.1, 0.1, 0.2]:
        #     for node in G_new.nodes():
        #         new_sharp_corners_prob =  old_attrs[node]*(1+perc)
        #         nx.set_node_attributes(G_new, {node: {'sharp_corners_prob': new_sharp_corners_prob}})
        #         probs = np.array([G_new.nodes[node]['dead_ends_prob'], G_new.nodes[node]['sharp_corners_prob'], G_new.nodes[node]['shore_boats_prob'], G_new.nodes[node]['shore_veg_prob'], G_new.nodes[node]['water_veg_prob']])
        #         nx.set_node_attributes(G_new, {node: {'stuck_probability': (1-np.prod(1-probs))}})

        #     stuck = [G_new.nodes[node]['stuck_probability'] for node in G_new.nodes()]
        #     stuck_matrix = np.repeat([stuck], len(stuck), axis = 0).T

        #     A = nx.adjacency_matrix(G_new, nodelist = G_new.nodes(), weight = 'transition_probability').toarray()
        #     C_new = (1-stuck_matrix) * A
        #     load_instance.write_outputs(G_new, n, K, K_i, betas, alpha, C_new, b, c, Bmax, w, 'sharp_corners_'+str(int(perc*100))+'percent_'+str(n)+'nodes.txt')

        filenames = ['308nodes.txt', 'sharp_corners_-20percent_308nodes.txt', 'sharp_corners_-10percent_308nodes.txt', 'sharp_corners_10percent_308nodes.txt', 'sharp_corners_20percent_308nodes.txt']
        filenames = [str(n)+'nodes.txt', 'sharp_corners_-20percent_'+str(n)+'nodes.txt', 'sharp_corners_-10percent_'+str(n)+'nodes.txt', 'sharp_corners_10percent_'+str(n)+'nodes.txt', 'sharp_corners_20percent_'+str(n)+'nodes.txt']
        # labels = ['base', 'base-20percent', 'base-10percent', 'base+10percent', 'base+20percent']
        labels = ['base', r'$q_{i0}^c \cdot 0.8$', r'$q_{i0}^c \cdot 0.9$', r'$q_{i0}^c \cdot 1.1$', r'$q_{i0}^c \cdot 1.2$']
        fixed_index = 0

        fig = compare_runs(filenames, labels, fixed_index)
        # plt.suptitle("Sensitivity analysis of sharp corners in stuck probability")
        fig.savefig('plots/sharp_corners_prob.png', bbox_inches='tight', pad_inches=0.05)


    elif vary_factor == 3:
        # old_attrs = nx.get_node_attributes(G, 'shore_boats_prob')
        # G_new = copy.deepcopy(G)
        # for perc in [0.1, 0.2, 0.4, 0.5]:
        #     for node in G_new.nodes():
        #         new_shore_boats_prob =  perc if old_attrs[node] > 0 else 0
        #         nx.set_node_attributes(G_new, {node: {'shore_boats_prob': new_shore_boats_prob}})
        #         probs = np.array([G_new.nodes[node]['dead_ends_prob'], G_new.nodes[node]['sharp_corners_prob'], G_new.nodes[node]['shore_boats_prob'], G_new.nodes[node]['shore_veg_prob'], G.nodes[node]['water_veg_prob']])
        #         nx.set_node_attributes(G_new, {node: {'stuck_probability': (1-np.prod(1-probs))}})

        #     stuck = [G_new.nodes[node]['stuck_probability'] for node in G_new.nodes()]
        #     stuck_matrix = np.repeat([stuck], len(stuck), axis = 0).T

        #     A = nx.adjacency_matrix(G_new, nodelist = G_new.nodes(), weight = 'transition_probability').toarray()
        #     C_new = (1-stuck_matrix) * A
        #     load_instance.write_outputs(G_new, n, K, K_i, betas, alpha, C_new, b, c, Bmax, w, 'shore_boats_'+str(int(perc*100))+'percent_'+str(n)+'nodes.txt')

        filenames = [''+str(n)+'nodes.txt', 'shore_boats_10percent_'+str(n)+'nodes.txt', 'shore_boats_20percent_'+str(n)+'nodes.txt', 'shore_boats_40percent_'+str(n)+'nodes.txt', 'shore_boats_50percent_'+str(n)+'nodes.txt']
        labels = ['base', r'$q_{i0}^b=0.1$', r'$q_{i0}^b=0.2$', r'$q_{i0}^b=0.4$', r'$q_{i0}^b=0.5$']
        # labels = ['base', 'base-0.2', 'base-0.1', 'base+0.1', 'base+0.2']
        fixed_index = 0

        fig = compare_runs(filenames, labels, fixed_index)
        # plt.suptitle("Sensitivity analysis of docked boats in stuck probability")
        fig.savefig('plots/shore_boats_prob.png', bbox_inches='tight', pad_inches=0.05)


    elif vary_factor == 4:
        # old_attrs = nx.get_node_attributes(G, 'shore_veg_prob')
        # G_new = copy.deepcopy(G)
        # for perc in [0.1, 0.2, 0.4, 0.5]:
        #     for node in G_new.nodes():
        #         new_shore_veg_prob = perc if old_attrs[node] > 0 else 0
        #         nx.set_node_attributes(G_new, {node: {'shore_veg_prob': new_shore_veg_prob}})
        #         probs = np.array([G_new.nodes[node]['dead_ends_prob'], G_new.nodes[node]['sharp_corners_prob'], G_new.nodes[node]['shore_boats_prob'], G_new.nodes[node]['shore_veg_prob'], G_new.nodes[node]['water_veg_prob']])
        #         nx.set_node_attributes(G_new, {node: {'stuck_probability': (1-np.prod(1-probs))}})

        #     stuck = [G_new.nodes[node]['stuck_probability'] for node in G_new.nodes()]
        #     stuck_matrix = np.repeat([stuck], len(stuck), axis = 0).T

        #     A = nx.adjacency_matrix(G_new, nodelist = G_new.nodes(), weight = 'transition_probability').toarray()
        #     C_new = (1-stuck_matrix) * A
        #     load_instance.write_outputs(G_new, n, K, K_i, betas, alpha, C_new, b, c, Bmax, w, 'shore_veg_'+str(int(perc*100))+'percent_'+str(n)+'nodes.txt')

        filenames = [''+str(n)+'nodes.txt', 'shore_veg_10percent_'+str(n)+'nodes.txt', 'shore_veg_20percent_'+str(n)+'nodes.txt', 'shore_veg_40percent_'+str(n)+'nodes.txt', 'shore_veg_50percent_'+str(n)+'nodes.txt']
        labels = ['base', 'shore_veg_prob = 0.1', 'shore_veg_prob = 0.2', 'shore_veg_prob = 0.4', 'shore_veg_prob = 0.5']
        labels = ['base', r'$q_{i0}^s=0.1$', r'$q_{i0}^s=0.2$', r'$q_{i0}^s=0.4$', r'$q_{i0}^s=0.5$']
        
        fixed_index = 0

        fig = compare_runs(filenames, labels, fixed_index)
        # plt.suptitle("Sensitivity analysis of shore vegetation in stuck probability")
        fig.savefig('plots/shore_veg_prob.png', bbox_inches='tight', pad_inches=0.05)

    elif vary_factor == 5:
        # old_attrs = nx.get_node_attributes(G, 'water_veg_prob')
        # G_new = copy.deepcopy(G)
        # for perc in [0, 0.05, 0.3, 0.6, 0.9]:
        #     for node in G_new.nodes():
        #         new_water_veg_prob =  perc if old_attrs[node] > 0 else 0
        #         nx.set_node_attributes(G_new, {node: {'water_veg_prob': new_water_veg_prob}})
        #         probs = np.array([G_new.nodes[node]['dead_ends_prob'], G_new.nodes[node]['sharp_corners_prob'], G_new.nodes[node]['shore_boats_prob'], G_new.nodes[node]['shore_veg_prob'], G_new.nodes[node]['water_veg_prob']])
        #         nx.set_node_attributes(G_new, {node: {'stuck_probability': (1-np.prod(1-probs))}})

        #     stuck = [G_new.nodes[node]['stuck_probability'] for node in G_new.nodes()]
        #     stuck_matrix = np.repeat([stuck], len(stuck), axis = 0).T

        #     # if perc == 0:
        #     #     Bmax = 1.2
        #     # # elif perc == 0.05:
        #     #     # Bmax = 1.8
        #     # else:
        #     #     Bmax = 1.8

        #     A = nx.adjacency_matrix(G_new, nodelist = G_new.nodes(), weight = 'transition_probability').toarray()
        #     C_new = (1-stuck_matrix) * A
        #     load_instance.write_outputs(G_new, n, K, K_i, betas, alpha, C_new, b, c, Bmax, w, 'water_veg_'+str(int(perc*100))+'percent_'+str(n)+'nodes.txt')

        filenames = [''+str(n)+'nodes.txt', 'water_veg_0percent_'+str(n)+'nodes.txt', 'water_veg_5percent_'+str(n)+'nodes.txt', 'water_veg_30percent_'+str(n)+'nodes.txt', 'water_veg_60percent_'+str(n)+'nodes.txt', 'water_veg_90percent_'+str(n)+'nodes.txt']
        labels = ['base', 'water_veg_prob = 0', 'water_veg_prob = 0.05', 'water_veg_prob = 0.3', 'water_veg_prob = 0.6', 'water_veg_prob = 0.9']
        labels = ['base', r'$q_{i0}^w=0$', r'$q_{i0}^w=0.05$', r'$q_{i0}^w=0.3$', r'$q_{i0}^w=0.6$', r'$q_{i0}^w=0.9$']
        fixed_index = 0

        # filenames = ['308nodes.txt', 'water_veg_30percent_308nodes.txt', 'water_veg_60percent_308nodes.txt', 'water_veg_90percent_308nodes.txt']
        # labels = ['estimated', 'water_veg_prob = 0.3', 'water_veg_prob = 0.6', 'water_veg_prob = 0.9']
        # fixed_index = 0

        fig = compare_runs(filenames, labels, fixed_index)
        # plt.suptitle("Sensitivity analysis of water vegetation in stuck probability")
        fig.savefig('plots/water_veg_prob.png', bbox_inches='tight', pad_inches=0.05)
# year = 2022
# MAX_DIST_NODES = 60
# G, n, K, K_i, betas, alpha, C, b, c, B, w = load_instance.MIP_input(year, MAX_DIST_NODES, random_wind = False)
change_stuck_prob(1, G, n, K, K_i, betas, alpha, C, b, c, B, w)
change_stuck_prob(2, G, n, K, K_i, betas, alpha, C, b, c, B, w)
change_stuck_prob(3, G, n, K, K_i, betas, alpha, C, b, c, B, w)
change_stuck_prob(4, G, n, K, K_i, betas, alpha, C, b, c, B, w)
change_stuck_prob(5, G, n, K, K_i, betas, alpha, C, b, c, B, w)

#%%
def change_catching_prob(G, n, K, K_i, betas, alpha, C, b, c, B, w):
    # Bmax = 2
    # old_attrs = nx.get_node_attributes(G, 'catching_probability')
    # G_new = copy.deepcopy(G)
    # for perc in [-0.2, -0.1, 0.1, 0.2]:
    #     for node in G_new.nodes():
    #         new_catching_prob =  old_attrs[node]*(1+perc)
    #         nx.set_node_attributes(G_new, {node: {'catching_probability': new_catching_prob}})

    #     catching = np.array([G_new.nodes[node]['catching_probability'] for node in G_new.nodes()])
    #     new_betas = np.stack((0.98*catching, 0.85*catching)).T

    #     load_instance.write_outputs(G_new, n, K, K_i, new_betas, alpha, C, b, c, Bmax, w, 'catching_'+str(int(perc*100))+'percent_'+str(n)+'nodes.txt')

    filenames = [''+str(n)+'nodes.txt', 'catching_-20percent_'+str(n)+'nodes.txt', 'catching_-10percent_'+str(n)+'nodes.txt', 'catching_10percent_'+str(n)+'nodes.txt', 'catching_20percent_'+str(n)+'nodes.txt']
    labels = ['estimated', 'estimated-20percent', 'estimated-10percent', 'estimated+10percent', 'estimated+20percent']
    labels = ['base', 'base-20percent', 'base-10percent', 'base+10percent', 'base+20percent']
    fixed_index = 0

    fig = compare_runs(filenames, labels, fixed_index)
    plt.suptitle("Sensitivity analysis of catching probability")
    # fig.savefig('plots/catching_prob.png', bbox_inches='tight', pad_inches=0.05)

# G, n, K, K_i, betas, alpha, C, b, c, B, w = load_instance.MIP_input(year, MAX_DIST_NODES, random_wind = False)
# change_catching_prob(G, n, K, K_i, betas, alpha, C, b, c, B, w)

#%%

def change_impact_factor(G, n, K, K_i, betas, alpha, C, b, c, B, w):
    Bmax = 2
    G_new = copy.deepcopy(G)
    ## 1. impact factor the same value everywhere, higher lower etc
    ## impact factor = 0
    # alpha_new = n * [1e-10]
    # for index, node in enumerate(G_new.nodes()):
    #     nx.set_node_attributes(G_new, {node: {'impact_factor': alpha_new[index]}})
    # load_instance.write_outputs(G_new, n, K, K_i, betas, alpha_new, C, b, c, Bmax, w, 'impact_factor_0_'+str(n)+'nodes.txt', show_impact_flow = True)

    # ### examine M1 and M2 for values of alpha
    
    # M1 = b.T @ np.linalg.inv(np.eye(n)-C)
    M2 = np.zeros((n,K))
    for i in range(n):
        for k in range(K):
            diagB = np.eye(n)
            diagB[i,i] = 1 - betas[i,k]
            M2[i,k] = (b.T @ np.linalg.inv(np.eye(n)- diagB @ C))[i]

    # alpha_new = n * [np.min((betas*M2)[(betas*M2) > 0])]
    # for index, node in enumerate(G_new.nodes()):
    #     nx.set_node_attributes(G_new, {node: {'impact_factor': alpha_new[index]}})
    # load_instance.write_outputs(G_new, n, K, K_i, betas, alpha_new, C, b, c, Bmax, w, 'impact_factor_minbetaM2_'+str(n)+'nodes.txt', show_impact_flow = True)

    
    # alpha_new = n * [np.mean((betas*M2)[(betas*M2) > 0])]
    # for index, node in enumerate(G_new.nodes()):
    #     nx.set_node_attributes(G_new, {node: {'impact_factor': alpha_new[index]}})
    # load_instance.write_outputs(G_new, n, K, K_i, betas, alpha_new, C, b, c, Bmax, w, 'impact_factor_meanbetaM2_'+str(n)+'nodes.txt', show_impact_flow = True)

    # alpha_new = n * [0.25*np.max((betas*M2)[(betas*M2) > 0])]
    # for index, node in enumerate(G_new.nodes()):
    #     nx.set_node_attributes(G_new, {node: {'impact_factor': alpha_new[index]}})
    # load_instance.write_outputs(G_new, n, K, K_i, betas, alpha_new, C, b, c, Bmax, w, 'impact_factor_25maxbetaM2_'+str(n)+'nodes.txt', show_impact_flow = True)

    # alpha_new = n * [0.5*np.max((betas*M2)[(betas*M2) > 0])]
    # for index, node in enumerate(G_new.nodes()):
    #     nx.set_node_attributes(G_new, {node: {'impact_factor': alpha_new[index]}})
    # load_instance.write_outputs(G_new, n, K, K_i, betas, alpha_new, C, b, c, Bmax, w, 'impact_factor_halfmaxbetaM2_'+str(n)+'nodes.txt', show_impact_flow = True)

    # alpha_new = n * [np.max((betas*M2)[(betas*M2) > 0])]
    # for index, node in enumerate(G_new.nodes()):
    #     nx.set_node_attributes(G_new, {node: {'impact_factor': alpha_new[index]}})
    # load_instance.write_outputs(G_new, n, K, K_i, betas, alpha_new, C, b, c, Bmax, w, 'impact_factor_maxbetaM2_'+str(n)+'nodes.txt', show_impact_flow = True)

    filenames = ['impact_factor_0_'+str(n)+'nodes.txt', 'impact_factor_minbetaM2_'+str(n)+'nodes.txt', 'impact_factor_meanbetaM2_'+str(n)+'nodes.txt', 'impact_factor_25maxbetaM2_'+str(n)+'nodes.txt', 'impact_factor_halfmaxbetaM2_'+str(n)+'nodes.txt', 'impact_factor_maxbetaM2_'+str(n)+'nodes.txt']

    alphas = [0, np.min((betas*M2)[(betas*M2) > 0]), np.mean((betas*M2)[(betas*M2) > 0]), 0.25*np.max((betas*M2)[(betas*M2) > 0]), 0.5*np.max((betas*M2)[(betas*M2) > 0]), np.max((betas*M2)[(betas*M2) > 0])]
    labels = ['alpha = 0', 'alpha = min(beta*M2)='+str(round(alphas[1],5)), 'alpha = mean(beta*M2)='+str(round(alphas[2],5)), 'alpha = 0.25*max(beta*M2)='+str(round(alphas[3],5)), 'alpha = 0.5*max(beta*M2)='+str(round(alphas[3],5)), 'alpha = max(beta*M2)='+str(round(alphas[4],5))]
    fixed_index = 0
    fixed_index = 5

    # fig = compare_runs(filenames, labels, fixed_index, True, alphas)
    fig = compare_runs_impact_factor(filenames, labels, alphas, np.arange(9))
    # plt.suptitle("Sensitivity analysis of impact factor for catching early")
    # fig.savefig('plots/catching_early'+str(n)+'nodes.png', bbox_inches='tight', pad_inches=0.05)


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
    # load_instance.write_outputs(G, n, K, K_i, betas, n*[0], C, b, c, Bmax, w, 'impact_factor_area0_'+str(n)+'nodes.txt', show_impact_flow = True)
    # load_instance.write_outputs(G, n, K, K_i, betas, alpha_new5, C, b, c, Bmax, w, 'impact_factor_area05_'+str(n)+'nodes.txt', show_impact_flow = True)
    # load_instance.write_outputs(G, n, K, K_i, betas, alpha_new7, C, b, c, Bmax, w, 'impact_factor_area07_'+str(n)+'nodes.txt', show_impact_flow = True)
    # load_instance.write_outputs(G, n, K, K_i, betas, alpha_new9, C, b, c, Bmax, w, 'impact_factor_area09_'+str(n)+'nodes.txt', show_impact_flow = True)
    # for mult in [1, 3]:
        # alpha_new = [G.nodes[node]['impact_factor']*1 for node in G.nodes()]

    # alpha_new1 = np.zeros(n)
    # alpha_new3 = np.zeros(n)
    # for index, node in enumerate(G.nodes()):
    #     alpha_new1[index] += G.nodes[node]['impact_factor']*1
    #     alpha_new3[index] += G.nodes[node]['impact_factor']*3
    # load_instance.write_outputs(G, n, K, K_i, betas, alpha_new1, C, b, c, Bmax, w, 'impact_factor_area01_'+str(n)+'nodes.txt', show_impact_flow = True)
    # load_instance.write_outputs(G, n, K, K_i, betas, alpha_new3, C, b, c, Bmax, w, 'impact_factor_area03_'+str(n)+'nodes.txt', show_impact_flow = True)


    filenames = ['impact_factor_area0_'+str(n)+'nodes.txt', 'impact_factor_area01_'+str(n)+'nodes.txt', 'impact_factor_area03_'+str(n)+'nodes.txt', 'impact_factor_area05_'+str(n)+'nodes.txt', 'impact_factor_area07_'+str(n)+'nodes.txt', 'impact_factor_area09_'+str(n)+'nodes.txt']
    labels = ['alpha = 0', 'alpha = 0.1', 'alpha = 0.3', 'alpha = 0.5', 'alpha = 0.7', 'alpha = 0.9']
    alphas = [0, 0.1, 0.3, 0.5, 0.7, 0.9]
    fixed_index = 0
    fixed_index = 5

    # fig = compare_runs(filenames, labels, fixed_index, True, alphas)
    fig = compare_runs_impact_factor(filenames, labels, alphas, [1, 3, 5, 7, 9])
    # plt.suptitle("Sensitive area in city center")
    # fig.savefig('plots/sensitive_area'+str(n)+'nodes.png', bbox_inches='tight', pad_inches=0.05)

    ### 3. impact factor zero and value for edge, higher lower
    ### impact factor value everywhere and extra for edge, higher and lower
    ## plot amount of flow caught in total vs amount of flow in area


    # tests = [1e-10, 1,2,3]
    # tests = [4, 5, 6]
    # node_label = 122
    # for impact in tests:
    #     G_new = copy.deepcopy(G)
    #     for index, node in enumerate(G_new.nodes()):
    #         nx.set_node_attributes(G_new, {node: {'impact_factor': 0}})
    #         if index == node_label -1:
    #             nx.set_node_attributes(G_new, {node: {'impact_factor': impact}})
    #     alpha_new = [G_new.nodes[node]['impact_factor'] for node in G_new.nodes()]
    #     load_instance.write_outputs(G_new, n, K, K_i, betas, alpha_new, C, b, c, Bmax, w, 'impact_factor_edge'+str(round(impact))+'_'+str(n)+'nodes.txt', show_impact_flow = True)


    filenames = ['impact_factor_edge0_'+str(n)+'nodes.txt', 'impact_factor_edge1_'+str(n)+'nodes.txt', 'impact_factor_edge2_'+str(n)+'nodes.txt', 'impact_factor_edge3_'+str(n)+'nodes.txt', 'impact_factor_edge4_'+str(n)+'nodes.txt', 'impact_factor_edge5_'+str(n)+'nodes.txt', 'impact_factor_edge6_'+str(n)+'nodes.txt']
    labels = ['alpha = 0', 'alpha = 1', 'alpha = 2' , 'alpha = 3', 'alpha = 4', 'alpha = 5', 'alpha = 6']
    alphas = [0, 1, 2, 3, 4, 5, 6]
    fixed_index = 0
    fixed_index = 6


    # fig = compare_runs(filenames, labels, fixed_index, True, alphas)
    fig = compare_runs_impact_factor(filenames, labels, alphas, [1, 3, 5, 7, 9])
    # plt.suptitle("Sensitive area at edge node")
    # fig.savefig('plots/sensitive_edge'+str(n)+'nodes.png', bbox_inches='tight', pad_inches=0.05)
# year = 2022
# MAX_DIST_NODES = 60
# G, n, K, K_i, betas, alpha, C, b, c, B, w = load_instance.MIP_input(year, MAX_DIST_NODES, random_wind = False)
# change_impact_factor(G, n, K, K_i, betas, alpha, C, b, c, B, w)

#%% test accuracy of catching systems
def change_accuracy_types(G, n, K, K_i, betas, alpha, C, b, c, B, w):
    # Bmax = 2
    # catching = np.array([G.nodes[node]['catching_probability'] for node in G.nodes()])
    # # for acc in [0.1, 0.2, 0.3, 0.4, 0.6]:
    # # test = [0.98*0.2-0.1, 0.98*0.2, 0.98*0.2+0.1, 0.98*0.2+0.2]
    # for acc in [0.096, 0.196, 0.296, 0.396]:
    #     new_betas = np.stack((0.98*catching, acc*catching)).T
    #     load_instance.write_outputs(G, n, K, K_i, new_betas, alpha, C, b, c, Bmax, w, 'catching_accuracy_k2_'+str(int(acc*100))+'percent_'+str(n)+'nodes.txt')



    ### plot
    filenames = ['308nodes.txt', 'catching_accuracy_k2_10percent_308nodes.txt', 'catching_accuracy_k2_20percent_308nodes.txt', 'catching_accuracy_k2_30percent_308nodes.txt','catching_accuracy_k2_40percent_308nodes.txt', 'catching_accuracy_k2_60percent_308nodes.txt']
    labels = ['estimated', r"a_2 = 0.1", r"a_2 = 0.2", r"a_2 = 0.3", r"a_2 = 0.4", r"a_2 = 0.6"]
    fixed_index = 0

    filenames = ['catching_accuracy_k2_10percent_308nodes.txt', 'catching_accuracy_k2_20percent_308nodes.txt', 'catching_accuracy_k2_30percent_308nodes.txt','catching_accuracy_k2_40percent_308nodes.txt']
    labels = ["$a_2 = 0.1$", "$a_2 = 0.2$", "$a_2 = 0.3$", "$a_2 = 0.4$"]
    labels = ['0.1', '0.2', '0.3', '0.4']

    filenames = ['catching_accuracy_k2_9percent_'+str(n)+'nodes.txt', 'catching_accuracy_k2_19percent_'+str(n)+'nodes.txt', 'catching_accuracy_k2_29percent_'+str(n)+'nodes.txt','catching_accuracy_k2_39percent_'+str(n)+'nodes.txt']
    labels = ["$a_2 = 0.1$", "$a_2 = 0.2$", "$a_2 = 0.3$", "$a_2 = 0.4$"]
    labels = ['0.1', '0.2', '0.3', '0.4']
    # labels = ['BE-0.1', 'BE', 'BE+0.1', 'BE+0.2']
    fixed_index = 0

    runs = []
    for filename in filenames:
        with open(filename) as f:
            run = f.readlines()
        run = [eval(line.strip()) for line in run]
        runs += [run]

    data = [[[sum(1 for i in budget[-1] if i[1] == 1), sum(1 for i in budget[-1] if i[1]==2)]  for budget in run[1:]] for run in runs]

    num_clusters = len(data[0]) #number of clusters
    num_bars = len(data) #bars per cluster

    cluster_positions = np.arange(num_clusters)
    bar_width = 0.2

    colors = ['blue', 'orange']
    stack_labels = ['Type 1', 'Type 2']
    
    # Plotting
    fig, ax = plt.subplots(figsize=(16, 8))
    
    for i in range(num_bars):
        # Positions of the bars in the current cluster
        bar_positions = cluster_positions - (num_bars / 2 - i) * bar_width
    
        # Bottom position for the second stack
        bottoms = np.zeros(num_clusters)
    
        for j in range(2):  # Because there are two stacks
            heights = [data[i][cluster][j] for cluster in range(num_clusters)]
            ax.bar(bar_positions, heights, color=colors[j], width=bar_width, edgecolor='white',
                    label=stack_labels[j] if i == 0 else "", bottom=bottoms)
            bottoms += heights  # Update the bottoms for the next stack

    # Customizing the plot
    ax.set_xlabel('$a_2$', rotation = 0, fontdict={'fontsize': 15})
    ax.set_ylabel('Number of catching systems', fontdict={'fontsize': 16})

    # Correct x-tick labels for each bar within each cluster
    all_bar_positions = np.array([cluster_positions - (num_bars / 2 - i) * bar_width for i in range(num_bars)]).flatten()
    all_bar_positions.sort()
    # Replicate each group label `num_clusters` times in the proper sequence
    group_labels = np.tile(labels, num_clusters)
    group_labels = np.tile([0.096, 0.196, 0.296, 0.396], num_clusters)
    
    ax.set_xticks(all_bar_positions)  # Set as minor ticks
    ax.set_xticklabels(group_labels, rotation=90, fontdict={'fontsize': 14})
    
    # Secondary x-axis for cluster labels below the plot
    ax2 = ax.secondary_xaxis('bottom')
    ax2.set_xticks(cluster_positions)
    ax2.set_xticklabels([f'{round((i+1)*0.2,1)}' for i in range(num_clusters)], fontdict={'fontsize': 14})
    ax2.xaxis.set_ticks_position('bottom')
    ax2.xaxis.set_label_position('bottom')
    ax2.spines['bottom'].set_visible(False)
    ax2.spines['bottom'].set_position(('outward', 60))  # Move the secondary x-axis downward
    ax2.set_xlabel('Budget', fontdict={'fontsize': 16})
    # Remove ticks on the secondary x-axis
    ax2.tick_params(axis='x', which='both', length=0)  # Removes the tick marks


    ## second axis above plot
    # ax.set_xticks(all_bar_positions)
    # ax.set_xticklabels(group_labels, rotation=45, ha="center")

    # # Ensure that the x-ticks do not overlap
    # plt.xticks(rotation=90)

    # ax2 = ax.twiny()  # Create a second x-axis
    # ax2.set_xticks(cluster_positions)
    # ax2.set_xticklabels([f'{round((i+1)*0.2,1)}' for i in range(num_clusters)])
    # ax2.set_xlim(ax.get_xlim())  # Ensure the secondary x-axis aligns with the primary
    # ax2.set_xlabel('Budget')

    handles, labels = ax.get_legend_handles_labels()
    by_label = dict(zip(labels, handles))  # Remove duplicate labels
    plt.legend(by_label.values(), by_label.keys())
    
    # Show the plot
    plt.tight_layout()
    plt.show()
    # plt.suptitle("Sensitivity analysis of catching probability")
    fig.savefig("plots/catching_accuracy.png")

# G, n, K, K_i, betas, alpha, C, b, c, B, w = load_instance.MIP_input(year, MAX_DIST_NODES, random_wind = False)
change_accuracy_types(G, n, K, K_i, betas, alpha, C, b, c, B, w)

# G, n, K, K_i, betas, alpha, C, b, c, B, w = load_instance.MIP_input(year, MAX_DIST_NODES, random_wind = False)
# change_transition_prob()

# G, n, K, K_i, betas, alpha, C, b, c, B, w = load_instance.MIP_input(year, MAX_DIST_NODES, random_wind = False)
# change_stuck_prob(5, G, n, K, K_i, betas, alpha, C, b, c, B, w)

# G, n, K, K_i, betas, alpha, C, b, c, B, w = load_instance.MIP_input(year, MAX_DIST_NODES, random_wind = False)
# change_init_prob(G, n, K, K_i, betas, alpha, C, b, c, B, w)

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

### for chapter 5 choose impact factor!
# n = 308

year = 2022
MAX_DIST_NODES = 100
G, n, K, K_i, betas, alpha, C, b, c, B, w = load_instance.MIP_input(year, MAX_DIST_NODES, random_wind = False)

M2 = np.zeros((n,K))
for i in range(n):
    for k in range(K):
        diagB = np.eye(n)
        diagB[i,i] = 1 - betas[i,k]
        M2[i,k] = (b.T @ np.linalg.inv(np.eye(n)- diagB @ C))[i]


filenames = ['impact_factor_0_'+str(n)+'nodes.txt', str(n)+'nodes.txt', 'impact_factor_meanbetaM2_'+str(n)+'nodes.txt', 'impact_factor_halfmaxbetaM2_'+str(n)+'nodes.txt', 'impact_factor_maxbetaM2_'+str(n)+'nodes.txt']
filenames = ['runs_n308_oldalpha/'+filename for filename in filenames]
alphas = [0, np.min((betas*M2)[(betas*M2) > 0]), np.mean((betas*M2)[(betas*M2) > 0]), 0.5*np.max((betas*M2)[(betas*M2) > 0]), np.max((betas*M2)[(betas*M2) > 0])]
labels = ['alpha = 0', 'alpha = min(beta*M2)='+str(round(alphas[1],5)), 'alpha = mean(beta*M2)='+str(round(alphas[2],5)), 'alpha = 0.5*max(beta*M2)='+str(round(alphas[3],5)), 'alpha = max(beta*M2)='+str(round(alphas[4],5))]
budget_indices = [4, 9, 14, 19]
fig = compare_runs_impact_factor(filenames, labels, alphas, budget_indices, True)
fig.savefig('plots/sensitive_catching_early'+str(n)+'nodes.png', bbox_inches='tight', pad_inches=0.05)

filenames = ['impact_factor_area0_'+str(n)+'nodes.txt','impact_factor_area05_'+str(n)+'nodes.txt', 'impact_factor_area07_'+str(n)+'nodes.txt', 'impact_factor_area09_'+str(n)+'nodes.txt']
filenames = ['runs_n308_oldalpha/'+filename for filename in filenames]
labels = ['alpha = 0', 'alpha = 0.5', 'alpha = 0.7', 'alpha = 0.9']
alphas = [0, 0.5, 0.7, 0.9]


# fig = compare_runs(filenames, labels, fixed_index, True, alphas)
fig = compare_runs_impact_factor(filenames, labels, alphas, budget_indices, True)
# # plt.suptitle("Sensitive area in city center")
fig.savefig('plots/sensitive_city_center'+str(n)+'nodes.png', bbox_inches='tight', pad_inches=0.05)


filenames = ['impact_factor_edge0_'+str(n)+'nodes.txt', 'impact_factor_edge1_'+str(n)+'nodes.txt', 'impact_factor_edge2_'+str(n)+'nodes.txt', 'impact_factor_edge3_'+str(n)+'nodes.txt']
filenames = ['runs_n308_oldalpha/'+filename for filename in filenames]
labels = ['alpha = 0', 'alpha = 1', 'alpha = 2' , 'alpha = 3']
alphas = [0, 1, 2, 3]


# fig = compare_runs(filenames, labels, fixed_index, True, alphas)
fig = compare_runs_impact_factor(filenames, labels, alphas, budget_indices, True)
# # plt.suptitle("Sensitive area at edge node")
fig.savefig('plots/sensitive_edge_node'+str(n)+'nodes.png', bbox_inches='tight', pad_inches=0.05)


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