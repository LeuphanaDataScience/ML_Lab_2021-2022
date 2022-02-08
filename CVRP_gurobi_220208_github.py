# -*- coding: utf-8 -*-
"""
Created on Tue Dec 14 13:24:13 2021

@author: Christian
"""
import pandas as pd
import time
import numpy as np
import matplotlib.pyplot as plt
import os

def data_preparation():
       
    #DataPreparation Distances
    raw_data_distances = pd.read_csv(os.getcwd() + r'\Data\full_distance_matrix_lueneburg.csv', sep = ';')
    
    liste = raw_data_distances.columns.values
    liste[0] = 'names'
    df = raw_data_distances.copy()
    df.columns = liste
    
    columns = liste[1:]
    df.drop(columns= 'names', inplace = True)
    cost_table = df.values
    
    cost_table[cost_table == 0.0] = 9999
    
    cost_matrix = np.asmatrix(cost_table[:,:])
    
    #from cost_table to cost_dict
    cost_dict = {}
    for i in range(0, cost_matrix.shape[0]):
        for j in range(0, cost_matrix.shape[0]):
            cost_dict[(i,j)] = cost_matrix[i,j]
    
    
    #DataPreparation Passengers
    Set = 1
    
    if Set == 1:
        raw_data_passengers = pd.read_csv(path + r'\Data\city_stops_and_passengers_1.csv', sep = ',')
    elif Set == 2:
        raw_data_passengers = pd.read_csv(path + r'\Data\city_stops_and_passengers_2.csv', sep = ',')
    elif Set == 3:
        raw_data_passengers = pd.read_csv(path + r'\Data\city_stops_and_passengers_3.csv', sep = ',')
    elif Set == 4:
        raw_data_passengers = pd.read_csv(path + r'\Data\scenario_1.csv', sep = ',')       
    
    coordinates = {}   
    for i in range(raw_data_passengers.shape[0]):
        coordinates[i] = raw_data_passengers['geometry'].values[i]
        coordinates[i] = coordinates[i][7:-2].split(' ') 
    
    passenger_table = []    
    for i in range(raw_data_passengers.shape[0]):
        passenger_table.append([i,raw_data_passengers['passengers'].values[i]])

    
    #from passenger_table to passenger_dict
    passenger_dict = {}
    for i in range(len(passenger_table)):
        passenger_dict[i] = passenger_table[i][1]   
    
    
    return cost_dict, passenger_dict, coordinates


def max_k_filter(passenger_dict, cost_dict, k_normal, k_overcrowded, arena):
    routes_overcrowded = {}
    distance_overcrowded = 0
    no_vehicles_overcrowded = 0
    for node in passenger_dict:
        while passenger_dict[node] > k_normal:
            routes_overcrowded['O_' + str(no_vehicles_overcrowded)] = [node, arena]
            distance_overcrowded +=  cost_dict[(node,arena)] 
            passenger_dict[node]+= -k_overcrowded
            no_vehicles_overcrowded += 1
    return passenger_dict, routes_overcrowded, distance_overcrowded

def CVRP_gurobipy(cost_dict, passenger_dict, arena = 164, k = 70, time_limit = 30, filter_on_off = True):
    #determine n
    i_max = 0
    for i,j in cost_dict:
        if i > i_max:
            i_max = i + 1
    n = i_max + 1
    
    #remove stops with no passengers
    H = [i for i in range(n) if i != arena] #Assign Bus Stops
    
    for i in range(n):
        if passenger_dict[i] == 0 and i in H:
                H.remove(i)
    
    cost_dict_copy = cost_dict.copy()
    for i,j in cost_dict_copy:
        if i not in H + [arena] and j not in H + [arena]:
            del cost_dict[i,j]
    
    
    
    #Update n
    i_max = 0
    for i,j in cost_dict:
        if i > i_max:
            i_max = i + 1
    n = i_max + 1
    
    #######################################
    #Pre-Processing k<p_i
    
    #filter_on_off = True
    if filter_on_off:
        passenger_dict, routes_overcrowded, distance_overcrowded  = max_k_filter(passenger_dict, cost_dict, k, 70, arena)
    else:
        routes_overcrowded = {}
        distance_overcrowded = 0
    #######################################

    
    N = [arena] + H     #Add Target/ Depot to nodes
    G = [(i, j) for i in N for j in N if i != j] #Set up full Graph for Nodes N
    d = cost_dict #set Distances as Cost Parameter
    k = k #Set maximal Bus Capacity
    p = passenger_dict #Assign passengers to Bus Stops
    
    # to take a depot into account, the distances from arena to first stop are substituted by distances from depot to first stop
    # depot is not further considered but imaginally existing as arena
    
    from gurobipy import Model, GRB, quicksum  
    
    mdl = Model('CVRP')  
    
    
    #Variables and Parameters
    x = mdl.addVars(G, vtype=GRB.BINARY)
    u = mdl.addVars(H, vtype=GRB.CONTINUOUS)
    
    #Objective Function
    mdl.modelSense = GRB.MINIMIZE
    mdl.setObjective(quicksum(x[i, j]*d[i, j] for i, j in G if i!= arena) + quicksum(x[i, j]*2500 for i, j in G if i== arena))
    
    #Constraints
    mdl.addConstrs(quicksum(x[i, j] for j in N if j != i) == 1 for i in H)
    mdl.addConstrs(quicksum(x[i, j] for i in N if i != j) == 1 for j in H)
    mdl.addConstrs((x[i, j] == 1) >> (u[i]+p[j] == u[j]) for i, j in G if i != arena and j != arena)
    mdl.addConstrs(u[i] >= p[i] for i in H)
    mdl.addConstrs(u[i] <= k for i in H)
    
    mdl.Params.MIPGap = .5#0.1
    mdl.Params.TimeLimit = time_limit # seconds
    mdl.optimize()
       
    active_arcs = [a for a in G if x[a].x > 0.99]
    del mdl
    return active_arcs, passenger_dict, distance_overcrowded, routes_overcrowded, k

