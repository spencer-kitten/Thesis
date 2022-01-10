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
from Torpedo import *

class Submarine:
    '''Improved class to store data of USS Lubbock'''
    
    def __init__(self,loc,crs = rand.randrange(0, 360),spd = 3, depth = 150):
        self.loc = loc
        self.crs = crs
        self.spd = spd
        self.depth = depth
        # detections and detected before split to allow prioritization by the submarine
        self.detections = []
        self.detected_before = []
        # allows time between maneuvers 
        self.ranging_timer = 0
        # Forces submarine to return to center postion to resume search if reach boundry 
        self.return_fun = False
        # Uniform intermaneuver times 
        self.inter_maneuver = 2 + rand.random()*5
        self.tracked = []
        self.torpedoes = []
        self.torp_timer = 50
        self.tracking_timer = 0
        
    def update_position(self):
        '''Geometric Hops'''
        
        radians = self.bearing_to_rads(self.crs)
        d = self.spd*(1/3600)
        
        # Logic of Submarine Movment
        if (len(self.detections) > 0) & (self.return_fun == False):
            # At least on target detected, submarine not near left edge of waterspace 
            self.tracking_timer += 1
            
            if self.loc.dist_to(self.detections[0].loc) > 20000/2000:
                # Within detection range, not within tracking range 
                # Speed up to close distance 
                self.crs = self.loc.bearing(self.detections[0].loc)
                self.spd = 33
               
            elif (self.ranging_timer <= 0) and (self.loc.dist_to(self.detections[0].loc) <= 20000/2000):
                # Within tracking range 
                self.spd = 16
                
                if self.detections[0].status != 'Target':
                    # Determine if target or neutral 
                    self.detections.pop(0)
                    self.crs = round(rand.random())*180
                    
                elif (self.detections[0].status == 'Target'):
                    self.torp_timer -= 1
                    
                if self.torp_timer <= 0:
                    self.torp_timer = 50
                    self.torpedoes.append(Torpedo('Torpedo', self.loc, self.loc.bearing(self.detections[0].loc), speed = 40))
                    
                if len(self.detections) > 0:
                    # If Contact is of "target" type, begin tracking
                    
                    # Store name 
                    if self.detections[0].name not in self.tracked:
                        self.tracked.append(self.detections[0].name)
                        
                    if self.inter_maneuver <= 0:
                        
                        randomizing_factor = rand.random()

                        # Maneuvers performed astern of target while in trail 
                        if (randomizing_factor < .5) and (self.detections[0].status == 'Target'):
                            self.crs = self.loc.bearing(self.detections[0].loc) + 90
                            self.ranging_timer = (2 + 30*rand.random())*60
                            self.inter_maneuver = 2 + rand.random()*5

                        elif (.5 <= randomizing_factor < 1) and (self.detections[0].status == 'Target'):
                            self.crs = self.loc.bearing(self.detections[0].loc) - 90
                            self.ranging_timer = (2 + 30*rand.random())*60
                            self.inter_maneuver = 2 + rand.random()*5
                    else:
                        self.inter_maneuver = self.inter_maneuver - 1
            
                        
        elif (self.return_fun == True):
            # Return to search position 
            self.crs = 270
            self.spd = 33
            
        if self.ranging_timer > 0: 
            self.ranging_timer = self.ranging_timer - 1
            
            
        # Geometric hops
        updated_lat = self.loc.lat + math.sin(radians)*d
        updated_lon = self.loc.lon + math.cos(radians)*d
        
        # Re-store location as Coord object in .loc
        self.loc = Coord(updated_lat,updated_lon)
        
        # Prevent Submarine from leaving top or bottom of waterspace 
        # Needs reflection modification 
        if self.loc.lat >= 100 - 40000/2000:
            self.crs = 180
        elif self.loc.lat <= 0 + 40000/2000:
            self.crs = 0
        
        # Prevent submarine from leaving waterspace 
        if self.loc.lon >= 200 - 40000/2000:
            self.return_fun = True
            self.detections.pop(0)
            self.crs = 270
        elif (self.loc.lon >= 100) & (len(self.detections) == 0):
            self.return_fun = True
            self.crs = 270
        elif (len(self.detections) != 0) & (self.return_fun == True):
            self.return_fun = False
            self.crs = rand.randint(0, 1)*180
        elif (self.loc.lon < 100) & (self.return_fun == True):
            self.return_fun = False
            self.crs = rand.randint(0, 1)*180
        
        # Torpedo updating 
        if len(self.torpedoes) > 0:
            for torp in self.torpedoes:
                if len(self.detections) > 0:
                    torp.crs = self.loc.bearing(self.detections[0].loc)  
                    dist = torp.loc.dist_to(self.detections[0].loc)
                    if dist <= 2:
                        torp.loc = Coord(1000,1000)
                        torp.spd = 0
                        torp.alive = False
                        self.torpedoes.remove(torp)
                    elif dist >= 200:
                        torp.loc = Coord(1000,1000)
                        torp.spd = 0
                        torp.alive = False
                        self.torpedoes.remove(torp)
        
    def ping(self, target_list):
        '''Verifies if any targets are within detection range'''
        
        #  range in nm
        ping_range = 40000/2000
        
        for targets in target_list:
            distance = self.loc.dist_to(targets.loc)
            
            if distance < ping_range:
                if (targets.name not in self.detections) and (targets.name not in self.detected_before):
                    self.detections.append(targets)
                    self.detected_before.append(targets.name)
                    
            elif (distance >= ping_range) and (targets in self.detections):
                self.detections.remove(targets)
                    
        if len(self.detections) > 0:
            return 'Ping'
                
        
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
                
        if current_crs >= 360:
            self.crs = current_crs - 360
        elif current_crs < 0:
            self.crs = current_crs + 360
        else: 
            self.crs = current_crs 
            
            
        
        
            
    def __str__(self):
        return "(%f,%f), spd = %f, crs = %d" % (self.loc.lat,self.loc.lon,self.spd, self.crs)

 

