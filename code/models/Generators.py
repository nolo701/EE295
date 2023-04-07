from __future__ import division
from itertools import count
from scripts.global_vars import global_vars


class Generators:
    _ids = count(0)
    RemoteBusGens = dict()
    RemoteBusRMPCT = dict()
    gen_bus_key_ = {}
    total_P = 0

    def __init__(self,
                 Bus_id,
                 P,
                 Vset,
                 Qmax,
                 Qmin,
                 Pmax,
                 Pmin,
                 Qinit,
                 RemoteBus,
                 RMPCT,
                 gen_type):
        """Initialize an instance of a generator in the power grid.

        Args:
            Bus (int): the bus number where the generator is located.
            P (float): the current amount of active power the generator is providing.
            Vset (float): the voltage setpoint that the generator must remain fixed at.
            Qmax (float): maximum reactive power
            Qmin (float): minimum reactive power
            Pmax (float): maximum active power
            Pmin (float): minimum active power
            Qinit (float): the initial amount of reactive power that the generator is supplying or absorbing.
            RemoteBus (int): the remote bus that the generator is controlling
            RMPCT (float): the percent of total MVAR required to hand the voltage at the controlled bus
            gen_type (str): the type of generator
        """

        self.id = self._ids.__next__()
        self.Bus_id = Bus_id
        #Normalize the P with 100 to convert to pu
        self.P = P/100
        self.Vset = Vset
        self.Qmax = Qmax
        self.Qmin = Qmin
        self.Pmax = Pmax
        self.Pmin = Pmin
        self.Qinit = Qinit
        self.RemoteBus = RemoteBus
        self.RMPCT = RMPCT
        self.gen_type = gen_type

        # You will need to implement the remainder of the __init__ function yourself.
        # You should also add some other class functions you deem necessary for stamping,
        # initializing, and processing results.
        return
    
    def assign_buses(self, bus_vec):
        self.bus = bus_vec[self.Bus_id-1]
        return
    
    def stamp_dense(self, inputY, inputJ, prev_sol):
        # grab values used to evaluate the functions
        P = -self.P
        Vr = prev_sol[self.bus.node_Vr]
        Vi = prev_sol[self.bus.node_Vi]
        Q = prev_sol[self.bus.node_Q]
        # helpful value that is repeated
        denom = (Vr**2+Vi**2)
        
        # Constant Current source of RE
        # evaluate the functions to get info for circuit element stamps
        Irg_prev = (P*Vr-Q*Vi)/denom
        dIrg_wrt_Vr = (P*(Vi**2-Vr**2) + 2*Q*Vr*Vi)/(denom)**2
        dIrg_wrt_Vi = (Q*(Vi**2-Vr**2) - 2*P*Vr*Vi)/(denom)**2
        dIrg_wrt_Q = -Vi/denom
        # Get summed value for the CCS
        Vr_gen = Irg_prev - dIrg_wrt_Vr*Vr - dIrg_wrt_Vi*Vi - dIrg_wrt_Q*Q
        # stamp the conductance
        inputY[self.bus.node_Vr, self.bus.node_Vr] += dIrg_wrt_Vr
        # stamp the VCCS
        inputY[self.bus.node_Vr, self.bus.node_Vi] += dIrg_wrt_Vi
        # stamp the extra var
        inputY[self.bus.node_Vr, self.bus.node_Q] += dIrg_wrt_Q
        # stamp the CCS
        inputJ[self.bus.node_Vr] += -Vr_gen
        
        # Constant Current source of IM
        # evaluate the functions to get info to stamp the constant current source
        Iig_prev = (P*Vi+Q*Vr)/denom
        dIig_wrt_Vr = dIrg_wrt_Vi
        dIig_wrt_Vi = -dIrg_wrt_Vr
        dIig_wrt_Q = Vr/denom
        # Final value of Taylor Series Expansion
        Vi_gen = Iig_prev - dIig_wrt_Vr*Vr - dIig_wrt_Vi*Vi - dIig_wrt_Q*Q
        # stamp the conductance
        inputY[self.bus.node_Vi, self.bus.node_Vr] += dIig_wrt_Vr
        # stamp the VCCS
        inputY[self.bus.node_Vi, self.bus.node_Vi] += dIig_wrt_Vi
        # stamp the extra var
        inputY[self.bus.node_Vi, self.bus.node_Q] += dIig_wrt_Q
        # stamp the CCS
        inputJ[self.bus.node_Vi] += -Vi_gen
        
        # Apply the VSet constraint (not a circuit element but required for coupling)
        Vset_prev = self.Vset**2 - Vr**2 - Vi**2
        dVset_wrt_Vr = 2*Vr
        dVset_wrt_Vi = 2*Vi
        Vset_gen = -Vset_prev - dVset_wrt_Vi*Vi - dVset_wrt_Vr*Vr
        # stamp them
        inputY[self.bus.node_Q, self.bus.node_Vr] += dVset_wrt_Vr
        inputY[self.bus.node_Q, self.bus.node_Vi] += dVset_wrt_Vi
        inputJ[self.bus.node_Q] += -Vset_gen
            
        return
    
    