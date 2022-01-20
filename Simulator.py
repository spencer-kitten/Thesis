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

def generate_objects(n_merch,n_tgts,n_subs,speed_sub):
    '''Generates a requested number of merchants, targets, and submarines. Submarine speed may be specified.'''

    # Lambda for interarrival
    ld = 1000

    # Target name builder
    tgt_name = 'Target_'
    tgt_names = []
    for i in range(1,n_tgts+1):
        tgt_names.append(tgt_name + str(i))

    # Target builder
    time_delay = 0
    Targets = []
    for i in tgt_names:
        Targets.append(Merchant_Ship(i, Coord(random.uniform(0,100),0),time_delay))
        time_delay += py.random.exponential(ld)


    # Merchant name builder
    merch_name = 'Merchant_'
    merch_names = []
    for i in range(1,n_merch+1):
        merch_names.append(merch_name + str(i))

    # Merchant builder
    time_delay = py.random.gamma(n_merch,scale = 1/ld)
    Merchants = []
    for j in merch_names:
        Merchants.append(Merchant_Ship(j, Coord(random.uniform(0,100),0),time_delay))
        time_delay += py.random.exponential(ld)

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
        Submarines.append(Submarine(location,crs = course, spd = speed_sub, index = indexer))
        indexer += 1

    return Targets,Merchants,Submarines

def contact_picture(tgt_list,merch_list,sub_list,torp_list,plot_lim = 1):
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

    # Torpedoes
    for item_p in torp_list:
        plt.plot(item_p.loc.lon,item_p.loc.lat, 'yo')

    plt.xlim(0,200 + 200*(plot_lim - 1))
    plt.ylim(0,100)
    #plt.axis('equal')

def Simulator(n_targets,n_merchants,n_submarines,speed_sub,max_time, plotter = True,gif = False,seed = 10):
    #Print RNG seed for output... be able to recreate
    '''Performs one simulation of a submarine tracking event'''
    random.seed(seed)
    py.random.seed(seed)

    # Generate enviroment objects
    Targets, Merchants, Submarines = generate_objects(n_merchants,n_targets,n_submarines,speed_sub)
    Torpedoes = []

    # Working indexes
    plotter_index = 0
    max_timer = 0

    # Clear any existing plots
    plt.clf()

    filenames = []
    i = 1

    while max_timer < max_time:
        '''Simulate only as long as submarine is within boundary'''
        # Update postion of eviroment objects
        target_list = Targets + Merchants

        for item_s in Submarines:
            # Move sumbarine
            item_s.update_position()

            # Move torpedo
            item_s.ping(target_list)
            if len(item_s.torpedoes) > 0:
                for torpedo in item_s.torpedoes:
                    if torpedo.alive == True:
                        torpedo.update_position()
                        if torpedo.name not in Torpedoes:
                            Torpedoes.append(torpedo)

        for item_m in Merchants:
            # Move merchant
            item_m.update_position()

            # Check if target is dead
            if item_m.alive == False:
                Merchants.pop(item_m)

        for item_t in Targets:
            # Move target
            item_t.update_position()

            # Check if target has been shot
            for item_s in Submarines:
                if len(item_s.torpedoes) > 0:
                    for torpedo in item_s.torpedoes:
                        item_t.torpedo_check(torpedo.loc)

        plotter_index += 1

        # Plotting only occurs once in 800 steps. Set to improve visual clarity and runtime
        if plotter_index > 500:
            plotter_index = 0
            if plotter == True:
                contact_picture(Targets,Merchants,Submarines,Torpedoes,len(Submarines))
                if gif == True:
                    filename = f'{i}.png'
                    i += 1
                    filenames.append(filename)
                    plt.savefig(filename)
                    plt.close()


        # Ensure if no detections occurs that simulation will halt
        max_timer += 1

    if gif == True:
        with imageio.get_writer('mygif.gif', mode='I') as writer:
            for filename in filenames:
                image = imageio.imread(filename)
                writer.append_data(image)

        # Remove files
        for filename in set(filenames):
            os.remove(filename)

    return Targets,Merchants,Submarines


if __name__ == "__main__":

    n_targets = 30
    n_merchants = 1
    n_submarines = 1
    seeds = 15
    Targets, Merchants, Submarines = Simulator(n_targets,n_merchants,n_submarines,12,1e5,False,False,seeds)

    Killed_Targets = {}
    for sub in Submarines:
        Killed_Targets[sub.indexer] = sub.kills

    Killed_Targets = pd.DataFrame(Killed_Targets)
    pd.to_csv(Killed_Targets, index = False)
