# -*- coding: utf-8 -*-
"""
Created on Tue Dec 28 21:43:33 2021

Main File ACO-Clustering

@author: eirene
"""

# %% Variables to be defined

cluster = True

if cluster == True:
    src = '.'  # root directory
else:
    src = "C:/Users/fried/AppData/Local/Packages/CanonicalGroupLimited.UbuntuonWindows_79rhkp1fndgsc/LocalState/rootfs/home/eirene/CL-ACO_Hybrid"
    src2 = "C:/Users/fried/AppData/Local/Packages/CanonicalGroupLimited.UbuntuonWindows_79rhkp1fndgsc/LocalState/rootfs/home/eirene/download/CL-ACO_Hybrid"

# Scenario (event)
Scenario = 'city_stops_and_passengers_1.csv'

# Clustering
capacity = 70                 # how many people should be in one cluster

# %% Import modules & functions

import os
import pickle
import pandas as pd
import numpy as np
import time

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


'''
# Create clusters
cluster_nodelist_dict, bus_stops_df = runCluster(method)

# export results
# exportClusters(bus_stops_df, cluster_nodelist_dict, src, method)  # requires geopandas

for i in range(0, len(methods)):
    exportClusters(bus_stops_df, cluster_nodelist_dict, src, methods[i])  # requires geopandas
'''

# %% ACO

'''
# Data pre-processing
df_clusters, cl_df = dataprep_ACO(src, method)
# Let the ants run!
best_routes_all_clusters, total_cost_all_clusters = run_all_clusters(df_clusters, cl_df)

# save the dictonary in a pickle
dict_routes = best_routes_all_clusters
filehandler = open(f'{src}/pickles/dict_routes.obj', 'wb')
pickle.dump(dict_routes, filehandler)

# create dataframe with named stations
best_routes_all_clusters_names = namedRoute(best_routes_all_clusters, df_clusters)

dict_routes_names = best_routes_all_clusters_names
filehandler = open(f'{src}/pickles/dict_routes_names.obj', 'wb')
pickle.dump(dict_routes, filehandler)
'''

# %% Combined function


def runClusterACO(method):

    # (1) Clustering step
    # Data pre-processing
    # import dataframe including number of passengers assigned to stations
    scenario = pd.read_csv(src+"/data/"+Scenario)
    matrix, distances_to_arena, bus_names, bus_stops_df = dataprep_CL(src+"/data/", scenario)
    # Create clusters
    cluster_nodelist_dict, bus_stops_df = runCluster(method)
    # export results
    exportClusters(bus_stops_df, cluster_nodelist_dict, src, method)

    # (2) ACO step
    # Data pre-processing
    df_clusters, cl_df = dataprep_ACO(src, method)
    # Let the ants run!
    best_routes_all_clusters, total_cost_all_clusters = run_all_clusters(df_clusters, cl_df)
    # save the dictonary in a pickle
    dict_routes = best_routes_all_clusters
    filehandler = open(src+"/pickles/dict_routes_"+method+".obj", 'wb')
    pickle.dump(dict_routes, filehandler)
    # create dataframe with named stations
    best_routes_all_clusters_names = namedRoute(best_routes_all_clusters, df_clusters)
    dict_routes_names = best_routes_all_clusters_names
    filehandler = open(src+"/pickles/dict_routes_names_"+method+".obj", 'wb')
    pickle.dump(dict_routes_names, filehandler)

    return best_routes_all_clusters_names, total_cost_all_clusters

'''
methods = ["CONVEX_HULL_CLOUD", "CONVEX_HULL_SEQUENCE", "CONVEX_HULL_A_STAR"]
method = methods[1]
runClusterACO(method)
'''

# %% Run with different clustering methods

"""
results = {}
for i in range(0, len(methods)):
    print(methods[i])
    results[i] = runClusterACO(methods[i])
    table = results[i]
"""
    
# %% Run multiple times to determine best clustering method (TAKES LOOONG!!!)

methods = ["CONVEX_HULL_CLOUD_random", "CONVEX_HULL_SEQUENCE_random",
           "CONVEX_HULL_CLOUD_distance", "CONVEX_HULL_SEQUENCE_distance"]

iterations = 250

routes = {}
costs = {}
comp_time = {}

for i in range(0, len(methods)):
    T1 = time.time()
    costs[i] = []
    routes[i] = []
    comp_time[i] = []
    for j in range(0,iterations):
        seconds = time.time()
        print(f'{methods[i]} (Method {i+1}/{len(methods)}), Iteration {j+1}/{iterations} Time: {time.ctime(seconds)}')       
        t0 = time.time()  
        route, cost = runClusterACO(methods[i])
        t1 = time.time()
        ET = t1-t0
        costs[i].append(cost)
        routes[i].append(route)
        comp_time[i].append(ET)
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

#%%

methods = ["CONVEX_HULL_CLOUD_random", "CONVEX_HULL_SEQUENCE_random",
           "CONVEX_HULL_CLOUD_distance", "CONVEX_HULL_SEQUENCE_distance"]

if cluster == False:
    results = pd.read_pickle(src2+"/pickles/results_eval_cluster_methods.obj")
    for i in range(0,len(methods)):
        print(f'{methods[i]} : {np.mean(results[i])}')

