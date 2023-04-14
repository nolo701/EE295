from __future__ import division
from models.Buses import Buses
from itertools import count
import numpy as np
import pandas as pd

def process_results(v_sol, buses):
    numBuses = len(buses)
    # Create a table to convert the rectangular for each bus to polar
    # get each variable name as well as the final value
    
    polar = np.zeros([numBuses+1,5])
    # assign the first row as string headers
    i = 0
    minV_idx = None
    minVBusid = None
    maxV_idx = None
    maxVBusid = None
    minAng_idx = None
    minAngBusid = None
    maxAng_idx = None
    maxAngBusid = None
    for bus in buses:
        polar[i,0] = bus.Bus
        polar[i,1] = v_sol[bus.node_Vr]
        polar[i,2] = v_sol[bus.node_Vi]
        polar[i,3] = np.sqrt(v_sol[bus.node_Vr]**2+v_sol[bus.node_Vi]**2)
        polar[i,4] = np.rad2deg(np.arctan2(v_sol[bus.node_Vi], v_sol[bus.node_Vr]))
        # if there is not a min or max set (for first bus), set it
        if minV_idx == None:
            minV_idx = i
            minVBusid = bus.Bus
            maxV_idx = i
            maxVBusid = bus.Bus
            minAng_idx = i
            minAngBusid = bus.Bus
            maxAng_idx = i
            maxAngBusid = bus.Bus
        # voltages    
        # Check for min
        if polar[i,3] <= polar[minV_idx,3]:
            minV_idx = i
            minVBusid = bus.Bus
        # Check for max
        if polar[i,3] >= polar[maxV_idx,3]:
            maxV_idx = i
            maxVBusid = bus.Bus
        # Angles    
        # Check for min
        if polar[i,4] <= polar[minAng_idx,4]:
            minAng_idx = i
            minAngBusid = bus.Bus
        # Check for max
        if polar[i,4] >= polar[maxAng_idx,4]:
            maxAng_idx = i
            maxAngBusid = bus.Bus
        i+=1
    #print(polar)
    data_df = pd.DataFrame(polar)
    writer = pd.ExcelWriter("Polar_Results.xlsx")
    data_df.to_excel(writer,float_format="%.4f")
    print("Maximum voltage at bus: {} with {} p.u @ {} deg".format(maxVBusid,polar[maxV_idx,3],polar[maxV_idx,4]))
    print("Minimum voltage at bus: {} with {} p.u @ {} deg".format(minVBusid,polar[minV_idx,3],polar[minV_idx,4]))
    print("Maximum Angle at bus: {} with {} p.u @ {} deg".format(maxAngBusid,polar[maxAng_idx,3],polar[maxAng_idx,4]))
    print("Minimum Angle at bus: {} with {} p.u @ {} deg".format(minAngBusid,polar[minAng_idx,3],polar[minAng_idx,4]))
    pass