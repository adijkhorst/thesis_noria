# -*- coding: utf-8 -*-
"""
Created on Wed Apr  3 20:51:45 2024

@author: Anne-Fleur
"""

from pulp import *
import networkx as nx
import numpy as np
import time
import MDP_exact

sys.path.insert(1, "C:/Users/Anne-Fleur/OneDrive - Noria/Documents - Noria Internship/Anne Fleur/1. Working Folder/3. GIS/Network FCLM/thesis_noria/spyder scripts")
import load_instance


def fixed_solution_caught_flow(G, n, K, K_i, betas, alpha, C, b, c, B, w, x_fixed):
    #(number_nodes, number_catching_systems, possible_catching_systems, catching_probabilities, impact_factor, transition_matrix, initial_distribution, costs, budget):
    prob = LpProblem("MDP-FCLM", LpMaximize)

    M1 = b.T @ np.linalg.inv(np.eye(n)-C)
    M2 = np.zeros((n,K))
    for i in range(n):
        for k in range(K):
            diagB = np.eye(n)
            diagB[i,i] = 1 - betas[i,k]
            M2[i,k] = (b.T @ np.linalg.inv(np.eye(n)- diagB @ C))[i]

    ## create variables for all locations
    xs = [[LpVariable("x{}{}".format(i+1, j+1), cat="Binary") for j in range(K)] for i in range(n)] #look at indices +1!
    v1 = [LpVariable("v{}1".format(i+1), 0) for i in range(n)]
    v2 = [[LpVariable("v{}{}2".format(i+1, j+1), 0) for j in range(K)] for i in range(n)] #look at indices +1!

    ### create constraints
    for i in range(n):
        prob += v1[i] + sum(v2[i]) - sum(C[j,i] * v1[j] for j in range(n)) \
            - sum(sum((1-betas[j,k])*C[j,i]*v2[j][k] for k in range(K)) for j in range(n)) == b[i]
    
        prob += v1[i] <= (1-sum(xs[i][k] for k in range(K))) * M1[i]
    
        for k in range(K):
            prob += v2[i][k] <= M2[i]*xs[i][k]

        prob += sum(xs[i][k-1] for k in range(K)) <= 1

        # some catching systems equal to zero
        setK = set(range(1, 1+K))

        for k in setK - set(K_i[i+1]):
            prob += xs[i][k-1] == 0

    prob += sum(sum(c[k] * xs[i][k] for k in range(K)) for i in range(n)) <= B

    ### constraint for fixed xs
    for i in range(n):
        for k in range(K):
            prob += xs[i][k] == x_fixed[i][k]

    ### create objective function
    obj_function = sum(betas[i,k]*v2[i][k] for i in range(n) for k in range(K)) \
                - w *sum(sum(c[k] * xs[i][k] for k in range(K)) for i in range(n))  \
                - sum(alpha[i]*v for i, v in enumerate(v1)) \
                - sum(alpha[i]*sum((1-betas[i, k])*v2[i][k] for k in range(K)) for i in range(n))
    prob += obj_function

    ### solve
    status = prob.solve(GUROBI_CMD(keepFiles=True, options = [('LogToConsole', 1)]))
    # status = prob.solve()

    print('Solution is: ', LpStatus[status])

    solution_nodes = []
    print('Catching systems located at:')
    for i in prob.variables():
        if i.varValue == 1.0:
            print(i, i.varValue)
            solution_nodes += [[int(str(i)[1:-1]), int(str(i)[-1])]]
    
    print(value(prob.objective))
    flow_caught = value(sum(betas[i,k-1]*v2[i][k-1] for i in range(n) for k in K_i[i+1]))
    print('flow caught: ', flow_caught)

    ### give nodes that are in the solution an attribute
    mapping = {key: index+1 for index, key in enumerate(G.nodes.keys())}
    inv_map = {v: k for k, v in mapping.items()}

    solution_attrs = {}
    for sol in solution_nodes:
        solution_attrs[inv_map[sol[0]]] = {'catching_system_type': int(sol[1])}
    nx.set_node_attributes(G, solution_attrs)

    flow_attrs = {}
    for index, node in enumerate(G.nodes()):
        flow_attrs[node] = {'plastic_flow': M1[index]}
    nx.set_node_attributes(G, flow_attrs)

    return prob, G, solution_nodes, flow_caught

if __name__ == '__main__':
    G, n, K, K_i, betas, alpha, C, b, c, B, w = load_instance.MIP_input(2022, 100, random_wind = False)

    output = []
    for B in np.arange(0.2, 4.2, 0.2):
        start = time.time()
        _, _, _, _, x_fixed = MDP_exact.solve_MDP(G, n, K, K_i, betas, alpha, C, b, c, B, w, show_solution = True)
        end = time.time()
        output += [x_fixed]

    with open('308nodes_fixed_solutions.txt', 'w+') as f:
    # with open('without_gurobi'+str(n)+'nodes.txt', 'w+') as f:
        # write elements of list
        for items in output:
            f.write('%s\n' %items)
        print("File written successfully")
    f.close()