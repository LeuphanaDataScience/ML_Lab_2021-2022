# -*- coding: utf-8 -*-
"""
Created on Tue Dec 28 21:43:33 2021

Main File ACO-Clustering

@author: eirene
"""

# %% Variables to be defined

testing = True
cluster = False


Iterations = 10

if cluster == True:
    testing = False

if testing == True:
    cluster = False

if cluster == True:
    src = '.'  # root directory
else:
    src = "C:/Users/fried/AppData/Local/Packages/CanonicalGroupLimited.UbuntuonWindows_79rhkp1fndgsc/LocalState/rootfs/home/eirene/CL-ACO_Hybrid"
    src2 = "C:/Users/fried/AppData/Local/Packages/CanonicalGroupLimited.UbuntuonWindows_79rhkp1fndgsc/LocalState/rootfs/home/eirene/download/CL-ACO_Hybrid"




# Scenario (event)
Scenario = 'scenario_1.csv'

# Clustering: How many people should be in one cluster (bus capacity)
capacity = 70       

# Clustering: Methods
methods = ["CONVEX_HULL_CLOUD_random", "CONVEX_HULL_SEQUENCE_random",
           "CONVEX_HULL_CLOUD_distance", "CONVEX_HULL_SEQUENCE_distance"]           

# %% Import modules & functions

import os
import pickle
import pandas as pd
import numpy as np
import time

import warnings

warnings.filterwarnings("ignore") # don't print warnings

if cluster == False:
    os.chdir(src)

from data_prep import dataprep_CL, dataprep_ACO, exportClusters, namedRoute
from Clustering import convex_cloud_cluster, convex_a_star_cluster, convex_sequence_cluster
from ACO import run_all_clusters


# %% Clustering step

def runCluster(method):

    # Data pre-processing
    # import dataframe including number of passengers assigned to stations
    scenario = pd.read_csv(src+"/data/"+Scenario)
    matrix, distances_to_arena, bus_names, df_clusters_CL = dataprep_CL(src+"/data/", scenario)

    # Define some variables
    distances_to_arena_check = distances_to_arena.copy()  # list of possible stops
    bus_names_check = bus_names.copy()

    if method == "CONVEX_HULL_CLOUD_random":
        dict_clusters_CL = convex_cloud_cluster(df_clusters_CL , capacity,
                                                     distances_to_arena_check,
                                                     bus_names_check, matrix,
                                                     choice='random')
    elif method == "CONVEX_HULL_CLOUD_distance":
        dict_clusters_CL = convex_sequence_cluster(df_clusters_CL , capacity,
                                                        distances_to_arena_check,
                                                        bus_names_check, matrix,
                                                        choice='distance')
    elif method == "CONVEX_HULL_SEQUENCE_random":
        dict_clusters_CL = convex_sequence_cluster(df_clusters_CL , capacity,
                                                        distances_to_arena_check,
                                                        bus_names_check, matrix,
                                                        choice='random')
    
    elif method == "CONVEX_HULL_SEQUENCE_distance":
        dict_clusters_CL = convex_sequence_cluster(df_clusters_CL , capacity,
                                                        distances_to_arena_check,
                                                        bus_names_check, matrix,
                                                        choice='distance')

    elif method == "CONVEX_HULL_A_STAR_random":
        dict_clusters_CL = convex_a_star_cluster(df_clusters_CL , capacity,
                                                      distances_to_arena_check,
                                                      bus_names_check, matrix, k=3,
                                                      choice='random')

    elif method == "CONVEX_HULL_A_STAR_distance":
        dict_clusters_CL = convex_a_star_cluster(df_clusters_CL , capacity,
                                                      distances_to_arena_check,
                                                      bus_names_check, matrix, k=3,
                                                      choice='distance')

    return dict_clusters_CL, df_clusters_CL


# %% Combined function


def runClusterACO(method):

    ### (1) Clustering step ###
    
    # Data pre-processing
    # import dataframe including number of passengers assigned to stations
    scenario = pd.read_csv(src+"/data/"+Scenario)
    matrix, distances_to_arena, bus_names, bus_stops_df = dataprep_CL(src+"/data/", scenario)
    # Create clusters
    dict_clusters_CL, df_clusters_CL = runCluster(method)
    # export results
    exportClusters(dict_clusters_CL, df_clusters_CL, src+"/data", method)

    # -------------------------------------------------------------------------


    ### (2) ACO step ###
    
    # Data pre-processing
    dict_clusters, df_clusters, df_clusters_raw = dataprep_ACO(src, method)
    
    # Let the ants run!
    best_routes_all_clusters, total_cost_all_clusters = run_all_clusters(dict_clusters, df_clusters)
    
    # create dataframe with named stations
    best_routes_all_clusters_names = namedRoute(best_routes_all_clusters, dict_clusters)
    
    # save the dictonaries in a pickles
    dict_routes = best_routes_all_clusters
    filehandler = open(src+"/pickles/dict_routes_"+method+".obj", 'wb')
    pickle.dump(dict_routes, filehandler)    
    dict_routes_names = best_routes_all_clusters_names
    filehandler = open(src+"/pickles/dict_routes_names_"+method+".obj", 'wb')
    pickle.dump(dict_routes_names, filehandler)

    # -------------------------------------------------------------------------

    return best_routes_all_clusters_names, total_cost_all_clusters, dict_clusters, df_clusters, df_clusters_CL, dict_clusters_CL
    
