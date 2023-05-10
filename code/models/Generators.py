from __future__ import division
from itertools import count
from scripts.global_vars import global_vars
from models.Buses import Buses
from scripts.stamp_helpers import *
from models.global_vars import global_vars

#from sympy import Subs
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
PF_eq_gen_real = (-var_P*var_Vr + var_Q*var_Vi)/(var_Vr**2 + var_Vi**2)
PF_eq_gen_imag = (-var_P*var_Vi - var_Q*var_Vr)/(var_Vr**2 + var_Vi**2)
Q_eq_gen = var_Vr**2 + var_Vi**2 - (var_Vset**2)
#sym.pprint(PF_eq_load_real)

Lagrange_eq_gen = var_Lr*PF_eq_gen_real + var_Li*PF_eq_gen_imag + var_Lq*Q_eq_gen
sym.pprint(Lagrange_eq_gen)
# Dual current equations
Dual_eq_r = sym.diff(Lagrange_eq_gen,var_Vr)
Dual_eq_i = sym.diff(Lagrange_eq_gen,var_Vi)
Dual_eq_q = sym.diff(Lagrange_eq_gen,var_Q)
#sym.pprint(Dual_eq_r)
#sym.pprint(sym.diff(PF_eq_load_real,var_Vr))

# Need to linearize the TSE again
# Real terms
lin_dual_eq_r_wrt_vr = sym.diff(Dual_eq_r,var_Vr)
lin_dual_eq_r_wrt_vi = sym.diff(Dual_eq_r,var_Vi)
lin_dual_eq_r_wrt_q = sym.diff(Dual_eq_r,var_Q)
lin_dual_eq_r_wrt_lr = sym.diff(Dual_eq_r,var_Lr)
lin_dual_eq_r_wrt_li = sym.diff(Dual_eq_r,var_Li)
lin_dual_eq_r_wrt_lq = sym.diff(Dual_eq_r,var_Lq)

# Imag terms
lin_dual_eq_i_wrt_vr = sym.diff(Dual_eq_i,var_Vr)
lin_dual_eq_i_wrt_vi = sym.diff(Dual_eq_i,var_Vi)
lin_dual_eq_i_wrt_q = sym.diff(Dual_eq_i,var_Q)
lin_dual_eq_i_wrt_lr = sym.diff(Dual_eq_i,var_Lr)
lin_dual_eq_i_wrt_li = sym.diff(Dual_eq_i,var_Li)
lin_dual_eq_i_wrt_lq = sym.diff(Dual_eq_i,var_Lq)

# Q Terms
lin_dual_eq_q_wrt_vr = sym.diff(Dual_eq_q,var_Vr)
lin_dual_eq_q_wrt_vi = sym.diff(Dual_eq_q,var_Vi)
lin_dual_eq_q_wrt_q = sym.diff(Dual_eq_q,var_Q)
lin_dual_eq_q_wrt_lr = sym.diff(Dual_eq_q,var_Lr)
lin_dual_eq_q_wrt_li = sym.diff(Dual_eq_q,var_Li)
lin_dual_eq_q_wrt_lq = sym.diff(Dual_eq_q,var_Lq)

