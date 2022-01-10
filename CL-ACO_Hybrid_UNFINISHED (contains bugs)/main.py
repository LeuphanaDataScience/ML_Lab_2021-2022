# -*- coding: utf-8 -*-
"""
Created on Tue Dec 28 21:43:33 2021

Main File ACO-Clustering

@author: eirene
"""

# %% Import modules & functions

import os
import pickle
import pandas as pd
import time
import math as mt
import warnings
import shutil
import geopandas as gp

warnings.filterwarnings("ignore") # don't print warnings

os.chdir(os.path.dirname(os.path.realpath(__file__)))

from data_prep import dataprep_CL, dataprep_ACO, exportClusters, namedRoute
from Clustering import runCluster 
from ACO import runACO 

# %% Combined functions

def runClusterACO(src, 
                  scenario, 
                  capacity, 
                  method, 
                  iteration,
                  new_result_dir,
                  single_run=False, 
                  previous_run=False, 
                  named=True):

    ### (1) Clustering step ###
    
    '''
    Don't (re-)calculate clustering if
        -   previously computed results are used
        -   deterministic clustering is used & the clustering has been 
            calculated previously for that 
    '''
    
    # Data pre-processing
    matrix, distances_to_arena, bus_names, inputFile = dataprep_CL(src, scenario)
    oC_dict_clusters = runCluster(src, method, scenario, capacity)  
#    oC_df_clusters = exportClusters(src, oC_dict_clusters, inputFile, method, purpose = "tmp")

    '''
    # Create/ load clusterings
    if previous_run==False:
        if method.endswith("random") or iteration==0: # -> do clustering
            oC_dict_clusters = runCluster(src, method, scenario, capacity)  
            oC_df_clusters = exportClusters(src, oC_dict_clusters, inputFile, method, purpose = "tmp")
        
        else: # -> load clustering from previous iteration
            oC_df_clusters = pd.read_csv(src + f'/tmp/tmp_{method}.csv' )
  
    else:
         oC_df_clusters = pd.read_csv(src + f'results/{previous_run}/best/best_clusters_{method}.csv')
         oC_df_clusters.to_csv(src+ f'/tmp/tmp_{method}.csv')
    '''
    
    # -------------------------------------------------------------------------

    ### (2) ACO step ###
    
    # Data pre-processing
    iA_dict_clusters, iA_df_clusters = dataprep_ACO(matrix, oC_df_clusters) 
        
    # Let the ants run!
    best_routes_all_clusters, total_cost_all_clusters = runACO(iA_dict_clusters, iA_df_clusters)

    # Create dataframe with named stations    
    if named == True:
        best_routes_all_clusters = namedRoute(best_routes_all_clusters, iA_dict_clusters)

    # -------------------------------------------------------------------------
    
    return best_routes_all_clusters, total_cost_all_clusters, iA_dict_clusters, iA_df_clusters, oC_dict_clusters, oC_df_clusters, inputFile
    

