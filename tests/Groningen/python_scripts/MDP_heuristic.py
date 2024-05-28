# -*- coding: utf-8 -*-
"""
Created on Tue Jan  9 10:37:57 2024

@author: Anne-Fleur
"""
import numpy as np


def flow_caught(x, n, betas, alpha, C, b):
    transition_matrix = np.diag(np.ones(n) - np.sum(betas*x, axis = 1)) @ np.copy(C)
    c_n1 = np.sum(betas*x, axis = 1)
    return b.T @ np.linalg.inv(np.eye(n)-transition_matrix) @ c_n1


def objective_value(n, b, betas, C, x, w, costs, alpha):
    transition_matrix = np.diag(np.ones(n) - np.sum(betas*x, axis = 1)) @ np.copy(C)

    binverse = b.T @ np.linalg.inv(np.eye(n)-transition_matrix)
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
            # relative_objectives = (np.array(objectives)-objective)/np.repeat([c], n, axis = 0) # old version with cost term
            relative_objectives = (objectives_without_cost_term-objective+w*costs)/np.repeat([c], n, axis = 0)
            index_i, index_k = np.unravel_index(np.argmax(relative_objectives), relative_objectives.shape) #indices of maximum objective value

            x[index_i, index_k] = 1
            N_not_Ak.remove(index_i+1)
            Ak.add(index_i+1)
            objective = objectives[index_i, index_k]
            costs += c[index_k]
    print(Ak)
    print(np.argwhere(x>0.8))
    print(objective)

    solution = [[i[0]+1, i[1]+1] for i in np.argwhere(x>0.8)]


    return x, objective, solution