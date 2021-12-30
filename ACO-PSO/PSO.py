#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Dec 11 00:49:57 2021

@author: niklas-maximilianepping
"""

# %% IMPORTING DEPENDENCIES AND PACKAGES
# -----------------------------------------------------------------------------
import numpy as np
import pandas as pd
import random
import time

from ACO import run_all_clusters

# %% CLASSES
# -----------------------------------------------------------------------------
class Particle:
    def __init__(self, param):
        '''Particle Class

        Parameters
        ----------
        param : vector with numerical values
            Parameters to be optimized.

        Returns
        -------
        None.

        '''
        self.position_i = []        # particle position
        self.velocity_i = []        # particle velocity
        self.pbest_i = []           # best position individual
        self.err_pbest_i = -1       # best error individual
        self.err_i = -1             # error individual

        for i in range(0, num_dimensions):
            self.velocity_i.append(random.uniform(-1, 1))
            self.position_i.append(param[i])

    # evaluate current fitness
    def evaluate(self, costFunc):
        '''Function to evaluate particles' fitness

        Parameters
        ----------
        costFunc : function
            Cost function, utilized to evaluating fitness in order to optimize
            parameters.

        Returns
        -------
        None.

        '''
        self.err_i = costFunc(self.position_i)

        # check to see if the current position is an individual best
        if self.err_i < self.err_pbest_i or self.err_pbest_i == -1:
            self.pbest_i = self.position_i
            self.err_pbest_i = self.err_i

    # update particle velocity
    def update_velocity(self, pos_gbest):
        ''' Function to update velocity
        Updating depends among others on inertia weight omega (w).
        w can be represented by
        A) a constant
        B) a function, with decreasing value by increasing iterations
            1) Linear Time Varying (LTV)
            2) Non-linear Time Varying (NLTV)

        Parameters
        ----------
        pos_gbest : vector
            Best position of an individual of the swarm.

        Returns
        -------
        None.

        '''
        # A) a constant
        # w = 0.9

        # B-1) Linear Time Varying
        w_min, w_max = 0.4, 0.9     # bounds for omega, constant inertia weight
        w = ((w_max - w_min) * ((max_iterations - iterations) / max_iterations)) + w_max

        # # B-2) Non-linear Time Varying
        # w = 0.9                     # omega, constant inertia weight
        # w = (w - 0.4) * ((max_iterations - iterations)/(max_iterations + 0.4))

        c1 = 1                      # learning factor, cognitive constant
        c2 = 2                      # learning factor, social constant

        for i in range(0, num_dimensions):
            r1 = random.random()
            r2 = random.random()

            vel_cognitive = c1 * r1 * (self.pbest_i[i] - self.position_i[i])
            vel_social = c2 * r2 * (pos_gbest[i] - self.position_i[i])
            self.velocity_i[i] = w * self.velocity_i[i] + vel_cognitive + vel_social

    # update particle position
    def update_position(self, bounds):
        '''Function to update position

        Parameters
        ----------
        bounds : list (of lists), each with two numeric values (e. g. [0, 1]).
            Definition of the search space.

        Returns
        -------
        None.

        '''
        for i in range(0, num_dimensions):
            self.position_i[i] = self.position_i[i] + self.velocity_i[i]

            # adjust maximum position if necessary
            if self.position_i[i] > bounds[i][1]:
                self.position_i[i] = bounds[i][1]

            # adjust minimum position if neseccary
            if self.position_i[i] < bounds[i][0]:
                self.position_i[i] = bounds[i][0]


class PSO():
    def __init__(self, costFunc, param, bounds, num_particles, num_iter_max):
        '''PSO Maintenance Class
        Class maintaining swarm and performing optimization

        Parameters
        ----------
        costFunc : function
            Cost function, utilized to evaluating fitness in order to optimize
            parameters.
        param : vector with numerical values
            Parameters to be optimized.
        bounds : list (of lists), each with two numeric values (e. g. [0, 1]).
            Definition of the search space.
        num_particles : int
            Number of particles in swarm.
        num_iter_max : int
            Number of max. iterations

        Returns
        -------
        None.

        '''
        global num_dimensions, iterations, max_iterations

        num_dimensions = len(param)
        err_gbest = -1              # best error for swarm
        pos_gbest = []              # best position for swarm

        # Initalize swarm
        swarm = []
        for i in range(0, num_particles):
            swarm.append(Particle(param))

        # Optimization loop
        iterations = 0
        max_iterations = num_iter_max
        while iterations < num_iter_max:
            print('---------------')
            print('Iteration: ' + str(iterations))
            # Print i, err_gbest
            # Cycle through particles in swarm and evaluate fitness
            for j in range(0, num_particles):
                swarm[j].evaluate(costFunc)

                # Comparison of pbest with pos_gbest
                # pos_gbest replaced by pbest if better solution
                if swarm[j].err_i < err_gbest or err_gbest == -1:
                    pos_gbest = list(swarm[j].position_i)
                    err_gbest = float(swarm[j].err_i)

            # Iterate thorugh swarm (size) and update velocities and positions
            for j in range(0, num_particles):
                swarm[j].update_velocity(pos_gbest)
                swarm[j].update_position(bounds)
            iterations += 1
            # Print results
            print('> Best Parameters found so far:')
            print(pos_gbest)
            print(err_gbest)

        # Print results
        print('>>>>> Optimized Parameters:')
        print(pos_gbest)
        print(err_gbest)


# %% RUN PSO
# -----------------------------------------------------------------------------
# function, of which parameters should be optimized
costfunc = run_all_clusters

# SET 1
# Set initial starting location [alpha (a), beta (b), gamma (g), rho (r), ...]
initial = [1,                       # alpha
           1,                       # beta
           100,                     # gamma
           0.95]                    # rho
# Set input bounds [(a_min, a_max),(b_min, b_max), ...]
bounds = [(0.001, 10.00),           # alpha
          (0.001, 10.00),           # beta
          (0.001, 100.0),           # gamma
          (0.001, 0.999)]           # rho

# # SET 2 : ERRORS --> parameters such as colony size etc. can only be integers
# # Set initial starting location
# initial = [20,                      # n_colony
#            2,                       # n_elite
#            20,                      # n_iter_max
#            1,                       # alpha
#            1,                       # beta
#            100,                     # gamma
#            0.95]                    # rho
# # Set input bounds
# bounds = [(10, 50),                 # n_colony
#           (1, 5),                   # n_elite
#           (10, 50),                 # n_iter_max
#           (0.001, 10.00),           # alpha
#           (0.001, 10.00),           # beta
#           (0.001, 100.0),           # gamma
#           (0.001, 0.999)]           # rho

# Run optimization
PSO(costfunc, initial, bounds, num_particles=25, num_iter_max=50)
