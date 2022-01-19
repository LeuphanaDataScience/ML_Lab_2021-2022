# -*- coding: utf-8 -*-
"""
Created on Mon Jan 10 20:41:32 2022

@author: eirene
"""

import pandas as pd
import numpy as np
import copy

#%%

def dataprep(src, scenario):

    inputData = {}
    
    # import distance matrix
    if scenario.endswith("LK.csv"):
        datafile = src+'data/full_distance_matrix_LK.csv'
        matrix = pd.read_csv(datafile, sep=",", index_col="name")
        inputData[0] = matrix
    else:
        datafile = src+'data/full_distance_matrix_lueneburg.csv'
        matrix = pd.read_csv(datafile, sep=";", index_col='name')
        inputData[0] = matrix
    
    # importing file with bus stations & passengers assigned to them
    inputFile = pd.read_csv(src+f'INPUT/{scenario}')
    
    # merge with osm information
    osminfo = pd.read_csv(src+"data/stop_info_osm.csv")
    inputFile = (osminfo.merge(inputFile,
                      on=['name'], how='left',
                      indicator=True).drop(columns='_merge'))
    inputFile = inputFile.dropna(axis = 0)
    
    inputFile.index = inputFile['name']
    inputFile = inputFile.drop('name', axis=1)
    inputData[1] = inputFile
    
    # remark: no name for osmid 354506387 (not present in bus name file)

    # remove stations at which no. passengers = 0    
    
    
    # list of distances to arena
    distances_to_arena = list(matrix.loc["Schlachthof"])
    inputData[2] = distances_to_arena
    
    # list of bus stop names
    bus_names = list(matrix.columns)
    inputData[3] = bus_names
    
    return inputData

def clusters_DF(src, inputData, clustersDICT, 
                method, export=True, best=False):
    
    clustersDF = inputData[1].copy()                                                          
    clustersDF['cluster'] = [np.nan]*clustersDF.shape[0]
    
    for station in enumerate(clustersDF.index):
        for cluster in clustersDICT.keys():
            if station[1] in clustersDICT[cluster]:
                clustersDF.cluster[station[1]] = int(cluster)
                
    if best == True:
        export = False
        clustersDF.to_csv(f'{src}best/bestClusterOverall_({method}).csv')    
    if export == True:
        clustersDF.to_csv(f'{src}tmp/tmp_{method}.csv')
           
    return clustersDF
    

def dataprep_ACO(src, inputData, clustersDF):
    
    # Reduce data frame by dropping columns that aren't needed
    clustersDF_tmp = clustersDF.drop(['x', 'y', 'passengers', 'osmid'], axis=1)
    
    # Merge distance matrix & cluster dataframe 
    inputACO_df = (clustersDF_tmp.merge(inputData[0],
                      on=['name'], how='left',
                      indicator=True).drop(columns='_merge'))

    # remove stations at which no. passengers = 0   
    arena = inputACO_df[inputACO_df.index == "Schlachthof"]
    inputACO_df = inputACO_df.dropna(axis = 0)
    inputACO_df = pd.concat([inputACO_df, arena])
    
    inputACO_dict = {}
    
    for i in range(0, int(inputACO_df['cluster'].max()+1)):
        inputACO_df.cluster[inputACO_df.index == "Schlachthof"] = i  # arena
        df_1 = inputACO_df[inputACO_df['cluster'] == i] 
        
        # re-order dataframe such that arena is last entry
        end = df_1[df_1.index == "Schlachthof"]
        tmp = df_1[df_1.index != "Schlachthof"]    
        df_2 = pd.concat([tmp, end])
         
        # only include columns that are needed
        df_2 = df_2[df_2.index[df_2['cluster'] == i]]
        inputACO_dict[i] = df_2
        
        # Replace distances between bus stops == 0 by np.inf/ very high number
        inputACO_dict[i] = inputACO_dict[i].replace(0, 999999)
        
    inputACO = {}
    inputACO[0] = inputACO_dict
    inputACO[1] = inputACO_df
    inputACO[2] = copy.deepcopy(inputData[3])
    inputACO[3] = clustersDF.drop(['x', 'y', 'passengers'], axis=1)
        
    return inputACO



#%%

'''

# Put names to distance matrix

busstops = pd.read_csv(src+"data/busstops_LK.csv")
matrix = pd.read_csv(src+"data/full_distance_matrix_LK_only osmid.csv")

datafile = src+'data/full_distance_matrix_lueneburg.csv'
matrix_s = pd.read_csv(datafile, sep=";", index_col='name')

                                     
matrix['name'] = [np.nan]*matrix.shape[0]

for i, j in enumerate(matrix.osmid):
    for k, l in enumerate(busstops.osmid):
        if j == l:
            matrix.name[i] = busstops.name[k]
            matrix.columns.values[i+1] = busstops.name[k]

matrix.index = matrix['name']


matrix = matrix.drop('name', axis=1)
matrix = matrix.drop(['osmid'], axis=1)

matrix.to_csv(f'{src}data/distance_matrix_LK.csv')
'''
