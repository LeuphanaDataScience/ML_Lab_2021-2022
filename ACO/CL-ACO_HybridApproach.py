#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Dec 12 15:07:35 2021

@author: niklas-maximilianepping
modifications: friederikebaier

Questions:
1)  What happens, if in a given data set, there are more than e. g. 70 people to
    pick up at a station? Will there be multiple entries for one bus stop with
    two different cluster IDs?
    print(cl_df['passengers'].max())
    
'''
"""

# =============================================================================
#%% IMPORTING PACKAGES
# -----------------------------------------------------------------------------
import numpy as np
import pandas as pd
import time


# =============================================================================
#%% LOADING DATA
# -----------------------------------------------------------------------------

# file_path = '/Users/niklas-maximilianepping/Desktop/MyProjects/ACO/'

file_path = '/Users/fried/Documents/GitHub/ML_Lab_2021-2022/ACO/'
file_dm = 'full_distance_matrix_lueneburg.csv'  # distance matrix
file_cl = 'cluster_gdf_1.csv'                   # pre-processed by cluster group


# Load information on clusters
# -----------------------------------------------------------------------------
cl_df = pd.read_csv(file_path + file_cl)

# Reduce data frame by dropping columns that aren't needed
cl_df = cl_df.drop(['element_type', 'osmid', 'x', 'y', 'geometry', 'passengers'],
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

#%% Process both data frames
# -----------------------------------------------------------------------------

# Merge data frames
df = (cl_df.merge(dm_df,
                  on=['name'],
                  how='left',
                  indicator=True)
      .drop(columns='_merge')
      )
print(df)

# Select only rows, which have cluster ID != 0
df = df[df.cluster != 0]


# Replace distances between bus stops == 0 by np.inf/ very high number
# df = df.replace(0, np.inf)
df = df.replace(0, 999999)

#%% Cluster subsets

# Loop over all clusters to create subsets of the data

df_clusters = {}

for i in range(1, cl_df['cluster'].max()+1):
    df.cluster[df['name']== "Schlachthof"] = i # arena (end point)
    df.cluster[df['name']== "Hagen Wendeplatz"] = i # depot (start point)   
    df_1 = df[df['cluster']==i]
    
    start = df_1[df_1['name']=="Hagen Wendeplatz"]
    end = df_1[df_1['name']== "Schlachthof"]
    tmp = df_1[df_1['name'] != "Schlachthof"]
    tmp = tmp[tmp['name'] != "Hagen Wendeplatz"]

    df_2 = pd.concat([start, tmp, end], ignore_index = True)
    
    df_2 = df_2[df_2['name'][df_2['cluster']==i]]

    df_clusters[i] = df_2

#%%
# =============================================================================
# CLASSES
# -----------------------------------------------------------------------------
class AntColony(object):

    def __init__(self, dist, n_colony, n_elite, n_iter, n_iter_max,
                 alpha, beta, gamma, rho):
        '''Ant Colony Class

        Arguments
        ---------
        dm : 2D numpy.array
            Square matrix of distances. Diagonal assumed to be np.inf.
        n_colony : int
            Number of ants running per iteration/swarm size)
        n_elite : int
            Number of best/elitist ants who deposit pheromone
        n_iter : int
            Number of iterations
        n_iter_max (int): Number of maximum iterations
        alpha : int or float
            Exponenet on pheromone. Higher alpha gives pheromone more weight.
            Default=1
        beta : int or float
            Exponent on distance. Higher beta gives distance more weight.
            Default=1
        gamma : float
            Pheromone supply of an ant.
            Default=100
        rho : float
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
        self.alpha = alpha  # weight factor on pheromone concentration and dist
        self.beta = beta  # weight factor on pheromone concentration and dist
        self.gamme = gamma  # pheromone supply of an ant
        self.rho = rho  # decay/evaporation factor of pheromone, double, rho<1

