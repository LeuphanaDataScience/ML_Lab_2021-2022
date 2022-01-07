# -*- coding: utf-8 -*-
"""
Created on Fri Jan  7 02:03:07 2022

@author: Andrey
"""

# %% SETUP

from collections import defaultdict

#%%

#CLUSTERING ALGORITHM with CLOUD approach

def cloud_cluster(bus_stops_df, capacity, distances_to_arena_check, bus_names_check, matrix):
    cluster_nodelist_dict = defaultdict(list)
    cluster_number = 0  # cluster number
    while len(bus_names_check) != 0:#iterate till all nodes are assigned to clusters
        people_assigned = 0
        max_dist = max(distances_to_arena_check)
        ind_max_dist = distances_to_arena_check.index(max_dist)
        cluster_center = bus_names_check[ind_max_dist]
        distances_to_arena_check.remove(max_dist)
        bus_names_check.remove(cluster_center)
        #to ignore stops with 0 people assigned:
        people_assigned_next = bus_stops_df.loc[cluster_center, 'passengers']
        if people_assigned_next == 0:
            continue
        cluster_nodelist_dict[cluster_number] += [cluster_center]  # assign cluster center to cluster
        # assigning people to cluster to check the capacity constraint:
        people_assigned += people_assigned_next
        # creating a list to assign to the current cluster:
        cluster_candidates = (matrix.loc[cluster_center,bus_names_check]).to_dict() 
        cluster_candidates_names = list(cluster_candidates.keys())
        cluster_candidates_dist = list(cluster_candidates.values())
        while len(cluster_candidates_dist) != 0:
            min_dist = min(cluster_candidates_dist)
            ind_min_dist = cluster_candidates_dist.index(min_dist)
            new_clust_elem = cluster_candidates_names[ind_min_dist]
            ind_bus_stop = bus_names_check.index(new_clust_elem)
            people_assigned_next = bus_stops_df.loc[new_clust_elem, 'passengers']
            # make sure we do not put in the cluster the stops with 0 people assigned
            if people_assigned_next == 0: #make sure we do not put in cluster the 
                distances_to_arena_check.pop(ind_bus_stop)
                bus_names_check.remove(new_clust_elem)
                cluster_candidates_dist.pop(ind_min_dist)
                cluster_candidates_names.remove(new_clust_elem)
                continue
            if people_assigned + people_assigned_next > capacity: #check capacity constraint
                break
            cluster_nodelist_dict[cluster_number] +=  [new_clust_elem]
            people_assigned += people_assigned_next
            distances_to_arena_check.pop(ind_bus_stop)
            bus_names_check.remove(new_clust_elem)
            cluster_candidates_dist.pop(ind_min_dist)
            cluster_candidates_names.remove(new_clust_elem) 
        cluster_number += 1
    return cluster_nodelist_dict


#CLUSTERING ALGORITHM with SEQUENCE approach

def sequence_cluster(bus_stops_df, capacity, distances_to_arena_check, bus_names_check, matrix):
    cluster_nodelist_dict = defaultdict(list)
    cluster_number = 0  # cluster number
    while len(bus_names_check) != 0:
        people_assigned = 0
        max_dist = max(distances_to_arena_check)
        ind_max_dist = distances_to_arena_check.index(max_dist)
        cluster_center = bus_names_check[ind_max_dist]
        distances_to_arena_check.remove(max_dist)
        bus_names_check.remove(cluster_center)
        people_assigned_next = bus_stops_df.loc[cluster_center, 'passengers']
        if people_assigned_next == 0:
            continue
        cluster_nodelist_dict[cluster_number] += [cluster_center]
        people_assigned += people_assigned_next
        while (people_assigned + people_assigned_next <= capacity) and len(bus_names_check) != 0:
            cluster_candidates = (matrix.loc[cluster_center,bus_names_check]).to_dict()
            cluster_candidates_names = list(cluster_candidates.keys())
            cluster_candidates_dist = list(cluster_candidates.values())
            min_dist = min(cluster_candidates_dist)
            ind_min_dist = cluster_candidates_dist.index(min_dist)
            cluster_center = cluster_candidates_names[ind_min_dist]
            people_assigned_next = bus_stops_df.loc[cluster_center, 'passengers']
            if people_assigned_next == 0:
                ind_bus_stop = bus_names_check.index(cluster_center)
                distances_to_arena_check.pop(ind_bus_stop)
                bus_names_check.remove(cluster_center)
                continue
            if people_assigned + people_assigned_next > capacity:
                break
            cluster_nodelist_dict[cluster_number] +=  [cluster_center]
            ind_bus_stop = bus_names_check.index(cluster_center)
            distances_to_arena_check.pop(ind_bus_stop)
            bus_names_check.remove(cluster_center)
            people_assigned += people_assigned_next
        cluster_number += 1
    return cluster_nodelist_dict

