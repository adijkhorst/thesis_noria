# -*- coding: utf-8 -*-
"""
Created on Tue Jan  9 10:37:57 2024

@author: Anne-Fleur
"""
import numpy as np




def objective_value(b, betas, C, x):
    transition_matrix = np.repeat([np.ones(n) - np.sum(betas*x)], n, axis = 0).T * np.copy(C)
    c_n1 = np.sum(betas*x, axis = 1)

    return b.T @ np.linalg.inv(np.eye(n)-transition_matrix) @ c_n1

### instance
n = 6
k = 1

betas = 0.8 * np.ones((n,k))
c_1 = 1
B = 1.5

Q = np.zeros((7,7));
indices = [[0, 0], [1, 0], [2, 1], [3, 4], [4, 5], [5, 2], [6, 5]]
for i in indices:
    Q[i[0], i[1]] = 1

b = np.array([0, 0, 0.6, 0, 0, 0.4])
C = Q[1:, 1:]

### greedy heuristic algorithm
costs = 0
x = np.zeros((n,k))
N_not_Ak = set(np.arange(1,n+1))
Ak = set()

while B - costs >= c_1:
    objectives = np.zeros(n)
    for i in N_not_Ak:
        x_plus1 = np.copy(x)
        x_plus1[i-1, 0] = 1
        objectives[i-1] = objective_value(b, betas, C, x_plus1)
    i = np.argmax(objectives)
    x[i, 0] = 1
    N_not_Ak.remove(i+1)
    Ak.add(i+1)

for i in range(n):
    if i+1 in Ak:
        x_min1 = np.copy(x)
        x_min1[i, 0] = 0
