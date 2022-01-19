# -*- coding: utf-8 -*-
"""
Created on Sun Jan 16 23:04:15 2022

@author: Ilkin, minor modifications by eirene
"""

import osmnx as ox
import networkx as nx
import geopandas as gpd
import pandas as pd
import numpy as np
import warnings
import copy

warnings.filterwarnings("ignore")

#%%

towns = ['Bardowick, Bardowick, Germany',
         'Vögelsen, Bardowick, Germany' ,
         'Barum, Bardowick, Germany',
         'Handorf, Bardowick, Germany',
         'Mechtersen, Bardowick, Germany',
         'Radbruch, Bardowick, Germany',
         'Wittorf, Bardowick, Germany',
         
         'Kirchgellersen, Gellersen, Germany',
         'Reppenstedt, Gellersen, Germany',
         'Südergellersen, Gellersen, Germany',
         'Westergellersen, Gellersen, Germany',
         
         'Barnstedt, Ilmenau, Germany',
         'Deutsch Evern, Ilmenau, Germany',
         'Embsen, Ilmenau, Germany',
         'Melbeck, Ilmenau, Germany',
         
         'Barendorf, Ostheide, Germany',
         'Neetze, Ostheide, Germany',
         'Reinstorf, Ostheide, Germany',
         'Thomasburg, Ostheide, Germany',
         'Vastorf, Ostheide, Germany',
         'Wendisch Evern, Ostheide, Germany',
         
         'Artlenburg, Scharnebeck, Germany',
         'Brietlingen, Scharnebeck, Germany',
         'Echem, Scharnebeck, Germany',
         'Hittbergen, Scharnebeck, Germany',
         'Lüdersburg, Scharnebeck, Germany',
         'Rullstorf, Scharnebeck, Germany',
         'Scharnebeck, Scharnebeck, Germany',
        
        'Lüneburg, Germany',
        
        'Adendorf, Germany',
                'Amelinghausen, Amelinghausen, Germany',
         
        'Bleckede, Lüneburg, Germany',
         
        'Dahlenburg, Dahlenburg, Germany']

# downloading the graph from osm
L = ox.graph_from_place(towns, network_type='drive_service', simplify=True)

# obtaining bus stops coordinates in the same area
bus_stops = ox.geometries_from_place(towns, {'highway':"bus_stop"})

bus_points = bus_stops[bus_stops.geom_type == "Point"]

# getting osmid values to a column
bus_points.index.name = '#'
bus_points.reset_index(inplace=True)

# dropping duplicate bus stops
unique_stops = bus_points.drop_duplicates(subset=['name'])
unique_stops['osmid'] = ox.distance.nearest_nodes(L, unique_stops.geometry.x, unique_stops.geometry.y)

bus_ids = unique_stops['osmid'].tolist()

#%% Create a datafile including x & y

stops = copy.deepcopy(unique_stops)

stops['x'] = [np.nan]*stops.shape[0]
stops['y'] = [np.nan]*stops.shape[0]

for i in stops.index: 
    # get the coordinates of stop
    stops.x[i] = stops.geometry.x[i]
    stops.y[i] = stops.geometry.y[i]

    
src = "C:/Users/fried/AppData/Local/Packages/CanonicalGroupLimited.UbuntuonWindows_79rhkp1fndgsc/LocalState/rootfs/home/eirene/CL-ACO_Hybrid/"

stops.to_csv(f'{src}stop_info_osm.csv')   
