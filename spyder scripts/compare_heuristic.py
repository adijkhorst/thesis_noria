# -*- coding: utf-8 -*-
"""
Created on Tue Apr 23 14:41:47 2024

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

plt.rc('font', size=12)
def compare_heuristic(filenames, labels):
    runs_heur = []
    for filename in filenames:
        # with open('runs_n308_oldalpha/heuristic_'+filename) as f:
        with open('heuristic_results_plots/heuristic_v2_'+filename) as f:
            run = f.readlines()
        run = [eval(line.strip()) for line in run]
        runs_heur += [run]

    runs_exact = []
    for filename in filenames:
        with open('heuristic_results_plots/'+filename) as f:
            run = f.readlines()
        run = [eval(line.strip()) for line in run]
        runs_exact += [run]

    n_rows = len(runs_heur) #rows are the number of different scenarios
    n_cols = len(runs_heur[1])-1 #columns are the different budget, we use the number of budgets of the second file in the input filenames
    mean_distances = np.zeros((n_rows, n_cols))
    max_distances = np.zeros((n_rows, n_cols))
    flow_heur = np.zeros((n_rows, n_cols)) # difference between caught flow with fixed solution and expected flow (from base scenario) with fixed solution
    flow_exact = np.zeros((n_rows, n_cols)) # difference between caught flow with fixed solution and caught flow with optimal solution in new scenario (compared to having perfect knowledge)

    runtime_heur = np.zeros((n_rows, n_cols))
    runtime_exact = np.zeros((n_rows, n_cols))

    for i in range(n_rows):
            for j in range(n_cols):
                # , budget in enumerate(run[1:]):
                if j < n_cols:
                    locations_heur = [list(system[-1]) for system in runs_heur[i][j+1][-1]]
                    locations_exact = [list(system[-1]) for system in runs_exact[i][j+1][-1]]
        
                    pairwise_distances = distance.cdist(locations_heur, locations_exact)
                    row_ind, col_ind = linear_sum_assignment(pairwise_distances)
        
                    # choose one of three to report
                    total_distance = pairwise_distances[row_ind, col_ind].sum()
                    mean_distance = (pairwise_distances[row_ind, col_ind].sum())/len(locations_heur)
                    max_distance = np.max(pairwise_distances[row_ind, col_ind])
        
                    mean_distances[i, j] = mean_distance
                    max_distances[i, j] = max_distance

                    flow_heur[i,j] = runs_heur[i][j+1][2] #2 is objective value, 3 is flow caught
                    flow_exact[i,j] = runs_exact[i][j+1][2] #2 is objective value, 3 is flow caught

                    runtime_heur[i,j] = runs_heur[i][j+1][1]
                    runtime_exact[i,j] = runs_exact[i][j+1][1]

    budgets = [row[0] for row in runs_heur[1][1:]]

    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize = (18, 5))
    # ax.title("Sensitivity analysis of wind directions compared to 2022")
    
    ax1.grid()
    ax1.set_title('Maximum and mean distance between heuristic \n and exact solution')
    ax1.set_xlabel('budget')
    ax1.set_ylabel('distance between solutions')
    ax1.set_ylim(bottom = -50, top = 1800)

    # ax1a = ax1.twinx()

    ax2.set_title("Objective value heuristic solution/ \n objective value exact solution")
    ax2.set_xlabel('budget')
    ax2.set_ylabel('objective value heuristic/objective value exact')
    ax2.set_ylim(bottom = 0.988, top = 1.0002)

    ax2.grid()
    # ax2.plot(budgets, [runs[fixed_index][j+1][3] for j in range(len(runs[1])-1)], '--', label = 'flow caught base situation')
    for i in range(n_rows):
        ax1.plot(budgets, max_distances[i], label = labels[i])

        ax2.plot(budgets, flow_heur[i]/flow_exact[i], label = labels[i])
        ax3.plot(budgets, runtime_exact[i], label = 'exact '+labels[i])
    ax1.set_prop_cycle(None)
    ax3.set_prop_cycle(None)

    ax3.grid()
    ax3.set_xlabel('budget')
    ax3.set_ylabel('runtime (s)')
    ax3.set_title('Runtime of exact solver (solid line) \n and heuristic (dashed line)')
    ax3.set_ylim(bottom = 0, top = 800)

    # ax2.ticklabel_format(style='plain')
    # ax3.ticklabel_format(style='plain')


    for i in range(n_rows):
        ax1.plot(budgets, mean_distances[i], 'x')#, label = plot_labels[i] + ' mean distance solutions')
        ax3.plot(budgets, runtime_heur[i], '--')
    # ax1.legend()
    ax2.legend()
    # ax3.legend()

    return fig


if __name__ == "__main__":
    year = 2022
    # node_dists = [75, 70, 60, 50, 40, 30]
    Bmax = 4.0
    node_dists = [150, 125, 100]
    # # node_dists = [30]
    # node_dists = [100, 75, 50]
    # for dist in node_dists:
    #     G, n, K, K_i, betas, alpha, C, b, c, B, w =load_instance.MIP_input(year, dist, random_wind = False, version_alpha='')
    #     for index, node in enumerate(G.nodes()):
    #         nx.set_node_attributes(G, {node: {'impact_factor': alpha[index]}})
    #     load_instance.write_outputs_heuristic(G, n, K, K_i, betas, alpha, C, b, c, Bmax, w, str(n)+'nodes.txt')

    # filenames = ['784nodes_B2.txt', '622nodes_B2.txt', '522nodes_B2.txt', '444nodes_B2.txt', '308nodes.txt', '244nodes.txt', '198nodes.txt']
    # labels = ['d=40', 'd=50', 'd=60', 'd=70', 'd=100', 'd=125', 'd=150']

    # compare_heuristic(filenames, labels)

    ### WERKT NIET
    # filenames = ['runs_different_n/compared_n308d100/'+ file for file in['784nodes_B2.txt', '622nodes_B2.txt', '522nodes_B2.txt', '444nodes_B2.txt']]
    # labels = ['d=40', 'd=50', 'd=60', 'd=70']

    # fig = compare_heuristic(filenames, labels)
    # fig.savefig('plots/heuristic_manynodes,png')

    # filenames = ['308nodes.txt', '244nodes.txt', '198nodes.txt']
    # labels = ['d=100', 'd=125', 'd=150']

    # fig = compare_heuristic(filenames, labels)
    # fig.savefig('plots/heuristic_fewnodes.png', bbox_inches='tight', pad_inches=0.05)

#%% base scenario
    year = 2022
    MAX_DIST_NODES = 100
    G, n, K, K_i, betas, alpha, C, b, c, B, w = load_instance.MIP_input(year, MAX_DIST_NODES, random_wind = False, version_alpha = '')

#%% init prob
    Bmax = 4.0

    # np.random.seed(0)
    # b_new = b*np.random.choice([0.9, 1.1], n)
    # b_new = b_new/np.sum(b_new)
    # load_instance.write_outputs_heuristic(G, n, K, K_i, betas, alpha, C, b_new, c, Bmax, w, 'init_prob_choice10_1_'+str(n)+'nodes.txt')

    
    # b_new = b*np.random.choice([0.8, 1.2], n)
    # b_new = b_new/np.sum(b_new)
    # load_instance.write_outputs_heuristic(G, n, K, K_i, betas, alpha, C, b_new, c, Bmax, w, 'init_prob_choice20_1_+str(n)+'nodes.txt')

    # b_new = b*np.random.choice([0.7, 1.3], n)
    # b_new = b_new/np.sum(b_new)
    # load_instance.write_outputs_heuristic(G, n, K, K_i, betas, alpha, C, b_new, c, Bmax, w, 'init_prob_choice30_1_'+str(n)+'nodes.txt')
    
    # b_new = np.ones(n)/n
    # load_instance.write_outputs_heuristic(G, n, K, K_i, betas, alpha, C, b_new, c, Bmax, w, 'init_prob_uniform_'+str(n)+'nodes.txt')

    filenames = ['init_prob_uniform_308nodes.txt', 'init_prob_choice10_1_308nodes.txt', 'init_prob_choice20_1_308nodes.txt', 'init_prob_choice30_1_308nodes.txt']
    labels = ['init_prob uniform', 'init_prob +- 10 percent choice',  'init_prob +- 20 percent choice', 'init_prob +- 30 percent choice']
    labels = [r'$\mathbf{b}\pm 0.1\mathbf{b}$', r'$\mathbf{b}\pm 0.2\mathbf{b}$',r'$\mathbf{b}\pm 0.3\mathbf{b}$', '1/n']

    fig = compare_heuristic(filenames, labels)
    fig.savefig('plots/heuristic_initprob.png', bbox_inches='tight', pad_inches=0.05)



#%% wind
    Bmax = 4.0
    # for year in [2020, 2021, 2023]:
    #     G, n, K, K_i, betas, alpha, C, b, c, B, w = load_instance.MIP_input(year, MAX_DIST_NODES, random_wind = False, version_alpha='')
    #     load_instance.write_outputs_heuristic(G, n, K, K_i, betas, alpha, C, b, c, Bmax, w, 'wind_year'+str(year)+'_'+str(n)+'nodes.txt')

    # G, n, K, K_i, betas, alpha, C, b, c, B, w = load_instance.MIP_input(year, MAX_DIST_NODES, random_wind = True, version_alpha = '')
    # load_instance.write_outputs_heuristic(G, n, K, K_i, betas, alpha, C, b, c, Bmax, w, 'transition_prob_uniform_'+ str(n)+'nodes.txt')


    filenames = ['wind_year2020_308nodes.txt', 'wind_year2021_308nodes.txt', 'wind_year2023_308nodes.txt', 'transition_prob_uniform_308nodes.txt']
    labels = ['2020', '2021', '2023', 'turbulent']

    fig = compare_heuristic(filenames, labels)
    fig.savefig('plots/heuristic_wind.png', bbox_inches='tight', pad_inches=0.05)
    
#%% water veg
    year = 2022
    MAX_DIST_NODES = 100
    # G, n, K, K_i, betas, alpha, C, b, c, B, w = load_instance.MIP_input(year, MAX_DIST_NODES, random_wind = False, version_alpha = '')

    # Bmax = 2.0
    # old_attrs = nx.get_node_attributes(G, 'water_veg_prob')
    # for perc in [0, 0.3, 0.6, 0.9]:
    #     for node in G.nodes():
    #         new_water_veg_prob =  perc if old_attrs[node] > 0 else 0
    #         nx.set_node_attributes(G, {node: {'water_veg_prob': new_water_veg_prob}})
    #         probs = np.array([G.nodes[node]['dead_ends_prob'], G.nodes[node]['sharp_corners_prob'], G.nodes[node]['shore_boats_prob'], G.nodes[node]['shore_veg_prob'], G.nodes[node]['water_veg_prob']])
    #         nx.set_node_attributes(G, {node: {'stuck_probability': (1-np.prod(1-probs))}})

    #     stuck = [G.nodes[node]['stuck_probability'] for node in G.nodes()]
    #     stuck_matrix = np.repeat([stuck], len(stuck), axis = 0).T

    #     A = nx.adjacency_matrix(G, nodelist = G.nodes(), weight = 'transition_probability').toarray()
    #     C_new = (1-stuck_matrix) * A
    #     load_instance.write_outputs_heuristic(G, n, K, K_i, betas, alpha, C_new, b, c, Bmax, w, 'water_veg_'+str(int(perc*100))+'percent_'+str(n)+'nodes.txt')

    filenames = ['water_veg_0percent_308nodes_B2.txt', 'water_veg_30percent_308nodes_B2.txt', 'water_veg_60percent_308nodes_B2.txt', 'water_veg_90percent_308nodes_B2.txt']
    labels = ['water_veg_prob = 0', 'water_veg_prob = 0.3', 'water_veg_prob = 0.6', 'water_veg_prob = 0.9']
    labels = [r'$q_{i0}^w=0$', r'$q_{i0}^w=0.3$', r'$q_{i0}^w=0.6$', r'$q_{i0}^w=0.9$']

    fig = compare_heuristic(filenames, labels)
    fig.savefig('plots/heuristic_waterveg.png', bbox_inches='tight', pad_inches=0.05)