def Run(src, 
        iterations, 
        scenario, 
        capacity, 
        methods, 
        random_only = False, 
        previous_run=False, 
        overall=True,
        testing=False):
        
    
    # Automatically (re-)define variables
    if random_only == True:
        methods = methods[0:3]  
    if testing == True:
        iterations = 2
        methods = methods[0:1]   
      
    T_initial = time.time()                 # for displaying progress
 
    # Create folder for new results
    time_now = time.localtime() 
    time_string = time.strftime("%d-%m-%Y_%H-%M", time_now)
    
    if previous_run == False:    
        new_result_dir = src+f'results/{time_string}/'    
    if previous_run != False:
        new_result_dir = src+f'results/{time_string}_refined_{previous_run}/'

    # Delete directory if it is already existent...
    if os.path.isdir(new_result_dir):
        shutil.rmtree(new_result_dir)
    # ... for being able to create new one    
    os.makedirs(new_result_dir)
    os.makedirs(new_result_dir+'/best')
    
    # re-define methods based on those that were used previously 
    if previous_run != False:
        methods = []
        for file in os.listdir(src+"results/"+previous_run+"/best"):
            if overall == True:
                if file.startswith("best_clusters_overall"):
                    filename = file
                    methods.append(filename[23:-5])
            else:
                if file.startswith("best_clusters") and not(file.startswith("best_clusters_overall")):
                    filename = file
                    methods.append(filename[14:-4])
    
    # initialize variables
    routes = {}
    costs = {}
    clusters = {}
    comp_time = {}
    
    best_routes = []
    best_costs_method = int(99999999999999)
    best_costs = int(99999999999999)
    
    its_total = len(methods)*iterations
    

    # Run for selected methods & iterations
   
    for i in range(0, len(methods)):
     
        # initialize variables
        best_costs_method = int(99999999999999)    
        
        costs[i] = []
        routes[i] = []
        comp_time[i] = []
        clusters[i] = []
        
        for j in range(0,iterations):
    
            # To display progress         
            T_now = time.time()
            T_passed = T_now - T_initial
            print(f'Current method: {methods[i]} (Method {i+1}/{len(methods)}), \nIteration {j+1}/{iterations}')              
            if T_passed >= 1:
                its = i*iterations+j
                time_per_it = mt.floor(T_passed/(its))
                time_left = time_per_it*(its_total-its)
                print(f'Time passed: {mt.floor(T_passed)}s ({time_per_it}s/iteration)')
                print(f'Estimated time left: {mt.floor(time_left/60)} minutes')
        
            t0 = time.time()  
            
            # This is the main step:            
            route, cost, dict_clusters2, inputFile2, dict_clusters, inputFile = runClusterACO(   
                src,
                scenario, 
                capacity,
                methods[i],
                j,
                new_result_dir)
            
            t1 = time.time()
            ET = t1-t0
            
            # add current results to result dictonary
            costs[i].append(cost)
            routes[i].append(route)
            clusters[i].append(clusters)
            comp_time[i].append(ET)
    
            # to find best solution for cluster method
            if cost < best_costs_method:
                best_costs_method = cost
                best_routes_method = route
         #       exportClusters(new_result_dir,
         #                      dict_clusters, 
         #                      inputFile, 
         #                      methods[i], 
         #                      purpose = "best_method")
                
            # to find best solution
            if cost < best_costs:
                best_costs = cost
                best_routes = route
                best_dict_clusters = dict_clusters
                best_inputFile = inputFile
                best_method = methods[i]
                                 
        # export results        
        if testing != False:
            current_result_dir = src+'results/mostRecent'
            if os.path.isdir(current_result_dir):
                shutil.rmtree(current_result_dir)
            os.makedirs(current_result_dir)
            os.makedirs(current_result_dir+'best')
            filehandler = open(current_result_dir+f'/best/best_costs_{methods[i]}.obj', 'wb')
            pickle.dump(best_costs_method, filehandler)
            filehandler = open(current_result_dir+f'/best/best_routes_{methods[i]}.obj', 'wb')
            pickle.dump(best_routes_method, filehandler)
        
        filehandler = open(new_result_dir+f'best/best_costs_{methods[i]}.obj', 'wb')
        pickle.dump(best_costs_method, filehandler)
        filehandler = open(new_result_dir+f'best/best_routes_{methods[i]}.obj', 'wb')
        pickle.dump(best_routes_method, filehandler)

                      
            
    # save other results outside python
    filehandler = open(new_result_dir+"costs.obj", 'wb')
    pickle.dump(costs, filehandler)
    
    filehandler = open(new_result_dir+"/routes.obj", 'wb')
    pickle.dump(routes, filehandler)
    
    filehandler = open(new_result_dir+"/comp-time.obj", 'wb')
    pickle.dump(comp_time, filehandler)
    
    filehandler = open(new_result_dir+"/best/best_costs.obj", 'wb')
    pickle.dump(best_costs, filehandler)
    
    filehandler = open(new_result_dir+"/best/best_routes.obj", 'wb')
    pickle.dump(best_routes, filehandler)
    
 #   exportClusters(best_dict_clusters, best_inputFile, 
 #                  new_result_dir, best_method, purpose = "best_overall")

#%%
# Displaying results

'''

def getResults():
    # Move content from last results folder in "current_results"

    src_results = src+"/current_results"
    results = pd.read_pickle(src_results+"/costs.obj")
    print("Mean distance")
    for i in range(0,len(methods)):        
        print(f'{methods[i]} : {np.mean(results[i])}')
    print("\nMinimum distance")
    for i in range(0,len(methods)):
        print(f'{methods[i]} : {np.min(results[i])}')
    print("\nMaximum distance")
    for i in range(0,len(methods)):
        print(f'{methods[i]} : {np.max(results[i])}')        
    print("\nStandard Deviation")
    for i in range(0,len(methods)):
        print(f'{methods[i]} : {np.std(results[i])}')        

    best_costs = pd.read_pickle(src_results+"/best/best_costs.obj")
    best_routes = pd.read_pickle(src_results+"/best/best_routes_CONVEX_HULL_SEQUENCE_random.obj")
    routes = pd.read_pickle(src_results+"/routes.obj")
    costs = pd.read_pickle(src_results+"/costs.obj")
    
    return best_costs, best_routes, routes, costs

src_results_prev = src+"/current_results"
src_results = new_result_dir

if cluster == False:
    results_new = pd.read_pickle(src_results+"/costs.obj")
    results = pd.read_pickle(src_results_prev+"/costs.obj")
    print("Mean distance")
    for i in range(0,len(methods)):        
        print(f'{methods[i]} (new): {np.mean(results_new[i])}')
        print(f'{methods[i]} (old): {np.mean(results[i])}')
    print("\nMinimum distance")
    for i in range(0,len(methods)):
        print(f'{methods[i]} (new): {np.min(results_new[i])}')
        print(f'{methods[i]} (old): {np.min(results[i])}')
    print("\nMaximum distance")
    for i in range(0,len(methods)):
        print(f'{methods[i]} (new): {np.max(results_new[i])}') 
        print(f'{methods[i]} (old): {np.max(results[i])}')        
    print("\nStandard Deviation")
    for i in range(0,len(methods)):
        print(f'{methods[i]} (new): {np.std(results_new[i])}')   
        print(f'{methods[i]} (old): {np.std(results[i])}')    

best_costs = pd.read_pickle(src_results+"/best/best_costs.obj")
best_routes = pd.read_pickle(src_results+"/best/best_routes_CONVEX_HULL_SEQUENCE_random.obj")
routes = pd.read_pickle(src_results+"/routes.obj")
costs = pd.read_pickle(src_results+"/costs.obj")
'''