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
K = 2
# k = 1

### later proberen met sets K_i
K_i = {}
for i in range(1,7):
    K_i[i] = {1,2} #try with two types of catching systems later
    if i == 5:
        K_i[i] = {}

beta_1 = 0.8
alpha = n*[0.1]
# alpha = 0.1
c = [1, 1.5]
B = 1.5

np.random.seed(0)
# betas = np.random.uniform(0.1, 0.8, (n, K))
betas = 0.8 * np.ones((n,K))

### TEST CASES

#case 1: 6 nodes deterministic
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

# #case 2: 2 nodes recurring flow
# n = 2
# Q = np.zeros((3,3))
# Q[0, 0] = 1; Q[2, 1] = 1
# Q[1, 0] = 0.75; Q[1, 2] = 0.25

# b = np.array([0.4, 0.6])

#%%

C = Q[1:, 1:]

M1 = b.T @ np.linalg.inv(np.eye(n)-C)
M2 = np.zeros((n,K))
for i in range(n):
    for k in range(K):
        diagB = np.eye(n)
        diagB[i,i] = 1 - betas[i,k]
        M2[i,k] = (b.T @ np.linalg.inv(np.eye(n)- diagB @ C))[i]


### create variables x_ik, v_i1, v_ik2
# xs = [[LpVariable("x{}{}".format(i+1, j+1), cat="Binary") for j in range(k)] for i in range(n)]
v1 = [LpVariable("v{}1".format(i+1), 0) for i in range(n)]
# v2 = [[LpVariable("v{}{}2".format(i+1, j+1), 0) for j in range(k)] for i in range(n)]

## later proberen met sets K_i
xs = [[LpVariable("x{}{}".format(i+1, j), cat="Binary") for j in K_i[i+1]] for i in range(n)] #look at indices +1!
v2 = [[LpVariable("v{}{}2".format(i+1, j), 0) for j in K_i[i+1]] for i in range(n)] #look at indices +1!

### create constraints and obj func
for i in range(n):
    prob += v1[i] + sum(v2[i]) - sum(C[j,i] * v1[j] for j in range(n)) - sum(sum((1-betas[j,k-1])*C[j,i]*v2[j][k-1] for k in K_i[j+1]) for j in range(n)) == b[i]

    prob += v1[i] <= (1-sum(xs[i][k-1] for k in K_i[i+1])) * M1[i]

    for k in K_i[i+1]:
        prob += v2[i][k-1] <= M2[i]*xs[i][k-1]

    prob += sum(xs[i][k-1] for k in K_i[i+1]) <= 1

prob += sum(sum(c[k-1] * xs[i][k-1] for k in K_i[i+1]) for i in range(n)) <= B

### test if a solution is optimal
# prob += xs[1][0] == 1
# prob += xs[0][0] == 0
# prob += xs[2][0] == 0
# prob += xs[3][0] == 0
# prob += xs[5][0] == 0

#obj func
flow_caught = sum(betas[i,k-1]*v2[i][k-1] for i in range(n) for k in K_i[i+1]) - sum(alpha[i]*v for i,v in enumerate(v1))
# flow_caught = sum(beta_1*v for v_i in v2 for v in v_i) #- sum(alpha*v for v in v1)
prob += flow_caught

### solve
status = prob.solve(GUROBI_CMD(options = [('LogToConsole', 1)]))
print(LpStatus[status])

for i in prob.variables():
    print(i, i.varValue)

print(value(prob.objective))
print('flow caught: ', value(sum(betas[i,k-1]*v2[i][k-1] for i in range(n) for k in K_i[i+1])))
# print(prob.variables)