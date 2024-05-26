# -*- coding: utf-8 -*-
"""
Created on Sun May  5 10:49:40 2024

@author: Anne-Fleur
"""

import numpy as np
from pulp import *
import matplotlib.pyplot as plt
import networkx as nx
import copy
import time

### LOAD INPUT
import load_instance

import os
dirname = os.path.dirname(__file__)
layers_folder = os.path.normpath(os.path.join(dirname, '../../'))

import sys
sys.path.insert(1, dirname+'\\pulp_scripts')
import MDP_exact
import MDP_heuristic


def write_outputs(G, n, K, K_i, betas, alpha, C, b, c, Bmax, w, filename, warm_version, without_gurobi, time_limit = 12*3600):
    label_to_position = {value: key for key, value in nx.get_node_attributes(G, 'label').items()}
    
    output = [['budget', 'runtime', 'objective_value', 'flow_caught_optimal', 'flow_caught_fixed_solution', 'flow_impact_area', ['solution']]]
    output = [['budget', 'runtime', 'objective_value', 'flow_caught_optimal', ['solution']]]
    old_solution = np.zeros((n, K))#n*[K*[0]]
    for B in np.arange(0.2, Bmax+0.2, 0.2):
        start = time.time()
        if without_gurobi == False:
            if warm_version == '':
                prob, G, solution, flow_caught, flow_impact_area, old_solution = MDP_exact.solve_MDP(G, n, K, K_i, betas, alpha, C, b, c, B, w, False, [], False, False, time_limit)# = 12*3600)
            elif warm_version == 'previous':
                prob, G, solution, flow_caught, flow_impact_area, old_solution = MDP_exact.solve_MDP(G, n, K, K_i, betas, alpha, C, b, c, B, w, False, old_solution, True, False, time_limit)# = 3600)
            elif warm_version == 'heuristic':
                x_heur, objective, solution = MDP_heuristic.MDP_heuristic(n, K, K_i, betas, alpha, C, b, c, B, w)
                prob, G, solution, flow_caught, flow_impact_area, old_solution = MDP_exact.solve_MDP(G, n, K, K_i, betas, alpha, C, b, c, B, w, False, x_heur, True, False, time_limit)
        else:
            if warm_version == '':
                prob, G, solution, flow_caught, flow_impact_area, old_solution = MDP_exact.solve_MDP(G, n, K, K_i, betas, alpha, C, b, c, B, w, False, [], False, True, time_limit)# = 12*3600)
            elif warm_version == 'previous':
                prob, G, solution, flow_caught, flow_impact_area, old_solution = MDP_exact.solve_MDP(G, n, K, K_i, betas, alpha, C, b, c, B, w, False, old_solution, True, True, time_limit)# = 12*3600)
            elif warm_version == 'heuristic':
                x_heur, objective, solution = MDP_heuristic.MDP_heuristic(n, K, K_i, betas, alpha, C, b, c, B, w)
                prob, G, solution, flow_caught, flow_impact_area, old_solution = MDP_exact.solve_MDP(G, n, K, K_i, betas, alpha, C, b, c, B, w, False, x_heur, True, True, time_limit)# = 12*3600)
        end = time.time()

        output += [[B, end-start, value(prob.objective), flow_caught, [[system[0], system[1], label_to_position[system[0]]] for system in solution]]]

        if end-start > time_limit:
            break


    with open(filename, 'w+') as f:
        # write elements of list
        for items in output:
            f.write('%s\n' %items)
        print("File written successfully")
    f.close()


def plot_runtimes(filenames, labels, fig, ax):
    runs = []
    for filename in filenames:
        with open(filename) as f:
            run = f.readlines()
        run = [eval(line.strip()) for line in run]
        runs += [run]

    n_rows = len(runs) #rows are different types of methods
    n_cols = len(runs[1])-1 #columns are runtime per budget
    runtimes = np.zeros((n_rows, n_cols))


    runtimes = [[]]

    for i, run in enumerate(runs):
        for j, budget in enumerate(run[1:]):
            runtimes[i] += [budget[1]]
        runtimes += [[]]
            # if j < n_cols:
            #     runtimes[i,j]  = budget[1]

    budgets = [row[0] for row in runs[1][1:]]
    # ax.set_title("Runtime against budget for different solution methods")
    for i in range(len(filenames)):
        # ax.plot(budgets, runtimes[i], label = labels[i])
        ax.plot(0.2*np.arange(len(runtimes[i]))+0.2, np.array(runtimes[i])/3600, label = labels[i])
    ax.set_xlabel('budget')
    ax.set_ylabel('runtime (hours)')
    ax.set_ylim(bottom = -0.5, top = 12)
    # ax.legend()

    return fig

#%%


