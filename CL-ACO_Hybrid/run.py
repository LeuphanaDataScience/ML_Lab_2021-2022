# -*- coding: utf-8 -*-
"""
Created on Sun Jan  9 19:39:40 2022

@author: eirene
"""

###### Setup, Import modules & functions ######################################

import os
import warnings
warnings.filterwarnings("ignore") # don't print warnings
os.chdir(os.path.dirname(os.path.realpath(__file__)))
from main import Run


###### VARIABLES TO BE DEFINED BY USER ########################################

#src = "C:/Users/fried/AppData/Local/Packages/CanonicalGroupLimited.UbuntuonWindows_79rhkp1fndgsc/LocalState/rootfs/home/eirene/CL-ACO_Hybrid/"
src = "./"
iterations = 100
scenario = 'scenario_1_LK.csv' # input file
capacity = 70                  # max people per cluster (bus capacity)


###### Technical details ######################################################

methods = ["CONVEX_HULL_CLOUD_random", 
           "CONVEX_HULL_SEQUENCE_random",
      #     "CONVEX_HULL_A_STAR_random",
           
           "CONVEX_HULL_CLOUD_distance", 
           "CONVEX_HULL_SEQUENCE_distance",
      #     "CONVEX_HULL_A_STAR_distance", 
           
           "CLOUD", 
           "SEQUENCE", 
      #     "A_STAR", 
      #     "A_STAR_K_NEXT" 
           ]                 # clustering methods
#methods = methods[2:4]      # select methods (e.g. [3:] for only non-random ones)
random_only = False      
previous_run = False        # or e.g. "08-01-2022_03-40"
overall = True
testing = False

###### RUN ####################################################################

Run(src, 
    iterations, 
    scenario, 
    capacity, 
    methods,
    random_only=random_only, 
    previous_run=previous_run, 
    overall=overall,
    testing=testing)
