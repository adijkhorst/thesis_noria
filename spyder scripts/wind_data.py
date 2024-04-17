# -*- coding: utf-8 -*-
"""
Created on Fri Nov 17 13:37:32 2023

@author: Anne-Fleur
"""
import pandas as pd
import matplotlib.pyplot as plt
import os

def get_wind_directions(year):
    ### adjust later such that year and file are inputs to the function!!!
    weather_data_path = 'C:/Users/Anne-Fleur/OneDrive - Noria/Documents - Noria Internship/Anne Fleur/1. Working Folder/6. Model/etmgeg_344.txt'
    dirname = os.path.dirname(__file__)
    weather_data_path = dirname + '\etmgeg_344.txt'
    # weather_data_path = os.path.normpath(os.path.join(dirname, '\etmgeg_344.txt'))
    
    
    
    df = pd.read_csv(weather_data_path, skiprows=50)
    
    min_date = int(str(year)+'0101')
    max_date = int(str(year)+'1231')
    
    df = df.loc[df['YYYYMMDD'] >= min_date]
    df = df.loc[df['YYYYMMDD'] <= max_date]
    df = df.loc[df['DDVEC'] > 0] #only consider days where direction was not calm/variable

    df['DDVEC'] = df['DDVEC'].astype(float)

    wind_directions = df['DDVEC'].to_numpy()

    return (wind_directions + 180) % 360 #convert to direction where wind is blowing for later calculations

if __name__ == '__main__':
 
    for year in [2020, 2021, 2022, 2023]:
        wind_directions = get_wind_directions(year)
        plt.figure()
        hist = plt.hist(wind_directions, bins = 20)