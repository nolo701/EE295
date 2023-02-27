import numpy as np
from itertools import count
from classes.Nodes import Nodes
#from lib.stamping_functions import stamp_y_sparse, stamp_j_sparse

class Capacitors:
    def __init__(self, name, from_node, to_node, c):
        self.name = name
        self.c = c
        self.from_node = from_node
        self.to_node = to_node
        # You are welcome to / may be required to add additional class variables   
        
    # Some suggested functions to implement, 
    def assign_node_indexes_in_capacitors(self, count_idx, node_dict):
        # create intermediate node for the voltage source
        self.intermediate_node_idx = count_idx
        count_idx += 1
        # add it to the dict
        node_dict[str(self.name)+"_int"] = self.intermediate_node_idx
        #assign the index to to_node
        if(self.to_node != "gnd"):
            self.to_node_idx = node_dict[self.to_node]
        #assign the index to from_node
        if(self.from_node != "gnd"):
            self.from_node_idx = node_dict[self.from_node]
    
        #create a constraint for the voltage source
        self.vs_constraint_node_idx = count_idx
        count_idx += 1
        # add to the dict
        node_dict["vs_"+str(self.name)] = self.vs_constraint_node_idx
        
        #return the current number of nodes
        return(count_idx)
        
    def stamp_sparse(self,):
        pass

    def stamp_dense(self,Y,J,results_t,t,SETTINGS):
        #stamp the resistance
        self.r = SETTINGS["Time Step"]/(2*self.c)
        # if neither nodes are ground
        if (self.from_node != "gnd"):
            Y[self.from_node_idx,self.from_node_idx] += 1/self.r
            Y[self.intermediate_node_idx,self.intermediate_node_idx] += 1/self.r
            Y[self.from_node_idx,self.intermediate_node_idx] += -1/self.r
            Y[self.intermediate_node_idx,self.from_node_idx] += -1/self.r
        # if from node is grounded
        elif (self.from_node == "gnd"):
            Y[self.intermediate_node_idx,self.intermediate_node_idx] += 1/self.r
        # if to node is grounded
        elif (self.to_node == "gnd"):
            Y[self.from_node_idx,self.from_node_idx] += 1/self.r

        # Stamp the voltage source
        # solve for the voltage value for t
        # check if referencing ground
        if self.to_node == "gnd":
            V_t = (results_t[self.from_node_idx])+ self.r*results_t[self.vs_constraint_node_idx]
        elif self.to_node != "gnd":
            V_t = (results_t[self.from_node_idx] - results_t[self.to_node_idx])+ self.r*results_t[self.vs_constraint_node_idx]
        #V_t = self.amp_ph_ph_rms*np.sqrt(2/3)*np.cos(2*np.pi*self.frequency_hz*t +(self.phase_deg))
        Y[self.vs_constraint_node_idx, self.intermediate_node_idx] += 1
        if self.to_node != "gnd":
            Y[self.vs_constraint_node_idx, self.to_node_idx] += -1
        J[self.vs_constraint_node_idx] += V_t
        Y[self.intermediate_node_idx, self.vs_constraint_node_idx] += 1
        if self.to_node != "gnd":
            Y[self.to_node_idx, self.vs_constraint_node_idx] += -1
        
        
        
        
        '''
        
        # Old stamp
        Y[self.vs_constraint_node_idx, self.intermediate_node_idx] += 1
        if self.to_node != "gnd":
            Y[self.vs_constraint_node_idx, self.to_node_idx] += -1
        
        Y[self.intermediate_node_idx, self.vs_constraint_node_idx] += 1
        if self.to_node != "gnd":
            Y[self.to_node_idx, self.vs_constraint_node_idx] += -1
        # check to see if the total voltage is reference to ground or not
        if(self.to_node == "gnd"):
            # if the cap is connected to ground then the voltage
            # is just the from node's voltage
            J[self.vs_constraint_node_idx] += results_t[self.from_node_idx] + self.r * results_t[self.vs_constraint_node_idx]
        # otherwise it will be the difference between from and to nodes
        else:
            J[self.vs_constraint_node_idx] += (results_t[self.from_node_idx] - results_t[self.to_node_idx]) + self.r * results_t[self.vs_constraint_node_idx]
    
        '''
    def stamp_open(self,):
        pass