# -*- coding: utf-8 -*-
"""
Created on Wed Jan 12 17:15:44 2022

@author: eirene
"""

#%% Setup

import os
import warnings
import pandas as pd
import time
import shutil
import math as mt
import pickle

warnings.filterwarnings("ignore") # don't print warnings
os.chdir(os.path.dirname(os.path.realpath(__file__)))

from dataprep import dataprep, clusters_DF, dataprep_ACO
from Clustering import runCluster
from ACO import runACO


#%% Main pipeline

def Run(src, 
        iterations, 
        scenario, 
        capacity, 
        methods, 
        random_only=False, 
        previous_run=False, 
        overall=True,
        testing=False):
        
            ####### SETUP #################################################################
            
            # Automatically (re-)define variables
            if random_only == True:
                methods = methods[0:3]  
            if testing == True:
                iterations = 2
                methods = methods[2:3]   
            
            # for displaying progress
            T_initial = time.time()                 
         
            # Create folder for new results
            time_now = time.localtime() 
            time_string = time.strftime("%d-%m-%Y_%H-%M", time_now)
            
            if previous_run == False:    
                new_result_dir = src+f'results/{time_string}/'    
            if previous_run != False:
                new_result_dir = src+f'results/{time_string}_refined_{previous_run}/'
        
            # Delete directory if it is already existent...
            if os.path.isdir(new_result_dir):
                shutil.rmtree(new_result_dir)
            # ... for being able to create new one    
            os.makedirs(new_result_dir)
            os.makedirs(new_result_dir+'/best')
            
            # re-define methods based on those that were used previously 
            if previous_run != False:
                methods = []
                for file in os.listdir(src+"results/"+previous_run+"/best"):
                    if overall == True:
                        if file.startswith("bestClusterOverall"):
                            filename = file
                            methods.append(filename[23:-5])
                    else:
                        if file.startswith("bestCluster") and not(file.startswith("bestClusterOverall")):
                            filename = file
                            methods.append(filename[14:-4])
            
            # initialize variables
            routes = {}
            costs = {}
            comp_time = {}
            
            best_routes = []
            best_costs_method = int(99999999999999)
            best_costs = int(99999999999999)
            
            its_total = len(methods)*iterations
            
            inputData = dataprep(src, scenario)

        # -----------------------------------------------------------------------------
            for method in range(0, len(methods)):
                
                methodName = methods[method]
                
                # initialize variables
                best_costs_method = int(99999999999999)  
                costs[methodName] = []
                routes[methodName] = []
                comp_time[methodName] = []
                
                
                for iteration in range(iterations): 
                    
                    # To display progress  
                    print(f'Current method: {methods[method]} (Method {method+1}/{len(methods)}), \nIteration {iteration+1}/{iterations}')              
                    T_now = time.time()
                    t0 = time.time() 
                 
        ####### DATA PRE-PROCESSING ###################################################
                    
                    # Do clustering if not done before
                    
                    if previous_run==False:
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
                               
          #              else: # -> load clustering from previous iteration
          #                  clustersDF = pd.read_csv(src + f'tmp/tmp_{methodName}.csv')
          #                  clustersDF = clustersDF.set_index('name')
                      
                    else:
                         clustersDF = pd.read_csv(src + f'results/{previous_run}/best/best_clusters_{methodName}.csv')
                         clustersDF = clustersDF.set_index('name')
                         clustersDF.to_csv(src+ f'tmp/tmp_{methodName}.csv')
                 
        # -----------------------------------------------------------------------------
        
        
        ####### ACO ###################################################################
        
                    # Data pre-processing for ACO
                    inputACO = dataprep_ACO(src, inputData, clustersDF)
                    
                    T_passed = T_now - T_initial
                    if T_passed >= 1:
                        its = method*iterations+iteration
                        time_per_it = mt.floor(T_passed/(its))
                        time_left = time_per_it*(its_total-its)
                        print(f'Time passed: {mt.floor(T_passed)}s ({time_per_it}s/iteration)')
                        print(f'Estimated time left: {mt.floor(time_left/60)} minutes')
                    
                    # ACO step
                    route, cost = runACO(inputACO)
                        
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
                    #    best_routes_method = route
                    #...
                        
                    # to find best solution overall
                if best_costs_method < best_costs:
                    best_costs = cost
                    best_routes = route
                    best_clustersDICT = clustersDICT
                    best_method = methodName
                    
            # save other results outside python
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
            
            clusters_DF(new_result_dir, inputData, best_clustersDICT, 
                        best_method, export=True, best=True)
            
        
        
        
        








'''
For trying out step-by-step

# Clustering step
clustersDICT = runCluster(src, inputData, method, capacity)

# Export clusters (as csv)
clustersDF = clusters_DF(src, inputData, clustersDICT, method)

# Data pre-processing for ACO
inputACO = dataprep_ACO(src, inputData, clustersDF)


# ACO step
best_routes_all_clusters, total_cost_all_clusters = runACO(inputACO)


# Maybe implement later
                      
# export results        
if testing != False:
    current_result_dir = src+'results/mostRecent'
    if os.path.isdir(current_result_dir):
        shutil.rmtree(current_result_dir)
    os.makedirs(current_result_dir)
    os.makedirs(current_result_dir+'best')
    
    filehandler = open(current_result_dir+f'/best/best_costs_{methods[i]}.obj', 'wb')
    pickle.dump(best_costs_method, filehandler)
    filehandler = open(current_result_dir+f'/best/best_routes_{methods[i]}.obj', 'wb')
    pickle.dump(best_routes_method, filehandler)


filehandler = open(new_result_dir+f'best/best_costs_{methods[i]}.obj', 'wb')
pickle.dump(best_costs_method, filehandler)
filehandler = open(new_result_dir+f'best/best_routes_{methods[i]}.obj', 'wb')
pickle.dump(best_routes_method, filehandler)
'''
