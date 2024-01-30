# -*- coding: utf-8 -*-
"""
Created on Tue Jan  9 10:37:57 2024

@author: Anne-Fleur
"""
import numpy as np

import sys
sys.path.insert(1, "C:/Users/Anne-Fleur/OneDrive - Noria/Documents - Noria Internship/Anne Fleur/1. Working Folder/3. GIS/Network FCLM/thesis_noria/spyder scripts")
import simulate_markov_chain

def objective_value(P, fp, K_i, betas, x, alphas = 1):
    # total = 0
    # for path in P:
        # total += fp * sum(sum(betas[i-1,k-1]*x[i-1,k-1] for k in K_i[i]) for i in path
    objective = 0
    for index_path in range(len(P)):
        path = P[index_path]
        totalsum = 0
        for index_i in range(len(path)): #index_i is the index of the node in the path, that means i = path[index_i]
            i = path[index_i]
            for k in K_i[i]:
                totalproduct = 1
                # ONLY CALCULATE PRODUCT IF X_IK = 1?
                if x[i-1, k-1] == 1:
                    for j in path[:index_i]:
                        for k_j in K_i[j]:
                            totalproduct *= 1-betas[j-1, k_j-1]*x[j-1, k_j-1]
                if alphas == 1:
                    totalsum += betas[i-1, k-1]*x[i-1, k-1] * totalproduct
                else:
                    totalsum += alphas[index_path][index_i]*betas[i-1, k-1]*x[i-1, k-1] * totalproduct
        objective += fp[index_path] * totalsum

    return objective

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
# #uncomment next lines for case 6 nodes probabilistic
# Q[2, 1] = 0.5
# Q[2, 3] = 0.5
# K_i[2] = {}
# K_i[3] = {}

b = np.array([0, 0, 0, 0.6, 0, 0, 0.4]) #should this include 0 and n+1?

# # #case 2: 2 nodes recurring flow
# n = 2
# K = 2
# K_i = {}
# for i in range(1, 3):
#     K_i[i] = {1}

# Q = np.zeros((3,3))
# Q[0, 0] = 1; Q[2, 1] = 1
# Q[1, 0] = 0.75; Q[1, 2] = 0.25

# b = np.array([0, 0.4, 0.6])

P = [[3, 4, 5, 2, 1],[6, 5, 2, 1]] #CHECK IF LIST OR DICT IS A BETTER DATA STRUCTURE LATER ON
fp = [3, 2]
# P, fp = simulate_markov_chain.simulate_P_fp(b, Q, 20)

alphas = [[1, 0.9, 0.8, 0.7, 0.6], [1, 0.866, 0.733, 0.6]]
alphas = [[10, 9, 8, 7, 6], [10, 8.66, 7.33, 6]]
alphas = 1
betas = 0.8 * np.ones((n,K))
c = [1, 0.5]
Budget = 1.5

### greedy heuristic algorithm
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
            if costs + c[k-1] < Budget:
                x_plus1 = np.copy(x)
                x_plus1[i-1, 0] = 1
                objectives[i-1, k-1] = objective_value(P, fp, K_i, betas, x_plus1, alphas)

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

print(Ak)
print(x)
print(objective)

### cleaning step!
for i in Ak: #this is the actual i, not index
    x_min1 = np.copy(x)
    index_k = np.argmax(x_min1[i-1])
    x_min1[i-1, index_k] = 0
    new_objective = objective_value(P, fp, K_i, betas, x_min1, alphas)
    if new_objective > objective:
        x = np.copy(x_min1)
        N_not_Ak.add(i)
        Ak.remove(i)
        objective = new_objective
        costs -= c[index_k]

print(Ak)
print(x)
print(objective)
