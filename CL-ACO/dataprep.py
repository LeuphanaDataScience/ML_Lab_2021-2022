# -*- coding: utf-8 -*-
"""
Created on Mon Jan 10 20:41:32 2022

@author: eirene
"""

import pandas as pd
import numpy as np
import copy
import string
import openpyxl
from openpyxl.styles import Font

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
    inputACO_df = inputACO_df[inputACO_df.index != "Schlachthof"]
    inputACO_df = inputACO_df.dropna(axis = 0)
    inputACO_df = pd.concat([inputACO_df, arena])
    
    inputACO_dict = {}
    
    for i in range(0, int(inputACO_df['cluster'].max()+1)):
        inputACO_df.cluster[inputACO_df.index == "Schlachthof"] = i  # arena
        df_1 = inputACO_df[inputACO_df['cluster'] == i] 
        
        # re-order dataframe such that arena is last entry
    #    end = df_1[df_1.index == "Schlachthof"]
     #   tmp = df_1[df_1.index != "Schlachthof"]    
      #  df_2 = pd.concat([tmp, end])
         
        # only include columns that are needed
        df_1 = df_1[df_1.index[df_1['cluster'] == i]]
        inputACO_dict[i] = df_1
        
        # Replace distances between bus stops == 0 by np.inf/ very high number
        inputACO_dict[i] = inputACO_dict[i].replace(0, 999999)
        
    inputACO = {}
    inputACO[0] = inputACO_dict
    inputACO[1] = inputACO_df
    inputACO[2] = copy.deepcopy(inputData[3])
    inputACO[3] = clustersDF.drop(['x', 'y', 'passengers'], axis=1)
        
    return inputACO

def export_excel(best_routes, new_result_dir, best_method):
    best_routes_clean = best_routes
    for key, values in best_routes.items():
        new_values = []
        for v in values:
            new_values.append(v[0])
        best_routes_clean[key] = new_values

    best_routes_df = pd.DataFrame.from_dict(best_routes_clean, orient='index')
    col_names = []
    for col in best_routes_df.columns:
        col_names.append("Stop: " + str(col))
    best_routes_df.columns = col_names
    best_routes_df.index.names = ["BUS"]

    alphabet_string = string.ascii_uppercase
    alphabet_list = list(alphabet_string)

    best_routes_df.to_excel(new_result_dir + f'/best/best_routes_{best_method}.xlsx', sheet_name='route')
    wb = openpyxl.load_workbook(new_result_dir + f'/best/best_routes_{best_method}.xlsx')
    ws = wb.active

    for col in alphabet_list[:len(best_routes_df.columns)]:
        ws.column_dimensions[col].width = 16

    wb.save(new_result_dir + f'/best/best_routes_{best_method}.xlsx')

#%%
