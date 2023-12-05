# -*- coding: utf-8 -*-
"""
Created on Fri Nov 17 15:09:03 2023

@author: Anne-Fleur
"""

import wind_data
import numpy as np

def get_transition_probabilities(edge_angle_deg):
    ### make code robust for errors with radians and degrees?
    wind_directions = wind_data.get_wind_directions()
    
    forward = 0
    backward = 0
    
    threshold = np.cos(80/360*2*np.pi)
    
    for direction in wind_directions:
        # print(direction)
        if direction != 0: #check for windless days
            innerproduct = np.cos((edge_angle_deg-direction)/180*np.pi)
            # print(innerproduct)
            if innerproduct > threshold:
                forward += 1
                # print('forward + 1')
            elif innerproduct < -threshold:
                backward += 1
                # print('backward + 1')
    
    # print(forward, backward)
    total = forward+backward
    forward_probability = forward/total
    backward_probability = backward/total
    return forward_probability, backward_probability

if __name__ == '__main__':
    for i in range(18):
        print(get_transition_probabilities(i*10))