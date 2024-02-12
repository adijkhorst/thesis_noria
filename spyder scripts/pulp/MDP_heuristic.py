# -*- coding: utf-8 -*-
"""
Created on Tue Jan  9 10:37:57 2024

@author: Anne-Fleur
"""
import numpy as np


def objective_value(b, betas, C, x):
    transition_matrix = np.diag(np.ones(n) - np.sum(betas*x, axis = 1)) @ np.copy(C)
    c_n1 = np.sum(betas*x, axis = 1)

    return b.T @ np.linalg.inv(np.eye(n)-transition_matrix) @ c_n1


### greedy heuristic algorithm


def MDP_heuristic(n, K, K_i, betas, alpha, C, b, c, B):
    costs = 0
    x = np.zeros((n,K))
    N_not_Ak = set(np.arange(1,n+1))
    Ak = set()
    objective = 0
    
    stop = False
    while not stop:
        objectives = np.zeros((n,K))
        for i in N_not_Ak: #i in the set is the actual i, not index
            for k in K_i[i]:
                if costs + c[k-1] < B:
                    x_plus1 = np.copy(x)
                    x_plus1[i-1, 0] = 1
                    objectives[i-1, k-1] = objective_value(b, betas, C, x_plus1)
    
        #check if objective can still improve and check if any objective values were calculated, otherwise there is no i,k left within the budget
        if not np.any(objectives > 0) or np.max(objectives) < objective:
            stop = True
        else:
            index_i, index_k = np.unravel_index(np.argmax(objectives), objectives.shape) #indices of maximum objective value
            x[index_i, index_k] = 1
            N_not_Ak.remove(index_i+1)
            Ak.add(index_i+1)
            objective = objectives[index_i, index_k]
            costs += c[index_k]
    print("First stage of heuristic:")
    print(Ak)
    print(x)
    print(objective)
    
    ### cleaning step!
    for i in Ak: #this is the actual i, not index
        x_min1 = np.copy(x)
        index_k = np.argmax(x_min1[i-1])
        x_min1[i-1, index_k] = 0
        new_objective = objective_value(b, betas, C, x_min1)
        if new_objective > objective:
            x = np.copy(x_min1)
            N_not_Ak.add(i)
            Ak.remove(i)
            objective = new_objective
            costs -= c[index_k]
    print("After clean up step:")
    print(Ak)
    print(x)
    print(objective)

    return x, objective


if __name__ == '__main__':

    ### TEST CASES
    
    #case 1: 6 nodes deterministic
    n = 6
    K = 2
    K_i = {}
    for i in range(1,7):
        K_i[i] = {1} #{1,2} #try with two types of catching systems later
        if i == 5:
            K_i[i] = {}
    
    Q = np.zeros((7,7));
    indices = [[0, 0], [1, 0], [2, 1], [3, 4], [4, 5], [5, 2], [6, 5]]
    for i in indices:
        Q[i[0], i[1]] = 1
    #uncomment next lines for case 6 nodes probabilistic
    # Q[2, 1] = 0.5
    # Q[2, 3] = 0.5
    # K_i[2] = {}
    # K_i[3] = {}
    
    b = np.array([0, 0, 0.6, 0, 0, 0.4]) #should this include 0 and n+1?
    
    # # #case 2: 2 nodes recurring flow
    # n = 2
    # K = 2
    # K_i = {}
    # for i in range(1, 3):
    #     K_i[i] = {1}
    
    # Q = np.zeros((3,3))
    # Q[0, 0] = 1; Q[2, 1] = 1
    # Q[1, 0] = 0.75; Q[1, 2] = 0.25
    
    # b = np.array([0.4, 0.6])
    
    
    
    ###
    betas = 0.8 * np.ones((n,K))
    c = [1, 0.5]
    Budget = 1.5
    C = Q[1:, 1:]
    
    alpha = 0

    x, objective = MDP_heuristic(n, K, K_i, betas, alpha, C, b, c, Budget)