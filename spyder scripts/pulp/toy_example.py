# -*- coding: utf-8 -*-
"""
Created on Mon Jan  8 15:43:15 2024

@author: Anne-Fleur
"""

from pulp import *
import numpy as np

prob = LpProblem("MDP-FCLM", LpMaximize)

### instance parameters
n = 6
# k = 1

### later proberen met sets K_i
K_i = {}
for i in range(1,7):
    K_i[i] = {1} #{1,2} #try with two types of catching systems later
    if i == 5:
        K_i[i] = {}

beta_1 = 0.8
c_1 = 1
B = 4.5

Q = np.zeros((7,7));
indices = [[0, 0], [1, 0], [2, 1], [3, 4], [4, 5], [5, 2], [6, 5]]
for i in indices:
    Q[i[0], i[1]] = 1

b = np.array([0, 0, 0.6, 0, 0, 0.4]) #should this include 0 and n+1?

### not instance specific!

C = Q[1:, 1:]

M1 = b.T @ np.linalg.inv(np.eye(n)-C)
M2 = np.zeros(n)
for i in range(n):
    diagB = np.eye(n)
    diagB[i,i] = 1 - beta_1
    M2[i] = (b.T @ np.linalg.inv(np.eye(n)- diagB @ C))[i]


### create variables x_ik, v_i1, v_ik2
# xs = [[LpVariable("x{}{}".format(i+1, j+1), cat="Binary") for j in range(k)] for i in range(n)]
v1 = [LpVariable("v{}1".format(i+1), 0) for i in range(n)]
# v2 = [[LpVariable("v{}{}2".format(i+1, j+1), 0) for j in range(k)] for i in range(n)]

## later proberen met sets K_i
xs = [[LpVariable("x{}{}".format(i+1, j), cat="Binary") for j in K_i[i+1]] for i in range(n)] #look at indices +1!
v2 = [[LpVariable("v{}{}2".format(i+1, j), 0) for j in K_i[i+1]] for i in range(n)] #look at indices +1!

### create constraints and obj func
for i in range(n):
    prob += v1[i] + sum(v2[i]) - sum(C[j,i] * v1[j] for j in range(n)) - sum(sum((1-beta_1)*C[j,i]*v2[j][k-1] for k in K_i[j+1]) for j in range(n)) == b[i]

    prob += v1[i] <= (1-sum(xs[i][k-1] for k in K_i[i+1])) * M1[i]

    for k in K_i[i+1]:
        prob += v2[i][k-1] <= M2[i]*xs[i][k-1]

    prob += sum(xs[i][k-1] for k in K_i[i+1]) <= 1

prob += sum(sum(c_1 * xs[i][k-1] for k in K_i[i+1]) for i in range(n)) <= B

#obj func
flow_caught = sum(beta_1*v for v_i in v2 for v in v_i)
prob += flow_caught

### solve
status = prob.solve()
print(LpStatus[status])

for i in prob.variables():
    print(i, i.varValue)


# print(prob.variables)