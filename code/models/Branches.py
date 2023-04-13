from __future__ import division
from itertools import count
from models.Buses import Buses
import numpy as np

class Branches:
    _ids = count(0)

    def __init__(self,
                 from_bus,
                 to_bus,
                 r,
                 x,
                 b,
                 status,
                 rateA,
                 rateB,
                 rateC):
        """Initialize a branch in the power grid.

        Args:
            from_bus (int): the bus number at the sending end of the branch.
            to_bus (int): the bus number at the receiVing end of the branch.
            r (float): the branch resistance
            x (float): the branch reactance
            b (float): the branch susceptance
            status (bool): indicates if the branch is online or offline
            rateA (float): The 1st rating of the line.
            rateB (float): The 2nd rating of the line
            rateC (float): The 3rd rating of the line.
        """
        self.id = self._ids.__next__()
        self.from_bus_id = from_bus
        self.to_bus_id = to_bus
        self.r = r
        self.x = x
        self.b = b
        self.status = status
        self.rateA = rateA
        self.rateB = rateB
        self.rateC = rateC
        self.tx_v = 0
        self.tx_gamma = 1
        
        return
        # You will need to implement the remainder of the __init__ function yourself.
        # You should also add some other class functions you deem necessary for stamping,
        # initializing, and processing results.
        
    # this is a custom function to allow each bus to reference the bus    
    def assign_buses(self, bus_vec):
        self.from_bus = bus_vec[self.from_bus_id-1]
        self.to_bus = bus_vec[self.to_bus_id-1]
        
        return
    def stamp_dense(self, inputY):
        # get the series conductance
        G = self.r/(self.r**2 + self.x**2)
        # Amplify by the TX stepping parameters
        G = G*(1+self.tx_v*self.tx_gamma)
        # stamp the conductance into the RE
        inputY[self.to_bus.node_Vr,self.to_bus.node_Vr] += G
        inputY[self.from_bus.node_Vr,self.from_bus.node_Vr] += G
        inputY[self.to_bus.node_Vr,self.from_bus.node_Vr] += -G
        inputY[self.from_bus.node_Vr,self.to_bus.node_Vr] += -G
        # stamp the conductance into the IM
        inputY[self.to_bus.node_Vi,self.to_bus.node_Vi] += G
        inputY[self.from_bus.node_Vi,self.from_bus.node_Vi] += G
        inputY[self.to_bus.node_Vi,self.from_bus.node_Vi] += -G
        inputY[self.from_bus.node_Vi,self.to_bus.node_Vi] += -G
        
        # get the Voltage Controlled Current Source (VCCS) Gain
        Av = self.x/(self.x**2 + self.r**2)
        # Amplify by the TX stepping parameters
        Av = Av*(1+self.tx_v*self.tx_gamma)
        # stamp the VCCS into RE
        inputY[self.to_bus.node_Vr,self.to_bus.node_Vi] += Av
        inputY[self.to_bus.node_Vr,self.from_bus.node_Vi] += -Av
        inputY[self.from_bus.node_Vr,self.to_bus.node_Vi] += -Av
        inputY[self.from_bus.node_Vr,self.from_bus.node_Vi] += Av
        
        # stamp the VCCS into IM
        inputY[self.to_bus.node_Vi,self.to_bus.node_Vr] += -Av
        inputY[self.to_bus.node_Vi,self.from_bus.node_Vr] += Av
        inputY[self.from_bus.node_Vi,self.to_bus.node_Vr] += Av
        inputY[self.from_bus.node_Vi,self.from_bus.node_Vr] += -Av
        
        # get the splitting current (VCCS) gain
        Av2 = self.b/2
        # Amplify by the TX stepping parameters
        Av2 = Av2*(1+self.tx_v*self.tx_gamma)
        # it references ground therefore only one stamp in RE & 1 in IM
        # from node shunt
        inputY[self.from_bus.node_Vr,self.from_bus.node_Vi] += -Av2
        inputY[self.from_bus.node_Vi,self.from_bus.node_Vr] += Av2
        # to node shunt
        inputY[self.to_bus.node_Vr,self.to_bus.node_Vi] += -Av2
        inputY[self.to_bus.node_Vi,self.to_bus.node_Vr] += Av2
        
        
        return
    
    def stamp_sparse(self, inputY_r, inputY_c, inputY_val):
        # get the series conductance
        G = self.r/(self.r**2 + self.x**2)
        # Amplify by the TX stepping parameters
        G = G*(1+self.tx_v*self.tx_gamma)
        # stamp the conductance into the RE
        #inputY[self.to_bus.node_Vr,self.to_bus.node_Vr] += G
        inputY_r = np.append(inputY_r,self.to_bus.node_Vr)
        inputY_c = np.append(inputY_c,self.to_bus.node_Vr)
        inputY_val = np.append(inputY_val,G)
        
        #inputY[self.from_bus.node_Vr,self.from_bus.node_Vr] += G
        inputY_r = np.append(inputY_r,self.from_bus.node_Vr)
        inputY_c = np.append(inputY_c,self.from_bus.node_Vr)
        inputY_val = np.append(inputY_val,G)
        
        #inputY[self.to_bus.node_Vr,self.from_bus.node_Vr] += -G
        inputY_r = np.append(inputY_r,self.to_bus.node_Vr)
        inputY_c = np.append(inputY_c,self.from_bus.node_Vr)
        inputY_val = np.append(inputY_val,-G)
        
        #inputY[self.from_bus.node_Vr,self.to_bus.node_Vr] += -G
        inputY_r = np.append(inputY_r,self.from_bus.node_Vr)
        inputY_c = np.append(inputY_c,self.to_bus.node_Vr)
        inputY_val = np.append(inputY_val,-G)
        
        # stamp the conductance into the IM
        #inputY[self.to_bus.node_Vi,self.to_bus.node_Vi] += G
        inputY_r = np.append(inputY_r,self.to_bus.node_Vi)
        inputY_c = np.append(inputY_c,self.to_bus.node_Vi)
        inputY_val = np.append(inputY_val,G)
        
        #inputY[self.from_bus.node_Vi,self.from_bus.node_Vi] += G
        inputY_r = np.append(inputY_r,self.from_bus.node_Vi)
        inputY_c = np.append(inputY_c,self.from_bus.node_Vi)
        inputY_val = np.append(inputY_val,G)
        
        #inputY[self.to_bus.node_Vi,self.from_bus.node_Vi] += -G
        inputY_r = np.append(inputY_r,self.to_bus.node_Vi)
        inputY_c = np.append(inputY_c,self.from_bus.node_Vi)
        inputY_val = np.append(inputY_val,-G)
        
        #inputY[self.from_bus.node_Vi,self.to_bus.node_Vi] += -G
        inputY_r = np.append(inputY_r,self.from_bus.node_Vi)
        inputY_c = np.append(inputY_c,self.to_bus.node_Vi)
        inputY_val = np.append(inputY_val,-G)
        
        
        # get the Voltage Controlled Current Source (VCCS) Gain
        Av = self.x/(self.x**2 + self.r**2)
        # Amplify by the TX stepping parameters
        Av = Av*(1+self.tx_v*self.tx_gamma)
        # stamp the VCCS into RE
        #inputY[self.to_bus.node_Vr,self.to_bus.node_Vi] += Av
        inputY_r = np.append(inputY_r,self.to_bus.node_Vr)
        inputY_c = np.append(inputY_c,self.to_bus.node_Vi)
        inputY_val = np.append(inputY_val,Av)
        
        #inputY[self.to_bus.node_Vr,self.from_bus.node_Vi] += -Av
        inputY_r = np.append(inputY_r,self.to_bus.node_Vr)
        inputY_c = np.append(inputY_c,self.from_bus.node_Vi)
        inputY_val = np.append(inputY_val,-Av)
        
        #inputY[self.from_bus.node_Vr,self.to_bus.node_Vi] += -Av
        inputY_r = np.append(inputY_r,self.from_bus.node_Vr)
        inputY_c = np.append(inputY_c,self.to_bus.node_Vi)
        inputY_val = np.append(inputY_val,-Av)
        
        #inputY[self.from_bus.node_Vr,self.from_bus.node_Vi] += Av
        inputY_r = np.append(inputY_r,self.from_bus.node_Vr)
        inputY_c = np.append(inputY_c,self.from_bus.node_Vi)
        inputY_val = np.append(inputY_val,Av)
        
        
        # stamp the VCCS into IM
        #inputY[self.to_bus.node_Vi,self.to_bus.node_Vr] += -Av
        inputY_r = np.append(inputY_r,self.to_bus.node_Vi)
        inputY_c = np.append(inputY_c,self.to_bus.node_Vr)
        inputY_val = np.append(inputY_val,-Av)
        
        #inputY[self.to_bus.node_Vi,self.from_bus.node_Vr] += Av
        inputY_r = np.append(inputY_r,self.to_bus.node_Vi)
        inputY_c = np.append(inputY_c,self.from_bus.node_Vr)
        inputY_val = np.append(inputY_val,Av)
        
        #inputY[self.from_bus.node_Vi,self.to_bus.node_Vr] += Av
        inputY_r = np.append(inputY_r,self.from_bus.node_Vi)
        inputY_c = np.append(inputY_c,self.to_bus.node_Vr)
        inputY_val = np.append(inputY_val,Av)
        
        #inputY[self.from_bus.node_Vi,self.from_bus.node_Vr] += -Av
        inputY_r = np.append(inputY_r,self.from_bus.node_Vi)
        inputY_c = np.append(inputY_c,self.from_bus.node_Vr)
        inputY_val = np.append(inputY_val,-Av)
        
        
        # get the splitting current (VCCS) gain
        Av2 = self.b/2
        # Amplify by the TX stepping parameters
        Av2 = Av2*(1+self.tx_v*self.tx_gamma)
        # it references ground therefore only one stamp in RE & 1 in IM
        # from node shunt
        #inputY[self.from_bus.node_Vr,self.from_bus.node_Vi] += -Av2
        inputY_r = np.append(inputY_r,self.from_bus.node_Vr)
        inputY_c = np.append(inputY_c,self.from_bus.node_Vi)
        inputY_val = np.append(inputY_val,-Av2)
        
        #inputY[self.from_bus.node_Vi,self.from_bus.node_Vr] += Av2
        inputY_r = np.append(inputY_r,self.from_bus.node_Vi)
        inputY_c = np.append(inputY_c,self.from_bus.node_Vr)
        inputY_val = np.append(inputY_val,Av2)
        
        # to node shunt
        #inputY[self.to_bus.node_Vr,self.to_bus.node_Vi] += -Av2
        inputY_r = np.append(inputY_r,self.to_bus.node_Vr)
        inputY_c = np.append(inputY_c,self.to_bus.node_Vi)
        inputY_val = np.append(inputY_val,-Av2)
        
        #inputY[self.to_bus.node_Vi,self.to_bus.node_Vr] += Av2
        inputY_r = np.append(inputY_r,self.to_bus.node_Vi)
        inputY_c = np.append(inputY_c,self.to_bus.node_Vr)
        inputY_val = np.append(inputY_val,Av2)
        
        return inputY_r, inputY_c, inputY_val
        
    def set_tx(self, inputTx_V, inputTx_Gamma):
        self.tx_v = inputTx_V
        self.tx_gamma = inputTx_Gamma
        
        return
        
        
        
        
        
        