# -*- coding: utf-8 -*-
"""
Created on Tue Dec 28 21:44:26 2021

@author: niklas-maximilianepping, eirene

"""


# %% IMPORTING PACKAGES

import numpy as np
import copy 

# %% CLASSES

class AntColony(object):

    def __init__(self, dist, n_colony, n_elite, n_iter, n_iter_max,
                 n_no_better_sol, n_no_better_sol_max, alpha, beta, gamma, rho):
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
        self.n_no_better_sol = n_no_better_sol
        self.n_no_better_sol_max = n_no_better_sol_max
        self.alpha = alpha
        self.beta = beta
        self.gamma = gamma
        self.rho = rho
        
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

        route_lbest = None
        route_gbest = ("placeholder", np.inf)
        while self.n_no_better_sol < (self.n_no_better_sol_max+1):  # test of new termination criteria
        # for self.n_iter in range(self.n_iter_max):

            all_routes = self.gen_all_routes()
            self.spread_pheromone(all_routes,
                                  self.n_elite,
                                  route_lbest=route_lbest)
            route_lbest = min(all_routes, key=lambda x: x[1])
            if route_lbest[1] < route_gbest[1]:
                route_gbest = route_lbest
                self.n_no_better_sol = 1
            self.pheromone = self.pheromone * self.rho
            self.n_no_better_sol += 1  # test of new termination criteria
            self.n_iter += 1  # test of new termination criteria
        return route_gbest 

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
        all_routes : ###
            ###.
        '''
        all_routes = []
        for i in range(self.n_colony):
            route = self.gen_route(0, len(self.dist) - 1)  
            # set depot = start & arena = end
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

# %% "Full" solution (all clusters)

# Loop over all data subsets (defined by clusters) in df_clusters

def runACO(dict_clusters, df_clusters, a=2, b=5, g=80, r=0.8):

    best_routes_all_clusters = {}
    total_cost_all_clusters = 0

    for i in range(1, int(df_clusters['cluster'].max()+1)):
        cost_matrix = dict_clusters[i]
        distance_matrix = np.asarray(cost_matrix)
        new_matrix = np.array(distance_matrix)
        ant_colony = AntColony(new_matrix,
                               n_colony=22,
                               n_elite=3,
                               n_iter=1,
                               n_iter_max=50,
                               n_no_better_sol=1,
                               n_no_better_sol_max=10,
                               alpha=a,
                               beta=b,
                               gamma=g,
                               rho=r)
        route_gbest = ant_colony.run()
        best_routes_all_clusters[i] = route_gbest[0]  
        total_cost_all_clusters += route_gbest[-1]
#        print("Cluster: ", i)
    return best_routes_all_clusters, total_cost_all_clusters

#%%