def evaluation(active_arcs, cost_dict, passenger_dict, distance_overcrowded, routes_overcrowded, k, arena):
    total_distance = 0 + distance_overcrowded
    for i,j in active_arcs:
        if i != arena:
            total_distance += cost_dict[(i,j)]
    
    no_vehicles_overcrowded = 0
    for key in routes_overcrowded:  #taking care of routes of overcrwoded nodes
        no_vehicles_overcrowded +=1
    
        
    
    first_stops = []
    no_vehicles = 0
    for arcs in active_arcs:
        if arcs[0] == arena:
            no_vehicles += 1
            first_stops.append(arcs[1])


    routes = {}

    for b in range(no_vehicles):
        if b not in routes:
            routes[b] = [first_stops[b]]
            while routes[b][-1]!= arena:
                for arc in active_arcs:
                    i,j = arc
                    if i == routes[b][-1]:
                        routes[b].append(arc[1])
                        
    
    vehicles = {}
    passengers = 0
    for b in routes:
        passengers_per_bus = 0
        for bus_stop in routes[b]:
            passengers_per_bus += passenger_dict[bus_stop]
            passengers += passenger_dict[bus_stop]
        vehicles[b] = passengers_per_bus
    for b in routes_overcrowded:
        vehicles[b] = k
        passengers += k
        
    print(passengers)

    return total_distance, routes, routes_overcrowded, no_vehicles, no_vehicles_overcrowded, vehicles


## main execution

cost_dict, passenger_dict_raw, coordinates = data_preparation()

arena = 164

if True:
    #manipulating passenger sample for testing
    passenger_dict_raw[arena] = 0 #no passengers at target destination
    #passenger_dict_raw[57] = 147 #overcrowded bus stop

passenger_dict = passenger_dict_raw.copy()

#Filtering and Optimization
active_arcs, passenger_dict_new, distance_overcrowded, routes_overcrowded, k = CVRP_gurobipy(cost_dict.copy(), 
                                                                                      passenger_dict, arena = arena,
                                                                                      k=70, time_limit = 10)
# Evaluation
total_distance, routes, routes_overcrowded, no_vehicles, no_vehicles_overcrowded, vehicles = evaluation(active_arcs, cost_dict, passenger_dict, distance_overcrowded, routes_overcrowded, k, arena)





# Export
# open file for writing
f = open("routes_"+ str(time.time()) + '.txt',"w")
f.write( str(routes) )
f.write('\n')
f.write(str(passenger_dict_raw))
f.close()


print('##################')
print('#### RESULTS ####')
print('##################')
print('total distance: ', total_distance)
print('amount of vehicles (normal): ', no_vehicles)
print('amount of vehicles (overcrowded): ', no_vehicles_overcrowded)
number_of_passengers = 0
for key in passenger_dict_raw:
    number_of_passengers += passenger_dict_raw[key]
print('number of passengers: ', number_of_passengers)
print('routes: ')
print('vehicle -- passengers per bus -- route')
passengers_check = 0
for bus in routes_overcrowded:
    print(bus, ' -- ', vehicles[bus], '--', routes_overcrowded[bus])
    passengers_check += vehicles[bus]
for bus in routes:
    print(bus, ' -- ', vehicles[bus], '--', routes[bus])
    passengers_check += vehicles[bus]
print(passengers_check,'/', number_of_passengers,' passengers collected.')
        

'''
fig = []
ax = []

i=0
for bus in routes:
    fig.append('a')
    ax.append('a')
    fig[-1], ax[-1] = plt.subplots()
    route_coodinate_X = []
    route_coodinate_Y = []  
    for element in routes[bus]:
        route_coodinate_X.append(float(coordinates[element][0]))
        route_coodinate_Y.append(float(coordinates[element][1]))
    ax[-1] = plt.plot(route_coodinate_X, route_coodinate_Y, '-')
    ax[-1] = plt.plot(route_coodinate_X[-1], route_coodinate_Y[-1], 'ro')
    #ax = plt.xlim([10.35,10.5])
    fig[-1] = plt.savefig('bus_routes_' + str(i) + '.jpg', dpi = 1000)
    i +=1
'''






