# -*- coding: utf-8 -*-
"""
Created on Sat Dec 18 21:08:34 2021

@author: spenc
"""

import random as rand  
import math, time
from fastkml import kml
from shapely.geometry import Point, LineString, Polygon
import pandas as pd  
import numpy as np
import matplotlib.pyplot as plt

from Coord import *



class Torpedo:
    '''Improved class to store Merchant Ship data'''

    
    def __init__(self, name, loc,course = 90, speed=16):
        self.name = name
        self.loc = loc
        self.spd = speed
        self.crs = course
        
    def bearing_to_rads(self, crs):
        '''Converts nautical bearing to unit circle radians'''
        if crs == 360:
            crs = 0
            
        if crs < 90:
            crs = (math.pi/180)*(90-crs)
        elif crs == 90:
            crs = (math.pi/180)*0
        elif crs >90 and crs < 180:
            crs = (math.pi/180)*(360 - (crs - 90))
        elif crs == 180:
            crs = (math.pi/180)*(270)
        elif crs > 180 and crs < 270:
            crs = (math.pi/180)*(180 + 90 - (crs - 180))
        elif crs == 270:
            crs = (math.pi/180)*180
        elif crs > 270 and crs < 360:
            crs = (math.pi/180)*(360 - crs + 90)
        else:
            crs = (math.pi/180)*90
    
        return crs

            
    def update_position(self):
        '''Geometric Hops'''
        
        radians = self.bearing_to_rads(self.crs)
        d = self.spd*(1/3600)
        
        updated_lat = self.loc.lat + math.sin(radians)*d
        updated_lon = self.loc.lon + math.cos(radians)*d
        
        self.loc = Coord(updated_lat,updated_lon)
       



        
    def __str__(self):
        return "(%f,%f), spd = %f, crs = %d" % (self.loc.lat,self.loc.lon,self.spd, self.crs)
    