# -*- coding: utf-8 -*-
"""
Created on Tue Aug 10 12:56:34 2021

@author: spenc
Need to make map imported from somewhere else
"""

import random as rand
import math, time
from fastkml import kml
from shapely.geometry import Point, LineString, Polygon
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from Coord import *



class Merchant_Ship:
    '''Improved class to store Merchant Ship data'''


    def __init__(self, name, loc, time_delay,course = 90, speed=16):
        self.name = name
        self.loc = loc
        self.spd = speed
        self.crs = course
        self.td  = time_delay
        self.alive = True
        if self.name[0] == "T":
            self.status = 'Target'
        else:
            self.status = 'Merchant'

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

        if self.td > 0:
            self.td = self.td - 1

        elif (self.loc.lat <= 10000):

            radians = self.bearing_to_rads(self.crs)
            d = self.spd*(1/3600)

            updated_lat = self.loc.lat + math.sin(radians)*d
            updated_lon = self.loc.lon + math.cos(radians)*d

            self.loc = Coord(updated_lat,updated_lon)

        elif (self.loc.lat <= 10000) or (self.loc.lon >= 2000):
            self.alive = False

    def torpedo_check(self,other):
        '''Verifies if self has been destroyed by torpedo.'''

        distance = self.loc.dist_to(other)

        if (distance < 2):
            self.loc = Coord(10000,10000)
            self.alive = False






    def __str__(self):
        return "(%f,%f), spd = %f, crs = %d" % (self.loc.lat,self.loc.lon,self.spd, self.crs)
