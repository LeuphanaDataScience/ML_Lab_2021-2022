# -*- coding: utf-8 -*-
"""
Created on Tue Dec 28 21:54:46 2021

"""

#%% Import modules

import pandas as pd
import copy

#%% Clustering

def dataprep_CL(src, scenario):
    # import files with passengers distributions
    bus_stops_people = scenario
    
    # import distance matrix 
    datafile = src+'/full_distance_matrix_lueneburg.csv'
    matrix = pd.read_csv(datafile, sep=";", index_col = 'name')
    
    # list of distances to arena
    distances_to_arena = list(matrix.loc["Schlachthof"])
    
    # list of bus stop names
    bus_names = list(matrix.columns)
    
    # creating the dataframe with bus_stops and people assigned to them:
    bus_stops_df = scenario
    bus_stops_df.index = bus_stops_df['name']
    bus_stops_df= bus_stops_df.drop('name', axis = 1)
    
    return matrix, distances_to_arena, bus_names, bus_stops_df


# new dataframe with cluster numbers (and passenger numbers)

def exportClusters(bus_stops_df):
    bus_stops_gdf = gp.GeoDataFrame(bus_stops_df, geometry=gp.points_from_xy(bus_stops_df.x, bus_stops_df.y))
    cluster_gdf = bus_stops_gdf.copy()
    cluster_gdf['cluster'] = ['']*cluster_gdf.shape[0]
    for clr_number, clr_list in cluster_nodelist_dict.items():
        cluster_gdf.loc[clr_list, "cluster"] = clr_number
    cluster_gdf['name'] = cluster_gdf.index
    cluster_gdf.index = [i for i in range(cluster_gdf.shape[0])]

    cluster_gdf.to_csv(f'{src}/data/Clustered_road_distance_{method}.csv') 


#%% ACO

def dataprep_ACO(src, method):
    method = method
    file_path = f'{src}/data'
    file_dm = f'{file_path}/full_distance_matrix_lueneburg.csv'    # distance matrix
    file_cl = file_path + f'/Clustered_road_distance_{method}.csv' # pre-processed by cluster group
    
    # Load information on clusters
    cl_df = pd.read_csv(file_cl)

    # Reduce data frame by dropping columns that aren't needed
    cl_df = cl_df.drop(['element_type', 'osmid', 'x', 'y', 'geometry', 'passengers'],
                       axis=1)

    # Load information on distance matrix
    dm_df = pd.read_csv(file_dm, sep=';')

    # Merge data frames
    df = (cl_df.merge(dm_df,
                      on=['name'],
                      how='left',
                      indicator=True)
          .drop(columns='_merge')
          )

    # Select only rows, which have cluster ID != 0
    df = df[df.cluster != 0]

    # Replace distances between bus stops == 0 by np.inf/ very high number
    df = df.replace(0, 999999)

    # Loop over all clusters to create subsets of the data

    df_clusters = {}

    for i in range(1, int(cl_df['cluster'].max()+1)):
        df.cluster[df['name']== "Schlachthof"] = i # arena (end point)
        df.cluster[df['name']== "Hagen Wendeplatz"] = i # depot (start point)   
        df_1 = df[df['cluster']==i]
        
        start = df_1[df_1['name']=="Hagen Wendeplatz"]
        end = df_1[df_1['name']== "Schlachthof"]
        tmp = df_1[df_1['name'] != "Schlachthof"]
        tmp = tmp[tmp['name'] != "Hagen Wendeplatz"]
    
        df_2 = pd.concat([start, tmp, end], ignore_index = True)    
        df_2 = df_2[df_2['name'][df_2['cluster']==i]]
        df_clusters[i] = df_2
    
    return df_clusters, cl_df
    
def namedRoute(best_routes_all_clusters, df_clusters):
    # Create dictonary with stop names instead of just indexes    
    # Delete the plot object from the dictonary
    for j in range(1,len(best_routes_all_clusters)+1): #[0,14]  
        best_routes_all_clusters[j] = list(best_routes_all_clusters[j])
        del best_routes_all_clusters[j][-1]
    
    # make a copy of the dictonary containing lists with routes for all clusters
    # -> values (numbers) for stations should be overwritten with station names
    best_routes_all_clusters_names = copy.deepcopy(best_routes_all_clusters)
    
    
    # replace numbers by station names in copied dictonary
    for j in range(1,len(best_routes_all_clusters)+1): #[0,14]  
        for i in range(0,len(best_routes_all_clusters[j][0][0])): #[1,15]
            for k in range(2):
                index = best_routes_all_clusters[j][0][0][i][k]            
                best_routes_all_clusters_names[j][0][0][i] = list(best_routes_all_clusters_names[j][0][0][i])
                best_routes_all_clusters_names[j][0][0][i][k] = df_clusters[j].columns.values[index]
    
    return best_routes_all_clusters_names
