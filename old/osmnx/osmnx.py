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

#%% nearestNodes function -> (WHY) IS IT BUGGY?

import networkx as nx
import numpy as np

from osmnx import projection
from osmnx import utils_graph

try:
    from scipy.spatial import cKDTree
except ImportError:  # pragma: no cover
    cKDTree = None
    
# scikit-learn is optional dependency for unprojected nearest-neighbor search
try:
    from sklearn.neighbors import BallTree
except ImportError:  # pragma: no cover
    BallTree = None
    
EARTH_RADIUS_M = 6_371_009

X = 53.272312
Y = 10.427605

def nearest_nodes(G, X, Y, return_dist=False):
    """
    Find the nearest node to a point or to each of several points.
    If `X` and `Y` are single coordinate values, this will return the nearest
    node to that point. If `X` and `Y` are lists of coordinate values, this
    will return the nearest node to each point.
    If the graph is projected, this uses a k-d tree for euclidean nearest
    neighbor search, which requires that scipy is installed as an optional
    dependency. If it is unprojected, this uses a ball tree for haversine
    nearest neighbor search, which requires that scikit-learn is installed as
    an optional dependency.
    Parameters
    ----------
    G : networkx.MultiDiGraph
        graph in which to find nearest nodes
    X : float or list
        points' x (longitude) coordinates, in same CRS/units as graph and
        containing no nulls
    Y : float or list
        points' y (latitude) coordinates, in same CRS/units as graph and
        containing no nulls
    return_dist : bool
        optionally also return distance between points and nearest nodes
    Returns
    -------
    nn or (nn, dist) : int/list or tuple
        nearest node IDs or optionally a tuple where `dist` contains distances
        between the points and their nearest nodes
    """
    
    is_scalar = False
    if not (hasattr(X, "__iter__") and hasattr(Y, "__iter__")):
        # make coordinates arrays if user passed non-iterable values
        is_scalar = True
        X = np.array([X])
        Y = np.array([Y])

    if np.isnan(X).any() or np.isnan(Y).any():  # pragma: no cover
        raise ValueError("`X` and `Y` cannot contain nulls")
    nodes = utils_graph.graph_to_gdfs(G, edges=False, node_geometry=False)[["x", "y"]]

    if projection.is_projected(G.graph["crs"]):
        # if projected, use k-d tree for euclidean nearest-neighbor search
        if cKDTree is None:  # pragma: no cover
            raise ImportError("scipy must be installed to search a projected graph")
        dist, pos = cKDTree(nodes).query(np.array([X, Y]).T, k=1)
        nn = nodes.index[pos]

    else:
        # if unprojected, use ball tree for haversine nearest-neighbor search
        if BallTree is None:  # pragma: no cover
            raise ImportError("scikit-learn must be installed to search an unprojected graph")
        # haversine requires lat, lng coords in radians
        nodes_rad = np.deg2rad(nodes[["x", "y"]])                                                   # changed order of X & Y
        points_rad = np.deg2rad(np.array([X, Y]).T)
        dist, pos = BallTree(nodes_rad, metric="haversine").query(points_rad, k=1)
        dist = dist[:, 0] * EARTH_RADIUS_M  # convert radians -> meters
        nn = nodes.index[pos[:, 0]]

    # convert results to correct types for return
    nn = nn.tolist()
    dist = dist.tolist()
    if is_scalar:
        nn = nn[0]
        dist = dist[0]
        
    if return_dist:
        return nn, dist
    else:
        return nn

# %% Setup

import osmnx as ox
# import networkx as nx
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
        
radius = 5000                        # meters

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

#%% Get nearest nodes to targets (use function in this script)

# get the nearest network nodes to two lat/lng points with the distance module

dest, dest_dist = nearest_nodes(graph, X = 53.272312, Y = 10.427605, return_dist = True) # city center
#dest, dest_dist = nearest_nodes(graph, X= 53.248706, Y= 10.407855, return_dist = True) # arena

orig, orig_dist = nearest_nodes(graph, X = lat,       Y = lon, return_dist = True)

print(graph.nodes[dest]['x'])
print(graph.nodes[orig]['x'])

# somehow the same -> THEY SHOULDN'T BE OF COURSE!!!

#%% Get nearest nodes to targets (use function in ox)

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