#CLUSTERING ALGORITHM with A-star approach
#k is hyperparameter to take into account portion of the distance to Arena
def a_star_cluster(bus_stops_df, capacity, distances_to_arena_check, bus_names_check, k, matrix):
    cluster_nodelist_dict = defaultdict(list)
    cluster_number = 0  # cluster number
    while len(bus_names_check) != 0:
        people_assigned = 0
        max_dist = max(distances_to_arena_check)
        ind_max_dist = distances_to_arena_check.index(max_dist)
        cluster_center = bus_names_check[ind_max_dist]
        distances_to_arena_check.remove(max_dist)
        bus_names_check.remove(cluster_center)
        cluster_nodelist_dict[cluster_number] += [cluster_center]
        people_assigned_next = bus_stops_df.loc[cluster_center, 'passengers']
        if people_assigned_next == 0:
            continue
        people_assigned += people_assigned_next
        people_assigned_next = 0
        while (people_assigned + people_assigned_next <= capacity) and len(bus_names_check) != 0:
            cluster_candidates = (matrix.loc[cluster_center, bus_names_check]).to_dict()
            for node, dist in cluster_candidates.items():
                dist_add = matrix.loc[node, "Schlachthof"]
                cluster_candidates[node] = dist + dist_add/k
            cluster_candidates_names = list(cluster_candidates.keys())
            cluster_candidates_dist = list(cluster_candidates.values())
            min_dist = min(cluster_candidates_dist)
            ind_min_dist = cluster_candidates_dist.index(min_dist)
            cluster_center = cluster_candidates_names[ind_min_dist]
            people_assigned_next = bus_stops_df.loc[cluster_center, 'passengers']
            if people_assigned_next == 0:
                ind_bus_stop = bus_names_check.index(cluster_center)
                distances_to_arena_check.pop(ind_bus_stop)
                bus_names_check.remove(cluster_center)
                continue
            if people_assigned + people_assigned_next > capacity:
                break
            cluster_nodelist_dict[cluster_number] +=  [cluster_center]
            ind_bus_stop = bus_names_check.index(cluster_center)
            distances_to_arena_check.pop(ind_bus_stop)
            bus_names_check.remove(cluster_center)
            people_assigned += people_assigned_next
        cluster_number += 1
    return cluster_nodelist_dict

#CLUSTERING ALGORITHM with A-star k-next approach
#k is hyperparameter how many next closest points to compare to get the one that leads to Arena
def a_star_k_next_cluster(bus_stops_df, capacity, distances_to_arena_check, bus_names_check, matrix, k = 3):
    cluster_nodelist_dict = defaultdict(list)
    cluster_number = 0  # cluster number
    while len(bus_names_check) != 0:
        people_assigned = 0
        max_dist = max(distances_to_arena_check)
        ind_max_dist = distances_to_arena_check.index(max_dist)
        cluster_center = bus_names_check[ind_max_dist]
        distances_to_arena_check.remove(max_dist)
        bus_names_check.remove(cluster_center)
        cluster_nodelist_dict[cluster_number] += [cluster_center]
        people_assigned_next = bus_stops_df.loc[cluster_center, 'passengers']
        if people_assigned_next == 0:
            continue
        people_assigned += people_assigned_next
        people_assigned_next = 0
        while (people_assigned + people_assigned_next <= capacity) and len(bus_names_check) != 0:
            cluster_candidates = (matrix.loc[cluster_center, bus_names_check]).to_dict()
            cluster_candidates_names = list(cluster_candidates.keys())
            cluster_candidates_dist = list(cluster_candidates.values())
            #Sorting lists to get access to the closest ti cluster center:
            lists_to_sort = zip(cluster_candidates_dist, cluster_candidates_names)
            sorted_lists = sorted(lists_to_sort)  # sorted according to cluster_candidates_dist
            cluster_candidates_dist_sorted = [elem for elem,_ in sorted_lists][:k]
            cluster_candidates_names_sorted = [elem for _,elem in sorted_lists][:k]
            #create new dictionary with k closest elements to the cluster center
            cluster_candidates_k_next = dict(zip(cluster_candidates_names_sorted, cluster_candidates_dist_sorted))
            #add the distance to the arena to evaluate the best way to go
            for node, dist in cluster_candidates_k_next.items():
                dist_add = matrix.loc[node, "Schlachthof"]
                cluster_candidates_k_next[node] = dist + dist_add*0.99 #0.99 to not choose next on the same line after closest
            cluster_candidates_k_next_dist = list(cluster_candidates_k_next.values())
            cluster_candidates_k_next_names = list(cluster_candidates_k_next.keys())
            min_dist = min(cluster_candidates_k_next_dist)
            ind_min_dist = cluster_candidates_k_next_dist.index(min_dist)
            cluster_center = cluster_candidates_k_next_names[ind_min_dist]
            people_assigned_next = bus_stops_df.loc[cluster_center, 'passengers']
            if people_assigned_next == 0:
                ind_bus_stop = bus_names_check.index(cluster_center)
                distances_to_arena_check.pop(ind_bus_stop)
                bus_names_check.remove(cluster_center)
                continue
            if people_assigned + people_assigned_next > capacity:
                break
            cluster_nodelist_dict[cluster_number] +=  [cluster_center]
            ind_bus_stop = bus_names_check.index(cluster_center)
            distances_to_arena_check.pop(ind_bus_stop)
            bus_names_check.remove(cluster_center)
            people_assigned += people_assigned_next
        cluster_number += 1
    return cluster_nodelist_dict

