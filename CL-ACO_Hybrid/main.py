# -*- coding: utf-8 -*-
"""
Created on Tue Dec 28 21:43:33 2021

Main File ACO-Clustering 

@author: eirene
"""

#%% Variables to be defined

# root directories of data
src = '/Users/fried/Documents/GitHub/ML_Lab_2021-2022/CL-ACO_Hybrid'

# Scenario (event)
Scenario = 'city_stops_and_passengers_1.csv' 

# Clustering
capacity = 70 # how many people we can get from one cluster
method = "CONVEX_HULL_CLOUD" # or "CONVEX_HULL_SEQUENCE" / "CONVEX_HULL_A_STAR"
 

#%% Import modules & functions

import pandas as pd
import pickle
import os

os.chdir(src)

from ACO import *
from Clustering import *
from data_prep import *

#%% Clustering step

# import dataframe including number of passengers assigned to stations
scenario = pd.read_csv(src+"/data/"+Scenario)

matrix, distances_to_arena, bus_names, bus_stops_df = dataprep_CL(src+"/data/", scenario)

# Define some variables
distances_to_arena_check = distances_to_arena.copy() # list of possible stops 
bus_names_check = bus_names.copy()


def runCluster(method):
    if method == "CONVEX_HULL_CLOUD":
        cluster_nodelist_dict = convex_cloud_cluster(bus_stops_df, capacity, distances_to_arena_check, bus_names_check, matrix, choice = 'random')
    elif method == "CONVEX_HULL_SEQUENCE":
        cluster_nodelist_dict = convex_sequence_cluster(bus_stops_df, capacity, distances_to_arena_check, bus_names_check, matrix, choice = 'random')
    elif method == "CONVEX_HULL_A_STAR":
        cluster_nodelist_dict = convex_a_star_cluster(bus_stops_df, capacity, distances_to_arena_check, bus_names_check, matrix, k = 3, choice = 'random')
    
    return cluster_nodelist_dict


# Create clusters
cluster_nodelist_dict = runCluster(method)


#exportClusters(bus_stops_df) # requires geopandas 

#%% ACO

# Data pre-processing
df_clusters, cl_df = dataprep_ACO(src, method)

# Let the ants run!
best_routes_all_clusters, total_cost_all_clusters = run_all_clusters(df_clusters, cl_df)

# save the dictonary in a pickle
dict_routes = best_routes_all_clusters
filehandler = open("f'{scr}/pickles/dict_routes.obj", 'wb')
pickle.dump(dict_routes, filehandler)

# create dataframe with named stations 
best_routes_all_clusters_names = namedRoute(best_routes_all_clusters, df_clusters)

dict_routes = best_routes_all_clusters_names
filehandler = open("f'{scr}/pickles/dict_routes_names.obj", 'wb')
pickle.dump(dict_routes, filehandler)


