### Approach combining Clustering & Ant Colony Optimization to solve bus routing problem ###

This approach is designed to find good bus routes based on different setups (people being assigned to bus stops where they start).
To run this, you need to follow these steps.

----- HOW TO USE -----

1) 	Put a csv file including bus stops and number of passengers assigned to them in the folder "data".
	Examples here are "scenario_1.csv", "scenario_2.csv" & "scenario_3.csv".

2)	In the file "run.py", specify following variables

Elementary (needs to be set to run on local machine)
	src:		project directory (string)
	
Basic
	Scenario:	file name -> specify which scenario (setup)/ file you want to use as input (string)
	iterations:	specify number of iterations to run per clustering method (integer)
	capacity:	bus capacity; specify number of passengers that should be at max in one bus (integer)
	methods:	specify which methods should be used in the clustering step (need to be selected from the following):
			["CONVEX_HULL_CLOUD_random", "CONVEX_HULL_SEQUENCE_random","CONVEX_HULL_A_STAR_random",
			"CONVEX_HULL_CLOUD_distance",  "CONVEX_HULL_SEQUENCE_distance", "CONVEX_HULL_A_STAR_distance", 
			"CLOUD", "SEQUENCE", "A_STAR", "A_STAR_K_NEXT"] (list)

Advanced
	random_only:	specify whether you only want to use clustering methods with random initialization (boolean)
	previous_run:	specify whether you want to try to improve the solution by running more iterations of the ACO 
			on the clustering which for which the cost was minimal
			if != False, specify which previous run to use (boolean/string)
	overall:	only matters if previous_run != False; specify whether you want to run the ACO again 
			on the overall best clustering solution (True) or on the best ones per clustering method (False) (boolean)
	testing:	indicating whether you only want to to a run for testing purposes with reduced
			amount of methods & little iterations (boolean)

3)	Run the script "run.py"

4)	The results are stored in a new folder (name starts with date & time run was started)

--------------------------------------------------------------------------------------------------------

----- TECHNICAL BACKGROUND -----

Scripts & Functions

data_prep.dataprep_CL(src, scenario)
Variables:
	src: project directory
	scenario: to be chosen
Output:
	matrix: matrix (matrix of distances between bus stops)
	distances_to_arena: list of distances of all stops to arena
	bus_names: list of all bus stop names
	inputFile: the raw input file as a pd DataFrame


What happens when you run "run.py"?

(TODO)

1) dataprep_CL
2) runCluster
3) dataprep_ACO
4) 