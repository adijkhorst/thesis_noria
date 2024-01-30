# -*- coding: utf-8 -*-
"""
Created on Tue Jan 30 10:50:31 2024

@author: Anne-Fleur
"""

from pulp import *
import numpy as np
import networkx as nx


import network_creation
import transition_probabilities_wind
import init_probability

### TEST DELFT

# import the networkx graph from network_creation.py, get transition probabilities and initial probabilities
G = network_creation.create_network()
transition_probabilities_wind.get_transition_probabilities(G)
init_probability.get_initial_probabilities(G)
init_probability.get_stuck_probabilities(G)

b = np.array([G.nodes[node]['init_probability'] for node in G.nodes()])

stuck = [G.nodes[node]['stuck_probability'] for node in G.nodes()]
stuck_matrix = np.repeat([stuck], len(stuck), axis = 0).T

A = nx.adjacency_matrix(G, nodelist = G.nodes(), weight = 'transition_probability').toarray()
C = (1-stuck_matrix) * A

attrs = {}
for index, node in enumerate(G.nodes()):
    attrs[node] = {'label': index+1, 'position' : node}
nx.set_node_attributes(G, attrs)

### instance parameters
n = len(G.nodes())
K = 2

no_system = init_probability.no_catching_system()
### later proberen met sets K_i
K_i = {}
for node in G.nodes():
    if node in no_system:
        K_i[G.nodes[node]['label']] = {}
    else:
        K_i[G.nodes[node]['label']] = {1, 2}

np.random.seed(0)
betas = np.random.uniform(0.1, 0.8, (n, K))
c_1 = 1
B = 7.5

#%%

prob = LpProblem("MDP-FCLM", LpMaximize)

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

prob += sum(sum(c_1 * xs[i][k-1] for k in K_i[i+1]) for i in range(n)) <= B


#obj func
flow_caught = sum(betas[i,k-1]*v2[i][k-1] for i in range(n) for k in K_i[i+1]) #- sum(alpha*v for v in v1)
prob += flow_caught

### solve
status = prob.solve(GUROBI_CMD(options = [('LogToConsole', 1)]))
print(LpStatus[status])

for i in prob.variables():
    if i.varValue == 1:
        print(i, i.varValue)
    # print(i, i.varValue)

print(value(prob.objective))
print('flow caught: ', value(sum(betas[i,k-1]*v2[i][k-1] for i in range(n) for k in K_i[i+1])))
# print(prob.variables)