# %% Run multiple times to determine best clustering method & solution
# (might take long depending on iterations)

if testing == True:
    methods = ["CONVEX_HULL_CLOUD_random"]
    iterations = 1
else:    
    methods = ["CONVEX_HULL_CLOUD_random", "CONVEX_HULL_SEQUENCE_random",
               "CONVEX_HULL_CLOUD_distance", "CONVEX_HULL_SEQUENCE_distance"]
    iterations = Iterations

# initialize variables
routes = {}
costs = {}
clusters = {}
comp_time = {}

best_cluster = []
best_routes = []
best_costs = int(99999999999999)


for i in range(0, len(methods)):
    
    T1 = time.time()
    
    # initiate some variables in dictonaries
    costs[i] = []
    routes[i] = []
    comp_time[i] = []
    clusters[i] = []
    
    for j in range(0,iterations):
        seconds = time.time()
        print(f'{methods[i]} (Method {i+1}/{len(methods)}), Iteration {j+1}/{iterations} Time: {time.ctime(seconds)}')       
        t0 = time.time()  
        
        # This is the main step:
        route, cost, dict_clusters, df_clusters, df_clusters_CL, dict_clusters_CL = runClusterACO(methods[i])
        
        t1 = time.time()
        ET = t1-t0
        
        # add current results to result dictonary
        costs[i].append(cost)
        routes[i].append(route)
        clusters[i].append(clusters)
        comp_time[i].append(ET)
        
        # to find best solution
        if cost < best_costs:
            best_costs = cost
            best_routes = routes
            best_cluster = df_clusters
            exportClusters(dict_clusters_CL, df_clusters_CL, src, methods[i], best = True)
            
    T2 = time.time()
    time_method = T2-T1
    
    print(f'Running {iterations} Iterations for method {methods[i]} took {time_method}.')
        
# save the dictonaries in pickles
filehandler = open(src+"/results/eval_costs.obj", 'wb')
pickle.dump(costs, filehandler)

filehandler = open(src+"/results/eval_routes.obj", 'wb')
pickle.dump(routes, filehandler)

filehandler = open(src+"/results/eval_comp-time.obj", 'wb')
pickle.dump(comp_time, filehandler)



filehandler = open(src+"/results/best/best_costs.obj", 'wb')
pickle.dump(best_costs, filehandler)

filehandler = open(src+"/results/best/best_routes.obj", 'wb')
pickle.dump(best_routes, filehandler)

#%% Load previously computed solutions

download = True

if download == True:
    src2 = "C:/Users/fried/AppData/Local/Packages/CanonicalGroupLimited.UbuntuonWindows_79rhkp1fndgsc/LocalState/rootfs/home/eirene/download/CL-ACO_Hybrid"
else:
    src2 = "C:/Users/fried/AppData/Local/Packages/CanonicalGroupLimited.UbuntuonWindows_79rhkp1fndgsc/LocalState/rootfs/home/eirene/CL-ACO_Hybrid"


if cluster == False:
    results = pd.read_pickle(src2+"/results/eval_costs.obj")
    print("Mean distance")
    for i in range(0,len(methods)):        
        print(f'{methods[i]} : {np.mean(results[i])}')
    print("\nMinimum distance")
    for i in range(0,len(methods)):
        print(f'{methods[i]} : {np.min(results[i])}')
    print("\nMaximum distance")
    for i in range(0,len(methods)):
        print(f'{methods[i]} : {np.max(results[i])}')        

best_costs = pd.read_pickle(src2+"/results/best/best_costs.obj")

#%% Test Run


if cluster == False:

    # Create clusters
    method = methods[0]
    dict_clusters, df_clusters = runCluster(method)

    # export results
    exportClusters(dict_clusters, df_clusters, src+"/data", method) 

    # Data pre-processing
    dict_clusters, df_clusters, df_clusters_raw = dataprep_ACO(src, method)

    # Let the ants run!
    best_routes_all_clusters, total_cost_all_clusters = run_all_clusters(dict_clusters, df_clusters)

    # named 
    named_routes = namedRoute(best_routes_all_clusters, dict_clusters)

# %%

'''
# Maybe for creating names of files for different runs 
# based on when they happened

named_tuple = time.localtime() # get struct_time
time_string = time.strftime("%Y%d%m-%H%M%S", named_tuple)

print(f'results/{time_string}_"{method}"_clusters')

'''