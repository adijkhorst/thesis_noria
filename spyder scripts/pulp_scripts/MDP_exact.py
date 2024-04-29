# -*- coding: utf-8 -*-
"""
Created on Thu Feb  1 14:39:46 2024

@author: Anne-Fleur
"""

from pulp import *
import networkx as nx
import numpy as np

def solve_MDP(G, n, K, K_i, betas, alpha, C, b, c, B, w, show_impact_flow = False, init_solution = [], warm_start = False, without_gurobi = False):
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
        status = prob.solve(GUROBI(mip = True, msg = False, warmStart = warm_start))
        # status = prob.solve(CPLEX_PY(warmStart = warm_start))
    else:
        # status = prob.solve()
        # status = prob.solve(GLPK_CMD())
        status = prob.solve(PULP_CBC_CMD(msg = False, warmStart = warm_start))

    print('Solution is: ', LpStatus[status])

    solution_nodes = []
    print('Catching systems located at:')
    for i in prob.variables():
        if i.varValue == 1.0:
            print(i, i.varValue)
            solution_nodes += [[int(str(i)[1:-1]), int(str(i)[-1])]]
    
    print(value(prob.objective))
    # flow_caught = value(sum(betas[i,k-1]*v2[i][k-1] for i in range(n) for k in K_i[i+1]))
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


if __name__ == '__main__':
    ### necessary inputs to run the exact MDP model:

    sys.path.insert(1, "C:/Users/Anne-Fleur/OneDrive - Noria/Documents - Noria Internship/Anne Fleur/1. Working Folder/3. GIS/Network FCLM/thesis_noria/spyder scripts")

    import network_creation
    import transition_probabilities_wind
    import init_probability

    # ### TEST DELFT
    # np.random.seed(1)

    # year = 2022

    # # import the networkx graph from network_creation.py, get transition probabilities and initial probabilities
    # G = network_creation.create_network()
    # transition_probabilities_wind.get_transition_probabilities(G, year)
    # init_probability.get_initial_probabilities(G)
    # init_probability.get_stuck_probabilities(G)

    # b = np.array([G.nodes[node]['init_probability'] for node in G.nodes()])

    # n = len(G.nodes())
    # K = 2

    # stuck = [G.nodes[node]['stuck_probability'] for node in G.nodes()]
    # stuck_matrix = np.repeat([stuck], len(stuck), axis = 0).T

    # A = nx.adjacency_matrix(G, nodelist = G.nodes(), weight = 'transition_probability').toarray()

    # C = (1-stuck_matrix) * A

    # attrs = {}
    # for index, node in enumerate(G.nodes()):
    #     attrs[node] = {'label': index+1, 'position' : node}
    # nx.set_node_attributes(G, attrs)

    # ### instance parameters

    # no_system = init_probability.no_catching_system()
    # K_i = {}
    # for node in G.nodes():
    #     if node in no_system:
    #         K_i[G.nodes[node]['label']] = {}
    #     else:
    #         K_i[G.nodes[node]['label']] = {1, 2}

    # betas = np.random.uniform(0.1, 0.8, (n, K))
    # c = [1, 1]
    # B = 8.5
    # w = 0.001
    # # alpha = 0.001*np.ones(n)
    # alpha = np.zeros(n)
    # alpha = np.random.uniform(0.001, 0.01, n)
    # alpha = np.ones(n)*0.1


    #%%
    # import time
    # start = time.time()
    # prob, G, solution, flow_caught, impact_area_flow = solve_MDP(G, n, K, K_i, betas, alpha, C, b, c, B, w)

    # end = time.time()
    # print('runtime for ', B, ' catching systems', end-start)

    #%%
    import load_instance

    for dist in [50, 75, 100, 125, 150]:
        year = 2022
        G, n, K, K_i, betas, alpha, C, b, c, B, w = load_instance.MIP_input(year, dist)
        B = 0
        prob, G, solution_nodes, flow_caught, _, _ = solve_MDP(G, n, K, K_i, betas, alpha, C, b, c, B, w)
        nx.write_gml(G, str(n)+'nodes.gml')

    #%% testing caught flow per catching system to check if value of w works correctly
    # test = []
    # for i in range(n):
    #     for k in range(K):
    #         if value(xs[i][k]) > 0:
    #             test += [betas[i][k]*value(v2[i][k])]
    #             print(betas[i][k]*value(v2[i][k]), betas[i][k]*M2[i][k])
    # test.sort()