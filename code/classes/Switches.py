import numpy as np
from itertools import count
from classes.Nodes import Nodes
# from lib.stamping_functions import stamp_y_sparse, stamp_j_sparse
import pickle

class Switches:
    def __init__(self, name, from_node, to_node, t_open, t_close):
        self.name = name
        self.from_node = from_node
        self.to_node = to_node
        self.t_open = t_open
        self.t_close = t_close
        # You are welcome to / may be required to add additional class variables   

    # Some suggested functions to implement, 
    def assign_node_indexes_in_switches(self, node_dict):
        if self.from_node != "gnd":
            self.from_node_idx = node_dict[self.from_node]
        if self.to_node != "gnd":
            self.to_node_idx = node_dict[self.to_node]
        pass
        
    def stamp_sparse(self,):
        pass

    def stamp_dense(self,Y,t):
        '''
        For the switch, I treat it as a large or small resistor
        
        There are two cases where t_open if before t_close:
            
        |    
        -
        |           ___________
    0V  ___________|           |___________
        
        or where t_close is before t_open
        |    
        -
        |__________              ___________
    0V |           |___________|         
        '''
        
        # check which state it should be
        if(self.t_open<self.t_close):
            # assume closed before t_open
            if( (t<=self.t_open) or (t>=self.t_close)):
                state = "short"
            else:
                state = "open"
        elif(self.t_close<self.t_open):
            # assume open before tc
            if((t>=self.t_close) and (t<=self.t__open)):
                state = "short"
            else:
                state = "open"
        if(state == "open"):
            self.r = 1*10**300
        elif(state == "short"):
            self.r = 1*10**-300
        
        # Stamp a resistor
        # if neither nodes are ground
        if (self.from_node != "gnd") and (self.to_node != "gnd"):
            Y[self.from_node_idx,self.from_node_idx] += 1/self.r
            Y[self.to_node_idx,self.to_node_idx] += 1/self.r
            Y[self.from_node_idx,self.to_node_idx] += -1/self.r
            Y[self.to_node_idx,self.from_node_idx] += -1/self.r
        # if from node is grounded
        elif (self.from_node == "gnd"):
            Y[self.to_node_idx,self.to_node_idx] += 1/self.r
        # if to node is grounded
        elif (self.to_node == "gnd"):
            Y[self.from_node_idx,self.from_node_idx] += 1/self.r
        
        pass
