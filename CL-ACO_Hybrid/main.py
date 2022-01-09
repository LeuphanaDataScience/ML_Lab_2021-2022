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

warnings.filterwarnings("ignore") # don't print warnings

os.path.dirname(os.path.realpath(__file__))

#if cluster == False:
#    os.chdir(src)

from data_prep import dataprep_CL, dataprep_ACO, exportClusters, namedRoute
from Clustering import runCluster 
from ACO import runACO 

# %% Combined functions

def runClusterACO(src, 
                  inputScenario, 
                  capacity, 
                  method, 
                  single_run=False, 
                  previous_run=False, 
                  named=True):

    if previous_run==False:
        
    ### (1) Clustering step ###
    
        # Data pre-processing: import df including no. of passengers assigned to stations
        inputScenario = pd.read_csv(inputScenario)
        matrix, distances_to_arena, bus_names, bus_stops_df = dataprep_CL(src+"/data/", inputScenario)

        # Create clusters
        dict_clusters_CL, df_clusters_CL = runCluster(method, src, inputScenario, capacity)
 
        # export results (will be used in the next step by ACO)
        exportClusters(dict_clusters_CL, df_clusters_CL, src, method)
    
    # -------------------------------------------------------------------------

    ### (2) ACO step ###
    
    # Data pre-processing
    dict_clusters, df_clusters, df_clusters_raw = dataprep_ACO(src, method)
    
    
    # To improve results, run ACO for just a specific clustering (that gave best result)
    if previous_run != False: 
        # Data pre-processing
        dict_clusters, df_clusters, df_clusters_raw = dataprep_ACO(src, previous_run=previous_run)
        
    # Let the ants run!
    best_routes_all_clusters, total_cost_all_clusters = runACO(dict_clusters, df_clusters)

    # Create dataframe with named stations    
    if named == True:
        best_routes_all_clusters = namedRoute(best_routes_all_clusters, dict_clusters)

    # -------------------------------------------------------------------------
    
    ### (3) Export the results

    # export the results if number of iterations = 1 (only single run)
    if single_run == True:
        dict_routes = best_routes_all_clusters
        filehandler = open(src+"/data/dict_routes_"+method+".obj", 'wb')
        pickle.dump(dict_routes, filehandler)    
        dict_routes_names = best_routes_all_clusters
        filehandler = open(src+"/data/dict_routes_names_"+method+".obj", 'wb')
        pickle.dump(dict_routes_names, filehandler)

    return best_routes_all_clusters, total_cost_all_clusters, dict_clusters, df_clusters, df_clusters_CL, dict_clusters_CL
    

