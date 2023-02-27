import numpy as np
from itertools import count
from classes.Nodes import Nodes
# from lib.stamping_functions import stamp_y_sparse, stamp_j_sparse

class VoltageSources:
    def __init__(self, name, vp_node, vn_node, amp_ph_ph_rms, phase_deg, frequency_hz):
        self.name = "vs_"+name
        self.vp_node = vp_node
        self.vn_node = vn_node
        self.amp_ph_ph_rms = amp_ph_ph_rms
        self.phase_deg = phase_deg
        self.frequency_hz = frequency_hz
        # You are welcome to / may be required to add additional class variables   

    # Some suggested functions to implement, 
    def assign_node_indexes_in_voltage_sources(self, node_count, node_dict):
        self.vs_idx = node_count
        node_count += 1
        node_dict[self.name] = self.vs_idx
        if self.vp_node != "gnd":
            self.vp_node_idx = node_dict[self.vp_node]
        if self.vn_node != "gnd":
            self.vn_node_idx = node_dict[self.vn_node]
        return(node_count)
        
    def stamp_sparse(self,):
        pass

    def stamp_dense(self,Y, J, t):
        # solve for the voltage value for t
        V_t = self.amp_ph_ph_rms*np.sqrt(2/3)*np.sin(2*np.pi*self.frequency_hz*t - np.deg2rad(self.phase_deg))
        #V_t = self.amp_ph_ph_rms*np.sqrt(2/3)*np.cos(2*np.pi*self.frequency_hz*t +(self.phase_deg))
        Y[self.vs_idx, self.vp_node_idx] += 1
        if self.vn_node != "gnd":
            Y[self.vs_idx, self.vn_node_idx] += -1
        J[self.vs_idx] += V_t
        Y[self.vp_node_idx, self.vs_idx] += 1
        if self.vn_node != "gnd":
            Y[self.vn_node_idk, self.vs_idx] += -1

    def stamp_open(self,):
        pass
        
