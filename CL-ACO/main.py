# -*- coding: utf-8 -*-
"""
Created on Wed Jan 12 17:15:44 2022

@author: eirene
"""

#%% Setup

import os
import warnings
import numpy as np
import time
import shutil
import math as mt
import pickle

warnings.filterwarnings("ignore") # don't print warnings
os.chdir(os.path.dirname(os.path.realpath(__file__)))

from dataprep import dataprep, clusters_DF, dataprep_ACO, export_excel
from Clustering import runCluster
from ACO import runACO


#%% Main pipeline

def Run(src, 
        scenario, 
        capacity, 
        identifier = "name",
        iterations = [20,100]):
        
            ####### SETUP #################################################################
            
            # clustering methods
            methods = [
                       "CONVEX_HULL_SEQUENCE_distance",
                       "CONVEX_HULL_SEQUENCE_random"
                       ]    
            
            # for displaying progress
            T_initial = time.time()                 
         
            # Create folder for new OUTPUT
            time_now = time.localtime() 
            time_string = time.strftime("%d-%m-%Y_%H-%M", time_now)
            new_result_dir = src+f'OUTPUT/{time_string}/'    

            # Delete directory if it is already existent...
            if os.path.isdir(new_result_dir):
                shutil.rmtree(new_result_dir)
            # ... for being able to create new one    
            os.makedirs(new_result_dir)
            os.makedirs(new_result_dir+'/best')
            
            
            # initialize variables
            routes = {}
            costs = {}
            comp_time = {}
            
            best_routes = []
            best_costs_method = int(99999999999999)
            best_costs = int(99999999999999)
            
            its_total = np.sum(iterations)
            
            inputData = dataprep(src, scenario)

        # -----------------------------------------------------------------------------
            for method in range(0, len(methods)):
                
                methodName = methods[method]
                
                # initialize variables
                best_costs_method = int(99999999999999)  
                costs[methodName] = []
                routes[methodName] = []
                comp_time[methodName] = []
                
                its = 0
                for iteration in range(iterations[method]): 
                    
                    its += 1
                    # To display progress  
                    print(f'Scenario: {scenario}')
                    print(f'Current method: {methodName} (Method {method+1}/{len(methods)})')
                    print(f'Iteration {iteration+1}/{iterations[method]}\n')              
                    T_now = time.time()
                    t0 = time.time() 
                 
        ####### DATA PRE-PROCESSING ###################################################
                    
                    # Do clustering if not done before
                    if methodName.endswith("random") or iteration==0: 
                            clustersDICT = runCluster(src, 
                                                      inputData, 
                                                      methodName, 
                                                      capacity)
                            
                            clustersDF = clusters_DF(src, 
                                                     inputData, 
                                                     clustersDICT, 
                                                     methodName, 
                                                     export=False)
                               
        # -----------------------------------------------------------------------------
        
        
        ####### ACO ###################################################################
        
                    # Data pre-processing for ACO
                    inputACO = dataprep_ACO(src, inputData, clustersDF)
                    
                    T_passed = T_now - T_initial
                    if T_passed >= 1:
                        time_per_it = mt.floor(T_passed/(its))
                        time_left = time_per_it*(its_total-its)
                        print(f'Time passed: {mt.floor(T_passed)}s ({time_per_it}s/iteration[method])')
                        print(f'Estimated time left: {mt.floor(time_left/60)} minutes')
                    
                    # ACO step
                    route, cost = runACO(inputACO, identifier = identifier)
                        
                    # Calculate computational time 
                    t1 = time.time()
                    ET = t1-t0
                    
                    # add current results to result dictonary
                    costs[methodName].append(cost)
                    routes[methodName].append(route)
                    comp_time[methodName].append(ET)
            
                    # to find best solution for cluster method
                    if cost < best_costs_method:
                        best_costs_method = cost
                        
                    # to find best solution overall
                if best_costs_method < best_costs:
                    best_costs = cost
                    best_routes = route
                    best_clustersDICT = clustersDICT
                    best_method = methodName
                    
            # save other OUTPUT outside python
            filehandler = open(new_result_dir+"costs.obj", 'wb')
            pickle.dump(costs, filehandler)
            
            filehandler = open(new_result_dir+"/routes.obj", 'wb')
            pickle.dump(routes, filehandler)


            
            filehandler = open(new_result_dir+"/comp-time.obj", 'wb')
            pickle.dump(comp_time, filehandler)
            
            filehandler = open(new_result_dir+f'/best/best_costs_{best_method}.obj', 'wb')
            pickle.dump(best_costs, filehandler)
            
            filehandler = open(new_result_dir+f'/best/best_routes_{best_method}.obj', 'wb')
            pickle.dump(best_routes, filehandler)

            export_excel(best_routes, new_result_dir, best_method)

            clusters_DF(new_result_dir, inputData, best_clustersDICT, 
                        best_method, export=True, best=True)
            
        