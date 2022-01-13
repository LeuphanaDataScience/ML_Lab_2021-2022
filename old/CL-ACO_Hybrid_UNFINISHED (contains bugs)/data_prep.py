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
    datafile = src+'data/full_distance_matrix_lueneburg.csv'
    matrix = pd.read_csv(datafile, sep=";", index_col='name')

    # list of distances to arena
    distances_to_arena = list(matrix.loc["Schlachthof"])
    
    # list of bus stop names
    bus_names = list(matrix.columns)
    
    # importing file with bus stations & passengers assigned to them
    inputFile = pd.read_csv(src+f'data/{scenario}')
    inputFile.index = inputFile['name']
    inputFile = inputFile.drop('name', axis=1)

    return matrix, distances_to_arena, bus_names, inputFile


def exportClusters(src, 
                   dict_clusters, 
                   inputFile, 
                   method, 
                   purpose = "tmp"):
    
    inputFile.index = inputFile['name']
    inputFile= inputFile.drop('name', axis = 1)
    
    inputFile_gdf = gp.GeoDataFrame(inputFile,
                                    geometry=gp.points_from_xy(inputFile.x, 
                                                               inputFile.y))
    outputFile_clusters = inputFile_gdf.copy()                                                          
    outputFile_clusters['cluster'] = ['']*outputFile_clusters.shape[0]
    for clr_number, clr_list in dict_clusters.items():
        outputFile_clusters.loc[clr_list, "cluster"] = clr_number
    outputFile_clusters['name'] = outputFile_clusters.index
    outputFile_clusters.index = [i for i in range(outputFile_clusters.shape[0])]

    
    if purpose == "best_method":
        outputFile_clusters.to_csv(f'{src}/best/best_clusters_{method}.csv')
    elif purpose == "best_overall":
        outputFile_clusters.to_csv(f'{src}/best/best_clusters_overall_({method}).csv')
    elif purpose == "tmp":
        outputFile_clusters.to_csv(f'{src}/tmp/tmp_{method}.csv')
        
    return outputFile_clusters
    
# %% ACO

def dataprep_ACO(matrix, outputFile_clusters):

    # Reduce data frame by dropping columns that aren't needed
    outputFile_clusters = outputFile_clusters.drop(['element_type', 'osmid', 
                                       'x', 'y', 
                                       'geometry', 'passengers'],
                                   axis=1)
    
    # remove stations at which no. passengers = 0
    inputFile_ACO_df = outputFile_clusters.dropna(axis = 0)
        
    # Merge distance matrix & cluster dataframe 
    inputFile_ACO_tmp = (outputFile_clusters.merge(matrix,
                      on=['name'],
                      how='left',
                      indicator=True)
          .drop(columns='_merge')
          )
    
    # Loop over all clusters to create subsets of the data
    
    inputFile_ACO_dict = {}
    
#    for i in range(0, 3):
    for i in range(0, int(inputFile_ACO_tmp['cluster'].max()+1)):
        inputFile_ACO_tmp.cluster[inputFile_ACO_tmp['name'] == "Schlachthof"] = i       # arena (end point)
        inputFile_ACO_tmp.cluster[inputFile_ACO_tmp['name'] == "Hagen Wendeplatz"] = i  # depot (start point)
        df_1 = inputFile_ACO_tmp[inputFile_ACO_tmp['cluster'] == i]
    
        start = df_1[df_1['name'] == "Hagen Wendeplatz"]
        end = df_1[df_1['name'] == "Schlachthof"]
        tmp = df_1[df_1['name'] != "Schlachthof"]
        tmp = tmp[tmp['name'] != "Hagen Wendeplatz"]
    
        df_2 = pd.concat([start, tmp, end], ignore_index=True)
        df_2 = df_2[df_2['name'][df_2['cluster'] == i]]
        inputFile_ACO_dict[i] = df_2
        
        # Replace distances between bus stops == 0 by np.inf/ very high number
        inputFile_ACO_dict[i] = inputFile_ACO_dict[i].replace(0, 999999)
        
        inputFile_ACO_dict = inputFile_ACO_tmp
        
    return inputFile_ACO_dict, inputFile_ACO_df


def namedRoute(best_routes_all_clusters, dict_clusters):

    # Create dictonary with stop names instead of just indexes

    # make a copy of the dictonary containing lists with routes for all clusters
    # -> values (numbers) for stations should be overwritten with station names

    best_routes_all_clusters_names = copy.deepcopy(best_routes_all_clusters)

    # replace numbers by station names in copied dictonary
    for j in range(0, len(best_routes_all_clusters)):  # [0,14]
        for i in range(0, len(best_routes_all_clusters[j])):  # [1,15]
            best_routes_all_clusters_names[j][i] = list(best_routes_all_clusters_names[j][i])
            for k in range(2):
                index = best_routes_all_clusters[j][i][k]
                best_routes_all_clusters_names[j][i][k] = dict_clusters[j].columns.values[index]

    return best_routes_all_clusters_names

#%% OLD


    '''
    
    for file in os.listdir(src+"/results/"+previous_run+"/best"):
        if file.startswith("best_clusters_overall"):
            filename = file
            method = filename[23:-5]
    '''        

'''


def dataprep_ACO(src, method, previous_run=False, overall=True):
        
    # Load distance matrix data
    path_dm = f'{src}/data/full_distance_matrix_lueneburg.csv' 
    df_dm = pd.read_csv(path_dm, sep=';')
    
    # Load information on clusters
    if previous_run==False:
        path_cl = src + f'/tmp/inputFile_{method}.csv'   
    if previous_run!=False:
        if overall == True:
            path_cl = src + f'results/{previous_run}/best/best_clusters_overall_({method}).csv'
        else:
            path_cl = src + f'results/{previous_run}/best/best_clusters_{method}.csv'
    
    inputFile = pd.read_csv(path_cl)    
    inputFile_raw = copy.deepcopy(inputFile)
    
    # Reduce data frame by dropping columns that aren't needed
    inputFile = inputFile.drop(['element_type', 'osmid', 'x', 'y', 
                                    'geometry', 'passengers'],
                                   axis=1)
    
    # remove stations at which no. passengers = 0
    inputFile = inputFile.dropna(axis = 0)
        
    # Merge distance matrix & cluster dataframe 
    df = (inputFile.merge(df_dm,
                      on=['name'],
                      how='left',
                      indicator=True)
          .drop(columns='_merge')
          )
    
    # Loop over all clusters to create subsets of the data
    
    dict_clusters = {}
    
    for i in range(0, int(inputFile['cluster'].max()+1)):
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
        
        inputFile = df
        
    return dict_clusters, inputFile, inputFile_raw



    # Load information on clusters
    if previous_run==False:
        path_cl = src + f'/tmp/tmp_{method}.csv'   
    if previous_run!=False:
        if overall == True:
            path_cl = src + f'results/{previous_run}/best/best_clusters_overall_({method}).csv'
        else:
            path_cl = src + f'results/{previous_run}/best/best_clusters_{method}.csv'    
            
    inputFile2 = pd.read_csv(path_cl)    

'''
