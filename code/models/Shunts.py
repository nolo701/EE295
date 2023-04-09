from __future__ import division
from itertools import count
from models.Buses import Buses
from scripts.global_vars import global_vars

class Shunts:
    _ids = count(0)

    def __init__(self,
                 Bus_id,
                 G_MW,
                 B_MVAR,
                 shunt_type,
                 Vhi,
                 Vlo,
                 Bmax,
                 Bmin,
                 Binit,
                 controlBus,
                 flag_control_shunt_bus=False,
                 Nsteps=[0],
                 Bstep=[0]):

        """ Initialize a shunt in the power grid.
        Args:
            Bus (int): the bus where the shunt is located
            G_MW (float): the active component of the shunt admittance as MW per unit voltage
            B_MVAR (float): reactive component of the shunt admittance as  MVar per unit voltage
            shunt_type (int): the shunt control mode, if switched shunt
            Vhi (float): if switched shunt, the upper voltage limit
            Vlo (float): if switched shunt, the lower voltage limit
            Bmax (float): the maximum shunt susceptance possible if it is a switched shunt
            Bmin (float): the minimum shunt susceptance possible if it is a switched shunt
            Binit (float): the initial switched shunt susceptance
            controlBus (int): the bus that the shunt controls if applicable
            flag_control_shunt_bus (bool): flag that indicates if the shunt should be controlling another bus
            Nsteps (list): the number of steps by which the switched shunt should adjust itself
            Bstep (list): the admittance increase for each step in Nstep as MVar at unity voltage
        """
        self.id = self._ids.__next__()
        self.bus_id = Bus_id
        self.g = G_MW/global_vars.MVAbase
        self.b = B_MVAR/global_vars.MVAbase
        self.shunt_type = shunt_type
        self.Vhi = Vhi
        self.Vlo = Vlo
        self.Bmax = Bmax
        self.Bmin = Bmin
        self.Binit = Binit
        self.controlBus = controlBus
        self.flag_control_shunt_bus = flag_control_shunt_bus
        self.Nsteps = Nsteps
        self.Bstep = Bstep

        # You will need to implement the remainder of the __init__ function yourself.
        # You should also add some other class functions you deem necessary for stamping,
        # initializing, and processing results.
        
        # this is a custom function to allow each bus to reference the bus    
    def assign_buses(self, bus_vec):
        self.bus = bus_vec[self.bus_id-1]
            
        pass
        
    def stamp_dense(self, inputY):
        # Stamp G RE
        inputY[self.bus.node_Vr, self.bus.node_Vr] += self.g
        # Stamp VCCS RE
        inputY[self.bus.node_Vr, self.bus.node_Vi] += -1*self.b
        # Stamp G IM
        inputY[self.bus.node_Vi, self.bus.node_Vi] += self.g
        # Stamp VCCS IM
        inputY[self.bus.node_Vi, self.bus.node_Vr] += self.b
            
        pass
    
    def stamp_sparse(self, inputY_r, inputY_c, inputY_val):
        # Stamp G RE
        #inputY[self.bus.node_Vr, self.bus.node_Vr] += self.g
        inputY_r.append(self.bus.node_Vr)
        inputY_c.append(self.bus.node_Vr)
        inputY_val.append(self.g)
        
        # Stamp VCCS RE
        #inputY[self.bus.node_Vr, self.bus.node_Vi] += -1*self.b
        inputY_r.append(self.bus.node_Vr)
        inputY_c.append(self.bus.node_Vi)
        inputY_val.append(-1*self.b)
        
        # Stamp G IM
        #inputY[self.bus.node_Vi, self.bus.node_Vi] += self.g
        inputY_r.append(self.bus.node_Vi)
        inputY_c.append(self.bus.node_Vi)
        inputY_val.append(self.g)
        
        # Stamp VCCS IM
        #inputY[self.bus.node_Vi, self.bus.node_Vr] += self.b
        inputY_r.append(self.bus.node_Vi)
        inputY_c.append(self.bus.node_Vr)
        inputY_val.append(self.b)
        
        
        return