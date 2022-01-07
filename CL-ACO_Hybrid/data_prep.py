# -*- coding: utf-8 -*-
"""
Created on Tue Dec 28 21:54:46 2021

"""

# %% Import modules

import pandas as pd
import copy
import geopandas as gp

# %% Clustering


def dataprep_CL(src, scenario):

    # import distance matrix
    datafile = src+'/full_distance_matrix_lueneburg.csv'
    matrix = pd.read_csv(datafile, sep=";", index_col='name')

    # list of distances to arena
    distances_to_arena = list(matrix.loc["Schlachthof"])

    # list of bus stop names
    bus_names = list(matrix.columns)

    # creating the dataframe with bus_stops and people assigned to them:
    bus_stops_df = scenario
    bus_stops_df.index = bus_stops_df['name']
    bus_stops_df = bus_stops_df.drop('name', axis=1)

    return matrix, distances_to_arena, bus_names, bus_stops_df


# new dataframe with cluster numbers (and passenger numbers)

def exportClusters(dict_clusters, df_clusters_raw, src, method, best = False):
    bus_stops_gdf = gp.GeoDataFrame(df_clusters_raw,
                                    geometry=gp.points_from_xy(df_clusters_raw.x, df_clusters_raw.y))
    cluster_gdf = bus_stops_gdf.copy()
    cluster_gdf['cluster'] = ['']*cluster_gdf.shape[0]
    for clr_number, clr_list in dict_clusters.items():
        cluster_gdf.loc[clr_list, "cluster"] = clr_number
    cluster_gdf['name'] = cluster_gdf.index
    cluster_gdf.index = [i for i in range(cluster_gdf.shape[0])]

    cluster_gdf.to_csv(f'{src}/df_clusters_{method}.csv')
    
    if best == True:
        cluster_gdf.to_csv(f'{src}/results/best/best_clusters_{method}.csv')


# %% ACO

def dataprep_ACO(src, method):
    method = method
    file_path = f'{src}/data'
    file_dm = f'{file_path}/full_distance_matrix_lueneburg.csv'     # distance matrix
    file_cl = file_path + f'/df_clusters_{method}.csv'  # pre-processed by cluster

    # Load information on clusters
    df_clusters = pd.read_csv(file_cl)    
    df_clusters_raw = copy.deepcopy(df_clusters)

    # Reduce data frame by dropping columns that aren't needed
    df_clusters = df_clusters.drop(['element_type', 'osmid', 'x', 'y', 'geometry', 'passengers'],
                       axis=1)

    # Load information on distance matrix
    dm_df = pd.read_csv(file_dm, sep=';')

    # Merge data frames
    df = (df_clusters.merge(dm_df,
                      on=['name'],
                      how='left',
                      indicator=True)
          .drop(columns='_merge')
          )
    
    # Loop over all clusters to create subsets of the data

    dict_clusters = {}

    for i in range(1, int(df_clusters['cluster'].max()+1)):
        df.cluster[df['name'] == "Schlachthof"] = i       # arena (end point)
        df.cluster[df['name'] == "Hagen Wendeplatz"] = i  # depot (start point)
        df_1 = df[df['cluster'] == i]

        start = df_1[df_1['name'] == "Hagen Wendeplatz"]
        end = df_1[df_1['name'] == "Schlachthof"]
        tmp = df_1[df_1['name'] != "Schlachthof"]
        tmp = tmp[tmp['name'] != "Hagen Wendeplatz"]

        df_2 = pd.concat([start, tmp, end], ignore_index=True)
        df_2 = df_2[df_2['name'][df_2['cluster'] == i]]
        dict_clusters[i] = df_2
        
        # Replace distances between bus stops == 0 by np.inf/ very high number
        dict_clusters[i] = dict_clusters[i].replace(0, 999999)
        
        df_clusters = df
    
    return dict_clusters, df_clusters, df_clusters_raw


def namedRoute(best_routes_all_clusters, dict_clusters):

    # Create dictonary with stop names instead of just indexes

    # make a copy of the dictonary containing lists with routes for all clusters
    # -> values (numbers) for stations should be overwritten with station names

    best_routes_all_clusters_names = copy.deepcopy(best_routes_all_clusters)

    # replace numbers by station names in copied dictonary
    for j in range(1, len(best_routes_all_clusters)+1):  # [0,14]
        for i in range(0, len(best_routes_all_clusters[j])):  # [1,15]
            for k in range(2):
                index = best_routes_all_clusters[j][i][k]
                best_routes_all_clusters_names[j][i] = list(best_routes_all_clusters_names[j][i])
                best_routes_all_clusters_names[j][i][k] = dict_clusters[j].columns.values[index]

    return best_routes_all_clusters_names

#%%
