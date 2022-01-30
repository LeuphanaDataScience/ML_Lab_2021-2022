# -*- coding: utf-8 -*-
"""
Clustering Part

@author: Andrey, eirene
"""

# %% SETUP

import random
import numpy as np
from collections import defaultdict
from scipy.spatial import ConvexHull
import copy


# %% CLUSTERING ALGORITHM

# with CONVEX HULL center assignment and SEQUENCE approach

def convex_sequence_cluster(inputData, capacity, choice='random'):

    matrix = copy.deepcopy(inputData[0])
    inputFile = copy.deepcopy(inputData[1])
    distances_to_arena_check = copy.deepcopy(inputData[2])
    bus_names_check = copy.deepcopy(inputData[3])

    cluster_nodelist_dict = defaultdict(list)
    cluster_number = 0  # cluster number
    while len(bus_names_check) != 0:  # iterate till all nodes are assigned to clusters
        people_assigned = 0
        # determine convex points:
        if len(bus_names_check) >= 3:  # to calculate convex hull we need more than 3 points:
            points_unassigned = np.array(
                [[inputFile.loc[name]['x']] + [inputFile.loc[name]['y']] for name in bus_names_check])
            hull = ConvexHull(points_unassigned)
            bus_names_to_choose = [bus_names_check[index] for index in hull.vertices]
            distances_to_arena_to_choose = [
                distances_to_arena_check[index] for index in hull.vertices]
        else:
            bus_names_to_choose = bus_names_check
            distances_to_arena_to_choose = distances_to_arena_check
        # choose among convex point:
        # choose randomly:
        if choice == 'random':
            cluster_center = random.choice(bus_names_to_choose)
            ind_to_remove = bus_names_check.index(cluster_center)
            distances_to_arena_check.pop(ind_to_remove)
            bus_names_check.remove(cluster_center)
        if choice == 'distance':
            max_dist = max(distances_to_arena_to_choose)
            ind_max_dist = distances_to_arena_to_choose.index(max_dist)
            cluster_center = bus_names_to_choose[ind_max_dist]
            distances_to_arena_check.remove(max_dist)
            bus_names_check.remove(cluster_center)
        # to ignore stops with 0 people assigned:
        people_assigned_next = inputFile.loc[cluster_center, 'passengers']
        if people_assigned_next == 0:
            continue
        # assign cluster center to cluster
        cluster_nodelist_dict[cluster_number] += [cluster_center]
        # assigning people to cluster to check the capacity constraint:
        people_assigned += people_assigned_next
        # creating a list to assign to the current cluster:
        people_assigned_next = 0
        while (people_assigned + people_assigned_next <= capacity) and len(bus_names_check) != 0:
            cluster_candidates = (matrix.loc[cluster_center, bus_names_check]).to_dict()
            cluster_candidates_names = list(cluster_candidates.keys())
            cluster_candidates_dist = list(cluster_candidates.values())
            min_dist = min(cluster_candidates_dist)
            ind_min_dist = cluster_candidates_dist.index(min_dist)
            cluster_center = cluster_candidates_names[ind_min_dist]
            people_assigned_next = inputFile.loc[cluster_center, 'passengers']
            if people_assigned_next == 0:
                ind_bus_stop = bus_names_check.index(cluster_center)
                distances_to_arena_check.pop(ind_bus_stop)
                bus_names_check.remove(cluster_center)
                continue
            if people_assigned + people_assigned_next > capacity:
                break
            cluster_nodelist_dict[cluster_number] += [cluster_center]
            ind_bus_stop = bus_names_check.index(cluster_center)
            distances_to_arena_check.pop(ind_bus_stop)
            bus_names_check.remove(cluster_center)
            people_assigned += people_assigned_next
        cluster_number += 1
    return cluster_nodelist_dict


#%% Function imported by main script


def runCluster(src, inputData, method, capacity):
       
    if method == "CONVEX_HULL_SEQUENCE_random":
        clustersDICT = convex_sequence_cluster(inputData, capacity, choice='random')
    
    elif method == "CONVEX_HULL_SEQUENCE_distance":
        clustersDICT = convex_sequence_cluster(inputData, capacity, choice='distance')

    return clustersDICT
