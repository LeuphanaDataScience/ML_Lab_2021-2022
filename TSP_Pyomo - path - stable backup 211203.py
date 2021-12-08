# -*- coding: utf-8 -*-
"""
Created on Mon Nov 29 14:06:51 2021

@author: Christian
"""

#basis: http://www.opl.ufc.br/post/tsp/



import pandas as pd
import time
import numpy as np
import pyomo.environ as pyEnv


raw_data = pd.read_csv('district_data.csv', sep = ',')

df = raw_data.copy()

columns = df['name']
df.drop('name', axis = 1, inplace = True)
cost_table = df.values

cost_table[cost_table == 0.0] = 9999

duration = []

start = time.time()
cost_table = cost_table[:15,:15]

n = cost_table.shape[0]





cost_matrix = np.asmatrix(cost_table)
#cost_matrix = cost_matrix.astype(int)




#from pyomo.opt import SolverFactory

#Model
model = pyEnv.ConcreteModel() # ConcreteModel() creates the model

#Setting Target Destination
T = 5

#Indexes for the cities
model.M = pyEnv.RangeSet(n) # RangeSet(n) creates an index from 1 to n             
model.N = pyEnv.RangeSet(n)
model.TARGET = pyEnv.RangeSet(T,T) #definition of Target

#Index for the dummy variable u
model.U = pyEnv.RangeSet(2,n) # RangeSet(2,n) creates an index from 2 to n.




#Decision variables xij
model.x = pyEnv.Var(model.N, model.M, within=pyEnv.Binary) 
# Var(model.N,model.M, within=pyEnv.Binary) creates binary decision variables of size

#Dummy variable ui
model.u = pyEnv.Var(model.N, within=pyEnv.NonNegativeIntegers,bounds=(0,n-1))
# Var(model.N, within=pyEnv.NonNegativeIntegers,bounds=(0,n-1)) creates  
# non-negative integer decision variables that can only assume values between 0 and n-1.



#Cost Matrix(file) cij
model.d = pyEnv.Param(model.N, model.M,initialize=lambda model, i, j: cost_matrix[i-1,j-1])
# Param(modelo.N, model.M,initialize=lambda model, i, j: cost_matrix[i-1][j-1]) provides a  
# n x m parameter to the model using a lambda function.



#Objective Function

def obj_func(model):
    liste = []
    for i in model.N:
        for j in model.M:
            if i!=T:
                liste.append(model.x[i,j] * model.d[i,j])    
    return sum(liste)

model.objective = pyEnv.Objective(rule=obj_func,sense=pyEnv.minimize)


#constraints
def rule_const1(model,M):
    liste = []
    for i in model.N:
        if i!=M:
            liste.append(model.x[i,M])
    return sum(liste) == 1

model.const1 = pyEnv.Constraint(model.M,rule=rule_const1)


def rule_const2(model,N):
    liste = []
    for j in model.M:
        if j!=N:
            liste.append(model.x[N,j])
    return sum(liste) == 1

model.rest2 = pyEnv.Constraint(model.N,rule=rule_const2)


def rule_const3(model,i,j):
    if i!=j: 
        return model.u[i] - model.u[j] + model.x[i,j] * n <= n-1
    else:
        #Yeah, this else doesn't say anything
        return model.u[i] - model.u[i] == 0 
    
model.rest3 = pyEnv.Constraint(model.U,model.N,rule=rule_const3)



def rule_const4(model):
    return sum(model.x[i,1] for i in [T]) == 1

model.rest4 = pyEnv.Constraint(rule = rule_const4) #setting target node to T as defined before


#Prints the entire model
#model.pprint()


#Solves
solver = pyEnv.SolverFactory('cplex')
result = solver.solve(model,tee = False)

#Prints the results
print(result)


List = list(model.x.keys())
List2 = []
for i in List:
    if model.x[i]() == 1:
        List2.append(i)
        print(i,'--', model.x[i]())
ende = time.time()
duration.append(ende - start)
print(duration[-1])


bus_route = [1, List2[0][1]]
for _ in range(len(List2)): #append tuple (i,j), for which j=i
    for i in range(len(List2)):
        if List2[i][0] == bus_route[-1] and List2[i][1] not in bus_route:
            bus_route.append(List2[i][1])
            #print(bus_route)
nr = 1    
for element in bus_route:
    print(nr,': ',columns.values[element -1])
    nr +=1

    
class RouteIncompleteError(Exception):
    pass   
if len(bus_route) != n:
    raise RouteIncompleteError("Route incomplete, edge missing! Change amount of nodes or chosen target.")
    

        
        
    
    


    
















