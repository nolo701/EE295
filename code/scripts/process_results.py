from __future__ import division
from models.Buses import Buses
from itertools import count
import numpy as np

def process_results(v_sol, buses):
    numBuses = len(buses)
    # Create a table to convert the rectangular for each bus to polar
    # get each variable name as well as the final value
    
    polar = np.zeros([numBuses+1,5])
    # assign the first row as string headers
    i = 0;
    for bus in buses:
        polar[i,1] = v_sol[bus.node_Vr]
        polar[i,2] = v_sol[bus.node_Vi]
        polar[i,3] = np.sqrt(v_sol[bus.node_Vr]**2+v_sol[bus.node_Vi]**2)
        polar[i,4] = np.rad2deg(np.arctan2(v_sol[bus.node_Vi], v_sol[bus.node_Vr]))
        i+=1
    print(polar)
    pass