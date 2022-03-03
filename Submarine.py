# -*- coding: utf-8 -*-
"""
Created on Tue Aug 10 12:57:49 2021

@author: spenc
"""

import random as rand
import math, time
from fastkml import kml
from shapely.geometry import Point, LineString, Polygon
import pandas as pd  # note that this is the accepted community naming convention to import pandas
import numpy as np
import matplotlib.pyplot as plt


from Coord import *

class Submarine:
    '''Improved class to store data of USS Lubbock'''

    def __init__(self,loc, crs = rand.randrange(0, 360),spd = 3, depth = 150, index = 1):
        self.loc = loc
        self.crs = crs
        self.spd = spd
        self.depth = depth
        # detections and detected before split to allow prioritization by the submarine
        self.detections = []
        self.detected_before = []
        self.focus = []
        self.prev_focus = []
        self.friends = []
        # Forces submarine to return to center postion to resume search if reach boundry
        self.return_fun = False
        self.descriminating_timer = 5*60
        self.torp_timer = 1*60
        self.indexer = index
        self.kills = []
        self.tracking_timer = []
        self.tracking_index = 0


    def update_position(self):
        '''Geometric Hops'''

        radians = self.bearing_to_rads(self.crs)
        d = self.spd*(1/3600)
        self.tracking_index += 1

        if (len(self.focus) > 0) & (self.return_fun == False):


            if self.loc.dist_to(self.focus[0].loc) > 20000/2000:
                # Within detection range, not within tracking range
                # Speed up to close distance
                self.crs = self.loc.bearing(self.focus[0].loc)
                self.spd = 33


            elif (self.loc.dist_to(self.focus[0].loc) <= 20000/2000):
                # Within tracking range
                self.spd = 17
                self.crs = self.loc.bearing(self.focus[0].loc)

                # Check if new target
                if self.focus[0].name != self.prev_focus:
                    self.descriminating_timer = 5*60
                    self.prev_focus = self.focus[0].name
                    self.tracking_timer.append(self.tracking_index)

                if self.descriminating_timer < 0:
                    if self.focus[0].status != 'Target':
                        # Determine if target or neutral
                        self.detections.pop(0)
                        self.friends.append(self.focus[0])
                        self.crs = rand.randint(0, 1)*180


                    elif (self.focus[0].status == 'Target'):
                        self.torp_timer -= 1

                        if self.torp_timer <= 0:
                            if rand.random() < 0.7:
                                self.focus[0].alive = False
                                self.torp_timer = 1*60
                                self.kills.append(self.focus[0].name)
                                self.friends.append(self.focus[0])
                                self.crs = rand.randint(0, 1)*180

                            else:
                                self.torp_timer = 1*60
                else:
                    self.descriminating_timer -= 1
        elif (len(self.focus) == 0) & (self.return_fun == False):

            self.spd = 12

            if self.loc.lat >= 100 - 30000/2000:
                self.crs = 180
            elif self.loc.lat <= 0 + 30000/2000:
                self.crs = 0

        elif (len(self.focus) > 0) & (self.return_fun == True):
            self.return_fun = False


        # Prevent submarine from leaving waterspace
        if self.loc.lon >= (110 + (self.indexer - 1)*200):
            if (len(self.focus) == 0):
                self.return_fun = True
                self.crs = 270
        if self.loc.lon <= (90 + (self.indexer - 1)*200):
            if (len(self.focus) == 0):
                self.return_fun = True
                self.crs = 90
        if ((85 + (self.indexer - 1)*200) < self.loc.lon < (105 + (self.indexer - 1)*200)) & (self.return_fun == True):
            self.return_fun = False
            self.crs = rand.randint(0, 1)*180
        if self.loc.lat >= 100:
            self.crs = 180
        elif self.loc.lat <= 0:
            self.crs = 0

        radians = self.bearing_to_rads(self.crs)
        d = self.spd*(1/3600)

        # Geometric hops
        updated_lat = self.loc.lat + math.sin(radians)*d
        updated_lon = self.loc.lon + math.cos(radians)*d

        # Re-store location as Coord object in .loc
        self.loc = Coord(updated_lat,updated_lon)


    def ping(self, target_list):
        '''Verifies if any targets are within detection range'''

        #  range in nm
        ping_range = 40000/2000
        min_dist  = 999999

        self.detections = []
        self.focus = []

        for targets in target_list:
            if targets.alive == True:
                if (targets.loc.lon <= 190 + (self.indexer - 1)*200) & (targets.loc.lon >= (self.indexer - 1)*200):
                    distance = self.loc.dist_to(targets.loc)
                    if (distance < ping_range):
                        if (targets in self.friends) or (targets.alive == False):
                            continue

                        if distance < min_dist:
                            min_dist = distance
                            self.detections.insert(0,targets)
                        else:
                            self.detections.append(targets)

                        if targets.name not in self.detected_before:
                            self.detected_before.append(targets.name)

        try:
            self.focus.append(self.detections[0])
        except:
            self.focus = []


    def bearing_to_rads(self, crs):
        '''Converts nautical bearing to unit circle radians'''
        if crs == 360:
            crs = 0

        if crs < 90:
            crs = (math.pi/180)*(90-crs)
        else:
            crs = (math.pi/180)*(450 - crs)

        return crs

    def change_depth(self,new_depth = 150):
        '''changes depth at 5ft per second'''

        current_depth = self.depth


        if current_depth == new_depth:
            # Staying the same depth
            return
        elif current_depth < new_depth:
            # Going deep
            current_depth += 5
            self.depth = current_depth
            return
        else:
            # Going Shallow
            current_depth -= 5
            self.depth = current_depth

    def change_speed(self,new_speed = 3, cavitate = False):
        '''Changes speed at 0.5 kts per second if cavitate = False, 2kts per second if cavitate = True'''

        current_speed = self.spd

        if cavitate == False:
            rate = 0.5
        else:
            rate = 2

        if current_speed == new_speed:
            return
        elif current_speed < new_speed:
            current_speed += rate
            self.spd = current_speed
            return
        else:
            current_speed -= rate
            self.spd = current_speed
            return

    def change_crs(self,new_crs, rudder = 10):
        '''Changes course at 1 degree per second at 10degree rudder.'''

        try:
            val = int(new_crs)
        except ValueError:
            return

        current_crs = self.crs


        if current_crs == new_crs:
            self.crs = new_crs
            return
        else:
            working_crs = current_crs + 180
            if new_crs < current_crs:
                new_crs += 360
            if working_crs >= new_crs:
                current_crs += 1*rudder/10
            else:
                current_crs -= 1*rudder/10

        # Compass conversion
        if current_crs >= 360:
            self.crs = current_crs - 360
        elif current_crs < 0:
            self.crs = current_crs + 360
        else:
            self.crs = current_crs





    def __str__(self):
        return "(%f,%f), spd = %f, crs = %d" % (self.loc.lat,self.loc.lon,self.spd, self.crs)
