# -*- coding: utf-8 -*-
"""
Created on Tue Mar 26 13:59:42 2024

@author: Anne-Fleur
"""

import numpy as np
from scipy.spatial import distance
from scipy.optimize import linear_sum_assignment
import matplotlib.pyplot as plt

### LOAD INPUT
import load_instance

year = 2022
MAX_DIST_NODES = 100
G, n, K, K_i, betas, alpha, C, b, c, B, w = load_instance.MIP_input(year, MAX_DIST_NODES, random_wind = False)


### CREATE PERTURBATIONS

def change_init_prob():
    # run for different perturbations of b, save to output files

    # b = b*np.random.uniform(0.8, 1.2, len(b))
    # b = b/np.sum(b)
    # b = np.ones(n)/n

    # plot differences in solution and flow caught

    pass

### RUN AND SAVE IMPORTANT OUTPUT FOR ALL PERTURBATIONS


### COMPARE SOLUTIONS
with open('308nodes.txt') as f:
    run1 = f.readlines()
run1 = [eval(line.strip()) for line in run1]

with open('338nodes.txt') as f:
    run2 = f.readlines()
run2 = [eval(line.strip()) for line in run2]


distances = np.zeros(len(run1)-1)
difference_caught_flow = np.zeros(len(run1)-1)
for budget_index in range(len(run1)-1):
    locations1 = [list(i[-1]) for i in run1[budget_index + 1][-1]]
    locations2 = [list(i[-1]) for i in run2[budget_index + 1][-1]]

    pairwise_distances = distance.cdist(locations1, locations2)
    row_ind, col_ind = linear_sum_assignment(pairwise_distances)
    mean_distance = pairwise_distances[row_ind, col_ind].sum()/len(locations1)
    max_distance = np.max(pairwise_distances[row_ind, col_ind])
    distances[budget_index] = max_distance
    # difference_caught_flow[budget_index] = run1[]

    # caught
#%%

filenames = ['wind_year2020_308nodes.txt', 'wind_year2021_308nodes.txt', '308nodes.txt', 'wind_year2023_308nodes.txt', 'transition_prob_uniform_308nodes.txt']
variations = ['2020', '2021', '2022', '2023', 'turbulent']
fixed_index = 2

runs = []
for filename in filenames:
    with open(filename) as f:
        run = f.readlines()
    run = [eval(line.strip()) for line in run]
    runs += [run]

distances = np.zeros((len(runs)-1, len(runs[1])-1))
flow_differences = np.zeros((len(runs)-1, len(runs[1])-1))

list_index = 0
for i, run in enumerate(runs):
    if i != fixed_index:
        for j, budget in enumerate(run[1:]):
            locations_i = [list(system[-1]) for system in budget[-1]]
            locations_fixed = [list(system[-1]) for system in runs[fixed_index][j+1][-1]]

            pairwise_distances = distance.cdist(locations_i, locations_fixed)
            row_ind, col_ind = linear_sum_assignment(pairwise_distances)
            total_distance = pairwise_distances[row_ind, col_ind].sum()
            mean_distance = pairwise_distances[row_ind, col_ind].sum()/len(locations1)
            max_distance = np.max(pairwise_distances[row_ind, col_ind])
            distances[list_index, j] = total_distance
            flow_differences[list_index,j] = budget[3]-runs[fixed_index][j+1][3]
        list_index += 1

budgets = [row[0] for row in runs[0][1:]]
plot_labels = variations[:fixed_index] + variations[fixed_index+1:]

#%% two plots

fig, (ax1, ax2) = plt.subplots(1, 2)
# ax.title("Sensitivity analysis of wind directions compared to 2022")

ax1.grid()
ax1.set_xlabel('budget')
ax1.set_ylabel('total distance between solutions')
ax1.legend()

ax2.set_ylabel('difference in proportion of flow caught')

ax2.grid()
ax2.axhline(y = 0, linewidth = 0.5, color = 'k')
for i in range(len(plot_labels)):
    ax1.plot(budgets, distances[i], label = plot_labels[i])
    ax2.plot(budgets, flow_differences[i], label = plot_labels[i])

ax2.legend()



#%% one plot with double axes

fig, ax1 = plt.subplots()
plt.title("Sensitivity analysis of wind directions compared to 2022")

ax1.set_xlabel('budget')
ax1.set_ylabel('total distance between solutions')

ax2 = ax1.twinx()
ax2.set_ylabel('difference in proportion of flow caught')
for i in range(len(plot_labels)):
    ax1.plot(budgets, distances[i], label = plot_labels[i])
    ax2.plot(budgets, flow_differences[i], '--', label = plot_labels[i])

plt.legend()


