from __future__ import division
from models.Buses import Buses
from itertools import count
import numpy as np


class Transformers:
    _ids = count(0)

    def __init__(self,
                 from_bus_id,
                 to_bus_id,
                 r,
                 x,
                 status,
                 tr,
                 ang,
                 Gsh_raw,
                 Bsh_raw,
                 rating):
        """Initialize a transformer instance

        Args:
            from_bus (int): the primary or sending end bus of the transformer.
            to_bus (int): the secondary or receiving end bus of the transformer
            r (float): the line resitance of the transformer in
            x (float): the line reactance of the transformer
            status (int): indicates if the transformer is active or not
            tr (float): transformer turns ratio
            ang (float): the phase shift angle of the transformer
            Gsh_raw (float): the shunt conductance of the transformer
            Bsh_raw (float): the shunt admittance of the transformer
            rating (float): the rating in MVA of the transformer
        """
        self.id = self._ids.__next__()
        self.from_bus_id = from_bus_id
        self.to_bus_id = to_bus_id
        self.r = r
        self.x = x
        self.status = status
        self.tr = tr
        self.tr_eff = tr
        self.ang = ang
        self.ang_eff = ang
        self.Gsh_raw = Gsh_raw
        self.Bsh_raw = Bsh_raw
        self.rating = rating
        self.tx_v = 0
        self.tx_gamma = 1

        # You will need to implement the remainder of the __init__ function yourself.
        # You should also add some other class functions you deem necessary for stamping,
        # initializing, and processing results.
    # this is a custom function to allow each bus to reference the bus    
    def assign_buses(self, bus_vec):
        self.from_bus = bus_vec[self.from_bus_id-1]
        self.to_bus = bus_vec[self.to_bus_id-1]    
    
    def assign_nodes(self):
        # Real - From 1
        self.vs_re_from_1 = Buses._node_index.__next__()
        # Imag - From 1
        self.vs_im_from_1 = Buses._node_index.__next__()
        # Real - From (V1R)
        self.node_re_from = Buses._node_index.__next__()
        # Imag - From (V1I)
        self.node_im_from = Buses._node_index.__next__()
        # Real - From 2
        self.vs_re_from_2 = Buses._node_index.__next__()       
        # Imag - From 2
        self.vs_im_from_2 = Buses._node_index.__next__()
        # Real - To (V2R)
        self.node_re_to = Buses._node_index.__next__()
        # Imag - To (V2I)
        self.node_im_to = Buses._node_index.__next__()
        return
        
    def stamp_dense(self, inputY):
        # Stamp VCVS RE-From 1
        # "Gain" of the source
        #inputY = 0*np.copy(inputY_test)
        
        Av = self.tr_eff * np.cos(self.ang_eff)
        # Set the location voltage drop
        inputY[self.from_bus.node_Vr, self.vs_re_from_1] += 1
        inputY[self.node_re_from, self.vs_re_from_1] += -1
        # Set the voltage value from KVL
        # + Terminal
        inputY[self.vs_re_from_1, self.from_bus.node_Vr] += 1
        # - Terminal
        inputY[self.vs_re_from_1, self.node_re_from] += -1
        # + Referenced Terminal
        inputY[self.vs_re_from_1, self.node_re_to] += -Av
        
        # Stamp VCVS RE-From 2
        # "Gain" of the source
        Av = -1 * self.tr_eff * np.sin(self.ang_eff)
        # Set the location voltage drop
        inputY[self.node_re_from, self.vs_re_from_2] += 1
        # Set the voltage value from KVL
        # + Terminal
        inputY[self.vs_re_from_2, self.node_re_from] += 1
        # - Terminal (grounded)
        #inputY[self.vs_re_from_2, self.node_re_from] += -1
        # + Referenced Terminal
        inputY[self.vs_re_from_2, self.node_im_to] += -Av
        
        # Stamp VCVS IM-From 1
        # "Gain" of the source
        Av = self.tr_eff * np.sin(self.ang_eff)
        # Set the location voltage drop
        inputY[self.from_bus.node_Vi, self.vs_im_from_1] += 1
        inputY[self.node_im_from, self.vs_im_from_1] += -1
        # Set the voltage value from KVL
        # + Terminal
        inputY[self.vs_im_from_1, self.from_bus.node_Vi] += 1
        # - Terminal
        inputY[self.vs_im_from_1, self.node_im_from] += -1
        # + Referenced Terminal
        inputY[self.vs_im_from_1, self.node_re_to] += -Av
        
        # Stamp VCVS IM-From 2
        # "Gain" of the source
        Av = self.tr_eff * np.cos(self.ang_eff)
        # Set the location voltage drop
        inputY[self.node_im_from, self.vs_im_from_2] += 1
        # Set the voltage value from KVL
        # + Terminal
        inputY[self.vs_im_from_2, self.node_im_from] += 1
        # - Terminal (grounded)
        #inputY[self.vs_re_from_2, self.node_re_from] += -1
        # + Referenced Terminal
        inputY[self.vs_im_from_2, self.node_im_to] += -Av
        
        # Stamp Current Controlled Current Sources on the To-Side
        # Stamp CCCS RE-TO: ref I1RE
        # Current "Gain"
        Av = -1 * self.tr_eff * np.cos(self.ang_eff)
        inputY[self.node_re_to, self.vs_re_from_1] += Av
        
        # Stamp CCCS RE-TO: ref I1IM
        # Current "Gain"
        Av = -1 * self.tr_eff * np.sin(self.ang_eff)
        inputY[self.node_re_to, self.vs_im_from_1] += Av
        
        # Stamp CCCS IM-TO: ref I1RE
        # Current "Gain"
        Av = self.tr_eff * np.sin(self.ang_eff)
        inputY[self.node_im_to, self.vs_re_from_1] += Av
        
        # Stamp CCCS IM-TO: ref I1IM
        # Current "Gain"
        Av = -1 * self.tr_eff * np.cos(self.ang_eff)
        inputY[self.node_im_to, self.vs_im_from_1] += Av
        
        # Stamp the psuedo branch that acts as as loss
        # Stamp the VCCS in the RE
        Av = self.x/(self.r**2+self.x**2)
        # Amplify by the TX stepping parameters
        Av = Av*(1+self.tx_v*self.tx_gamma)
        inputY[self.to_bus.node_Vr, self.to_bus.node_Vi] += Av
        inputY[self.node_re_to, self.to_bus.node_Vi] += -Av
        inputY[self.to_bus.node_Vr, self.node_im_to] += -Av
        inputY[self.node_re_to, self.node_im_to] += Av
        
        # Stamp the conductance in the RE
        G = self.r/(self.r**2+self.x**2)
        # Amplify by the TX stepping parameters
        G = G*(1+self.tx_v*self.tx_gamma)
        inputY[self.to_bus.node_Vr, self.to_bus.node_Vr] += G
        inputY[self.to_bus.node_Vr, self.node_re_to] += -G
        inputY[self.node_re_to,self.to_bus.node_Vr] += -G
        inputY[self.node_re_to,self.node_re_to] += G
        
        # Stamp the VCCS in the IM
        Av = -1*self.x/(self.r**2+self.x**2)
        # Amplify by the TX stepping parameters
        Av = Av*(1+self.tx_v*self.tx_gamma)
        inputY[self.to_bus.node_Vi, self.to_bus.node_Vr] += Av
        inputY[self.to_bus.node_Vi, self.node_re_to] += -Av
        inputY[self.node_im_to, self.to_bus.node_Vr] += -Av
        inputY[self.node_im_to, self.node_re_to] += Av
        
        # Stamp the conductance in the RE 
        G = self.r/(self.r**2+self.x**2)
        # Amplify by the TX stepping parameters
        G = G*(1+self.tx_v*self.tx_gamma)
        inputY[self.to_bus.node_Vi, self.to_bus.node_Vi] += G
        inputY[self.to_bus.node_Vi, self.node_im_to] += -G
        inputY[self.node_im_to,self.to_bus.node_Vi] += -G
        inputY[self.node_im_to,self.node_im_to] += G

        pass
        
        
    def stamp_sparse(self, inputY_r, inputY_c, inputY_val):
        Av = self.tr * np.cos(self.ang_eff)
        # Set the location voltage drop
        #inputY[self.from_bus.node_Vr, self.vs_re_from_1] += 1
        inputY_r.append(self.from_bus.node_Vr)
        inputY_c.append(self.vs_re_from_1)
        inputY_val.append(1)
        
        #inputY[self.node_re_from, self.vs_re_from_1] += -1
        inputY_r.append(self.node_re_from)
        inputY_c.append(self.vs_re_from_1)
        inputY_val.append(-1)
        
        # Set the voltage value from KVL
        # + Terminal
        #inputY[self.vs_re_from_1, self.from_bus.node_Vr] += 1
        inputY_r.append(self.vs_re_from_1)
        inputY_c.append(self.from_bus.node_Vr)
        inputY_val.append(1)
        
        # - Terminal
        #inputY[self.vs_re_from_1, self.node_re_from] += -1
        inputY_r.append(self.vs_re_from_1)
        inputY_c.append(self.node_re_from)
        inputY_val.append(-1)
        
        # + Referenced Terminal
        #inputY[self.vs_re_from_1, self.node_re_to] += -Av
        inputY_r.append(self.vs_re_from_1)
        inputY_c.append(self.node_re_to)
        inputY_val.append(-Av)
        
        # Stamp VCVS RE-From 2
        # "Gain" of the source
        Av = -1 * self.tr_eff * np.sin(self.ang_eff)
        # Set the location voltage drop
        #inputY[self.node_re_from, self.vs_re_from_2] += 1
        inputY_r.append(self.node_re_from)
        inputY_c.append(self.vs_re_from_2)
        inputY_val.append(1)
        
        # Set the voltage value from KVL
        # + Terminal
        #inputY[self.vs_re_from_2, self.node_re_from] += 1
        inputY_r.append(self.vs_re_from_2)
        inputY_c.append(self.node_re_from)
        inputY_val.append(1)
        
        # - Terminal (grounded)
        #inputY[self.vs_re_from_2, self.node_re_from] += -1
        # + Referenced Terminal
        #inputY[self.vs_re_from_2, self.node_im_to] += -Av
        inputY_r.append(self.vs_re_from_2)
        inputY_c.append(self.node_im_to)
        inputY_val.append(-Av)
        
        
        # Stamp VCVS IM-From 1
        # "Gain" of the source
        Av = self.tr_eff * np.sin(self.ang_eff)
        # Set the location voltage drop
        #inputY[self.from_bus.node_Vi, self.vs_im_from_1] += 1
        inputY_r.append(self.from_bus.node_Vi)
        inputY_c.append(self.vs_im_from_1)
        inputY_val.append(1)
        
        #inputY[self.node_im_from, self.vs_im_from_1] += -1
        inputY_r.append(self.node_im_from)
        inputY_c.append(self.vs_im_from_1)
        inputY_val.append(-1)
        
        # Set the voltage value from KVL
        # + Terminal
        #inputY[self.vs_im_from_1, self.from_bus.node_Vi] += 1
        inputY_r.append(self.vs_im_from_1)
        inputY_c.append(self.from_bus.node_Vi)
        inputY_val.append(1)
        
        # - Terminal
        #inputY[self.vs_im_from_1, self.node_im_from] += -1
        inputY_r.append(self.vs_im_from_1)
        inputY_c.append(self.node_im_from)
        inputY_val.append(-1)
        
        # + Referenced Terminal
        #inputY[self.vs_im_from_1, self.node_re_to] += -Av
        inputY_r.append(self.vs_im_from_1)
        inputY_c.append(self.node_re_to)
        inputY_val.append(-Av)
        
        
        # Stamp VCVS IM-From 2
        # "Gain" of the source
        Av = self.tr_eff * np.cos(self.ang_eff)
        # Set the location voltage drop
        #inputY[self.node_im_from, self.vs_im_from_2] += 1
        inputY_r.append(self.node_im_from)
        inputY_c.append(self.vs_im_from_2)
        inputY_val.append(1)
        
        # Set the voltage value from KVL
        # + Terminal
        #inputY[self.vs_im_from_2, self.node_im_from] += 1
        inputY_r.append(self.vs_im_from_2)
        inputY_c.append(self.node_im_from)
        inputY_val.append(1)
        
        # - Terminal (grounded)
        #inputY[self.vs_re_from_2, self.node_re_from] += -1
        # + Referenced Terminal
        #inputY[self.vs_im_from_2, self.node_im_to] += -Av
        inputY_r.append(self.vs_im_from_2)
        inputY_c.append(self.node_im_to)
        inputY_val.append(-Av)
        
        
        # Stamp Current Controlled Current Sources on the To-Side
        # Stamp CCCS RE-TO: ref I1RE
        # Current "Gain"
        Av = -1 * self.tr_eff * np.cos(self.ang_eff)
        #inputY[self.node_re_to, self.vs_re_from_1] += Av
        inputY_r.append(self.node_re_to)
        inputY_c.append(self.vs_re_from_1)
        inputY_val.append(Av)
        
        # Stamp CCCS RE-TO: ref I1IM
        # Current "Gain"
        Av = -1 * self.tr_eff * np.sin(self.ang_eff)
        #inputY[self.node_re_to, self.vs_im_from_1] += Av
        inputY_r.append(self.node_re_to)
        inputY_c.append(self.vs_im_from_1)
        inputY_val.append(Av)
        
        # Stamp CCCS IM-TO: ref I1RE
        # Current "Gain"
        Av = self.tr_eff * np.sin(self.ang_eff)
        #inputY[self.node_im_to, self.vs_re_from_1] += Av
        inputY_r.append(self.node_im_to)
        inputY_c.append(self.vs_re_from_1)
        inputY_val.append(Av)
        
        # Stamp CCCS IM-TO: ref I1IM
        # Current "Gain"
        Av = -1 * self.tr_eff * np.cos(self.ang_eff)
        #inputY[self.node_im_to, self.vs_im_from_1] += Av
        inputY_r.append(self.node_im_to)
        inputY_c.append(self.vs_im_from_1)
        inputY_val.append(Av)
        
        # Stamp the psuedo branch that acts as as loss
        # Stamp the VCCS in the RE
        Av = self.x/(self.r**2+self.x**2)
        # Amplify by the TX stepping parameters
        Av = Av*(1+self.tx_v*self.tx_gamma)
        #inputY[self.to_bus.node_Vr, self.to_bus.node_Vi] += Av
        inputY_r.append(self.to_bus.node_Vr)
        inputY_c.append(self.to_bus.node_Vi)
        inputY_val.append( Av)
        
        #inputY[self.node_re_to, self.to_bus.node_Vi] += -Av
        inputY_r.append(self.node_re_to)
        inputY_c.append(self.to_bus.node_Vi)
        inputY_val.append(-Av)
        
        #inputY[self.to_bus.node_Vr, self.node_im_to] += -Av
        inputY_r.append(self.to_bus.node_Vr)
        inputY_c.append(self.node_im_to)
        inputY_val.append(-Av)
        
        #inputY[self.node_re_to, self.node_im_to] += Av
        inputY_r.append(self.node_re_to)
        inputY_c.append(self.node_im_to)
        inputY_val.append(Av)
        
        
        # Stamp the conductance in the RE
        G = self.r/(self.r**2+self.x**2)
        # Amplify by the TX stepping parameters
        G = G*(1+self.tx_v*self.tx_gamma)
        #inputY[self.to_bus.node_Vr, self.to_bus.node_Vr] += G
        inputY_r.append(self.to_bus.node_Vr)
        inputY_c.append(self.to_bus.node_Vr)
        inputY_val.append(G)
        
        #inputY[self.to_bus.node_Vr, self.node_re_to] += -G
        inputY_r.append(self.to_bus.node_Vr)
        inputY_c.append(self.node_re_to)
        inputY_val.append(-G)
        
        #inputY[self.node_re_to,self.to_bus.node_Vr] += -G
        inputY_r.append(self.node_re_to)
        inputY_c.append(self.to_bus.node_Vr)
        inputY_val.append(-G)
        
        #inputY[self.node_re_to,self.node_re_to] += G
        inputY_r.append(self.node_re_to)
        inputY_c.append(self.node_re_to)
        inputY_val.append(G)
        
        # Stamp the VCCS in the IM
        Av = -1*self.x/(self.r**2+self.x**2)
        # Amplify by the TX stepping parameters
        Av = Av*(1+self.tx_v*self.tx_gamma)
        #inputY[self.to_bus.node_Vi, self.to_bus.node_Vr] += Av
        inputY_r.append(self.to_bus.node_Vi)
        inputY_c.append(self.to_bus.node_Vr)
        inputY_val.append(Av)
        
        #inputY[self.to_bus.node_Vi, self.node_re_to] += -Av
        inputY_r.append(self.to_bus.node_Vi)
        inputY_c.append(self.node_re_to)
        inputY_val.append(-Av)
        
        #inputY[self.node_im_to, self.to_bus.node_Vr] += -Av
        inputY_r.append(self.node_im_to)
        inputY_c.append(self.to_bus.node_Vr)
        inputY_val.append(-Av)
        
        #inputY[self.node_im_to, self.node_re_to] += Av
        inputY_r.append(self.node_im_to)
        inputY_c.append(self.node_re_to)
        inputY_val.append(Av)
        
        
        # Stamp the conductance in the RE 
        G = self.r/(self.r**2+self.x**2)
        # Amplify by the TX stepping parameters
        G = G*(1+self.tx_v*self.tx_gamma)
        #inputY[self.to_bus.node_Vi, self.to_bus.node_Vi] += G
        inputY_r.append(self.to_bus.node_Vi)
        inputY_c.append(self.to_bus.node_Vi)
        inputY_val.append(G)
        
        #inputY[self.to_bus.node_Vi, self.node_im_to] += -G
        inputY_r.append(self.to_bus.node_Vi)
        inputY_c.append(self.node_im_to)
        inputY_val.append(-G)
        
        #inputY[self.node_im_to,self.to_bus.node_Vi] += -G
        inputY_r.append(self.node_im_to)
        inputY_c.append(self.to_bus.node_Vi)
        inputY_val.append(-G)
        
        #inputY[self.node_im_to,self.node_im_to] += G
        inputY_r.append(self.node_im_to)
        inputY_c.append(self.node_im_to)
        inputY_val.append(G)
        
        return inputY_r, inputY_c, inputY_val
    
    def set_tx(self, inputTx_V, inputTx_Gamma):
        self.tx_v = inputTx_V
        self.tx_gamma = inputTx_Gamma
        # update the effective turn ratio
        self.tr_eff = self.tr - (self.tr-1)*self.tx_v
        # update the effective angle
        self.ang_eff = self.ang - (self.ang)*self.tx_v
        
        return