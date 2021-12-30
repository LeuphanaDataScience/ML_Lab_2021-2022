#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# %% IMPORTING PACKAGES
# -----------------------------------------------------------------------------
import numpy as np
import pandas as pd
import time


# %% CLASSES
# -----------------------------------------------------------------------------
class AntColony(object):

    def __init__(self, dist, n_colony, n_elite, n_iter, n_iter_max,
                 alpha, beta, gamma, rho):
        '''Ant Colony Class

        Arguments
        ---------
        dist : 2D numpy.array
            Square matrix of distances. Diagonal assumed to be np.inf.
        n_colony : int
            Number of ants running per iteration/swarm size)
        n_elite : int
            Number of best/elitist ants who deposit pheromone
        n_iter : int
            Number of iterations
        n_iter_max : int
            Number of maximum iterations
        alpha : double or float
            Weight factor on pheromone concentration (exponent).
            Higher alpha gives pheromone more weight.
            Default=1
        beta : double or float
            Weight factor on distance (exponent).
            Higher beta gives distance more weight.
            Default=1
        gamma : double or float
            Pheromone supply of an ant.
            Default=100
        rho : double or float
            Rate at which pheromone decays. The Smaller rho, the faster decay.
            I.e. 0.5 will lead to faster decay than 0.95 (since pheromone value
            is multiplied by rho.
            Default=0.95

        Example
        -------
        ant_colony = AntColony(dist, 100, 20, 2000, 0.95, alpha=1, beta=2)
        '''
        self.dist = dist
        self.pheromone = np.ones(self.dist.shape) / len(dist)
        self.all_inds = range(len(dist))
        self.n_colony = n_colony
        self.n_elite = n_elite
        self.n_iter = n_iter
        self.n_iter_max = n_iter_max
        self.alpha = alpha
        self.beta = beta
        self.gamma = gamma
        self.rho = rho

