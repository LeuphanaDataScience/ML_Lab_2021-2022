# -*- coding: utf-8 -*-
"""
Created on Thu Jan 27 20:34:28 2022

@author: eirene
"""

'''
Schule A, 121136981
'''

import pandas as pd
import numpy as np


# Remove duplicate osmids

src = "C:/Users/fried/AppData/Local/Packages/CanonicalGroupLimited.UbuntuonWindows_79rhkp1fndgsc/LocalState/rootfs/home/eirene/CL-ACO/"


matrix = pd.read_csv(src+"data/distance_matrix.csv")
busstops = pd.read_csv(src+"data/bus_stops.csv")

matrix.index = matrix.osmid
matrix = matrix.drop("osmid", axis = 1)

matrix = matrix.T.drop_duplicates().T
matrix = matrix.drop_duplicates()

busstops = busstops.drop_duplicates()
  
osmids = []
    
for i, j in enumerate(busstops.osmid):
    if j in osmids:
        busstops.drop(index = i, inplace = True)
    osmids.append(j)

keep = ["osmid","name","x","y"]
busstops = busstops[keep]
busstops = busstops.reset_index()

#%%
# Put names to distance matrix

                                
names = [np.nan]*matrix.shape[0]

for i, j in enumerate(matrix.index):
    for k, l in enumerate(busstops.osmid):  
        if j == l:
            names[i] = busstops.name[k]
            matrix.columns.values[i] = busstops.name[k]


#%%
matrix.to_csv(f'{src}data/distance_matrix_LK_cleaned.csv')

#%%

'''
# "Self-made" (but buggy) solution for dm

osmids = []

for i, j in enumerate(matrix.index):
    if j in osmids:
        matrix.drop(index = j, inplace = True)
        if str(j) in matrix.columns:
            print(j)
            matrix = matrix.drop(str(j), axis = 1)
    
    osmids.append(j)
 '''   