#%%
# =============================================================================
# ALGORITHMS AND FUNCTIONS
# -----------------------------------------------------------------------------
    def run(self):
        '''Ant Colony Optimization algorithm

        Returns
        -------
        route_gbest : TYPE
            DESCRIPTION.

        '''
        total_ET = 0
        CP = pd.DataFrame({'ET in sec': [],
                           'Cost': []})  # for eval

        route_lbest = None
        route_gbest = ("placeholder", np.inf)
        for self.n_iter in range(self.n_iter_max):

            t0 = time.process_time()  # for performance evaluation

            all_routes = self.gen_all_routes()
            self.spread_pheromone(all_routes,
                                  self.n_elite,
                                  route_lbest=route_lbest)
            route_lbest = min(all_routes, key=lambda x: x[1])
            if route_lbest[1] < route_gbest[1]:
                route_gbest = route_lbest
            self.pheromone = self.pheromone * self.rho

            t1 = time.process_time()   # for performance evaluation

            # Computational performance (CP) evaluation
            # -----------------------------------------------------------------
            ET = t1-t0
            total_ET += ET
            temp = pd.DataFrame({'ET in sec': [total_ET],
                                 'Cost_gbest': [route_gbest[-1]],
                                 'Cost_lbest': [route_lbest[-1]]})
            CP = CP.append(temp, ignore_index=True)
            # print(route_lbest)
            # print('>>>>>', 'Execution time: ', ET, 'sec')  # for eval

        return route_gbest, CP.plot(x='ET in sec',
                                    y=['Cost_gbest', 'Cost_lbest'])

    def spread_pheromone(self, all_routes, n_elite, route_lbest):
        '''Function defining deposition of pheromones.
        Initially the pheromone levels are the same. The amount of deposited
        pheromone depends among other possible influences primarily on choices
        made by ants, in fact the distances of each path.


        Parameters
        ----------
        all_routes : float
            
        n_elite : int
            Number of best/elitist ants who deposit pheromone
        route_lbest :

        Returns
        -------
        no value

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
                self.pheromone[move] += 1.0 / self.dist[move]

    def gen_route_dist(self, route):
        '''Function calculating total distance of a route.

        Parameters
        ----------
        route : TYPE
            DESCRIPTION.

        Returns
        -------
        None.

        '''
        total_dist = 0
        for ele in route:
            total_dist += self.dist[ele]
        return total_dist

    def gen_all_routes(self):
        '''Function generating all routes.

        Returns
        -------
        all_routes : TYPE
            DESCRIPTION.

        '''
        all_routes = []
        for i in range(self.n_colony):
            route = self.gen_route(0,len(self.dist) - 1) # set depot as start & arena as end point
            all_routes.append((route, self.gen_route_dist(route)))
        return all_routes

#    def gen_route(self, start):
    def gen_route(self, start, end):
        '''Function generating a route.

        Parameters
        ----------
        start : TYPE
            DESCRIPTION.

        Returns
        -------
        route : TYPE
            DESCRIPTION.

        '''
        route = []
        visited = set()
        visited.add(start) 
        visited.add(end) # add arena to "visited" list (so that it doesn't get visited until end)
        prev = start
        for i in range(len(self.dist) - 2):
            move = self.pick_move(self.pheromone[prev],
                                  self.dist[prev], visited)
            route.append((prev, move))
            prev = move
            visited.add(move)
        route.append((prev, end)) # add arena as last stop
        return route

    def pick_move(self, pheromone, dist, visited):
        '''Function deciding on next postion

        Parameters
        ----------
        pheromone : TYPE
            DESCRIPTION.
        dist : TYPE
            DESCRIPTION.
        visited : TYPE
            DESCRIPTION.

        Returns
        -------
        move : TYPE
            DESCRIPTION.

        '''
        pheromone = np.copy(pheromone)
        pheromone[list(visited)] = 0

        row = pheromone ** self.alpha * ((1.0 / dist) ** self.beta)

        norm_row = row / row.sum()
        move = np.random.choice(self.all_inds, 1, p=norm_row)[0]
        return move

#%% Let the ants run!

# Loop over all data subsets (defined by clusters) in df_clusters

def run_all_clusters(a = 1, b = 1, g = 100, r = 0.95):
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
                           n_iter_max=100,
                           alpha=a,
                           beta=b,
                           gamma=g,
                           rho=r)
        route_gbest = ant_colony.run()
        best_routes_all_clusters[i] = route_gbest
        total_cost_all_clusters += route_gbest[0][-1]
        print(i)
    return best_routes_all_clusters, total_cost_all_clusters

best_routes_all_clusters, total_cost_all_clusters = run_all_clusters()


#%% Run (fixed hyperparameters, one cluster)

cost_matrix = df_clusters[3] # here you can select one cluster
distance_matrix = np.asarray(cost_matrix)
new_matrix = np.array(distance_matrix)

ant_colony = AntColony(new_matrix,
                       n_colony=50,
                       n_elite=5,
                       n_iter=1,
                       n_iter_max=100,
                       alpha=1,
                       beta=1,
                       gamma=100,
                       rho=0.95)

route_gbest = ant_colony.run()
print("route_gbest: {}".format(route_gbest))

#%% Hyperparameter Tuning (Combinations) 

alphas = [0.5, 1]
betas = [0.5, 1]
gammas = [100, 200]
rhos = [0.5, 0.95]


parameter_search = {}

#for g in range(len(gammas)):
for a in alphas:
    parameter_search[a] = {}
    for b in betas:
        parameter_search[a][b] = {}
        for g in gammas:
            parameter_search[a][b][g] = {}
            for r in rhos:
                print(f"alpha = {a}, beta = {b}, gamma = {g}, rho = {r}")
                best_routes_all_clusters, total_cost_all_clusters = run_all_clusters(a,b,g,r)
                parameter_search[a][b][g][r] = total_cost_all_clusters
   
#%% OLD

#%% Put cost matrix in same format as the following example of nparray distances

# This step (recoding 0 = high number) already done before, right?

'''
# distances = np.array([[np.inf, 2, 2, 5, 7],
#                       [2, np.inf, 4, 8, 2],
#                       [2, 4, np.inf, 1, 3],
#                       [5, 8, 1, np.inf, 2],
#                       [7, 2, 3, 2, np.inf]])

