from __future__ import division
from models.Buses import Buses
import numpy as np


class Slack:

    def __init__(self,
                 bus_id,
                 Vset,
                 ang,
                 Pinit,
                 Qinit):
        """Initialize slack bus in the power grid.

        Args:
            Bus (int): the bus number corresponding to the slack bus.
            Vset (float): the voltage setpoint that the slack bus must remain fixed at.
            ang (float): the slack bus voltage angle that it remains fixed at.
            Pinit (float): the initial active power that the slack bus is supplying
            Qinit (float): the initial reactive power that the slack bus is supplying
        """
        # You will need to implement the remainder of the __init__ function yourself.
        self.bus_id = bus_id
        self.bus = None
        self.Pinit = Pinit
        self.Qinit = Qinit
        # initialize nodes
        self.node_Vr_Slack = None
        self.node_Vi_Slack = None
        self.Vset = Vset
        self.ang = ang
        self.Vr_set = Vset*np.cos(self.ang*np.pi/180)
        self.Vi_set = Vset*np.sin(self.ang*np.pi/180)


    def assign_nodes(self):
        """Assign the additional slack bus nodes for a slack bus.

        Returns:
            None
        """
        self.node_Vr_Slack = Buses._node_index.__next__()
        self.node_Vi_Slack = Buses._node_index.__next__()

    # this is a custom function to allow each bus to reference the bus    
    def assign_buses(self, bus_vec):
        self.bus = bus_vec[self.bus_id-1]

        return
    # You should also add some other class functions you deem necessary for stamping,
    # initializing, and processing results.
    def stamp_dense(self, inputY, inputJ):
        # stamp RE into y
        inputY[self.bus.node_Vr,self.node_Vr_Slack] += 1
        inputY[self.node_Vr_Slack,self.bus.node_Vr] += 1
        # stamp IM into y
        inputY[self.bus.node_Vi,self.node_Vi_Slack] += 1
        inputY[self.node_Vi_Slack,self.bus.node_Vi] += 1
        # stamp RE into J
        inputJ[self.node_Vr_Slack] += self.Vr_set
        # stamp IM into J
        inputJ[self.node_Vi_Slack] += self.Vi_set
        
        return
    
    def stamp_sparse(self, inputY_r, inputY_c, inputY_val, inputJ_r, inputJ_val):
        # stamp RE into y
        #inputY[self.bus.node_Vr,self.node_Vr_Slack] += 1
        inputY_r.append(self.bus.node_Vr)
        inputY_c.append(self.node_Vr_Slack)
        inputY_val.append(1)
        
        #inputY[self.node_Vr_Slack,self.bus.node_Vr] += 1
        inputY_r.append(self.node_Vr_Slack)
        inputY_c.append(self.bus.node_Vr)
        inputY_val.append(1)
        
        # stamp IM into y
        #inputY[self.bus.node_Vi,self.node_Vi_Slack] += 1
        inputY_r.append(self.bus.node_Vi)
        inputY_c.append(self.node_Vi_Slack)
        inputY_val.append(1)
        
        #inputY[self.node_Vi_Slack,self.bus.node_Vi] += 1
        inputY_r.append(self.node_Vi_Slack)
        inputY_c.append(self.bus.node_Vi)
        inputY_val.append(1)
        
        # stamp RE into J
        #inputJ[self.node_Vr_Slack] += self.Vr_set
        inputJ_r.append(self.node_Vr_Slack)
        inputJ_val.append(self.Vr_set)
        
        # stamp IM into J
        #inputJ[self.node_Vi_Slack] += self.Vi_set
        inputJ_r.append(self.node_Vi_Slack)
        inputJ_val.append(self.Vi_set)
        
        return inputY_r, inputY_c, inputY_val, inputJ_r, inputJ_val