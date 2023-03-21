from __future__ import division
from models.Buses import Buses
import numpy as np


class Slack:

    def __init__(self,
                 Bus,
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

    # You should also add some other class functions you deem necessary for stamping,
    # initializing, and processing results.
