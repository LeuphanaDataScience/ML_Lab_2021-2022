"""
Extract OSM data through Overpass API

author :        @nikhil_nagar, adjusted by Rike
created :       28,April,2020
description :   data_task_02 to perform data fetch operations on Open Street Map through overpy.Overpass() API 
requirements :  overpy==0.4 (pip install overpy)
                requests    (pip install requests)
"""

import overpy           # to import the overpy module
import pandas as pd     # to import pandas library
import json 			# to import json
import requests			# to import requests



#this function gets the input from user.  INPUT = {laitutde, longitude, search_radius, option to specify the data domain like hospital,education etc.}
def get_input():
	print("\nEnter latitude \nArena: 53.2723116 \nCenter Lueneburg: 53.248706")
	latitude = input()
	print("\nEnter longitude \nArena: 10.4276049 \nCenter Lueneburg: 10.407855")
	longitude = input()
	print("\nEnter scan radius for target (in meters) (EXAMPLE->'50000 or 5000')")
	search_radius = input()
	print("\nEnter an option.(integer) :\n1. Houses \n2. Schools \n3. Road Network \n4. Bus Stops \n5. Bus Stations")
	option = int(input("\n>>>"))
	while option not in [1,2,3,4,5]: 
		print("Invalid Option. Try Again \n>>")
		option = int(input())
	return([latitude,longitude,search_radius,option])   #returns the list of user inputs



def get_houses_query(user_input):
	prefix = """[out:json][timeout:50];("""  				          	#this is string of syntex in 'Overpass QL' language
#	dormitory="""node["amenity"="university"](around:""" 	
	apartments="""node["building"="apartments"]; way["building"="apartments"](around:"""		  	  #this is string of syntex in 'Overpass QL' language
#	dormitory="""node["building"="dormitory"]; way["building"="dormitory"]; relation["building"="dormitory"](around:"""		  	  #this is string of syntex in 'Overpass QL' language
#	detached="""node["building"="detached"]; way["building"="detached"]; relation["building"="detached"](around:"""		  	  #this is string of syntex in 'Overpass QL' language
#	se_detached="""node["building"="semidetached_house"]; way["building"="semidetached_house"]; relation["building"="semidetached_house"](around:"""		  	  #this is string of syntex in 'Overpass QL' language

	suffix = """);out body;>;out skel qt;"""				        	  #this is string of syntex in 'Overpass QL' language
	q = user_input[2]+','+user_input[0]+','+user_input[1]    	  #(radius,latitude,longitude) in a string form the user input
	built_query = prefix + apartments+ q + ');' +suffix  #combine all the above strings in correct order to form a query
#	built_query = prefix + apartments+ q +');'+ dormitory+ q +');'+ detached+ q +');' + se_detached+ q +');' +suffix  #combine all the above strings in correct order to form a query
	return built_query											                    #returns the complete overpass query


#this function arranges user inputs to build the 'query'(in overpass QL language) for schools,college,university and returns the query
def get_schools_query(user_input):
	prefix = """[out:json][timeout:50];("""  				          	#this is string of syntex in 'Overpass QL' language
	schoolnode="""node["amenity"="school"](around:""" 		  	  #this is string of syntex in 'Overpass QL' language
	collegenode="""node["amenity"="college"](around:"""		  	  #this is string of syntex in 'Overpass QL' language
	suffix = """);out body;>;out skel qt;"""				        	  #this is string of syntex in 'Overpass QL' language
	q = user_input[2]+','+user_input[0]+','+user_input[1]    	  #(radius,latitude,longitude) in a string form the user input
	built_query = prefix + schoolnode+ q +');'+ collegenode+ q +');'+ suffix  #combine all the above strings in correct order to form a query
	return built_query											                    #returns the complete overpass query



def get_busStops_query(user_input):
	prefix = """[out:json][timeout:50];(node["highway"="bus_stop"](around:""" #this is string of syntex in 'Overpass QL' language
	suffix = """););out body;>;out skel qt;"""							      #this is string of syntex in 'Overpass QL' language
	q = user_input[2]+','+user_input[0]+','+user_input[1]       #(radius,latitude,longitude) in a string from the user input
	built_query = prefix + q + suffix                           #arrange all above strings into a correct order to form complete query
	return built_query 			



