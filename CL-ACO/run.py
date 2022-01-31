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
import argparse

from main import Run

###### VARIABLES TO BE DEFINED BY USER ########################################

# local directory where project folder is stored
src = "./"

# input file with passengers assigned to stations
scenario = 'scenario_1_LK.csv' 

parsing = False

###### Technical details ######################################################

# bus capacity
capacity = 70                  

# iterations per method
iterations = [20,30]


if parsing == True:
    parser = argparse.ArgumentParser(description='Set variables for run')
    parser.add_argument('scenario', 
                        type = str,
                        default = 'scenario_1.csv',
                        help='Scenario')

    args, args_other = parser.parse_known_args()


###### RUN ####################################################################

    Run(src, 
        args.scenario, 
        capacity, 
        iterations,
        plot = True)

else:
    Run(src, 
        scenario, 
        capacity, 
        iterations,
        plot = True)