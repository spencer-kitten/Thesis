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

    def __init__(self,loc,P_k, crs = rand.randrange(0, 360),spd = 3, depth = 150, index = 1,comms = 1):
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
        self.descriminating_timer = 2*60*60
        self.torp_timer = 10*60
        self.indexer = index
        self.kills = []
        self.kill_prob = P_k
        self.tracking_timer = [0]
        #interdiciton
        self.alert_list = []
        self.interdict = False
        self.last_interdict = [0]
        self.IP = 0
        self.communication_index = 0
        if comms == 1:
            self.communication_timer = 0
        elif comms == 2:
            self.communication_timer = random.rand(0,12*60*60)
        elif comms == 3:
            self.communication_timer = 1e10
        #self.interdiction_point = Coord(0,0)

    def calc_interdiction_point(self,last_known_tgt_position,last_known_tgt_time,target_speed):
        self.spd = 30
        bearing_to_tgt = self.loc.bearing(Coord(last_known_tgt_position.lat,last_known_tgt_position.lon))


        if last_known_tgt_position.lat >= self.loc.lat:
            beta = last_known_tgt_position.bearing(self.loc) - 270
            if beta >= 180:
                beta = 360-beta
            beta = beta*np.pi/180
            alpha = np.arcsin(target_speed*np.sin(beta)/self.spd)*180/np.pi
            self.crs = bearing_to_tgt + alpha
        else:
            beta = 90 - last_known_tgt_position.bearing(self.loc)
            if beta >= 180:
                beta = 360-beta
            beta = beta*np.pi/180
            alpha = np.arcsin(target_speed*np.sin(beta)/self.spd)*180/np.pi
            self.crs = bearing_to_tgt - alpha

        radians = self.bearing_to_rads(self.crs)
        d = self.spd*(1/3600)

        optimal_lat = self.loc.lat + math.sin(radians)*d
        optimal_lon = self.loc.lon + math.cos(radians)*d
        # three different circumstances
        #1. meet at wall
        #2. too far ... if too far then ignore comms check
        #3. go get em


        if optimal_lon >= (190 + (self.indexer - 1)*200):
            self.interdict = False
            self.alert_list = communications_list[0].target_info[self.indexer - 1]
            return
        elif optimal_lon <=  (self.indexer - 1)*200:
            optimal_lon = (self.indexer - 1)*200


        return Coord(optimal_lat,optimal_lon)



    def comms_check(self,communications_list):
        #if self.communication_index > self.communication_timer:
        #    self.communication_index = 0
        if (self.indexer > 1) & ((self.indexer - 1) in communications_list[0].target_info.keys()):
            last_known_tgt_position = communications_list[0].target_info[self.indexer - 1][0]
            last_known_tgt_time = communications_list[0].target_info[self.indexer - 1][1]
            target_speed  = communications_list[0].target_info[self.indexer - 1][2]
            #perform calc to optimal update_position
            #set course
            if self.last_interdict[0] != last_known_tgt_position:
                self.last_interdict.pop(0)
                self.last_interdict.append(last_known_tgt_position)
                self.interdict = True
                try:
                    self.IP = self.calc_interdiction_point(last_known_tgt_position,last_known_tgt_time,target_speed)
                    self.crs = self.loc.bearing(self.IP)
                except:
                    pass
        #self.communication_index += 1


    def interdiction(self,communications_list):

        if self.loc.dist_to(self.IP) < 3:
            self.interdict = False

        else:
            #intercept
            pass


        if self.loc.lon >= (190 + (self.indexer - 1)*200):
            self.crs = 270
        if self.loc.lon <=  (self.indexer - 1)*200:
            self.crs = 90
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

        #self.communication_index += 1

    def update_position(self):
        '''Geometric Hops'''

        if (len(self.focus) > 0) & (self.return_fun == False):


            if self.loc.dist_to(self.focus[0].loc) > 20000/2000:
                # Within detection range, not within tracking range
                # Speed up to close distance
                self.crs = self.loc.bearing(self.focus[0].loc)
                self.spd = 30


            elif (self.loc.dist_to(self.focus[0].loc) <= 20000/2000):
                # Within tracking range
                self.spd = 17
                self.crs = self.loc.bearing(self.focus[0].loc)

                # Check if new target
                if self.focus[0].name != self.prev_focus:
                    self.descriminating_timer = 2*60*60
                    self.prev_focus = self.focus[0].name
                    self.tracking_timer.append(0)


                if self.descriminating_timer < 0:
                    if self.focus[0].status != 'Target':
                        # Determine if target or neutral
                        self.detections.pop(0)
                        self.friends.append(self.focus[0])
                        self.crs = rand.randint(0, 1)*180


                    elif (self.focus[0].status == 'Target'):
                        self.torp_timer -= 1

                        if self.torp_timer <= 0:
                            shoot = rand.random()
                            #print(shoot,self.kill_prob)
                            if shoot < self.kill_prob:
                                self.focus[0].alive = False
                                self.kills.append(self.focus[0].name)
                                self.friends.append(self.focus[0])
                                self.crs = rand.randint(0, 1)*180

                            self.torp_timer = 10*60

                    self.descriminating_timer = 2*60*60
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
        if ((95 + (self.indexer - 1)*200) < self.loc.lon < (105 + (self.indexer - 1)*200)) & (self.return_fun == True):
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

        try:
            if (self.focus[0].loc.lon >= (190 + (self.indexer - 1)*200)) & (self.focus[0] not in self.alert_list):
                self.alert_list.append(self.focus[0])
        except:
            pass
        self.detections = []
        self.focus = []

        for targets in target_list:
            if targets.alive == True:
                if (targets.loc.lon <= 190 + (self.indexer - 1)*200) & (targets.loc.lon >= (self.indexer - 1)*200) & (targets.loc.lat <= 100) & (targets.loc.lat >= 0):
                    distance = self.loc.dist_to(targets.loc)
                    if (distance < ping_range):
                        if (targets in self.friends):
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

        self.tracking_timer[-1] += 1


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
