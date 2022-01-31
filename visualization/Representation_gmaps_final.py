#!/usr/bin/env python
# coding: utf-8

# In[4]:


get_ipython().system('pip install gmaps')
get_ipython().system('pip install googlemaps')
get_ipython().system('pip install google')


# In[6]:


import pandas as pd
import os
import gmaps
import googlemaps
import matplotlib
import pickle

from google.colab import output
output.enable_custom_widget_manager()

API_KEY = ''
gmaps.configure(api_key=API_KEY)
#!jupyter labextension install jupyter-matplotlib@0.3.0


# In[12]:


#Hagen Wendeplatz
starting_point = {
    'location': (53.2429833, 10.4517648)
}
#Schlachthof
ending_point = {
    'location': (53.2727519, 10.4249277)
}
depot_layer = gmaps.symbol_layer(
    [starting_point['location'], ending_point['location']], hover_text='Depot', info_box_content='Depot', 
    fill_color='white', stroke_color='red', scale=8
)


# In[10]:


with open('bus_stations_loc.pkl', 'rb') as f:
    bus_stations_loc = pickle.load(f)
with open('bus_stations_location.pkl', 'rb') as f:
    bus_stations_location = pickle.load(f)
with open('routes.pkl', 'rb') as f:
    routes = pickle.load(f)
with open('bus_stations.pkl', 'rb') as f:
    bus_stations = pickle.load(f)


# In[ ]:


bus_station_locations = [bus_station['location'] for bus_station in bus_stations_location]
bus_station_labels = [bus_station['name'] for bus_station in bus_stations_location]

bus_station_layer = gmaps.symbol_layer(
    bus_station_locations, hover_text=bus_station_labels, 
    fill_color='white', stroke_color='black', scale=4)


# In[ ]:


def set_fig():
  figure_layout = {
    'width': '1400px',
    'height': '800px',
    'border': '1px solid black',
    'padding': '1px'}
  fig = gmaps.figure(layout=figure_layout)
  fig.add_layer(depot_layer)
  #fig.add_layer(bus_station_layer)
  return fig
fig = set_fig()
fig


# In[ ]:


#Second route
waypoints = []
waypoints_names = []
for shipment_index in routes[1][1:-1]:
   waypoints.append(bus_stations_loc[bus_stations[shipment_index]])
   waypoints_names.append(bus_stations[shipment_index])
#print(waypoints_names)
#print(len(waypoints))
route_layer = gmaps.directions_layer(starting_point['location'], ending_point['location'], waypoints=waypoints, show_markers=True, 
                                         stroke_color='red', stroke_weight=5, stroke_opacity=0.5)
fig = set_fig()
fig.add_layer(route_layer)
fig


# In[ ]:


#All routes
colors = ['blue','red','green','#800080','#000080','#008080','#00FF00', '#808080',
          '#FFFF00', '#00FFFF', '#FF00FF', '#000000', '#800000', '#000080', '#800080']
fig = set_fig()
for vehicle_id in routes:
  waypoints = []
  for b_station in routes[vehicle_id][1:-1]:
    waypoints.append(bus_stations_loc[bus_stations[b_station]])
  route_layer = gmaps.directions_layer(starting_point['location'], ending_point['location'], waypoints = waypoints,
                                       show_markers = False, stroke_color = colors[vehicle_id], stroke_weight=5,
                                       stroke_opacity=0.5)
  fig.add_layer(route_layer)
fig


# In[ ]:


#First route
waypoints = []
waypoints_names = []
# skip depot (occupies first and last index)
for shipment_index in routes[0][1:-1]:
   waypoints.append(bus_stations_loc[bus_stations[shipment_index]])
   waypoints_names.append(bus_stations[shipment_index])
#print(waypoints_names)
#print(len(waypoints))
route_layer = gmaps.directions_layer(starting_point['location'], ending_point['location'], waypoints=waypoints, show_markers=True, 
                                         stroke_color='red', stroke_weight=5, stroke_opacity=0.5)
fig = set_fig()
fig.add_layer(route_layer)
fig


# In[ ]:


#Third route
waypoints = []
waypoints_names = []
for shipment_index in routes[2][1:-1]:
   waypoints.append(bus_stations_loc[bus_stations[shipment_index]])
   waypoints_names.append(bus_stations[shipment_index])
#print(waypoints_names)
#print(len(waypoints))
route_layer = gmaps.directions_layer(starting_point['location'], ending_point['location'], waypoints=waypoints, show_markers=True, 
                                         stroke_color='red', stroke_weight=5, stroke_opacity=0.5)
fig = set_fig()
fig.add_layer(route_layer)
fig

