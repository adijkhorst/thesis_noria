# -*- coding: utf-8 -*-
"""
Created on Thu Feb  1 14:39:46 2024

@author: Anne-Fleur
"""

from pulp import *
import networkx as nx
import numpy as np

def solve_MDP(G, n, K, K_i, betas, alpha, C, b, c, B, w, show_impact_flow = False, init_solution = [], warm_start = False, without_gurobi = False, time_limit = None):
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

    ### if warm start is true, set x variables equal to init_solution
    if warm_start == True:
        for i in range(n):
            for k in range(K):
                xs[i][k].setInitialValue(init_solution[i][k])

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

    ### create objective function
    obj_function = sum(betas[i,k]*v2[i][k] for i in range(n) for k in range(K)) \
                - w *sum(sum(c[k] * xs[i][k] for k in range(K)) for i in range(n))  \
                - sum(alpha[i]*v for i, v in enumerate(v1)) \
                - sum(alpha[i]*sum((1-betas[i, k])*v2[i][k] for k in range(K)) for i in range(n))
    prob += obj_function

    ### solve
    if without_gurobi == False:
        # status = prob.solve(GUROBI_CMD(keepFiles=True, warmStart = warm_start, options = [('LogToConsole', 1)]))
        status = prob.solve(GUROBI(mip = True, msg = False, timeLimit = time_limit, warmStart = warm_start))
        # status = prob.solve(CPLEX_PY(warmStart = warm_start))
    else:
        # status = prob.solve()
        # status = prob.solve(GLPK_CMD())
        status = prob.solve(PULP_CBC_CMD(msg = False, timeLimit=time_limit, warmStart = warm_start))

    print('Solution is: ', LpStatus[status])

    solution_nodes = []
    print('Catching systems located at:')
    for i in prob.variables():
        if i.varValue == 1.0:
            print(i, i.varValue)
            solution_nodes += [[int(str(i)[1:-1]), int(str(i)[-1])]]
    
    print(value(prob.objective))
    flow_caught = value(sum(betas[i,k]*v2[i][k] for i in range(n) for k in range(K)))
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
    x = [[round(value(xik)) for xik in xi] for xi in xs]
    
    print('Solution time: ', prob.solutionTime)
    
    if show_impact_flow == True:
        impact_area = n*[False]
        impact_area_flow = 0
        for index, node in enumerate(G.nodes()):
            if G.nodes[node]['impact_factor'] > 0.0:
                impact_area_flow = impact_area_flow + value(v1[index]) + sum((1-betas[index][k])*value(v2[index][k]) for k in range(K))
                impact_area[index] = True
        return prob, G, solution_nodes, flow_caught, impact_area_flow, x
    else:
        return prob, G, solution_nodes, flow_caught, 0, x