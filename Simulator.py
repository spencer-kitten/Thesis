# -*- coding: utf-8 -*-
"""
Created on Tue Jan 18 10:38:10 2022

@author: spenc
"""
import numpy as py
import random as random
import matplotlib.pyplot as plt
import pandas as pd
from scipy import stats
from scipy.stats import t
import math
import time
import imageio
import os

from Coord import *
from Submarine import *
from Merchant_Ship import Merchant_Ship
from twitter_acces import *

def generate_objects(n_merch,n_tgts,n_subs,speed_sub,P_k,tgt_speed,Targets = [], Merchants = []):
    '''Generates a requested number of merchants, targets, and submarines. Submarine speed may be specified.'''

    # Target name builder
    try:
        starting_int = Targets[-1].name
        starting_int = int(starting_int[-1])
    except:
        starting_int = 0
    tgt_name = 'Target_'
    tgt_names = []
    for i in range(starting_int + 1,n_tgts+starting_int+1):
        tgt_names.append(tgt_name + str(i))

    # Target builder
    time_delay = 0
    for i in tgt_names:
        Targets.append(Merchant_Ship(i, Coord(random.uniform(0,100),0),time_delay))
        time_delay += py.random.exponential(1/ld_t)

    # Merchant name builder
    try:
        starting_int = Merchants[-1].name
        starting_int = int(starting_int[-1])
    except:
        starting_int = 0
    merch_name = 'Merchant_'
    merch_names = []
    for i in range(starting_int + 1,n_merch+starting_int+1):
        merch_names.append(merch_name + str(i))

    # Merchant builder
    time_delay = 0
    for j in merch_names:
        Merchants.append(Merchant_Ship(j, Coord(random.uniform(0,100),0),time_delay,tgt_speed))
        time_delay += py.random.exponential(1/ld_m)

    # Submarine name builder
    sub_name = 'Hunter_'
    sub_names = []
    for i in range(1,n_subs+1):
        sub_names.append(sub_name + str(i))

    # Submarine builder
    Submarines = []
    indexer = 1
    for i in sub_names:
        location = Coord(random.uniform(0,100),100 + 200*(indexer-1))
        course = round(random.random())*180
        Submarines.append(Submarine(location,P_k,crs = course, spd = speed_sub, index = indexer))
        indexer += 1

    return Targets,Merchants,Submarines

def contact_picture(tgt_list,merch_list,sub_list,plot_lim = 1):
    '''Plots contact picture'''

    # Targets
    for item_t in tgt_list:
        plt.plot(item_t.loc.lon,item_t.loc.lat, 'ro')

    # Merchants
    for item_m in merch_list:
        plt.plot(item_m.loc.lon,item_m.loc.lat, 'bo')

    # Submarines
    for item_s in sub_list:
        plt.plot(item_s.loc.lon,item_s.loc.lat, 'go')

    plt.xlim(0,200 + 200*(plot_lim - 1))
    plt.ylim(0,100)
    #plt.axis('equal')

def Pois(arrival_timer,Targets, Merchants,P_k,tgt_speed):

    if arrival_timer <= 0:
        RV = py.random.random()
        if RV < (ld_t/(ld_t + ld_m)):
            Targets, Merchants, Submarines = generate_objects(0,1,0,0,P_k,tgt_speed)
        else:
            Targets, Merchants, Submarines = generate_objects(1,0,0,0,P_k,tgt_speed)
        arrival_timer = py.random.exponential(1/(ld_m + ld_t))

    else:
        arrival_timer -= 1

    return Targets, Merchants, arrival_timer


def Simulator(n_targets,n_merchants,n_submarines,P_k,speed_sub,lad_t,lad_m,tgt_speed,max_time,seed, plotter = True,gif = True):
    #Print RNG seed for output... be able to recreate
    # Lambda for interarrival target & merchant
    global ld_t
    global ld_m
    ld_t = lad_t*1/(24*3600)
    ld_m = lad_m*1/(24*3600)

    Simulation_Stop = False

    '''Performs one simulation of a submarine tracking event'''
    random.seed(seed)
    py.random.seed(seed)

    # Generate enviroment objects
    Targets, Merchants, Submarines = generate_objects(n_merchants,n_targets,n_submarines,speed_sub,P_k,tgt_speed)

    # Working indexes
    plotter_index = 0
    max_timer = 0
    arrival_timer = 0

    # Clear any existing plots
    plt.clf()

    filenames = []
    i = 1

    while max_timer < max_time:
        '''Simulate only as long as submarine is within boundary'''
        # Update postion of eviroment objects
        target_list = Targets + Merchants

        for item_s in Submarines:

            # Move torpedo
            item_s.ping(target_list)

            # Move sumbarine
            item_s.update_position()

        for item_m in Merchants:
            # Move merchant
            item_m.update_position()

        for item_t in Targets:
            # Move target
            item_t.update_position()

        Targets, Merchants, arrival_timer = Pois(arrival_timer,Targets, Merchants,P_k,tgt_speed)

        plotter_index += 1

        # Plotting only occurs once in 800 steps. Set to improve visual clarity and runtime
        if plotter_index > 500:
            plotter_index = 0
            if plotter == True:
                contact_picture(Targets,Merchants,Submarines,len(Submarines))
                titlestring = str(n_submarines) +' Submarine(s), Seed = ' + str(seed) + r'$, P_{k} = $' + str(P_k) + r'$, \lambda_{T} = $' + str('{:0.3e}'.format(ld_t*24*3600)) + 'Arrivals/Day'
                plt.title(titlestring)
                filename = f'{i}.png'
                i += 1
                filenames.append(filename)
                plt.savefig(filename)
                plt.close()

        # Ensure if no detections occurs that simulation will halt
        max_timer += 1


    if gif == True:
        #gif creator
        with imageio.get_writer('mygif.gif', mode='I') as writer:
            for filename in filenames:
                image = imageio.imread(filename)
                writer.append_data(image)

        # Remove files
        for filename in set(filenames):
            os.remove(filename)

    return Targets,Merchants,Submarines
