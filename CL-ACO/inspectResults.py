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

outputfile = '29-01-2022_23-30_scenario_1'  # example  

#1330162044

# %%

def CI(n, method):
    
    # create confidence interval for population mean
    
    CI_borders = st.t.interval(alpha=0.95, df=n-1, 
                       loc=np.mean(costs[method]), 
                       scale=st.sem(costs[method]))
    CI_range = CI_borders[1] - CI_borders[0]
    return CI_borders, CI_range


def getResults(src, outputfile, distr_plot=False, ci_plot=False):

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
        
    for file in os.listdir(src_results+"best")[:-1]:
        if file.startswith("best_costs"):
            best_costs = pd.read_pickle(src_results+"best/"+file)
        if file.startswith("best_routes"):
            best_routes = pd.read_pickle(src_results+"best/"+file)

    routes = pd.read_pickle(src_results+"routes.obj")
    costs = pd.read_pickle(src_results+"costs.obj")
    
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
                                                  #  ci_plot=True,
                                                    distr_plot=True
                                                    )
#%%

src = 'C:/Users/fried/AppData/Local/Packages/CanonicalGroupLimited.UbuntuonWindows_79rhkp1fndgsc/LocalState/rootfs/home/eirene/CL-ACO/'
outputfile = '28-01-2022_16-45/'
src_results = src + "OUTPUT/"+ outputfile

costs = pd.read_pickle(src_results+"costs.obj")
routes = pd.read_pickle(src_results+"routes.obj")



