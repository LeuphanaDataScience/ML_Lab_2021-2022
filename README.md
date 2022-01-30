# ML_Lab_2021-2022

This repository is meant to be the hub for the code related to the course "Machine Learning Lab", winter term 2021/2022.

## Project Outline
The mission was to produce a flexible solution for a bus company to provide a bus service for events in new arena.
The input for the algorithms consists of csv files with a number of passengers assigned to the different bus stations.
The output should include routes for several buses (with a fixed capacity) picking up all customers and bringing them to the arena.
The objective was to find a good route (a short one).

## Approaches
Multiple approaches were implemented:
- Linear Programming using Pyomo 
- combined approach using clustering and Ant Colony Optimization (CL-ACO)
- combined approach using clustering and Simulated Anealing (CL-SA)
- ***Linear Programming using PULP (unfinished)***

The data extracted from Open Street Map can be found in "osmnx_distance_matrices" and sample data in "passenger_assignment"
