# -*- coding: utf-8 -*-
"""
Created on Tue Dec 28 21:43:33 2021

Main File ACO-Clustering

@author: eirene
"""

# %% Variables to be defined

cluster = False

if cluster == True:
    src = '.'  # root directory
else:
    src = "C:/Users/fried/AppData/Local/Packages/CanonicalGroupLimited.UbuntuonWindows_79rhkp1fndgsc/LocalState/rootfs/home/eirene/CL-ACO_Hybrid"
    src2 = "C:/Users/fried/AppData/Local/Packages/CanonicalGroupLimited.UbuntuonWindows_79rhkp1fndgsc/LocalState/rootfs/home/eirene/download/CL-ACO_Hybrid"

# Scenario (event)
Scenario = 'scenario_1.csv'

# Clustering
capacity = 70                 # how many people should be in one cluster

# %% Import modules & functions

import os
import pickle
import pandas as pd
import numpy as np
import time
import copy

if cluster == False:
    os.chdir(src)

from data_prep import dataprep_CL, dataprep_ACO, exportClusters, namedRoute
from Clustering import convex_cloud_cluster, convex_a_star_cluster, convex_sequence_cluster
from ACO import run_all_clusters

# %% Clustering step

methods = ["CONVEX_HULL_CLOUD_random", "CONVEX_HULL_SEQUENCE_random", "CONVEX_HULL_A_STAR_random",
           "CONVEX_HULL_CLOUD_distance", "CONVEX_HULL_SEQUENCE_distance", "CONVEX_HULL_A_STAR_distance"]


def runCluster(method):

    # Data pre-processing
    # import dataframe including number of passengers assigned to stations
    scenario = pd.read_csv(src+"/data/"+Scenario)
    matrix, distances_to_arena, bus_names, bus_stops_df = dataprep_CL(src+"/data/", scenario)

    # Define some variables
    distances_to_arena_check = distances_to_arena.copy()  # list of possible stops
    bus_names_check = bus_names.copy()

    if method == "CONVEX_HULL_CLOUD_random":
        cluster_nodelist_dict = convex_cloud_cluster(bus_stops_df, capacity,
                                                     distances_to_arena_check,
                                                     bus_names_check, matrix,
                                                     choice='random')
    elif method == "CONVEX_HULL_CLOUD_distance":
        cluster_nodelist_dict = convex_sequence_cluster(bus_stops_df, capacity,
                                                        distances_to_arena_check,
                                                        bus_names_check, matrix,
                                                        choice='distance')
    elif method == "CONVEX_HULL_SEQUENCE_random":
        cluster_nodelist_dict = convex_sequence_cluster(bus_stops_df, capacity,
                                                        distances_to_arena_check,
                                                        bus_names_check, matrix,
                                                        choice='random')
    
    elif method == "CONVEX_HULL_SEQUENCE_distance":
        cluster_nodelist_dict = convex_sequence_cluster(bus_stops_df, capacity,
                                                        distances_to_arena_check,
                                                        bus_names_check, matrix,
                                                        choice='distance')

    elif method == "CONVEX_HULL_A_STAR_random":
        cluster_nodelist_dict = convex_a_star_cluster(bus_stops_df, capacity,
                                                      distances_to_arena_check,
                                                      bus_names_check, matrix, k=3,
                                                      choice='random')

    elif method == "CONVEX_HULL_A_STAR_distance":
        cluster_nodelist_dict = convex_a_star_cluster(bus_stops_df, capacity,
                                                      distances_to_arena_check,
                                                      bus_names_check, matrix, k=3,
                                                      choice='distance')

    return cluster_nodelist_dict, bus_stops_df


#%% Test Run

# Create clusters

method = methods[1]

dict_clusters, df_clusters = runCluster(method)

# export results
exportClusters(dict_clusters, df_clusters, src+"/data", method) 

# Data pre-processing
dict_clusters, df_clusters = dataprep_ACO(src, method)

# Let the ants run!
best_routes_all_clusters, total_cost_all_clusters = run_all_clusters(dict_clusters, df_clusters)

# %% Combined function