year = 2022
MAX_DIST_NODES = 100
G, n, K, K_i, betas, alpha, C, b, c, B, w = load_instance.MIP_input(year, MAX_DIST_NODES, random_wind = False, version_alpha='')
Bmax = 4


### plot runtime vs budget for 4 different methods for 308 nodes
# write_outputs(G, n, K, K_i, betas, alpha, C, b, c, Bmax, w, '308nodes_gurobi_cold_PC_Noria.txt', '', False, time_limit = 3600)
# write_outputs(G, n, K, K_i, betas, alpha, C, b, c, Bmax, w, '308nodes_gurobi_warm_previous.txt', 'previous', False)
# write_outputs(G, n, K, K_i, betas, alpha, C, b, c, Bmax, w, '308nodes_gurobi_warm_heuristic_PC_Noria.txt', 'heuristic', False, time_limit = 3600)


#%%
# write_outputs(G, n, K, K_i, betas, alpha, C, b, c, Bmax, w, '308nodes_cbcsolver_cold_PC_Noria.txt', '', True, time_limit = 3600)
# write_outputs(G, n, K, K_i, betas, alpha, C, b, c, Bmax, w, '308nodes_cbcsolver_warm_previous.txt', 'previous', True)
# write_outputs(G, n, K, K_i, betas, alpha, C, b, c, Bmax, w, '308nodes_cbcsolver_warm_heuristic_PC_Noria.txt', 'heuristic', True, time_limit = 3600)

#%%

# filenames = ['308nodes_gurobi_cold.txt', '308nodes_gurobi_warm_previous.txt', '308nodes_gurobi_warm_heuristic.txt', '308nodes_cbcsolver_cold.txt', '308nodes_cbcsolver_warm_previous.txt', '308nodes_cbcsolver_warm_heuristic.txt']
# labels = ['Gurobi solver cold start', 'Gurobi solver warm start with solution B-0.2', 'Gurobi solver warm start with solution heuristic', 'CBC solver cold start', 'CBC solver warm start with solution B-0.2', 'CBC solver warm start with solution heuristic']
# # fig = plot_runtimes(filenames, labels)
# # fig.savefig("plots/runtimes_different_methods.png")

# filenames = ['308nodes_gurobi_cold_PC_Noria.txt', '308nodes_gurobi_warm_heuristic_PC_Noria.txt', '308nodes_cbcsolver_cold_PC_Noria.txt', '308nodes_cbcsolver_warm_heuristic_PC_Noria.txt']
# labels = ['Gurobi solver cold start', 'Gurobi solver warm start with heuristic solution', 'CBC solver cold start', 'CBC solver warm start with heuristic solution']
# fig = plot_runtimes(filenames, labels)
# fig.savefig("plots/runtimes_different_methods.png")


#%% --> console 2 PC noria
### plot runtime vs number of nodes for budgets 0.4, 0.8, 1.2, 1.6, 2.0 with Gurobi!

# for dist in [150, 125, 75, 50]: #100 has already been done!
# for dist in [50]:
#     G, n, K, K_i, betas, alpha, C, b, c, B, w = load_instance.MIP_input(year, dist, random_wind = False, version_alpha='')
#     write_outputs(G, n, K, K_i, betas, alpha, C, b, c, Bmax, w, str(n)+'nodes_gurobi_cold_PC_Noria.txt', '', False)
    # write_outputs(G, n, K, K_i, betas, alpha, C, b, c, Bmax, w, str(n)+'nodes_gurobi_warm_heuristic.txt', 'heuristic', False)

#%% try large number of nodes with CBC --> console 1 PC Noria
# for dist in [150, 125, 100, 75, 50]:
# for dist in [100, 75, 50]:
#     G, n, K, K_i, betas, alpha, C, b, c, B, w = load_instance.MIP_input(year, dist, random_wind = False, version_alpha='')
#     write_outputs(G, n, K, K_i, betas, alpha, C, b, c, Bmax, w, str(n)+'nodes_cbcsolver_cold_longtest.txt', '', without_gurobi = True)

#%%

# filenames = ['198nodes_gurobi_cold.txt', '198nodes_gurobi_warm_heuristic.txt', '244nodes_gurobi_cold.txt', '244nodes_gurobi_warm_heuristic.txt', '308nodes_gurobi_cold.txt', '308nodes_gurobi_warm_heuristic.txt', '412nodes_gurobi_cold.txt', '412nodes_gurobi_warm_heuristic.txt']
# labels = ['Gurobi solver cold start d = 150', 'Gurobi solver warm start heuristic d = 150', 'Gurobi solver cold start d = 125', 'Gurobi solver warm start heuristic d = 125', 'Gurobi solver cold start d = 100', 'Gurobi solver warm start heuristic d = 100', 'Gurobi solver cold start d = 75', 'Gurobi solver warm start heuristic d = 75']#, 'Gurobi solver cold start d = 50', 'Gurobi solver warm start heuristic d = 50']
# fig = plot_runtimes(filenames, labels)

