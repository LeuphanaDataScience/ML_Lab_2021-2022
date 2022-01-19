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

# local directory where project folder is stored
src = "./"
#src = "C:/Users/fried/AppData/Local/Packages/CanonicalGroupLimited.UbuntuonWindows_79rhkp1fndgsc/LocalState/rootfs/home/eirene/BusRouting_CL-ACO/"

# input file with passangers assigned to stations
scenario = 'scenario_3_LK.csv' 


###### Technical details ######################################################

# bus capacity
capacity = 70                  

# identifier in output 
identifier = "osmid"

# iterations per method
iterations = [20,100]

###### RUN ####################################################################

Run(src, 
    scenario, 
    capacity, 
    identifier,
    iterations)
