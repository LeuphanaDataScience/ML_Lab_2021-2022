# -*- coding: utf-8 -*-
"""
Created on Mon Jan 17 03:14:11 2022

Import & display previously computed results

@author: eirene
"""

import pandas as pd
import numpy as np
import os

src = 'C:/Users/fried/AppData/Local/Packages/CanonicalGroupLimited.UbuntuonWindows_79rhkp1fndgsc/LocalState/rootfs/home/eirene/CL-ACO_Hybrid/'

outputfile = '17-01-2022_21-20'  # example 


def getResults(src, outputfile):

    src_results = src+f'OUTPUT/{outputfile}/'
    results = pd.read_pickle(src_results+"costs.obj")
    print("Mean distance")
    for method in results.keys():        
        print(f'{method} : {np.mean(results[method])}')
    print("\nMinimum distance")
    for method in results.keys():
        print(f'{method} : {np.min(results[method])}')
    print("\nMaximum distance")
    for method in results.keys():
        print(f'{method} : {np.max(results[method])}')        
    print("\nStandard Deviation")
    for method in results.keys():
        print(f'{method} : {np.std(results[method])}')        
        
    for file in os.listdir(src_results+"best"):
        if file.startswith("best_costs"):
            best_costs = pd.read_pickle(src_results+"best/"+file)
        if file.startswith("best_routes"):
            best_routes = pd.read_pickle(src_results+"best/"+file)

    routes = pd.read_pickle(src_results+"routes.obj")
    costs = pd.read_pickle(src_results+"costs.obj")
    
    return best_costs, best_routes, routes, costs

#%%

best_costs, best_routes, routes, costs = getResults(src, outputfile)

