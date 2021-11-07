# -*- coding: utf-8 -*-
"""
Extract OSM data with osmnx

Created on Sun Nov  7 17:19:19 2021

@author: eirene

(Re-)Sources: 
    - https://automating-gis-processes.github.io/2017/lessons/L7/network-analysis.html
    - https://osmnx.readthedocs.io/en/stable/
    - https://github.com/gboeing/osmnx/blob/main/README.md
    - https://geoffboeing.com
"""

# %% Setup

import osmnx as ox
import matplotlib as plt
import networkx as nx
from geopy.geocoders import Nominatim

# %% Extract Lueneburg & Visualize

# %% Option A: By name 

# Attention: quite a large amount of data

# different options to extract location
place_name = "Luneburg, Germany"                            # A.1
place_name = {"city": "Luneburg", "country": "Germany"}     # A.2  

graph = ox.graph_from_place(place_name)

fig, ax = ox.plot_graph(graph)
plt.tight_layout()


# %% Option B: By coordinates (this example doesn't include arena)

city_center = (53.248706, 10.407855) # coordinates          
radius = 5000                        # meters
graph = ox.graph_from_point(city_center, dist=radius, network_type="drive")

fig, ax = ox.plot_graph(graph)

# %% Get coordinates for an address

geolocator = Nominatim(user_agent="sample app")

data = geolocator.geocode("17 Wichernstraße, Luneburg, Germany")

lat = data.raw.get("lat")
lat = float(lat)
lon = data.raw.get("lon")
lon = float(lon)

# %% GeoDataFrames

nodes, edges = ox.graph_to_gdfs(graph)
print(edges['highway'].value_counts())

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

# get the nearest network nodes to two lat/lng points with the distance module
dest = ox.distance.nearest_nodes(graph, X = 53.272312, Y = 10.427605) # city center
#dest = ox.distance.nearest_nodes(graph, X= 53.248706, Y= 10.407855) # arena

orig = ox.distance.nearest_nodes(graph, X = lat,       Y = lon)

print(graph.nodes[dest]['x'])
print(graph.nodes[orig]['x'])

# somehow the same -> THEY SHOULDN'T OF COURSE!!!

# %% Routing III: Find shortest path

# find the shortest path between nodes, minimizing travel time, then plot it
route = ox.shortest_path(graph, orig, dest, weight="travel_time")
fig, ax = ox.plot_graph_route(graph, route, node_size=0)

# %% Routing IV: Calculate length of routes (in meters)

edge_lengths = ox.utils_graph.get_route_edge_attributes(graph, route, "length")
print(round(sum(edge_lengths)))


#%% Visualize street centrality

'''
Here we plot the street network and color its edges (streets) 
by their relative closeness centrality.
Attention: takes very long!!
'''

# convert graph to line graph so edges become nodes and vice versa
edge_centrality = nx.closeness_centrality(nx.line_graph(graph))
nx.set_edge_attributes(graph, edge_centrality, "edge_centrality")

# color edges in original graph with closeness centralities from line graph
ec = ox.plot.get_edge_colors_by_attr(graph, "edge_centrality", cmap="inferno")
fig, ax = ox.plot_graph(graph, edge_color=ec, edge_linewidth=2, node_size=0)



