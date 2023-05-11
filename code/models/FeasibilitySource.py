from __future__ import division
import numpy as np
from models.Buses import Buses
from models.Buses import Buses
from scripts.stamp_helpers import *
from models.global_vars import global_vars

class FeasibilitySource:

    def __init__(self,
                 Bus):
        """Initialize slack bus in the power grid.

        Args:
            Bus (int): the bus number corresponding to this set of feasibility currents
        """
        self.Bus = Bus
        
        self.Ir_init = 0
        self.Ii_init = 0
        

    def assign_nodes(self, bus):
        """Assign the additional slack bus nodes for a slack bus.
        Args:
            You decide :)
        Returns:
            None
        """
        # TODO: You decide how to implement variables for the feasibility injections
        self.node_Vr = bus[Buses.bus_key_[self.Bus]].node_Vr
        self.node_Vi = bus[Buses.bus_key_[self.Bus]].node_Vi
        self.node_Lr = bus[Buses.bus_key_[self.Bus]].node_Lr
        self.node_Li = bus[Buses.bus_key_[self.Bus]].node_Li
        self.ifr = bus[Buses.bus_key_[self.Bus]].ifr
        self.ifi = bus[Buses.bus_key_[self.Bus]].ifi
        
        pass

    def stamp(self, V, Y_val, Y_row, Y_col, J_val, J_row, idx_Y, idx_J):
        # You need to implement this.
        idx_Y = stampY(self.node_Vr, self.ifr, 1, Y_val, Y_row, Y_col, idx_Y)
        idx_Y = stampY(self.node_Vi, self.ifi, 1, Y_val, Y_row, Y_col, idx_Y)
        
        return (idx_Y, idx_J)

    def stamp_dual(self, V, Y_val, Y_row, Y_col, J_val, J_row, idx_Y, idx_J):
        # You need to implement this.
        idx_Y = stampY(self.ifr, self.node_Lr, -1, Y_val, Y_row, Y_col, idx_Y)
        idx_Y = stampY(self.ifr, self.ifr, 2, Y_val, Y_row, Y_col, idx_Y)
        idx_Y = stampY(self.ifi, self.node_Li, -1, Y_val, Y_row, Y_col, idx_Y)
        idx_Y = stampY(self.ifi, self.ifi, 2, Y_val, Y_row, Y_col, idx_Y)
        
        return (idx_Y, idx_J)
