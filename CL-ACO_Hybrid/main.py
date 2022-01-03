# -*- coding: utf-8 -*-
"""
Created on Tue Dec 28 21:43:33 2021

Main File ACO-Clustering

@author: eirene
"""

# %% Variables to be defined

src = '.'  # root directory

# Scenario (event)
Scenario = 'city_stops_and_passengers_1.csv'

# Clustering
capacity = 70                 # how many people should be in one cluster
method = "CONVEX_HULL_CLOUD"  # or "CONVEX_HULL_SEQUENCE" / "CONVEX_HULL_A_STAR"


# %% Import modules & functions

import os
import pickle
import pandas as pd

#os.chdir(src)

from data_prep import dataprep_CL, dataprep_ACO, exportClusters, namedRoute
from Clustering import convex_cloud_cluster, convex_a_star_cluster, convex_sequence_cluster
from ACO import run_all_clusters

# %% Clustering step


methods = ["CONVEX_HULL_CLOUD", "CONVEX_HULL_SEQUENCE", "CONVEX_HULL_A_STAR"]


def runCluster(method):

    # Data pre-processing
    # import dataframe including number of passengers assigned to stations
    scenario = pd.read_csv(src+"/data/"+Scenario)
    matrix, distances_to_arena, bus_names, bus_stops_df = dataprep_CL(src+"/data/", scenario)

    # Define some variables
    distances_to_arena_check = distances_to_arena.copy()  # list of possible stops
    bus_names_check = bus_names.copy()

    if method == "CONVEX_HULL_CLOUD":
        cluster_nodelist_dict = convex_cloud_cluster(bus_stops_df, capacity,
                                                     distances_to_arena_check,
                                                     bus_names_check, matrix,
                                                     choice='random')
    elif method == "CONVEX_HULL_SEQUENCE":
        cluster_nodelist_dict = convex_sequence_cluster(bus_stops_df, capacity,
                                                        distances_to_arena_check,
                                                        bus_names_check, matrix,
                                                        choice='random')
    elif method == "CONVEX_HULL_A_STAR":
        cluster_nodelist_dict = convex_a_star_cluster(bus_stops_df, capacity,
                                                      distances_to_arena_check,
                                                      bus_names_check, matrix, k=3,
                                                      choice='random')

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

    return best_routes_all_clusters, best_routes_all_clusters_names


'''
methods = ["CONVEX_HULL_CLOUD", "CONVEX_HULL_SEQUENCE", "CONVEX_HULL_A_STAR"]
method = methods[1]
runClusterACO(method)
'''

# %% Run with different clustering methods

results = {}
for i in range(0, len(methods)):
    print(methods[i])
    results[i] = runClusterACO(methods[i])