# ALGORITHMS AND FUNCTIONS
# -----------------------------------------------------------------------------
    def run(self):
        '''Ant Colony Optimization algorithm
        Returns
        -------
        route_gbest : TYPE
            DESCRIPTION.
        '''
        # total_ET = 0
        # CP = pd.DataFrame({'ET in sec': [],
        #                    'Cost': []})  # for eval

        route_lbest = None
        route_gbest = ("placeholder", np.inf)
        for self.n_iter in range(self.n_iter_max):

            # t0 = time.process_time()  # for performance evaluation

            all_routes = self.gen_all_routes()
            self.spread_pheromone(all_routes,
                                  self.n_elite,
                                  route_lbest=route_lbest)
            route_lbest = min(all_routes, key=lambda x: x[1])
            if route_lbest[1] < route_gbest[1]:
                route_gbest = route_lbest
            self.pheromone = self.pheromone * self.rho

        #     t1 = time.process_time()   # for performance evaluation

        #     # Computational performance (CP) evaluation
        #     # -----------------------------------------
        #     ET = t1-t0
        #     total_ET += ET
        #     temp = pd.DataFrame({'ET in sec': [total_ET],
        #                          'Cost_gbest': [route_gbest[-1]],
        #                          'Cost_lbest': [route_lbest[-1]]})
        #     CP = CP.append(temp, ignore_index=True)
        #     # print(route_lbest)
        #     # print('>>>>>', 'Execution time: ', ET, 'sec')  # for eval

        return route_gbest,  # CP.plot(x='ET in sec',
        #                             y=['Cost_gbest', 'Cost_lbest'])

    def spread_pheromone(self, all_routes, n_elite, route_lbest):
        '''Function defining deposition of pheromones.
        Initially the pheromone levels are the same. The amount of deposited
        pheromone depends among other possible influences primarily on choices
        made by ants, in fact the distances of each path.

        Parameters
        ----------
        all_routes : ###
            ###
        n_elite : int
            Number of best/elitist ants who deposit pheromone
        route_lbest : ###
            ###

        Returns
        -------
        None.

        Example
        -------
        After all routes are generated:
        A) a selected number of ants (elite) deposits pheromones on their paths
        they traveled according to the following equation:
            1 / (dist between two positions)
        An elitist ant traveling two paths: [0,3] w dist=8 and [3,5] w dist=2.
        According to the equation: [0,3] += 0.125 and pheromone[3,5] += 0.5.
        Aim here is to keep track of successful routes
        '''
        sorted_routes = sorted(all_routes, key=lambda x: x[1])
        for route, dist in sorted_routes[:n_elite]:
            for move in route:
                self.pheromone[move] += self.gamma / self.dist[move]

    def gen_route_dist(self, route):
        '''Function calculating total distance of a route.

        Parameters
        ----------
        route : TYPE
            DESCRIPTION.

        Returns
        -------
        total_dist : ###
            ###.
        '''
        total_dist = 0
        for ele in route:
            total_dist += self.dist[ele]
        return total_dist

    def gen_all_routes(self):
        '''Function generating all routes.

        Returns
        -------
        all_routes : ###
            ###.
        '''
        all_routes = []
        for i in range(self.n_colony):
            # set depot as start and arena as end
            route = self.gen_route(0, len(self.dist) - 1)
            all_routes.append((route, self.gen_route_dist(route)))
        return all_routes

    def gen_route(self, start, end):
        '''Function generating a route.

        Parameters
        ----------
        start : ###
            First stop to be (marked as) visited.
        end : ###
            Last stop to be (marked as) visited.

        Returns
        -------
        route : list
            Route, in the form of indices of stops to be visited.
        '''
        route = []
        visited = set()
        visited.add(start)
        visited.add(end)  # add arena since it is not to be visited until end
        prev = start
        for i in range(len(self.dist) - 2):
            move = self.pick_move(self.pheromone[prev],
                                  self.dist[prev], visited)
            route.append((prev, move))
            prev = move
            visited.add(move)
        route.append((prev, end))  # add arena as last stop
        return route

    def pick_move(self, pheromone, dist, visited):
        '''Function deciding on next postion

        Parameters
        ----------
        pheromone : float
            List of pheromone concentrations for connections between current
            and all other stops.
        dist : list
            List of distances between current and all other stops.
        visited : list
            List of visited stops.

        Returns
        -------
        move : int
            Index of next stop, being marked as visited.
        '''
        pheromone = np.copy(pheromone)
        pheromone[list(visited)] = 0
        row = pheromone ** self.alpha * ((1.0 / dist) ** self.beta)
        norm_row = row / row.sum()
        move = np.random.choice(self.all_inds, 1, p=norm_row)[0]
        return move


# %% "FULL" SOLUTION (all clusters)
# -----------------------------------------------------------------------------
# SET 1
# Loop over all data subsets (defined by clusters) in df_clusters
def run_all_clusters(param):
    best_routes_all_clusters = {}
    total_cost_all_clusters = 0
    for i in range(1, cl_df['cluster'].max()+1):
        cost_matrix = df_clusters[i]
        distance_matrix = np.asarray(cost_matrix)
        new_matrix = np.array(distance_matrix)
        ant_colony = AntColony(new_matrix,
                               n_colony=50,
                               n_elite=5,
                               n_iter=1,
                               n_iter_max=25,
                               alpha=param[0],
                               beta=param[1],
                               gamma=param[2],
                               rho=param[3])
        route_gbest = ant_colony.run()
        best_routes_all_clusters[i] = route_gbest
        total_cost_all_clusters += route_gbest[0][-1]
        # print("Cluster: ", i)
    return total_cost_all_clusters

# # SET 2
# Loop over all data subsets (defined by clusters) in df_clusters
# def run_all_clusters(param):
#     best_routes_all_clusters = {}
#     total_cost_all_clusters = 0
#     for i in range(1, cl_df['cluster'].max()+1):
#         cost_matrix = df_clusters[i]
#         distance_matrix = np.asarray(cost_matrix)
#         new_matrix = np.array(distance_matrix)
#         ant_colony = AntColony(new_matrix,
#                                n_colony=param[0],
#                                n_elite=param[1],
#                                n_iter=1,
#                                n_iter_max=param[2],
#                                alpha=param[3],
#                                beta=param[4],
#                                gamma=param[5],
#                                rho=param[6])
#         route_gbest = ant_colony.run()
#         best_routes_all_clusters[i] = route_gbest
#         total_cost_all_clusters += route_gbest[0][-1]
#         # print("Cluster: ", i)
#     return total_cost_all_clusters


