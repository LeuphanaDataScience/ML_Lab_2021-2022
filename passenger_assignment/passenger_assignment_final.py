#import modules
import numpy as np
import pandas as pd
import osmnx as ox
from pandas.io.parsers import read_csv
import shapely as shp
import geopandas as gp
from matplotlib import pyplot as plt
from scipy import stats
import random
import os

from shapely import geometry

#working directory
os.getcwd()
os.chdir('C:\\Users\\cleme\\Documents\\GitHub\\ML_Lab_2021-2022\\passenger_assignment')


#%% read bus stop locations
def load_data(area, plot_graph = "n"):

    def plot_map(graph):
        fig, ax = ox.plot_graph(graph, show=False, close=False)
        plt.show()

    if area == "county":
        bus_stops_gdf = pd.read_csv('county_bus_stops.csv', index_col=False)
        bus_stops_geom = gp.read_file('county_bus_stops.shp')['geometry']
        bus_stops_gdf = gp.GeoDataFrame(bus_stops_gdf, geometry = bus_stops_geom)
        bus_stops_gdf = bus_stops_gdf.drop('Unnamed: 0', axis = 1)
        # get area of county Lüneburg and create "drive"-type network
        graph_lüneburg_gdf = ox.geocoder.geocode_to_gdf("R2084746", which_result=None, by_osmid=True, buffer_dist=None)
        graph_lüneburg_geom = graph_lüneburg_gdf['geometry'].iloc[0]
        graph = ox.graph_from_polygon(graph_lüneburg_geom, network_type ="drive")
        if plot_graph == "y":
            plot_map(graph)
        return [bus_stops_gdf, bus_stops_geom, graph]

    if area == "city":
        # get area of city of Lüneburg and create "drive"-type network
        bus_stops_loc_all = pd.read_csv("bus_stops_data.csv")

        #reduce to non-duplicate stations bus stops (667 stops)
        no_duplicates = np.array(pd.read_csv("stops_without_duplicates.csv", sep = ";")).flatten().tolist()
        bus_stops_loc = bus_stops_loc_all[bus_stops_loc_all["osmid"].isin(no_duplicates)]
        bus_stops_gdf = gp.GeoDataFrame(bus_stops_loc, geometry=gp.points_from_xy(bus_stops_loc.x, bus_stops_loc.y))
        bus_stops_gdf = bus_stops_gdf.drop(['x', 'y'], axis = 1)
        #hardcode wrong "Markt" coordinates into gdf
        markt_bus_stop = ox.geocoder.geocode_to_gdf("N415971821", which_result=None, by_osmid=True, buffer_dist=None)["geometry"]
        markt_index = bus_stops_gdf[bus_stops_gdf['name'] == 'Markt'].index[0]
        bus_stops_gdf.at[markt_index, 'geometry'] = markt_bus_stop.values[0]
        sparse_matrix = pd.read_csv("sparse_matrix_lueneburg.csv", sep = ";")
        bus_stops_gdf = bus_stops_gdf[bus_stops_gdf["name"].isin(sparse_matrix["name"])]
        bus_stops_geom = bus_stops_gdf['geometry']
        graph_lüneburg_gdf = ox.geocoder.geocode_to_gdf("R2420744", which_result=None, by_osmid=True, buffer_dist=None)
        graph_lüneburg_geom = graph_lüneburg_gdf['geometry'].iloc[0]
        graph = ox.graph_from_polygon(graph_lüneburg_geom, network_type ="drive")
        if plot_graph == "y":
            plot_map(graph)
        return [bus_stops_gdf, bus_stops_geom, graph]


data = load_data("county", "n")
data_city = load_data("city")

#%% sample passengers for all the bus stops

