from __future__ import division
from itertools import count
from models.Buses import Buses
from scripts.stamp_helpers import *
from models.global_vars import global_vars

import sympy as sym
from sympy import *
from sympy import *
init_printing(use_unicode=False, wrap_line=False, no_global=True)


# Code to create the functions used to evaluate the linearized model
# instantiate symbols
var_Lr = sym.symbols('lambda1')
var_Li = sym.symbols('lambda2')
var_Lq = sym.symbols('lambda3')
var_Vr = sym.symbols('Vr')
var_Vi = sym.symbols('Vi')
var_Q = sym.symbols('Q')
var_P = sym.symbols('P')
var_Vset = sym.symbols('Vset')

# USING P = +p notation

# Base equation
PF_eq_load_real = (var_P*var_Vr + var_Q*var_Vi)/(var_Vr**2 + var_Vi**2)
PF_eq_load_imag = (var_P*var_Vi - var_Q*var_Vr)/(var_Vr**2 + var_Vi**2)

#sym.pprint(PF_eq_load_real)

Lagrange_eq_load = var_Lr*PF_eq_load_real + var_Li*PF_eq_load_imag
sym.pprint(Lagrange_eq_load)
# Dual current equations
Dual_eq_r = sym.diff(Lagrange_eq_load,var_Vr)
Dual_eq_i = sym.diff(Lagrange_eq_load,var_Vi)

#sym.pprint(Dual_eq_r)
#sym.pprint(sym.diff(PF_eq_load_real,var_Vr))

# Need to linearize the TSE again
# Real terms
lin_dual_eq_r_wrt_vr = sym.diff(Dual_eq_r,var_Vr)
lin_dual_eq_r_wrt_vi = sym.diff(Dual_eq_r,var_Vi)

lin_dual_eq_r_wrt_lr = sym.diff(Dual_eq_r,var_Lr)
lin_dual_eq_r_wrt_li = sym.diff(Dual_eq_r,var_Li)


# Imag terms
lin_dual_eq_i_wrt_vr = sym.diff(Dual_eq_i,var_Vr)
lin_dual_eq_i_wrt_vi = sym.diff(Dual_eq_i,var_Vi)

