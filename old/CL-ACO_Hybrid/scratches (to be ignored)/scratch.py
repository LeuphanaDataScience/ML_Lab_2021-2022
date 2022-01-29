# -*- coding: utf-8 -*-
"""
Created on Sun Jan 16 20:58:33 2022

@author: eirene
"""

import pandas as pd
import numpy as np

import os
os.chdir(os.path.dirname(os.path.realpath(__file__)))
from dataprep import dataprep

src = "C:/Users/fried/AppData/Local/Packages/CanonicalGroupLimited.UbuntuonWindows_79rhkp1fndgsc/LocalState/rootfs/home/eirene/CL-ACO_Hybrid/"


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

#%%

matrix.names = matrix.osmid

#%%

import os
os.chdir(os.path.dirname(os.path.realpath(__file__)))
from dataprep import dataprep, clusters_DF



#%%

scenario = "scenario_1_LK.csv"
#scenario = 'scenario_1.csv'

inputData = dataprep(src, scenario)

#%%

clustersDICT = runCluster(src, 
                          inputData, 
                          methods[0], 
                          capacity)



#%%

clustersDF = clusters_DF(src, 
                         inputData, 
                         clustersDICT, 
                         methodName, 
                         export=False)

#%%

tmp = (data.merge(inputData[1],
                  on=['name'], how='left',
                  indicator=True).drop(columns='_merge'))

# remove stations at which no. passengers = 0    
tmp = tmp.dropna(axis = 0)