distance_matrix = np.asarray(cost_matrix)

# delete 1st row and col, because they incl. names
# distance_matrix = np.delete(distance_matrix, (0), axis=0)
# distance_matrix = np.delete(distance_matrix, (0), axis=1)

new_matrix = []
for i in distance_matrix:  # for each row in matrix
    row = []
    for j in i:  # for each value in row
        if j == 0:
            row.append(-np.inf)
        else:
            row.append(int(j))
    new_matrix.append(row)

new_matrix = np.array(new_matrix)
'''

#%% Hyperparameter Tuning (Combinations) (OLD)

alphas = [0.5, 1]
betas = [0.5, 1]
gammas = [100, 200]
rhos = [0.5, 0.95]


parameter_search = {}

#for g in range(len(gammas)):
for a in alphas:
    parameter_search[a] = {}
    for b in betas:
        parameter_search[a][b] = {}
        for g in gammas:
            parameter_search[a][b][g] = {}
            for r in rhos:
                print(f"alpha = {a}, beta = {b}, gamma = {g}, rho = {r}")
                ant_colony = AntColony(new_matrix,
                       n_colony=50,
                       n_elite=5,
                       n_iter=1,
                       n_iter_max=100,
                       alpha=a,
                       beta=b,
                       gamma=g,
                       rho=r)
                route_gbest = ant_colony.run()
                parameter_search[a][b][g][r] = route_gbest[0][-1]
                
