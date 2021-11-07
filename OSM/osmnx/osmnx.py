# -*- coding: utf-8 -*-
"""
Extract OSM data with osmnx

Created on Sun Nov  7 17:19:19 2021

@author: eirene

(Re-)Sources: 
    - https://automating-gis-processes.github.io/2017/lessons/L7/network-analysis.html
    - https://osmnx.readthedocs.io/en/stable/
    - https://github.com/gboeing/osmnx/
    - https://geoffboeing.com
"""

# %% Setup

import osmnx as ox
import networkx as nx
from geopy.geocoders import Nominatim
import random as rnd

# %% Extract Lueneburg & Visualize

# %% Option A: By name 

# Attention: quite a large amount of data

# different options to extract location
place_name = "Luneburg, Germany"                            # A.1
place_name = {"city": "Luneburg", "country": "Germany"}     # A.2  

graph = ox.graph_from_place(place_name, network_type ="drive")

fig, ax = ox.plot_graph(graph)

# %% Option B: By coordinates 

city_center = (53.248706, 10.407855)
arena       = (53.272312, 10.427605)
        
radius = 10000                        # meters

#graph = ox.graph_from_point(city_center, dist=radius, network_type="drive") # city_center
graph = ox.graph_from_point(arena, dist=radius, network_type="drive") # arena

fig, ax = ox.plot_graph(graph)

# %% GeoDataFrames

nodes, edges = ox.graph_to_gdfs(graph)

#%% Basic insides

# calculate size of area covered by graph
graph_area_m = nodes.unary_union.convex_hull.area

# show some basic stats about the network
stats_basic = ox.basic_stats(graph, area=graph_area_m, clean_int_tol=15)
# stats documentation: https://osmnx.readthedocs.io/en/stable/osmnx.html#module-osmnx.stats

#%% Routing I: Preparation

# impute missing edge speeds and calculate edge travel times with the speed module
graph = ox.speed.add_edge_speeds(graph)
graph = ox.speed.add_edge_travel_times(graph)


# %% Routing II: Define start & end point

# %% Get coordinates for an address

geolocator = Nominatim(user_agent="sample app")

data = geolocator.geocode("17 Wichernstraße, Luneburg, Germany")

lat = float(data.raw.get("lat"))
lon = float(data.raw.get("lon"))

#%% Get nearest nodes to targets

# get the nearest network nodes to two lat/lng points with the distance module
dest, dest_dist = ox.distance.nearest_nodes(graph, X = 53.272312, Y = 10.427605, return_dist = True) # city center
dest, dest_dist = ox.distance.nearest_nodes(graph, X= 53.248706, Y= 10.407855, return_dist = True) # arena

orig, orig_dist = ox.distance.nearest_nodes(graph, X = lat,       Y = lon, return_dist = True)

print(graph.nodes[dest]['x'])
print(graph.nodes[orig]['x'])

# somehow the same -> THEY SHOULDN'T BE OF COURSE!!!

#%% Select sample nodes (for demonstration purposes only)

nodes_id = graph.nodes._nodes
nodes_id = nodes_id.keys()
nodes_id = list(nodes_id)

orig = nodes_id[rnd.randrange(0,len(nodes_id))]
dest = nodes_id[rnd.randrange(0,len(nodes_id))]

# %% Routing III: Find shortest path

# find the shortest path between nodes, minimizing travel time, then plot it
route = ox.shortest_path(graph, orig, dest, weight="travel_time")
fig, ax = ox.plot_graph_route(graph, route, node_size=0)

# %% Routing IV: Calculate length of routes (in meters)

edge_lengths = ox.utils_graph.get_route_edge_attributes(graph, route, "length")
print(round(sum(edge_lengths)))

#%% Visualize street centrality (just for fun)

'''
Plot the street network & color edges by relative closeness centrality.
Attention: takes quite long
'''

# convert graph to line graph so edges become nodes and vice versa
edge_centrality = nx.closeness_centrality(nx.line_graph(graph))
nx.set_edge_attributes(graph, edge_centrality, "edge_centrality")

# color edges in original graph with closeness centralities from line graph
ec = ox.plot.get_edge_colors_by_attr(graph, "edge_centrality", cmap="inferno")
fig, ax = ox.plot_graph(graph, edge_color=ec, edge_linewidth=2, node_size=0)

#%%