#%%

# filenames = ['198nodes_gurobi_cold.txt', '244nodes_gurobi_cold.txt', '308nodes_gurobi_cold.txt', '412nodes_gurobi_cold.txt', '622nodes_gurobi_cold.txt']
# labels = ['Gurobi solver cold start d = 150', 'Gurobi solver cold start d = 125', 'Gurobi solver cold start d = 100', 'Gurobi solver cold start d = 75', 'Gurobi solver cold start d = 50', 'Gurobi solver warm start heuristic d = 50']
# fig = plot_runtimes(filenames, labels)
# fig.savefig("plots/runtimes_different_nodes.png")

#%% different n nodes gurobi PC noria

fig, axs = plt.subplots(1, 2, figsize = (14,6))
filenames = ['198nodes_gurobi_cold_PC_Noria.txt', '244nodes_gurobi_cold_PC_Noria.txt', '308nodes_gurobi_cold_PC_Noria.txt', '412nodes_gurobi_cold_PC_Noria.txt', '622nodes_gurobi_cold_PC_Noria.txt']
labels = ['Gurobi solver n=198, d=150', 'Gurobi solver n=244, d=125', 'Gurobi solver n=308, d=100', 'Gurobi solver n=412, d=75', 'Gurobi solver n=622 d=50']
labels = ['n=198, d=150', 'n=244, d=125', 'n=308, d=100', 'n=412, d=75', 'n=622 d=50']
fig = plot_runtimes(filenames, labels, fig, axs[0])
axs[0].legend()
axs[0].set_title("Gurobi solver cold start")
# fig.savefig("plots/runtimes_different_nodes_Gurobi.png")

#%% different n nodes cbc PC noria

filenames = ['198nodes_cbcsolver_cold_longtest.txt', '244nodes_cbcsolver_cold_longtest.txt', '308nodes_cbcsolver_cold_longtest.txt', '412nodes_cbcsolver_cold_longtest.txt', '622nodes_cbcsolver_cold_longtest.txt']
labels = ['CBC solver n=198, d=150', 'CBC solver n=244, d=125', 'CBC solver n=308, d=100', 'CBC solver n=412, d=75', 'CBC solver n=622 d=50']
fig = plot_runtimes(filenames, labels, fig, axs[1])
axs[1].set_title("CBC solver cold start")
fig.savefig("plots/runtimes_different_nodes_GurobiCBC.png")

#%% plot compare quality of solutions of CBC
filenames = ['308nodes_cbcsolver_cold_longtest.txt', '412nodes_cbcsolver_cold_longtest.txt', '622nodes_cbcsolver_cold_longtest.txt']
n_nodes = [308, 412, 622]
# runs = []
# for filename in filenames:
#     with open(filename) as f:
#         run = f.readlines()
#     run = [eval(line.strip()) for line in run]
#     runs += [run]



# for index, run in enumerate(runs):
#     #     G, n, K, K_i, betas, alpha, C, b, c, B, w = load_instance.MIP_input(year, dist, random_wind = False, version_alpha='')
#     x = np.zeros((n,K))
#     for system in run[-1][-1]:
#         x[system[0]-1, system[1]-1] = 1

### hand coded
fig, axs = plt.subplots(1, 2, figsize = (14,6))
axs[0].plot(np.arange(3), [0.1387321433549154, 0.11228169771016479, 0.11606872986421658], 'o', fillstyle = 'none', label = 'CBC solver after 12 hours')
axs[0].plot(np.arange(3), [0.13873214413467005, 0.11228205646527706, 0.11606872985344267], '+', label = 'Gurobi solver optimal solution')
axs[0].plot(np.arange(3), [0.13873214413466992, 0.11228169792440977, 0.11606872973370914], 'x', label = 'heuristic solution')
axs[0].set_xticks(np.arange(3), labels=['n=308, B=3.6', 'n=412, B=2.4', 'n=622, B=1.8'])
axs[0].set_ylabel("objective value")
axs[0].legend()

axs[1].plot(np.arange(2), [0.13706662324233038, 0.13182937247026105], '+', label = 'Gurobi solver after 12 hours')
axs[1].plot(np.arange(2), [0.1368813224255982, 0.1315775739854198], 'x', label = 'heuristic solution')
axs[1].set_xticks(np.arange(2), labels=['n=412, B=3.6', 'n=622, B=2.4'])
axs[1].set_ylabel("objective value")
axs[1].legend()