lin_dual_eq_i_wrt_lr = sym.diff(Dual_eq_i,var_Lr)
lin_dual_eq_i_wrt_li = sym.diff(Dual_eq_i,var_Li)

    
class Loads:
    _ids = count(0)
    
    def __init__(self,
                 Bus,
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
            self.P (float): the active power of a constant power (PQ) load.
            Q (float): the reactive power of a constant power (PQ) load.
            IP (float): the active power component of a constant current load.
            IQ (float): the reactive power component of a constant current load.
            ZP (float): the active power component of a constant admittance load.
            ZQ (float): the reactive power component of a constant admittance load.
            area (int): location where the load is assigned to.
            status (bool): indicates if the load is in-service or out-of-service.
        """
        self.Bus = Bus
        self.P_MW = P
        self.Q_MVA = Q
        self.IP_MW = IP
        self.IQ_MVA = IQ
        self.ZP_MW = ZP
        self.ZQ_MVA = ZQ
        self.area = area
        self.status = status
        self.id = Loads._ids.__next__()

        self.P = P/global_vars.base_MVA
        self.Q = Q/global_vars.base_MVA
        self.IP = IP/global_vars.base_MVA
        self.IQ = IQ/global_vars.base_MVA
        self.ZP = ZP/global_vars.base_MVA
        self.ZQ = ZQ/global_vars.base_MVA
    
    def assign_indexes(self, bus):
        # Nodes shared by generators on the same bus
        self.Vr_node = bus[Buses.bus_key_[self.Bus]].node_Vr
        self.Vi_node = bus[Buses.bus_key_[self.Bus]].node_Vi
        # check something about gen_type??
        self.Lr_node = bus[Buses.bus_key_[self.Bus]].node_Lr
        self.Li_node = bus[Buses.bus_key_[self.Bus]].node_Li
        
    
    def stamp(self, V, Y_val, Y_row, Y_col, J_val, J_row, idx_Y, idx_J):
        Vr = V[self.Vr_node]
        Vi = V[self.Vi_node]

        Irg_hist = (self.P*Vr+self.Q*Vi)/(Vr**2+Vi**2)
        dIrldVr = (self.P*(Vi**2-Vr**2) - 2*self.Q*Vr*Vi)/(Vr**2+Vi**2)**2
        dIrldVi = (self.Q*(Vr**2-Vi**2) - 2*self.P*Vr*Vi)/(Vr**2+Vi**2)**2
        Vr_J_stamp = -Irg_hist + dIrldVr*Vr + dIrldVi*Vi
        
        idx_Y = stampY(self.Vr_node, self.Vr_node, dIrldVr, Y_val, Y_row, Y_col, idx_Y)
        idx_Y = stampY(self.Vr_node, self.Vi_node, dIrldVi, Y_val, Y_row, Y_col, idx_Y)
        idx_J = stampJ(self.Vr_node, Vr_J_stamp, J_val, J_row, idx_J)

        Iig_hist = (self.P*Vi-self.Q*Vr)/(Vr**2+Vi**2)
        dIildVi = -dIrldVr
        dIildVr = dIrldVi
        Vi_J_stamp = -Iig_hist + dIildVr*Vr + dIildVi*Vi

        idx_Y = stampY(self.Vi_node, self.Vr_node, dIildVr, Y_val, Y_row, Y_col, idx_Y)
        idx_Y = stampY(self.Vi_node, self.Vi_node, dIildVi, Y_val, Y_row, Y_col, idx_Y)
        idx_J = stampJ(self.Vi_node, Vi_J_stamp, J_val, J_row, idx_J)

        return (idx_Y, idx_J)

    def stamp_dual(self, V, Y_val, Y_row, Y_col, J_val, J_row, idx_Y, idx_J):
        # You need to implement this.
        inVr = V[self.Vr_node]
        inVi = V[self.Vi_node]
        inQ = self.Q
        inLr = V[self.Lr_node]
        inLi = V[self.Li_node]

        ''' * * * * * VR * * * * * * * * * * * * * * * *    '''
        # Evaluate for the total
        eval_r = Dual_eq_r.subs([(var_Vr, inVr), (var_Vi, inVi), (var_Q, inQ), (var_Lr, inLr), (var_Li, inLi), (var_P, self.P)])
        # Primal Terms
        # VR
        eval_r_vr = lin_dual_eq_r_wrt_vr.subs([(var_Vr, inVr), (var_Vi, inVi), (var_Q, inQ), (var_Lr, inLr), (var_Li, inLi), (var_P, self.P)])
        # VI
        eval_r_vi = lin_dual_eq_r_wrt_vi.subs([(var_Vr, inVr), (var_Vi, inVi), (var_Q, inQ), (var_Lr, inLr), (var_Li, inLi), (var_P, self.P)])
        # Dual Terms
        # LR
        eval_r_lr = lin_dual_eq_r_wrt_lr.subs([(var_Vr, inVr), (var_Vi, inVi), (var_Q, inQ), (var_Lr, inLr), (var_Li, inLi), (var_P, self.P)])
        # LI
        eval_r_li = lin_dual_eq_r_wrt_li.subs([(var_Vr, inVr), (var_Vi, inVi), (var_Q, inQ), (var_Lr, inLr), (var_Li, inLi), (var_P, self.P)])
        
        ''' * * * * * VI * * * * * * * * * * * * * * * *    '''
        # Evaluate for the total
        eval_i = Dual_eq_i.subs([(var_Vr, inVr), (var_Vi, inVi), (var_Q, inQ), (var_Lr, inLr), (var_Li, inLi), (var_P, self.P)])
        # Primal Terms
        # VR
        eval_i_vr = lin_dual_eq_i_wrt_vr.subs([(var_Vr, inVr), (var_Vi, inVi), (var_Q, inQ), (var_Lr, inLr), (var_Li, inLi), (var_P, self.P)])
        # VI
        eval_i_vi = lin_dual_eq_i_wrt_vi.subs([(var_Vr, inVr), (var_Vi, inVi), (var_Q, inQ), (var_Lr, inLr), (var_Li, inLi), (var_P, self.P)])
        # Dual Terms
        # LR
        eval_i_lr = lin_dual_eq_i_wrt_lr.subs([(var_Vr, inVr), (var_Vi, inVi), (var_Q, inQ), (var_Lr, inLr), (var_Li, inLi), (var_P, self.P)])
        # LI
        eval_i_li = lin_dual_eq_i_wrt_li.subs([(var_Vr, inVr), (var_Vi, inVi), (var_Q, inQ), (var_Lr, inLr), (var_Li, inLi), (var_P, self.P)])
        
        ''' Start stamping the values calculated from above '''
        # Start stamping the terms in the Lr row
        # Add up the hitorical
        IR_hist = eval_r - (inVr*eval_r_vr) - (inVi*eval_r_vi) - (inLr*eval_r_lr) - (inLi*eval_r_li)
        II_hist = eval_i - (inVr*eval_i_vr) - (inVi*eval_i_vi) - (inLr*eval_i_lr) - (inLi*eval_i_li)
        # Stamp the historical
        idx_J = stampJ(self.Lr_node, -IR_hist, J_val, J_row, idx_J)
        idx_J = stampJ(self.Li_node, -II_hist, J_val, J_row, idx_J)
        # Stamp the terms related to row Lr
        idx_Y = stampY(self.Lr_node, self.Vr_node, eval_r_vr, Y_val, Y_row, Y_col, idx_Y)
        idx_Y = stampY(self.Lr_node, self.Vi_node, eval_r_vi, Y_val, Y_row, Y_col, idx_Y)
        idx_Y = stampY(self.Lr_node, self.Lr_node, eval_r_lr, Y_val, Y_row, Y_col, idx_Y)
        idx_Y = stampY(self.Lr_node, self.Li_node, eval_r_li, Y_val, Y_row, Y_col, idx_Y)
        # Stamp the terms related to row Li
        idx_Y = stampY(self.Li_node, self.Vr_node, eval_i_vr, Y_val, Y_row, Y_col, idx_Y)
        idx_Y = stampY(self.Li_node, self.Vi_node, eval_i_vi, Y_val, Y_row, Y_col, idx_Y)
        idx_Y = stampY(self.Li_node, self.Lr_node, eval_i_lr, Y_val, Y_row, Y_col, idx_Y)
        idx_Y = stampY(self.Li_node, self.Li_node, eval_i_li, Y_val, Y_row, Y_col, idx_Y)

        
        return (idx_Y, idx_J)

    def calc_residuals(self, resid, V):
        P = self.P
        Vr = V[self.Vr_node]
        Vi = V[self.Vi_node]
        Q = self.Q
        resid[self.Vr_node] += (P*Vr+Q*Vi)/(Vr**2+Vi**2)
        resid[self.Vi_node] += (P*Vi-Q*Vr)/(Vr**2+Vi**2)
