# -*- coding: utf-8 -*-
"""
Created on Tue Dec 12 13:34:38 2023

@author: Anne-Fleur
"""

import numpy as np

b = np.array([[0.8],[0.2]])
# b = np.random.random((2,1))
# b /= np.sum(b)

C_x = np.array([[0, 0.7], [0.5, 0]])
C = np.array([[0,0.7],[1, 0]])
c_n1 = np.array([[0],[0.5]])


### if beta = 1 then:
# C_x = np.array([[0, 0.7], [0, 0]])
# C = np.array([[0,0.7],[1, 0]])
# c_n1 = np.array([[0],[1]])

fundamental_matrix = np.linalg.inv(np.eye(2)-C_x)

z = b.T @ np.linalg.inv(np.eye(2)-C_x)

Mi1= b.T @ np.linalg.inv(np.eye(2)-C)


flow_intercepted = b.T @ np.linalg.inv(np.eye(2)-C_x) @ c_n1

A = np.zeros((2,2))
for n in range(100):
    A += np.linalg.matrix_power(C_x, n)