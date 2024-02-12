# -*- coding: utf-8 -*-
"""
Created on Thu Feb  1 14:39:46 2024

@author: Anne-Fleur
"""

from pulp import *
import numpy as np

def solve_MDP(n, K, K_i, betas, alpha, C, b, c, B):
    #(number_nodes, number_catching_systems, possible_catching_systems, catching_probabilities, impact_factor, transition_matrix, initial_distribution, costs, budget):
    prob = LpProblem("MDP-FCLM", LpMaximize)


    M1 = b.T @ np.linalg.inv(np.eye(n)-C)
    M2 = np.zeros((n,K))
    for i in range(n):
        for k in range(K):
            diagB = np.eye(n)
            diagB[i,i] = 1 - betas[i,k]
            M2[i,k] = (b.T @ np.linalg.inv(np.eye(n)- diagB @ C))[i]

    ## create variables for existing K_i
    xs = [[LpVariable("x{}{}".format(i+1, j), cat="Binary") for j in K_i[i+1]] for i in range(n)] #look at indices +1!
    v1 = [LpVariable("v{}1".format(i+1), 0) for i in range(n)]
    v2 = [[LpVariable("v{}{}2".format(i+1, j), 0) for j in K_i[i+1]] for i in range(n)] #look at indices +1!

    ### create constraints
    for i in range(n):
        prob += v1[i] + sum(v2[i]) - sum(C[j,i] * v1[j] for j in range(n)) - sum(sum((1-betas[j,k-1])*C[j,i]*v2[j][k-1] for k in K_i[j+1]) for j in range(n)) == b[i]
    
        prob += v1[i] <= (1-sum(xs[i][k-1] for k in K_i[i+1])) * M1[i]
    
        for k in K_i[i+1]:
            prob += v2[i][k-1] <= M2[i]*xs[i][k-1]
    
        prob += sum(xs[i][k-1] for k in K_i[i+1]) <= 1
    
    prob += sum(sum(c_1 * xs[i][k-1] for k in K_i[i+1]) for i in range(n)) <= B

    ### create objective function
    flow_caught = sum(betas[i,k-1]*v2[i][k-1] for i in range(n) for k in K_i[i+1]) #- sum(alpha*v for v in v1)
    prob += flow_caught

    ### solve
    status = prob.solve(GUROBI_CMD(options = [('LogToConsole', 1)]))
    print('Solution is: ', LpStatus[status])

    print('Catching systems located at:')
    for i in prob.variables():
        if i.varValue == 1.0:
            print(i, i.varValue)
    
    print(value(prob.objective))
    print('flow caught: ', value(sum(betas[i,k-1]*v2[i][k-1] for i in range(n) for k in K_i[i+1])))

    return prob

if __name__ == '__main__':
    ### necessary inputs to run the exact MDP model:

    import networkx as nx

    sys.path.insert(1, "C:/Users/Anne-Fleur/OneDrive - Noria/Documents - Noria Internship/Anne Fleur/1. Working Folder/3. GIS/Network FCLM/thesis_noria/spyder scripts")

    import network_creation
    import transition_probabilities_wind
    import init_probability

    ### TEST DELFT
    np.random.seed(1)

    # import the networkx graph from network_creation.py, get transition probabilities and initial probabilities
    G = network_creation.create_network()
    transition_probabilities_wind.get_transition_probabilities(G)
    init_probability.get_initial_probabilities(G)
    init_probability.get_stuck_probabilities(G)

    b = np.array([G.nodes[node]['init_probability'] for node in G.nodes()])

    n = len(G.nodes())
    K = 2

    stuck = [G.nodes[node]['stuck_probability'] for node in G.nodes()]
    # stuck = np.random.uniform(0.0, 0.6, n)
    stuck_matrix = np.repeat([stuck], len(stuck), axis = 0).T

    A = nx.adjacency_matrix(G, nodelist = G.nodes(), weight = 'transition_probability').toarray()

    ###random values but same adjacency matrix
    # A = nx.adjacency_matrix(G, nodelist = G.nodes(), weight = None).toarray()
    # A = np.random.uniform(0, 0.3, np.shape(A))*A
    # A = np.random.uniform(0, 1, np.shape(A))
    # row_sums = A.sum(axis=1)
    # A = A / row_sums[:, np.newaxis]


    C = (1-stuck_matrix) * A

    attrs = {}
    for index, node in enumerate(G.nodes()):
        attrs[node] = {'label': index+1, 'position' : node}
    nx.set_node_attributes(G, attrs)

    ### instance parameters

    no_system = init_probability.no_catching_system()
    ### later proberen met sets K_i
    K_i = {}
    for node in G.nodes():
        if node in no_system:
            K_i[G.nodes[node]['label']] = {}
        else:
            K_i[G.nodes[node]['label']] = {1, 2}

    betas = np.random.uniform(0.1, 0.8, (n, K))
    c_1 = 1
    B = 10.5
    alpha = 0

    #%%

    # n = 6
    # K = 2
    
    # K_i = {}
    # for i in range(1,7):
    #     K_i[i] = {1,2} #try with two types of catching systems later
    #     if i == 5:
    #         K_i[i] = {}

    # np.random.seed(0)
    # betas = np.random.uniform(0.1, 0.8, (n, K))
    # alpha = 0.1
    # c_1 = 1
    # B = 1.5
    
    # Q = np.zeros((7,7));
    # indices = [[0, 0], [1, 0], [2, 1], [3, 4], [4, 5], [5, 2], [6, 5]]
    # for i in indices:
    #     Q[i[0], i[1]] = 1
    
    # C = Q[1:, 1:]
    
    
    # b = np.array([0, 0, 0.6, 0, 0, 0.4]) #should this include 0 and n+1?

    #%%
    prob = solve_MDP(n, K, K_i, betas, alpha, C, b, c_1, B)
