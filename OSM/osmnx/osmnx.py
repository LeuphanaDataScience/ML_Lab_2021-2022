# -*- coding: utf-8 -*-
"""
Extract OSM data via API & with osmnx

Created on Sun Nov  7 17:19:19 2021

@author: eirene

(Re-)Sources: 
    - https://automating-gis-processes.github.io/2017/lessons/L7/network-analysis.html
    - https://osmnx.readthedocs.io/en/stable/
    - https://github.com/gboeing/osmnx/blob/main/README.md
    - https://geoffboeing.com/2018/03/osmnx-features-roundup/
"""

# %% Setup

import osmnx as ox
import matplotlib as plt
import networkx as nx
import pandas as pd

# %% Extract Lueneburg

place_name = "Luneburg, Germany"
graph = ox.graph_from_place(place_name)

fig, ax = ox.plot_graph(graph)

plt.tight_layout()

# %% Define nodes & edges

nodes, edges = ox.graph_to_gdfs(graph)
print(edges['highway'].value_counts())

#%%

graph_proj = ox.project_graph(graph)
fig, ax = ox.plot_graph(graph_proj)
plt.tight_layout()

#%%

# %% DOESNT WORK

#area = ox.gdf_from_place(place_name)
#buildings = ox.buildings_from_place(place_name)
