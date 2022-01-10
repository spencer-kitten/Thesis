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

    
    def __init__(self, name, loc,course, speed):
        self.name = name
        self.loc = loc
        self.spd = speed
        self.crs = course
        self.alive = True
        
    def bearing_to_rads(self, crs):
        '''Converts nautical bearing to unit circle radians'''
        if crs == 360:
            crs = 0
            
        if crs < 90:
            crs = (math.pi/180)*(90-crs)
        else:
            crs = (math.pi/180)*(450 - crs)
    
        return crs

            
    def update_position(self):
        '''Geometric Hops'''
        
        radians = self.bearing_to_rads(self.crs)
        d = self.spd*(1/3600)
        
        updated_lat = self.loc.lat + math.sin(radians)*d
        updated_lon = self.loc.lon + math.cos(radians)*d
        
        self.loc = Coord(updated_lat,updated_lon)
        
        if self.loc.lat >= 10000:
            self.alive = False
            
        elif self.loc.lon >= 200:
            self.loc.lat = 10000
       



        
    def __str__(self):
        return "(%f,%f), spd = %f, crs = %d" % (self.loc.lat,self.loc.lon,self.spd, self.crs)
    