# %% LOADING & PRE-PROCESSING DATA
# -----------------------------------------------------------------------------
# Set working directory
file_path = '/Users/niklas-maximilianepping/Desktop/MyProjects/ACO/'
# file_path = '/Users/fried/Documents/GitHub/ML_Lab_2021-2022/ACO/'

# Set file name of distance matrix being used
file_dm = 'full_distance_matrix_lueneburg.csv'  # distance matrix

# Set file name of pre-processed clusters

file_cl = 'cluster_gdf_1.csv'
# file_cl = 'cluster_gdf_2.csv'
# file_cl = 'cluster_gdf_3.csv'

# file_cl = 'Clustered_road_distance_A_star_1.csv'
# file_cl = 'Clustered_road_distance_A_star_2.csv'
# file_cl = 'Clustered_road_distance_A_star_3.csv'

# file_cl = 'Clustered_road_distance_cloud_1.csv'
# file_cl = 'Clustered_road_distance_cloud_2.csv'
# file_cl = 'Clustered_road_distance_cloud_3.csv'

# file_cl = 'Clustered_road_distance_sequence_1.csv'
# file_cl = 'Clustered_road_distance_sequence_2.csv'
# file_cl = 'Clustered_road_distance_sequence_3.csv'

# Load information on clusters
# -----------------------------------------------------------------------------
cl_df = pd.read_csv(file_path + file_cl)

# For Andrey'ys cluster
# cl_df = cl_df[cl_df['cluster'].isnull() == 0]
# cl_df['cluster'] = cl_df['cluster'].apply(np.int64)
# cl_df = cl_df.drop(['Unnamed: 0', 'Unnamed: 0.1'],
#                    axis=1)
# print(cl_df['cluster'].max())
# print(cl_df[cl_df['cluster']==15])

# For Clemens' cluster
# Reduce data frame by dropping columns that aren't needed
cl_df = cl_df.drop(['element_type', 'osmid','x', 'y', 'geometry', 'passengers'],
                    axis=1)

# Load information on distance matrix
# -----------------------------------------------------------------------------
dm_df = pd.read_csv(file_path + file_dm, sep=';')

'''
# Inspection
# Max. cluster ID == no. of clusters (n_cl) == no. of inputs for run()
cl_df['cluster'].max()
# Print entries with cluster ID == 1
print(cl_df[cl_df['cluster']==1])
'''

# Merge data frames
df = (cl_df.merge(dm_df,
                  on=['name'],
                  how='left',
                  indicator=True)
      .drop(columns='_merge')
      )
# print(df)

# Replace distances between bus stops == 0 by np.inf/ very high number
# df = df.replace(0, np.inf)
df = df.replace(0, 999999)

# %% Cluster subsets
# -----------------------------------------------------------------------------
# Loop over all clusters to create subsets of the data

df_clusters = {}

for i in range(1, cl_df['cluster'].max()+1):
    df.cluster[df['name'] == "Schlachthof"] = i  # arena (end point)
    df.cluster[df['name'] == "Hagen Wendeplatz"] = i  # depot (start point)
    df_1 = df[df['cluster'] == i]

    start = df_1[df_1['name'] == "Hagen Wendeplatz"]
    end = df_1[df_1['name'] == "Schlachthof"]
    tmp = df_1[df_1['name'] != "Schlachthof"]
    tmp = tmp[tmp['name'] != "Hagen Wendeplatz"]

    df_2 = pd.concat([start, tmp, end], ignore_index=True)
    df_2 = df_2[df_2['name'][df_2['cluster'] == i]]
    df_clusters[i] = df_2

# # %% Computational performance (CP) evaluation
# # -----------------------------------------------------------------------------
# ET_all = []

# for i in range(1):
#     print("Iteration: ", i+1)
#     t0 = time.process_time()  # for performance evaluation
#     total_cost_all_clusters = run_all_clusters()
#     t1 = time.process_time()   # for performance evaluation
#     ET = t1-t0
#     ET_all.append(ET)

# # %% Print results
# # -----------------------------------------------------------------------------
# print(total_cost_all_clusters)
# print(np.mean(ET_all))