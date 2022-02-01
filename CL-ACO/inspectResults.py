# -*- coding: utf-8 -*-
"""
Created on Mon Jan 17 03:14:11 2022

Import & display previously computed results

@author: eirene
"""

import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import scipy.stats as st

src = 'C:/Users/fried/AppData/Local/Packages/CanonicalGroupLimited.UbuntuonWindows_79rhkp1fndgsc/LocalState/rootfs/home/eirene/CL-ACO/'

outputfile = '01-02-2022_00-57_scenario_1'  # example  

#1330162044

# %%

def getResults(src, outputfile, distr_plot=False, ci_plot=False):

    src_results = src+f'OUTPUT/{outputfile}/'
    results = pd.read_pickle(src_results+"all/costs.obj")
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
        
    best_costs = pd.read_pickle(src_results+"best/best_costs.obj")
    best_routes = pd.read_pickle(src_results+"best/best_route_names.obj")

    routes = pd.read_pickle(src_results+"all/routes_names.obj")
    costs = pd.read_pickle(src_results+"all/costs.obj")
    
    if distr_plot == True:
        for method in results.keys():
            plt.hist(costs[method], bins = 20, label = method)
            plt.legend(loc=1, prop={'size': 7})
    
    if ci_plot == True:
    
        for method in results.keys():
            ranges = []
            for n in range(2,20):
                CI_borders, CI_range = CI(n, method)
                ranges.append(CI_range)                
            x = range(2,len(ranges)+2)
            y = ranges
            plt.plot(x, y, label = method)
            plt.legend(loc=1, prop={'size': 7})
                   
    return best_costs, best_routes, routes, costs

#%%

best_costs, best_routes, routes, costs = getResults(src, outputfile, 
                                                    distr_plot=True
                                                    )


