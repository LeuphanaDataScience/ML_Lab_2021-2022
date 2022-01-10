# -*- coding: utf-8 -*-
"""
Created on Sun Jan  9 19:39:40 2022

@author: eirene
"""

# Import modules & functions

import os
import warnings

warnings.filterwarnings("ignore") # don't print warnings

os.chdir(os.path.dirname(os.path.realpath(__file__)))

from main import Run

# Variables to be defined

src = "C:/Users/fried/AppData/Local/Packages/CanonicalGroupLimited.UbuntuonWindows_79rhkp1fndgsc/LocalState/rootfs/home/eirene/CL-ACO_Hybrid/"
iterations = 10
scenario = 'scenario_1.csv' # input file
capacity = 70               # max people per cluster (bus capacity)
methods = ["CONVEX_HULL_CLOUD_random", 
           "CONVEX_HULL_SEQUENCE_random",
           "CONVEX_HULL_A_STAR_random",
           
           "CONVEX_HULL_CLOUD_distance", 
           "CONVEX_HULL_SEQUENCE_distance",
           "CONVEX_HULL_A_STAR_distance", 
           
           "CLOUD", 
           "SEQUENCE", 
           "A_STAR", 
           "A_STAR_K_NEXT" 
           ]                # clustering methods

methods = methods[3:]        # select methods (e.g. [3:] for only non-random ones)
random_only = False      
previous_run = False        # or e.g. "08-01-2022_03-40"
#previous_run = "08-01-2022_03-40"
overall = False
testing = False

# Run
Run(src, 
    iterations, 
    scenario, 
    capacity, 
    methods,
    random_only=random_only, 
    previous_run=previous_run, 
    overall=overall,
    testing=testing)
