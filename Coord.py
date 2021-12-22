# -*- coding: utf-8 -*-
"""
Created on Tue Aug 10 12:52:51 2021

@author: spenc
"""

import random as rand  
import math, time
from fastkml import kml
from shapely.geometry import Point, LineString, Polygon
import pandas as pd  # note that this is the accepted community naming convention to import pandas
import numpy as np
import matplotlib.pyplot as plt

class Coord:
    '''An improved class to represent lat/lon values.'''
    
    def __init__(self,lat,lon):
        self.lat = float(lat)  # make sure it's a float
        self.lon = float(lon)
        
    # Follows the specification described in the Aviation Formulary v1.46
    # by Ed Williams (originally at http://williams.best.vwh.net/avform.htm)
    def dist_to(self, other):
        lat1 = self.lat
        lon1 = self.lon
        lat2 = other.lat
        lon2 = other.lon
        
        distance = math.sqrt((lat2-lat1)**2 + (lon2 - lon1)**2)

        return distance
    

    def __str__(self):
        return "(%f,%f)" % (self.lat,self.lon)
    
    def __repr__(self):
        return "Coord(%f,%f)" % (self.lat,self.lon)        

    def deg2rad(degrees):
        '''Converts degrees (in decimal) to radians.'''
        return (math.pi/180)*degrees

    
    def bearing(self,other):
        '''Calculates relative bearing to other object'''
        
        lat1 = Coord.deg2rad(self.lat)
        lon1 = Coord.deg2rad(self.lon)
        lat2 = Coord.deg2rad(other.lat)
        lon2 = Coord.deg2rad(other.lon)
        x = lon2 - lon1
        y = lat2 - lat1
        if x == 0 and y == 0:
            return 0
        if x >= 0 and y >= 0:
            return int(round(math.degrees(math.atan(x/y))))
        if x >= 0 and y < 0:
            return int(180 + round(math.degrees(math.atan(x/y))))
        if x < 0 and y >= 0:
            return int(360 + round(math.degrees(math.atan(x/y))))
        if x < 0 and y < 0:
            return int(180 + round(math.degrees(math.atan(x/y))))
        
                
    def bearing_to_rads(self, crs):
        '''Converts nautical bearing to unit circle radians'''
        if crs == 360:
            crs = 0
            
        if crs < 90:
            crs = (math.pi/180)*(90-crs)
        #elif crs == 90:
            #crs = (math.pi/180)*0
        #elif crs >90 and crs < 180:
            #crs = (math.pi/180)*(360 - (crs - 90))
        #elif crs == 180:
            #crs = (math.pi/180)*(270)
        #elif crs > 180 and crs < 270:
            #crs = (math.pi/180)*(180 + 90 - (crs - 180))
        #elif crs == 270:
            #crs = (math.pi/180)*180
        #elif crs > 270 and crs < 360:
            #crs = (math.pi/180)*(360 - crs + 90)
        else:
            crs = (math.pi/180)*(450 - crs)
    
        return crs
    
    def rel_bearing_to(self,crs,brg):
        '''Calculates relative bearing to tgt with ownship head at 0'''
        
        true_bearing = float(brg)
        
        relative_bearing = true_bearing - float(crs) 
        
        if relative_bearing > 180:
            return relative_bearing - 360
        elif relative_bearing <= 180 and relative_bearing > -180:
            return relative_bearing
        else:
            return relative_bearing + 360
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        