def runClusterACO(method):

    # (1) Clustering step
    # Data pre-processing
    # import dataframe including number of passengers assigned to stations
    scenario = pd.read_csv(src+"/data/"+Scenario)
    matrix, distances_to_arena, bus_names, bus_stops_df = dataprep_CL(src+"/data/", scenario)
    # Create clusters
    dict_clusters, df_clusters = runCluster(method)
    # export results
    exportClusters(dict_clusters, df_clusters, src+"/data", method)

    # (2) ACO step
    # Data pre-processing
    dict_clusters, df_clusters = dataprep_ACO(src, method)
    # Let the ants run!
    best_routes_all_clusters, total_cost_all_clusters = run_all_clusters(dict_clusters, df_clusters)
    # save the dictonary in a pickle
    dict_routes = best_routes_all_clusters
    filehandler = open(src+"/pickles/dict_routes_"+method+".obj", 'wb')
    pickle.dump(dict_routes, filehandler)
    # create dataframe with named stations
    best_routes_all_clusters_names = namedRoute(best_routes_all_clusters, dict_clusters)
    dict_routes_names = best_routes_all_clusters_names
    filehandler = open(src+"/pickles/dict_routes_names_"+method+".obj", 'wb')
    pickle.dump(dict_routes_names, filehandler)

    return best_routes_all_clusters_names, total_cost_all_clusters, dict_clusters, df_clusters

'''
methods = ["CONVEX_HULL_CLOUD", "CONVEX_HULL_SEQUENCE", "CONVEX_HULL_A_STAR"]
method = methods[1]
runClusterACO(method)
'''

    
# %% Run multiple times to determine best clustering method & solution
# (might take long depending on iterations)

testing = True

if testing == True:
    methods = ["CONVEX_HULL_CLOUD_random"]
    iterations = 1
else:    
    methods = ["CONVEX_HULL_CLOUD_random", "CONVEX_HULL_SEQUENCE_random",
               "CONVEX_HULL_CLOUD_distance", "CONVEX_HULL_SEQUENCE_distance"]
    iterations = 100



routes = {}
costs = {}
clusters = {}
comp_time = {}

best_cluster = []
best_routes = []
best_costs = 99999999999999

for i in range(0, len(methods)):
    T1 = time.time()
    costs[i] = []
    routes[i] = []
    comp_time[i] = []
    clusters[i] = []
    for j in range(0,iterations):
        seconds = time.time()
        print(f'{methods[i]} (Method {i+1}/{len(methods)}), Iteration {j+1}/{iterations} Time: {time.ctime(seconds)}')       
        t0 = time.time()  
        route, cost, dict_clusters, df_clusters = runClusterACO(methods[i])
        t1 = time.time()
        ET = t1-t0
        costs[i].append(cost)
        routes[i].append(route)
        clusters[i].append(clusters)
        comp_time[i].append(ET)
        if cost < best_costs:
            best_costs = costs
            best_routes = routes
            best_cluster = df_clusters
#            exportClusters(df_clusters, dict_clusters, src+"/best", methods[i])
    T2 = time.time()
    time_method = T2-T1
    print(f'Running {iterations} Iterations for method {methods[i]} took {time_method}.')
        
# save the dictonary in a pickle
filehandler = open(src+"/pickles/eval_costs.obj", 'wb')
pickle.dump(costs, filehandler)

filehandler = open(src+"/pickles/eval_routes.obj", 'wb')
pickle.dump(routes, filehandler)

filehandler = open(src+"/pickles/eval_comp-time.obj", 'wb')
pickle.dump(comp_time, filehandler)



filehandler = open(src+"/pickles/best_costs.obj", 'wb')
pickle.dump(best_costs, filehandler)

filehandler = open(src+"/pickles/best_routes.obj", 'wb')
pickle.dump(best_routes, filehandler)

#%%

methods = ["CONVEX_HULL_CLOUD_random", "CONVEX_HULL_SEQUENCE_random",
           "CONVEX_HULL_CLOUD_distance", "CONVEX_HULL_SEQUENCE_distance"]

if cluster == False:
    results = pd.read_pickle(src2+"/pickles/eval_costs.obj")
    print("Mean distance")
    for i in range(0,len(methods)):        
        print(f'{methods[i]} : {np.mean(results[i])}')
    print("\nMinimum distance")
    for i in range(0,len(methods)):
        print(f'{methods[i]} : {np.min(results[i])}')
    print("\nMaximum distance")
    for i in range(0,len(methods)):
        print(f'{methods[i]} : {np.max(results[i])}')        

#%%

results2 = pd.read_pickle(src2+"/pickles/eval_routes.obj")





