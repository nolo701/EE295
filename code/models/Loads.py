from __future__ import division
from itertools import count


class Loads:
    _ids = count(0)

    def __init__(self,
                 Bus_id,
                 P,
                 Q,
                 IP,
                 IQ,
                 ZP,
                 ZQ,
                 area,
                 status):
        """Initialize an instance of a PQ or ZIP load in the power grid.

        Args:
            Bus (int): the bus where the load is located
            P (float): the active power of a constant power (PQ) load.
            Q (float): the reactive power of a constant power (PQ) load.
            IP (float): the active power component of a constant current load.
            IQ (float): the reactive power component of a constant current load.
            ZP (float): the active power component of a constant admittance load.
            ZQ (float): the reactive power component of a constant admittance load.
            area (int): location where the load is assigned to.
            status (bool): indicates if the load is in-service or out-of-service.
        """
        self.id = Loads._ids.__next__()
        self.Bus_id = Bus_id
        # Normalize P and Q to convert into pu system
        self.P = P/100
        self.Q = Q/100
        self.IP = IP
        self.IQ = IQ
        self.ZP = ZP
        self.ZQ = ZQ
        self.area = area
        self.status = status
        # You will need to implement the remainder of the __init__ function yourself.
        # You should also add some other class functions you deem necessary for stamping,
        # initializing, and processing results.
        
    def assign_buses(self, bus_vec):
        self.bus = bus_vec[self.Bus_id-1]
        return
    
    def stamp_dense(self, inputY, inputJ, prev_sol):
        # grab values used to evaluate the functions
        P = self.P
        Vr = prev_sol[self.bus.node_Vr]
        Vi = prev_sol[self.bus.node_Vi]
        Q = self.Q
        # helpful value that is repeated
        denom = (Vr**2+Vi**2)
        
        # Constant Current source of RE
        # evaluate the functions to get info for circuit element stamps
        Irg_prev = (P*Vr+Q*Vi)/denom
        dIrg_wrt_Vr = (P*(Vi**2-Vr**2) - 2*Q*Vr*Vi)/(denom)**2
        dIrg_wrt_Vi = (Q*(Vr**2-Vi**2) - 2*P*Vr*Vi)/(denom)**2

        # Get summed value for the CCS
        Vr_load = -Irg_prev + dIrg_wrt_Vr*Vr + dIrg_wrt_Vi*Vi
        # stamp the conductance
        inputY[self.bus.node_Vr, self.bus.node_Vr] += dIrg_wrt_Vr
        # stamp the VCCS
        inputY[self.bus.node_Vr, self.bus.node_Vi] += dIrg_wrt_Vi
        # stamp the CCS
        inputJ[self.bus.node_Vr] += -Vr_load
        
        # Constant Current source of IM
        # evaluate the functions to get info to stamp the constant current source
        Iig_prev = (P*Vi-Q*Vr)/denom
        dIig_wrt_Vr = dIrg_wrt_Vi
        dIig_wrt_Vi = -dIrg_wrt_Vr

        # Final value of Taylor Series Expansion
        Vi_load = -Iig_prev + dIig_wrt_Vr*Vr + dIig_wrt_Vi*Vi
        # stamp the conductance
        inputY[self.bus.node_Vi, self.bus.node_Vr] += dIig_wrt_Vr
        # stamp the VCCS
        inputY[self.bus.node_Vi, self.bus.node_Vi] += dIig_wrt_Vi
        # stamp the CCS
        inputJ[self.bus.node_Vi] += -Vi_load
        
        
        
        
        
        
        return
        