def Run(src, 
        iterations, 
        Scenario, 
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

    inputScenario = src+"/data/"+Scenario        
    T_initial = time.time()                 # for displaying progress
 
    # Create folder for new results
    time_now = time.localtime() 
    time_string = time.strftime("%d-%m-%Y_%H-%M", time_now)
    
    if previous_run == False:    
        new_result_dir = src+f'/results/{time_string}'    
    if previous_run != False:
        new_result_dir = src+f'/results/{time_string}_refined_{previous_run}'

    if os.path.isdir(new_result_dir):
        shutil.rmtree(new_result_dir)
    os.makedirs(new_result_dir)
    os.makedirs(new_result_dir+'/best')
    
    # re-define methods based on those that were used previously 
    if previous_run != False:
        methods = []
        for file in os.listdir(src+"/results/"+previous_run+"/best"):
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
            route, cost, dict_clusters, df_clusters, df_clusters_CL, dict_clusters_CL = runClusterACO(src,
                                                                                                      inputScenario, 
                                                                                                      capacity,
                                                                                                      methods[i])
            
            t1 = time.time()
            ET = t1-t0
            
            # add current results to result dictonary
            costs[i].append(cost)
            routes[i].append(route)
            clusters[i].append(clusters)
            comp_time[i].append(ET)
            
            exportClusters(dict_clusters_CL, df_clusters_CL, new_result_dir+"/best", methods[i], best = "method")
    
            # to find best solution for cluster method
            if cost < best_costs_method:
                best_costs_method = cost
                best_routes_method = route
                exportClusters(dict_clusters_CL, df_clusters_CL, new_result_dir+"/best", methods[i], best = "method")
                
            # to find best solution
            if cost < best_costs:
                best_costs = cost
                best_routes = route
                best_dict_clusters_CL = dict_clusters_CL
                best_df_clusters_CL = df_clusters_CL
                best_method = methods[i]
                                 
        # export results
        filehandler = open(new_result_dir+f'/best/best_costs_{methods[i]}.obj', 'wb')
        pickle.dump(best_costs_method, filehandler)
    
        filehandler = open(new_result_dir+f'/best/best_routes_{methods[i]}.obj', 'wb')
        pickle.dump(best_routes_method, filehandler)
                      
    
            
    # save other results outside python
    filehandler = open(new_result_dir+"/costs.obj", 'wb')
    pickle.dump(costs, filehandler)
    
    filehandler = open(new_result_dir+"/routes.obj", 'wb')
    pickle.dump(routes, filehandler)
    
    filehandler = open(new_result_dir+"/comp-time.obj", 'wb')
    pickle.dump(comp_time, filehandler)
    
    filehandler = open(new_result_dir+"/best/best_costs.obj", 'wb')
    pickle.dump(best_costs, filehandler)
    
    filehandler = open(new_result_dir+"/best/best_routes.obj", 'wb')
    pickle.dump(best_routes, filehandler)
    
    exportClusters(best_dict_clusters_CL, best_df_clusters_CL, new_result_dir+"/best", best_method, best = "overall")

#%%
# Displaying results
'''
def getResults():
    # Move content from last results folder in "current_results"

    src_results = src+"/current_results"

    if cluster == False:
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
'''
#%% Test Run

'''
if cluster == False:

    # Create clusters
    method = methods[9]
    dict_clusters, df_clusters = runCluster(method, src, Scenario, capacity)

    # export results
    exportClusters(dict_clusters, df_clusters, src, method) 

    # Data pre-processing
    dict_clusters, df_clusters, df_clusters_raw = dataprep_ACO(src, method)

    # Let the ants run!
    best_routes_all_clusters, total_cost_all_clusters = runACO(dict_clusters, df_clusters)

    # named 
    named_routes = namedRoute(best_routes_all_clusters, dict_clusters)

'''
#%%     Run ACO multiple times on "best cluster"

'''
# Set variables
iterations = 2
previous_run = "08-01-2022_03-40"
overall = False

methods = []

for file in os.listdir(src+"/results/"+previous_run+"/best"):
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

best_cluster = []
best_routes = []

best_costs_method = int(99999999999999)
best_costs = int(99999999999999)

its_total = len(methods)*iterations
T_initial = time.time()



# Create folder for new results
time_now = time.localtime() 
time_string = time.strftime("%d-%m-%Y_%H-%M", time_now)
new_result_dir = src+f'/results/{time_string}_RunACOBestCluster_{previous_run}'
os.makedirs(new_result_dir)
os.makedirs(new_result_dir+'/best')

# Run for selected methods & iterations

for i in range(0, len(methods)):
 
    # initialize variables
    best_costs_CL = int(99999999999999)    
    T1 = time.time()
    
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
        route, cost, dict_clusters, df_clusters, df_clusters_CL, dict_clusters_CL = runACO_bestCluster(methods[i], previous_run, capacity)
        
        t1 = time.time()
        ET = t1-t0
        
        # add current results to result dictonary
        costs[i].append(cost)
        routes[i].append(route)
        clusters[i].append(clusters)
        comp_time[i].append(ET)
        
        exportClusters(dict_clusters_CL, df_clusters_CL, new_result_dir+"/best", methods[i], best = "method")

        # to find best solution for cluster method
        if cost < best_costs_method:
            best_costs_method = cost
            best_routes_method = route
            exportClusters(dict_clusters_CL, df_clusters_CL, new_result_dir+"/best", methods[i], best = "method")
            
        # to find best solution
        if cost < best_costs:
            best_costs = cost
            best_routes = route
            best_dict_clusters_CL = dict_clusters_CL
            best_df_clusters_CL = df_clusters_CL
            best_method = methods[i]
                             
    # export results
    filehandler = open(new_result_dir+f'/best/best_costs_{methods[i]}.obj', 'wb')
    pickle.dump(best_costs_method, filehandler)

    filehandler = open(new_result_dir+f'/best/best_routes_{methods[i]}.obj', 'wb')
    pickle.dump(best_routes_method, filehandler)
            
    T2 = time.time()
    time_method = T2-T1         

        
# save other results outside python
filehandler = open(new_result_dir+"/costs.obj", 'wb')
pickle.dump(costs, filehandler)

filehandler = open(new_result_dir+"/routes.obj", 'wb')
pickle.dump(routes, filehandler)

filehandler = open(new_result_dir+"/comp-time.obj", 'wb')
pickle.dump(comp_time, filehandler)

filehandler = open(new_result_dir+"/best/best_costs.obj", 'wb')
pickle.dump(best_costs, filehandler)

filehandler = open(new_result_dir+"/best/best_routes.obj", 'wb')
pickle.dump(best_routes, filehandler)

exportClusters(best_dict_clusters_CL, best_df_clusters_CL, new_result_dir+"/best", best_method, best = "overall")


#%%

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