# Approach combining Clustering & Ant Colony Optimization 

This approach is designed to find good bus routes based on different setups (people being assigned to bus stops where they start).
To run this, you need to follow these steps.

## ----- REQUIREMENTS ------

Used packages:

- pandas
- numpy
- copy
- collections
- scipy
- random 
- math
- shutil
- time
- pickle
- os
- warnings
- openpyxl
- osmnx

## ----- HOW TO USE -----

1) 	Put a csv file including bus stops and number of passengers assigned to them in the folder "data".
	Examples here are "scenario_1.csv", "scenario_2.csv" & "scenario_3.csv".

2)	In the file "run.py", specify following variables
	
### Basic
- scenario:	file name -> specify which scenario (setup)/ file you want to use as input (string)
- capacity:	bus capacity; specify number of passengers that should be at max in one bus (integer)
- src:		local project directory (string)

### Optional
- iterations:	specify number of iterations to run per clustering method (list of 2 integers)
- parsing:	can be enabled if run on a cluster for more convenience for specifying the input file (boolean)
- plot:		specify whether you want a visualization using OSM as html file (boolean)

3)	Run the script "run.py" 

4)	The results are stored in a new folder (name starts with date & time run was started),
	including a visualization with OSM (if plot = True)

--------------------------------------------------------------------------------------------------------

## ----- Additional -----

In the folder "ACO-PSO" there are approaches for finding good hyperparameter settings with Particle Swarm Optimization 
as well as new data for Landkreis Lüneburg including some more bus stations and a file for cleaning and adjusting 
the distance matrices extracted from OSM.