def get_busStations_query(user_input):
	prefix = """[out:json][timeout:50];(node["amenity"="bus_station"](around:""" #this is string of syntex in 'Overpass QL' language
	suffix = """););out body;>;out skel qt;"""							      #this is string of syntex in 'Overpass QL' language
	q = user_input[2]+','+user_input[0]+','+user_input[1]       #(radius,latitude,longitude) in a string from the user input
	built_query = prefix + q + suffix                           #arrange all above strings into a correct order to form complete query
	return built_query 	


#this function arrenge user inputs to build the 'query' (in overpass QL language) for roads data and returns the query
def get_roads_query(user_input):
	prefix = """[out:json][timeout:50];(way["highway"](around:""" #this is string of syntex in 'Overpass QL' language
	suffix = """););out body;"""							   	  #this is string of syntex in 'Overpass QL' language
	q = user_input[2]+','+user_input[0]+','+user_input[1]         #(radius,latitude,longitude) in a string from the user input
	built_query = prefix + q + suffix                             #arrange all above strings into a correct order to form complete query
	return built_query                                            #return the built query further



# this function uses the overpy.Overpass API to send a query and get the response from overpass servers in json format and then it extract the nodes(hospitals , schools) data to a csv file.
def extract_nodes_data_from_OSM(built_query):
	api = overpy.Overpass()                       # creating a overpass API instance 
	result = api.query(built_query)               # get result from API by sending the query to overpass servers
	list_of_node_tags = []                        # initializing empty list , we'll use it to form a dataframe .
	for node in result.nodes:                     # from each node , get the all tags information
		node.tags['latitude'] =  node.lat
		node.tags['longitude'] = node.lon
		node.tags['id'] = node.id
		list_of_node_tags.append(node.tags)
	data_frame = pd.DataFrame(list_of_node_tags)  # forming a pandas dataframe using list of dictionaries
	data_frame.to_csv('output_data.csv')
	print("\nCSV file created- 'output_data.csv'. Check the file in current directory.")
	return data_frame                             # return data frame if you want to use it further in main function.



# this function only extracts the raw  json data from overpass api through get request
def extract_raw_data_from_OSM(built_query):
	overpass_url = "http://overpass-api.de/api/interpreter" 				   # url of overpass api
	response = requests.get(overpass_url,params={'data': built_query})         # sending a get request and passing the overpass query as data parameter in url
	print(response.text)
	json_data = response.json()
	with open("output_data.json", "w") as outfile:  						   # writing the json output to a file
		json.dump(json_data, outfile)
	print("Raw Data extraction successfull!  check 'output_data.json' file.")
	return json_data
 
	
	


if __name__ == '__main__':  # main function to act accordingly to the user's input.

	user_input=get_input()
	option = user_input[3]
	if(option==1):
		query = get_houses_query(user_input)
		data_frame = extract_raw_data_from_OSM(query)
	elif(option==2):
		query = get_schools_query(user_input)
		data_frame= extract_nodes_data_from_OSM(query)
	elif(option==3):
		query = get_roads_query(user_input)
		data_frame = extract_raw_data_from_OSM(query)
	elif(option==4):
		query = get_busStops_query(user_input)
		data_frame = extract_nodes_data_from_OSM(query)
	elif(option==5):
		query = get_busStations_query(user_input)
		data_frame= extract_nodes_data_from_OSM(query)
	print("Note: \n1. Please rename the output file, so that it can't be overwritten when you execute this program again.\n2. output file shouldn't remain open while running this program, because writing will perform on the output file while executing the program next time. ")


'''
Uncomment only when needed

path  =

# to explore the JSON output:
with open(path) as f:
  data = json.load(f)
print(data)

# Pretty Printing JSON string back
print(json.dumps(data, indent=4, sort_keys=True))

for i in data['emp_details']:
	print(i)
'''
