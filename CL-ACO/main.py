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
            
            print("Setup")
            print("Scenario: " + scenario)
            print("Identifier: " + identifier)
            
            # for displaying progress
            T_initial = time.time()                 
         
            # Create folder for new OUTPUT
            time_now = time.localtime() 
            time_string = time.strftime("%d-%m-%Y_%H-%M", time_now)
            dir_name = time_string + "_" + scenario[:-4]
            new_result_dir = src+f'OUTPUT/{dir_name}/'    

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
            best_costs = int(99999999999999)
            
            its_total = np.sum(iterations)
            
            inputData = dataprep(src, scenario)
            
            its = 0
        # -----------------------------------------------------------------------------
            for method in range(0, len(methods)):
                
                methodName = methods[method]
                
                # initialize variables
                costs[methodName] = []
                routes[methodName] = []
                comp_time[methodName] = []
                
                
                for iteration in range(iterations[method]): 
                    
                    its += 1
                    # To display progress  
                    print(f'Current method: {methodName} (Method {method+1}/{len(methods)})')
                    print(f'Iteration {iteration+1}/{iterations[method]}\n')              
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
                    
                    # ACO step
                    route, cost = runACO(inputACO, identifier = identifier)
                        
                    # Calculate computational time 
                    T_now = time.time()
                    T_passed = T_now - T_initial
                    if T_passed >= 1:
                        time_per_it = mt.floor(T_passed/(its))
                        time_left = time_per_it*(its_total-its)
                        print(f'Time passed: {mt.floor(T_passed)}s')
                        print(f'Estimated time left: {mt.floor(time_left/60)} minutes')
                    
                    t1 = time.time()
                    ET = t1-t0

                    T_passed = T_now - T_initial
                    
                    # add current results to result dictonary
                    costs[methodName].append(cost)
                    routes[methodName].append(route)
                    comp_time[methodName].append(ET)
            
                    # to find best solution overall
                    if cost < best_costs:
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
            
          #  INFO_text = open(new_result_dir+"INFO.txt","w+")
            
          # Create file containing infos about run
            with open(new_result_dir+"INFO.txt","w+") as INFO:
                INFO.write("Scenario: "+scenario)
                INFO.write("\nComputational Time: "+str(mt.floor(T_passed))+"sec")
                INFO.write("\nClustering Methods: "+str(methods))
                INFO.write("\nIterations: "+str(iterations))
        