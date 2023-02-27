import sys
sys.path.append("..")
import numpy as np
from itertools import count
from classes.Nodes import Nodes
# from lib.stamping_functions import stamp_y_sparse, stamp_j_sparse

class Inductors:
    def __init__(self, name, from_node, to_node, l):
        self.name = name
        self.from_node = from_node
        self.to_node = to_node
        self.l = l
        
        # You are welcome to / may be required to add additional class variables   

    # Some suggested functions to implement, 
    def assign_node_indexes_in_inductors(self,count_idx, node_dict):
        #create the extra node between voltage source & etc
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
            
        # create constraint node for the 0V voltage source
        self.vs_constraint_node_idx = count_idx
        count_idx += 1
        # add to the dict
        node_dict["vs_"+str(self.name)] = self.vs_constraint_node_idx
        
        #return the current number of nodes
        return(count_idx)
        
    def stamp_sparse(self,):
        pass

    def stamp_dense(self,Y,J,results_t,t,SETTINGS):
        # stamp the conductange - G
        self.g = SETTINGS["Time Step"]/(2*self.l)
        # if neither nodes are ground
        if (self.to_node != "gnd"):
            Y[self.intermediate_node_idx,self.intermediate_node_idx] += self.g
            Y[self.to_node_idx,self.to_node_idx] += self.g
            Y[self.intermediate_node_idx,self.to_node_idx] += -self.g
            Y[self.to_node_idx,self.intermediate_node_idx] += -self.g

        # if to node is grounded
        elif (self.to_node == "gnd"):
            Y[self.intermediate_node_idx,self.intermediate_node_idx] += self.g
            
        # stamp the voltage source - Always 0V
        # solve for the voltage value for t
        V_t = 0
        Y[self.vs_constraint_node_idx, self.from_node_idx] += 1
        Y[self.vs_constraint_node_idx, self.intermediate_node_idx] += -1
        J[self.vs_constraint_node_idx] += V_t
        Y[self.from_node_idx, self.vs_constraint_node_idx] += 1
        Y[self.intermediate_node_idx, self.vs_constraint_node_idx] += -1
            
        # stamp the current source
        if (self.to_node != "gnd"):
            I = results_t[self.vs_constraint_node_idx] + self.g * (results_t[self.intermediate_node_idx]-results_t[self.to_node_idx])
            J[self.to_node_idx] += I
        else:
            I = results_t[self.vs_constraint_node_idx] + self.g*(results_t[self.from_node_idx])
            J[self.intermediate_node_idx] += -I
        
        

    def stamp_short(self,):
        pass