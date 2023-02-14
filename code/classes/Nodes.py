import sys
sys.path.append("..")
import numpy as np
from itertools import count

class Nodes:    
    def __init__(self, name, phase):
        self.name = name
        self.phase = phase
        # You are welcome to / may be required to add additional class variables
        

    # Some suggested functions to implement, 
    def assign_node_indexes_in_nodes(self, node_count, node_dict):
        self.idx = node_count
        node_count += 1
        node_dict[self.name] = self.idx
        return(node_count)