class Generators:
    _ids = count(0)
    RemoteBusGens = dict()
    RemoteBusRMPCT = dict()
    gen_bus_key_ = {}
    total_P = 0
    
    

    def __init__(self,
                 Bus,
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

        self.Bus = Bus
        self.P_MW = P
        self.Vset = Vset
        self.Qmax_MVAR = Qmax
        self.Qmin_MVAR = Qmin
        self.Pmax_MW = Pmax
        self.Pmin_MW = Pmin
        self.Qinit_MVAR = Qinit
        self.RemoteBus = RemoteBus
        self.RMPCT = RMPCT
        self.gen_type = gen_type
        # convert P/Q to pu
        self.P = P/global_vars.base_MVA
        self.Vset = Vset
        self.Qmax = Qmax/global_vars.base_MVA
        self.Qmin = Qmin/global_vars.base_MVA
        self.Qinit = Qinit/global_vars.base_MVA
        self.Pmax = Pmax/global_vars.base_MVA
        self.Pmin = Pmin/global_vars.base_MVA

        self.id = self._ids.__next__()

    def assign_indexes(self, bus):
        # Nodes shared by generators on the same bus
        self.Vr_node = bus[Buses.bus_key_[self.Bus]].node_Vr
        self.Vi_node = bus[Buses.bus_key_[self.Bus]].node_Vi
        # run check to make sure the bus actually has a Q node
        self.Q_node = bus[Buses.bus_key_[self.Bus]].node_Q
        
        self.Lr_node = bus[Buses.bus_key_[self.Bus]].node_Lr
        self.Li_node = bus[Buses.bus_key_[self.Bus]].node_Li
        self.Lq_node = bus[Buses.bus_key_[self.Bus]].node_Lq
    
    def stamp(self, V, Y_val, Y_row, Y_col, J_val, J_row, idx_Y, idx_J):
        P = -self.P
        Vr = V[self.Vr_node]
        Vi = V[self.Vi_node]
        Q = V[self.Q_node]

        Irg_hist = (P*Vr+Q*Vi)/(Vr**2+Vi**2)
        dIrgdVr = (P*(Vi**2-Vr**2) - 2*Q*Vr*Vi)/(Vr**2+Vi**2)**2
        dIrgdVi = (Q*(Vr**2-Vi**2) - 2*P*Vr*Vi)/(Vr**2+Vi**2)**2
        dIrgdQ = (Vi)/(Vr**2+Vi**2)
        Vr_J_stamp = -Irg_hist + dIrgdVr*Vr + dIrgdVi*Vi + dIrgdQ*Q

        idx_Y = stampY(self.Vr_node, self.Vr_node, dIrgdVr, Y_val, Y_row, Y_col, idx_Y)
        idx_Y = stampY(self.Vr_node, self.Vi_node, dIrgdVi, Y_val, Y_row, Y_col, idx_Y)
        idx_Y = stampY(self.Vr_node, self.Q_node, dIrgdQ, Y_val, Y_row, Y_col, idx_Y)
        idx_J = stampJ(self.Vr_node, Vr_J_stamp, J_val, J_row, idx_J)

        Iig_hist = (P*Vi-Q*Vr)/(Vr**2+Vi**2)
        dIigdVi = -dIrgdVr
        dIigdVr = dIrgdVi
        dIigdQ = -(Vr)/(Vr**2+Vi**2)
        Vi_J_stamp = -Iig_hist + dIigdVr*Vr + dIigdVi*Vi + dIigdQ*Q

        idx_Y = stampY(self.Vi_node, self.Vr_node, dIigdVr, Y_val, Y_row, Y_col, idx_Y)
        idx_Y = stampY(self.Vi_node, self.Vi_node, dIigdVi, Y_val, Y_row, Y_col, idx_Y)
        idx_Y = stampY(self.Vi_node, self.Q_node, dIigdQ, Y_val, Y_row, Y_col, idx_Y)
        idx_J = stampJ(self.Vi_node, Vi_J_stamp, J_val, J_row, idx_J)

        Vset_hist = self.Vset**2 - Vr**2 - Vi**2
        dVset_dVr = -2*Vr
        dVset_dVi = -2*Vi
        Vset_J_stamp = -Vset_hist + dVset_dVr*Vr + dVset_dVi*Vi

        idx_Y = stampY(self.Q_node, self.Vr_node, dVset_dVr, Y_val, Y_row, Y_col, idx_Y)
        idx_Y = stampY(self.Q_node, self.Vi_node, dVset_dVi, Y_val, Y_row, Y_col, idx_Y)
        idx_J = stampJ(self.Q_node, Vset_J_stamp, J_val, J_row, idx_J)

        return (idx_Y, idx_J)

    def stamp_dual(self, V, Y_val, Y_row, Y_col, J_val, J_row, idx_Y, idx_J):
        # You need to implement this.
        # Extract values from previous solution
        inVr = V[self.Vr_node]
        inVi = V[self.Vi_node]
        inQ = V[self.Q_node]
        inLr = V[self.Lr_node]
        inLi = V[self.Li_node]
        inLq = V[self.Lq_node]

        ''' * * * * * VR * * * * * * * * * * * * * * * *    '''
        # Evaluate for the total
        eval_r = Dual_eq_r.subs([(var_Vr, inVr), (var_Vi, inVi), (var_Q, inQ), (var_Lr, inLr), (var_Li, inLi), (var_Lq, inLq), (var_P, self.P), (var_Vset, self.Vset)])
        # Primal Terms
        # VR
        eval_r_vr = lin_dual_eq_r_wrt_vr.subs([(var_Vr, inVr), (var_Vi, inVi), (var_Q, inQ), (var_Lr, inLr), (var_Li, inLi), (var_Lq, inLq), (var_P, self.P), (var_Vset, self.Vset)])
        # VI
        eval_r_vi = lin_dual_eq_r_wrt_vi.subs([(var_Vr, inVr), (var_Vi, inVi), (var_Q, inQ), (var_Lr, inLr), (var_Li, inLi), (var_Lq, inLq), (var_P, self.P), (var_Vset, self.Vset)])
        # Q
        eval_r_q = lin_dual_eq_r_wrt_q.subs([(var_Vr, inVr), (var_Vi, inVi), (var_Q, inQ), (var_Lr, inLr), (var_Li, inLi), (var_Lq, inLq), (var_P, self.P), (var_Vset, self.Vset)])
        # Dual Terms
        # LR
        eval_r_lr = lin_dual_eq_r_wrt_lr.subs([(var_Vr, inVr), (var_Vi, inVi), (var_Q, inQ), (var_Lr, inLr), (var_Li, inLi), (var_Lq, inLq), (var_P, self.P), (var_Vset, self.Vset)])
        # LI
        eval_r_li = lin_dual_eq_r_wrt_li.subs([(var_Vr, inVr), (var_Vi, inVi), (var_Q, inQ), (var_Lr, inLr), (var_Li, inLi), (var_Lq, inLq), (var_P, self.P), (var_Vset, self.Vset)])
        # LQ
        eval_r_lq = lin_dual_eq_r_wrt_lq.subs([(var_Vr, inVr), (var_Vi, inVi), (var_Q, inQ), (var_Lr, inLr), (var_Li, inLi), (var_Lq, inLq), (var_P, self.P), (var_Vset, self.Vset)])
        
        ''' * * * * * VI * * * * * * * * * * * * * * * *    '''
        # Evaluate for the total
        eval_i = Dual_eq_i.subs([(var_Vr, inVr), (var_Vi, inVi), (var_Q, inQ), (var_Lr, inLr), (var_Li, inLi), (var_Lq, inLq), (var_P, self.P), (var_Vset, self.Vset)])
        # Primal Terms
        # VR
        eval_i_vr = lin_dual_eq_i_wrt_vr.subs([(var_Vr, inVr), (var_Vi, inVi), (var_Q, inQ), (var_Lr, inLr), (var_Li, inLi), (var_Lq, inLq), (var_P, self.P), (var_Vset, self.Vset)])
        # VI
        eval_i_vi = lin_dual_eq_i_wrt_vi.subs([(var_Vr, inVr), (var_Vi, inVi), (var_Q, inQ), (var_Lr, inLr), (var_Li, inLi), (var_Lq, inLq), (var_P, self.P), (var_Vset, self.Vset)])
        # Q
        eval_i_q = lin_dual_eq_i_wrt_q.subs([(var_Vr, inVr), (var_Vi, inVi), (var_Q, inQ), (var_Lr, inLr), (var_Li, inLi), (var_Lq, inLq), (var_P, self.P), (var_Vset, self.Vset)])
        # Dual Terms
        # LR
        eval_i_lr = lin_dual_eq_i_wrt_lr.subs([(var_Vr, inVr), (var_Vi, inVi), (var_Q, inQ), (var_Lr, inLr), (var_Li, inLi), (var_Lq, inLq), (var_P, self.P), (var_Vset, self.Vset)])
        # LI
        eval_i_li = lin_dual_eq_i_wrt_li.subs([(var_Vr, inVr), (var_Vi, inVi), (var_Q, inQ), (var_Lr, inLr), (var_Li, inLi), (var_Lq, inLq), (var_P, self.P), (var_Vset, self.Vset)])
        # LQ
        eval_i_lq = lin_dual_eq_i_wrt_lq.subs([(var_Vr, inVr), (var_Vi, inVi), (var_Q, inQ), (var_Lr, inLr), (var_Li, inLi), (var_Lq, inLq), (var_P, self.P), (var_Vset, self.Vset)])
        
        ''' * * * * * Q * * * * * * * * * * * * * * * *    '''
        # Evaluate for the total
        eval_q = Dual_eq_q.subs([(var_Vr, inVr), (var_Vi, inVi), (var_Q, inQ), (var_Lr, inLr), (var_Li, inLi), (var_Lq, inLq), (var_P, self.P), (var_Vset, self.Vset)])
        # Primal Terms
        # VR
        eval_q_vr = lin_dual_eq_q_wrt_vr.subs([(var_Vr, inVr), (var_Vi, inVi), (var_Q, inQ), (var_Lr, inLr), (var_Li, inLi), (var_Lq, inLq), (var_P, self.P), (var_Vset, self.Vset)])
        # VI
        eval_q_vi = lin_dual_eq_q_wrt_vi.subs([(var_Vr, inVr), (var_Vi, inVi), (var_Q, inQ), (var_Lr, inLr), (var_Li, inLi), (var_Lq, inLq), (var_P, self.P), (var_Vset, self.Vset)])
        # Q
        eval_q_q = lin_dual_eq_q_wrt_q.subs([(var_Vr, inVr), (var_Vi, inVi), (var_Q, inQ), (var_Lr, inLr), (var_Li, inLi), (var_Lq, inLq), (var_P, self.P), (var_Vset, self.Vset)])
        # Dual Terms
        # LR
        eval_q_lr = lin_dual_eq_q_wrt_lr.subs([(var_Vr, inVr), (var_Vi, inVi), (var_Q, inQ), (var_Lr, inLr), (var_Li, inLi), (var_Lq, inLq), (var_P, self.P), (var_Vset, self.Vset)])
        # LI
        eval_q_li = lin_dual_eq_q_wrt_li.subs([(var_Vr, inVr), (var_Vi, inVi), (var_Q, inQ), (var_Lr, inLr), (var_Li, inLi), (var_Lq, inLq), (var_P, self.P), (var_Vset, self.Vset)])
        # LQ
        eval_q_lq = lin_dual_eq_q_wrt_lq.subs([(var_Vr, inVr), (var_Vi, inVi), (var_Q, inQ), (var_Lr, inLr), (var_Li, inLi), (var_Lq, inLq), (var_P, self.P), (var_Vset, self.Vset)])
        
        ''' Start stamping the values calculated from above '''
        # Start stamping the terms in the Lr row
        # Add up the hitorical
        IR_hist = eval_r - (inVr*eval_r_vr) - (inVi*eval_r_vi) - (inQ*eval_r_q) - (inLr*eval_r_lr) - (inLi*eval_r_li) - (inLq*eval_r_lq)
        II_hist = eval_i - (inVr*eval_i_vr) - (inVi*eval_i_vi) - (inQ*eval_i_q) - (inLr*eval_i_lr) - (inLi*eval_i_li) - (inLq*eval_i_lq)
        IQ_hist = eval_q - (inVr*eval_q_vr) - (inVi*eval_q_vi) - (inQ*eval_q_q) - (inLr*eval_q_lr) - (inLi*eval_q_li) - (inLq*eval_q_lq)
        # Stamp the historical
        idx_J = stampJ(self.Lr_node, -IR_hist, J_val, J_row, idx_J)
        idx_J = stampJ(self.Li_node, -II_hist, J_val, J_row, idx_J)
        idx_J = stampJ(self.Lq_node, -IQ_hist, J_val, J_row, idx_J)
        # Stamp the terms related to row Lr
        idx_Y = stampY(self.Lr_node, self.Vr_node, eval_r_vr, Y_val, Y_row, Y_col, idx_Y)
        idx_Y = stampY(self.Lr_node, self.Vi_node, eval_r_vi, Y_val, Y_row, Y_col, idx_Y)
        idx_Y = stampY(self.Lr_node, self.Q_node, eval_r_q, Y_val, Y_row, Y_col, idx_Y)
        idx_Y = stampY(self.Lr_node, self.Lr_node, eval_r_lr, Y_val, Y_row, Y_col, idx_Y)
        idx_Y = stampY(self.Lr_node, self.Li_node, eval_r_li, Y_val, Y_row, Y_col, idx_Y)
        idx_Y = stampY(self.Lr_node, self.Lq_node, eval_r_lq, Y_val, Y_row, Y_col, idx_Y)
        # Stamp the terms related to row Li
        idx_Y = stampY(self.Li_node, self.Vr_node, eval_i_vr, Y_val, Y_row, Y_col, idx_Y)
        idx_Y = stampY(self.Li_node, self.Vi_node, eval_i_vi, Y_val, Y_row, Y_col, idx_Y)
        idx_Y = stampY(self.Li_node, self.Q_node, eval_i_q, Y_val, Y_row, Y_col, idx_Y)
        idx_Y = stampY(self.Li_node, self.Lr_node, eval_i_lr, Y_val, Y_row, Y_col, idx_Y)
        idx_Y = stampY(self.Li_node, self.Li_node, eval_i_li, Y_val, Y_row, Y_col, idx_Y)
        idx_Y = stampY(self.Li_node, self.Lq_node, eval_i_lq, Y_val, Y_row, Y_col, idx_Y)
        # Stamp the terms related to row Lq
        idx_Y = stampY(self.Lq_node, self.Vr_node, eval_q_vr, Y_val, Y_row, Y_col, idx_Y)
        idx_Y = stampY(self.Lq_node, self.Vi_node, eval_q_vi, Y_val, Y_row, Y_col, idx_Y)
        idx_Y = stampY(self.Lq_node, self.Q_node, eval_q_q, Y_val, Y_row, Y_col, idx_Y)
        idx_Y = stampY(self.Lq_node, self.Lr_node, eval_q_lr, Y_val, Y_row, Y_col, idx_Y)
        idx_Y = stampY(self.Lq_node, self.Li_node, eval_q_li, Y_val, Y_row, Y_col, idx_Y)
        idx_Y = stampY(self.Lq_node, self.Lq_node, eval_q_lq, Y_val, Y_row, Y_col, idx_Y)
        
        return (idx_Y, idx_J)

    def calc_residuals(self, resid, V):
        P = -self.P
        Vr = V[self.Vr_node]
        Vi = V[self.Vi_node]
        Q = V[self.Q_node]
        resid[self.Vr_node] += (P*Vr+Q*Vi)/(Vr**2+Vi**2)
        resid[self.Vi_node] += (P*Vi-Q*Vr)/(Vr**2+Vi**2)
        resid[self.Q_node] += self.Vset**2 - Vr**2 - Vi**2
