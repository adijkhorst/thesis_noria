# -*- coding: utf-8 -*-
"""
Created on Tue Jan  9 10:37:57 2024

@author: Anne-Fleur
"""
import numpy as np
import scipy
import sys
import os
dirname = os.path.dirname(__file__)
previous_folder = os.path.normpath(os.path.join(dirname, '../'))
sys.path.insert(1, previous_folder)
import load_instance

import networkx as nx


def flow_caught(x, n, betas, alpha, C, b):
    transition_matrix = np.diag(np.ones(n) - np.sum(betas*x, axis = 1)) @ np.copy(C)
    c_n1 = np.sum(betas*x, axis = 1)
    return b.T @ np.linalg.inv(np.eye(n)-transition_matrix) @ c_n1
    
    # inv_matrix = scipy.sparse.csc_matrix(np.eye(n)-transition_matrix)
    # return b.T @ scipy.sparse.linalg.inv(inv_matrix) @ c_n1


def objective_value(n, b, betas, C, x, w, costs, alpha):
    transition_matrix = np.diag(np.ones(n) - np.sum(betas*x, axis = 1)) @ np.copy(C)

    binverse = b.T @ np.linalg.inv(np.eye(n)-transition_matrix)
    # inv_matrix = scipy.sparse.csc_matrix(np.eye(n)-transition_matrix)
    # binverse = b.T @ scipy.sparse.linalg.inv(inv_matrix)

    c_n1 = np.sum(betas*x, axis = 1)

    alphaterm = alpha * (1 - np.sum(betas*x, axis = 1))
    return binverse @ c_n1 - w * costs - binverse @ alphaterm


### greedy heuristic algorithm


def MDP_heuristic(n, K, K_i, betas, alpha, C, b, c, B, w):
    costs = 0
    x = np.zeros((n,K))
    N_not_Ak = set(np.arange(1,n+1))
    Ak = set()
    objective = -10000
    
    #save second best options
    second_best = set()
    
    stop = False
    while not stop:
        objectives = -10000*np.ones((n,K))
        for i in N_not_Ak: #i in the set is the actual i, not index
            for k in K_i[i]:
                if round(costs + c[k-1],7) <= B:
                    x_plus1 = np.copy(x)
                    x_plus1[i-1, k-1] = 1
                    objectives[i-1, k-1] = objective_value(n, b, betas, C, x_plus1, w, costs+c[k-1], alpha)
    
        #check if objective can still improve and check if any objective values were calculated, otherwise there is no i,k left within the budget
        if not np.any(objectives > -10000) or np.max(objectives) < objective:
            stop = True
        else:
            objectives_without_cost_term =np.array(objectives) + w*np.repeat([c], n, axis = 0)
            # relative_objectives = (np.array(objectives)-objective)/np.repeat([c], n, axis = 0)
            relative_objectives = (objectives_without_cost_term-objective+w*costs)/np.repeat([c], n, axis = 0)
            index_i, index_k = np.unravel_index(np.argmax(relative_objectives), relative_objectives.shape) #indices of maximum objective value

            #to find second best element and save it
            relative_objectives[index_i, index_k] = 0
            second_index_i, second_index_k = np.unravel_index(np.argmax(relative_objectives), relative_objectives.shape)
            second_best.add(second_index_i + 1)

            x[index_i, index_k] = 1
            N_not_Ak.remove(index_i+1)
            Ak.add(index_i+1)
            objective = objectives[index_i, index_k]
            costs += c[index_k]
    print("First stage of heuristic:")
    print(Ak)
    print(np.argwhere(x>0.8))
    print(objective)
    
    ### cleaning step! seems unnecessary for this case
    # for i in Ak: #this is the actual i, not index
    #     x_min1 = np.copy(x)
    #     index_k = np.argmax(x_min1[i-1])
    #     x_min1[i-1, index_k] = 0
    #     new_objective = objective_value(n, b, betas, C, x_min1, w, costs, alpha)
    #     if new_objective > objective:
    #         x = np.copy(x_min1)
    #         N_not_Ak.add(i)
    #         Ak.remove(i)
    #         objective = new_objective
    #         costs -= c[index_k]
    # print("After clean up step:")
    # print(Ak)
    # print(np.argwhere(x>0.8))
    # print(objective)

    solution = [(i[0]+1, str(i[1]+1)) for i in np.argwhere(x>0.8)]
    solution = [[i[0]+1, i[1]+1] for i in np.argwhere(x>0.8)]
    
    print('second best options: ', second_best)

    return x, objective, solution

def local_search(n, K, K_i, betas, alpha, C, b, c, B, w, G, x, size_neighbourhood):
    # for
    
    return x


if __name__ == '__main__':

    year = 2022
    MAX_DIST_NODES = 100
    G, n, K, K_i, betas, alpha, C, b, c, B, w = load_instance.MIP_input(year, MAX_DIST_NODES, random_wind = False)
    
    old_attrs = nx.get_node_attributes(G, 'water_veg_prob')
    for perc in [0]:
        for node in G.nodes():
            new_water_veg_prob =  perc if old_attrs[node] > 0 else 0
            nx.set_node_attributes(G, {node: {'water_veg_prob': new_water_veg_prob}})
            probs = np.array([G.nodes[node]['dead_ends_prob'], G.nodes[node]['sharp_corners_prob'], G.nodes[node]['shore_boats_prob'], G.nodes[node]['shore_veg_prob'], G.nodes[node]['water_veg_prob']])
            nx.set_node_attributes(G, {node: {'stuck_probability': (1-np.prod(1-probs))}})

        stuck = [G.nodes[node]['stuck_probability'] for node in G.nodes()]
        stuck_matrix = np.repeat([stuck], len(stuck), axis = 0).T

        A = nx.adjacency_matrix(G, nodelist = G.nodes(), weight = 'transition_probability').toarray()
        C_new = (1-stuck_matrix) * A
    
    B = 0.6
    x, objective, solution = MDP_heuristic(n, K, K_i, betas, alpha, C_new, b, c, B, w)


    ### TEST CASES
    
    # #case 1: 6 nodes deterministic
    # n = 6
    # K = 2
    # K_i = {}
    # for i in range(1,7):
    #     K_i[i] = {1} #{1,2} #try with two types of catching systems later
    #     if i == 5:
    #         K_i[i] = {}
    
    # Q = np.zeros((7,7));
    # indices = [[0, 0], [1, 0], [2, 1], [3, 4], [4, 5], [5, 2], [6, 5]]
    # for i in indices:
    #     Q[i[0], i[1]] = 1
    # #uncomment next lines for case 6 nodes probabilistic
    # # Q[2, 1] = 0.5
    # # Q[2, 3] = 0.5
    # # K_i[2] = {}
    # # K_i[3] = {}
    
    # b = np.array([0, 0, 0.6, 0, 0, 0.4]) #should this include 0 and n+1?
    
    # # # #case 2: 2 nodes recurring flow
    # # n = 2
    # # K = 2
    # # K_i = {}
    # # for i in range(1, 3):
    # #     K_i[i] = {1}
    
    # # Q = np.zeros((3,3))
    # # Q[0, 0] = 1; Q[2, 1] = 1
    # # Q[1, 0] = 0.75; Q[1, 2] = 0.25
    
    # # b = np.array([0.4, 0.6])
    
    
    
    # ###
    # betas = 0.8 * np.ones((n,K))
    # c = [1, 0.5]
    # Budget = 1.5
    # C = Q[1:, 1:]
    
    # alpha = 0

    # x, objective = MDP_heuristic(n, K, K_i, betas, alpha, C, b, c, Budget)