def sample_passengers(data, area = "county", mu = 3500, sigma = 0.001, seed = 2, lower = 0, upper = 3500, empty_stops = 0.25):
    
    bus_stops_gdf, bus_stops_geom, graph = data

    #exclude arena and depot from assignment
    arena_index = bus_stops_gdf[bus_stops_gdf["name"] == "Schlachthof"].index[0]
    depot_index = bus_stops_gdf[bus_stops_gdf["name"] == "Hagen Wendeplatz"].index[0]
    arena_depot_stops = bus_stops_gdf[bus_stops_gdf.index.isin([arena_index, depot_index])]
    bus_stops_geom = bus_stops_geom[bus_stops_geom.index.isin([arena_index, depot_index]) == False]
    bus_stops_gdf = bus_stops_gdf[bus_stops_gdf.index.isin([arena_index, depot_index]) == False]
    
    #set seed for reproducability
    np.random.seed(seed)
    district_data = pd.read_csv("population_per_district.csv", sep = ";")

    #read district data
    if area == "county":
        pop = np.array(district_data["pop"][0:26]) #ignore Amt Neuhaus
        district_data = district_data[0:26]        #ignore Amt Neuhaus

    if area == "city":
        pop = np.array(district_data["pop"][0:17])
        district_data = district_data[0:17]
    
    perc = np.floor(pop/sum(pop) * 10000) / 10000

    #compute visitors with truncated normal distribution
    visitors = int(stats.truncnorm.rvs((lower-mu)/sigma,(upper-mu)/sigma,loc=mu,scale=sigma,size=1))

    #approximately realistic sample of vistors per district 
    visitors_per_district = np.random.multinomial(visitors, perc)

    # distribute passengers over bus stops
    #assigned_passengers_gdf = gp.GeoDataFrame(bus_stops_geom)
    #assigned_passengers_gdf["passengers"] = np.zeros(len(bus_stops_geom), dtype = int)
    all_selected_stops = np.zeros(len(bus_stops_geom), dtype = int)

    #check if bus stop lie within district
    for i,id in enumerate(district_data["osm_id"]):
 
        district_gdf = ox.geocoder.geocode_to_gdf(id, which_result=None, by_osmid=True, buffer_dist=None)
 
        district_polygon = district_gdf['geometry'].iloc[0]
        is_in_dis = [district_polygon.contains(j) for j in bus_stops_geom]

        if any(is_in_dis) == False:
            print('empty')
            print(visitors_per_district[i])
            print(district_data["district_name"][i])
            continue
        stops_in_dis = bus_stops_geom[is_in_dis]

        #distribute passengers per district evenly among bus stops, but optiopnally have % of bus stops without passengers
        num_of_stops = len(stops_in_dis)
        num_of_stops_with_pass = num_of_stops - int(num_of_stops * empty_stops)

        passengers_at_stop = np.random.multinomial(int(visitors_per_district[i]), [1/num_of_stops_with_pass] * num_of_stops_with_pass)

        stops_with_pass_index = sorted(random.sample(list(range(num_of_stops)), num_of_stops_with_pass))

        selected_stops = np.where(np.array(is_in_dis) == True)[0][stops_with_pass_index]
        all_selected_stops[selected_stops] = passengers_at_stop

    #add new column to dataframe with passenger numbers
    bus_stops_gdf = bus_stops_gdf.assign(passengers = all_selected_stops)
    arena_depot_stops = arena_depot_stops.assign(passengers = np.zeros(2, dtype = int))
    bus_stops_gdf = pd.concat([bus_stops_gdf, arena_depot_stops]).sort_index()

    return bus_stops_gdf


gdf_with_pass = sample_passengers(data)
sum(gdf_with_pass['passengers'])

pd.DataFrame(gdf_with_pass).to_csv("scenario_538_stations_3.csv")

#%% plot heat map of passengers numbers at stops

def plot_heatmap(gdf_with_pass, data):
#select only stops that actually have passengers
    stop_with_passengers = gdf_with_pass["passengers"] > 0
    only_stops_with_passengers = gdf_with_pass[stop_with_passengers]

    #divide bus stops into classes at a rate of +2 passengers
    heat_classes = list(range(1,14,2))
    heat_classes.insert(0,0)
    heat_stops_list = []
    for i in range(len(heat_classes)):
        if i < len(heat_classes) - 1:
            bus_stop_class = only_stops_with_passengers[(only_stops_with_passengers["passengers"] > heat_classes[i]) & (only_stops_with_passengers["passengers"] <= heat_classes[i + 1])]
            heat_stops_list.append(bus_stop_class)
        else:
            bus_stop_class = only_stops_with_passengers[only_stops_with_passengers["passengers"] > heat_classes[i]]
            heat_stops_list.append(bus_stop_class)

    #plot map
    graph = data[2]

    colors = iter(plt.cm.viridis(np.linspace(0.5, 1, len(heat_classes))))
    fig, ax = ox.plot_graph(graph, show=False, close=False)
    for df in heat_stops_list:
        df.plot(ax=ax, markersize = 15, color=next(colors) , alpha=1, zorder=7)
    plt.show()


plot_heatmap(gdf_with_pass, data)