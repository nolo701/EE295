import numpy as np
from scipy import sparse


class PowerFlow:

    def __init__(self,
                 SETTINGS,
                 size_Y):
        """Initialize the PowerFlow instance.

        Args:
            case_name (str): A string with the path to the test case.
            tol (float): The chosen NR tolerance.
            max_iters (int): The maximum number of NR iterations.
            enable_limiting (bool): A flag that indicates if we use voltage limiting or not in our solver.
        """
        # Clean up the case name string
        case_name =SETTINGS["case_name"]
        case_name = case_name.replace('.RAW', '')
        case_name = case_name.replace('testcases/', '')

        self.case_name = case_name
        self.tol = SETTINGS["Tolerance"]
        self.NR_max_iters = SETTINGS["NR_max_steps"]
        self.limiting = SETTINGS["Limiting"]
        self.limiting_limit = SETTINGS["Limiting-limit"]
        self.enable_limiting = SETTINGS["Limiting"]
        self.sparse = SETTINGS["Sparse"]
        self.size_Y = size_Y

    def solve_dense(self, inputY_lin, inputJ_lin, inputY_nonlin, inputJ_nonlin, prev_sol):
        Y = inputY_lin + inputY_nonlin
        J = inputJ_lin + inputJ_nonlin
        sol = np.linalg.solve(Y, J)

        return sol
    
    def solve_sparse(self, Y_lin_r, Y_lin_c, Y_lin_val, J_lin_r, J_lin_val,Y_nonlin_r,
                     Y_nonlin_c, Y_nonlin_val, J_nonlin_r, J_nonlin_val, v_sol):
        Y_r = []
        Y_r.extend(Y_lin_r)
        Y_r.extend(Y_nonlin_r)

        Y_c = []
        Y_c.extend(Y_lin_c)
        Y_c.extend(Y_nonlin_c)

        Y_val = []
        Y_val.extend(Y_lin_val)
        Y_val.extend(Y_nonlin_val)

        J_r = []
        J_r.extend(J_lin_r)
        J_r.extend(J_nonlin_r)

        J_val = []
        J_val.extend(J_lin_val)
        J_val.extend(J_nonlin_val)

        
        J_c = np.zeros([len(J_r),1]).flatten()
        
        Y = sparse.csr_matrix((np.asarray(Y_val, dtype=np.float64), \
                               (np.asarray(Y_r),
                                np.asarray(Y_c))),
                                shape = (self.size_Y, self.size_Y))
        '''
        Y = sparse.csr_matrix((Y_val, (Y_r, Y_c)), 
                          shape = (self.size_Y, self.size_Y))
        '''
        J = sparse.csr_matrix((np.asarray(J_val, dtype=np.float64), (J_r, J_c)), 
                          shape = (self.size_Y, 1), dtype=np.float)
        #J = sparse.csr_matrix(J_val,(J_r,1))
        sol = np.array(sparse.linalg.spsolve(Y,J))

        return sol

    def apply_limiting(self, newV, prevV, inBus):
        delta = newV - prevV
        for bus in inBus:
            # Check bus real
            # Check if positive limit hit
            if delta[bus.node_Vr] > self.limiting_limit:
                delta[bus.node_Vr] = self.limiting_limit
            # Check if negative limit hit
            if delta[bus.node_Vr] < self.limiting_limit:
                delta[bus.node_Vr] = -1*self.limiting_limit
            # Check bus imaginary
            # Check if positive limit hit
            if delta[bus.node_Vi] > self.limiting_limit:
                delta[bus.node_Vi] = self.limiting_limit
            # Check if negative limit hit
            if delta[bus.node_Vi] < self.limiting_limit:
                delta[bus.node_Vi] = -1*self.limiting_limit
        # recreate solution
        sol = prevV + delta
        return sol

    def check_error(self, step):
        error = max(abs(step))
        #error = np.linalg.norm(sol)
        return error

    def stamp_linear(self, inputBranch, inputSlack, inputShunt, inputTransformer):
        # Init differently if sparse is True or False
        if self.sparse == True:
            Y_lin_r = []
            Y_lin_c = []
            Y_lin_val = []
            J_lin_r = []
            J_lin_val = []
            
        else:
            # create linear Y & J
            Y_lin = np.zeros((self.size_Y,self.size_Y))
            J_lin = np.zeros((self.size_Y,1))
        
        for ele in inputBranch:
            if self.sparse == True:
                Y_lin_r, Y_lin_c, Y_lin_val = ele.stamp_sparse(Y_lin_r, Y_lin_c, Y_lin_val)
            else:
                ele.stamp_dense(Y_lin)
        for ele in inputSlack:
            if self.sparse == True:
                Y_lin_r, Y_lin_c, Y_lin_val, J_lin_r, J_lin_val = ele.stamp_sparse(Y_lin_r, Y_lin_c, Y_lin_val, J_lin_r, J_lin_val)
            else:
                ele.stamp_dense(Y_lin, J_lin) 
                
        for ele in inputShunt:
            if self.sparse == True:
                Y_lin_r, Y_lin_c, Y_lin_val = ele.stamp_sparse(Y_lin_r, Y_lin_c, Y_lin_val)
                pass
            else:
                ele.stamp_dense(Y_lin) 
       
        for ele in inputTransformer:
            if self.sparse == True:
                Y_lin_r, Y_lin_c, Y_lin_val = ele.stamp_sparse(Y_lin_r, Y_lin_c, Y_lin_val)
                pass
            else:
                ele.stamp_dense(Y_lin) 
                
        if self.sparse == True:
            return Y_lin_r, Y_lin_c, Y_lin_val, J_lin_r, J_lin_val
        else:
            return Y_lin, J_lin

    def stamp_nonlinear(self, v_prev, inputGenerator, inputLoad):
        # Set all values to zero
        if self.sparse == True:
            Y_nonlin_r = []
            Y_nonlin_c = []
            Y_nonlin_val = []
            J_nonlin_r = []
            J_nonlin_val = []
            pass
        else:
            pass
            # make nonlin inits too
            Y = np.zeros((self.size_Y,self.size_Y))
            J = np.zeros((self.size_Y,1))
            
        for ele in inputGenerator:
            if self.sparse == True:
                Y_nonlin_r, Y_nonlin_c, Y_nonlin_val, J_nonlin_r, J_nonlin_val = ele.stamp_sparse(Y_nonlin_r, Y_nonlin_c, Y_nonlin_val, J_nonlin_r, J_nonlin_val, v_prev)
            else:
                ele.stamp_dense(Y, J, v_prev) 
                
        for ele in inputLoad:
            if self.sparse == True:
                Y_nonlin_r, Y_nonlin_c, Y_nonlin_val, J_nonlin_r, J_nonlin_val = ele.stamp_sparse(Y_nonlin_r, Y_nonlin_c, Y_nonlin_val, J_nonlin_r, J_nonlin_val, v_prev)
            else:
                ele.stamp_dense(Y, J, v_prev)
                
        if self.sparse == True:
            return Y_nonlin_r, Y_nonlin_c, Y_nonlin_val, J_nonlin_r, J_nonlin_val
        else:
            return Y, J
            

    def run_powerflow(self,
                      v_init,
                      bus,
                      slack,
                      generator,
                      transformer,
                      branch,
                      shunt,
                      load):
        """Runs a positive sequence power flow using the Equivalent Circuit Formulation.

        Args:
            v_init (np.array): The initial solution vector which has the same number of rows as the Y matrix.
            bus (list): Contains all the buses in the network as instances of the Buses class.
            slack (list): Contains all the slack generators in the network as instances of the Slack class.
            generator (list): Contains all the generators in the network as instances of the Generators class.
            transformer (list): Contains all the transformers in the network as instance of the Transformers class.
            branch (list): Contains all the branches in the network as instances of the Branches class.
            shunt (list): Contains all the shunts in the network as instances of the Shunts class.
            load (list): Contains all the loads in the network as instances of the Load class.

        Returns:
            v(np.array): The final solution vector.

        """

        # # # Copy v_init into the Solution Vectors used during NR, v, and the final solution vector v_sol # # #
        v = np.copy(v_init)
        v_sol = np.copy(v)
        
        # # # Stamp Linear Power Grid Elements into Y matrix # # #
        # TODO: PART 1, STEP 2.1 - Complete the stamp_linear function which stamps all linear power grid elements.
        #  This function should call the stamp_linear function of each linear element and return an updated Y matrix.
        #  You need to decide the input arguments and return values.
        
        
        
        # stamp the linear
        if self.sparse == True:
            Y_lin_r, Y_lin_c, Y_lin_val, J_lin_r, J_lin_val = self.stamp_linear(branch,slack,shunt,transformer)
        else:
            Y_lin, J_lin = self.stamp_linear(branch,slack,shunt,transformer)

        # # # Initialize While Loop (NR) Variables # # #
        # TODO: PART 1, STEP 2.2 - Initialize the NR variables
        err_max = self.tol+1  # maximum error at the current NR iteration
        tol = self.tol  # chosen NR tolerance
        NR_count = 0  # current NR iteration
        step = 0

        # # # Begin Solving Via NR # # #
        # TODO: PART 1, STEP 2.3 - Complete the NR While Loop
        while (err_max > tol) and (NR_count < self.NR_max_iters):
            print("\tStarted Iter:{}",NR_count+1)
            # # # Stamp Nonlinear Power Grid Elements into Y matrix # # #
            # TODO: PART 1, STEP 2.4 - Complete the stamp_nonlinear function which stamps all nonlinear power grid
            #  elements. This function should call the stamp_nonlinear function of each nonlinear element and return
            #  an updated Y matrix. You need to decide the input arguments and return values.
            

            # # # Solve The System # # #
            # TODO: PART 1, STEP 2.5 - Complete the solve function which solves system of equations Yv = J. The
            #  function should return a new v_sol.
            #  You need to decide the input arguments and return values.
            #v_sol_next = self.solve(Y_lin, J_lin, Y_nonlin, J_nonlin, v_sol)
            if self.sparse == True:
               Y_nonlin_r, Y_nonlin_c, Y_nonlin_val, J_nonlin_r, J_nonlin_val = self.stamp_nonlinear(v_sol, generator, load)
               v_sol_next = self.solve_sparse(Y_lin_r, Y_lin_c, Y_lin_val, J_lin_r, J_lin_val,Y_nonlin_r, Y_nonlin_c, Y_nonlin_val, J_nonlin_r, J_nonlin_val, v_sol)
               v_sol_next = np.reshape(v_sol_next, [len(v_sol_next),1])
            else:
               Y_nonlin, J_nonlin = self.stamp_nonlinear(v_sol, generator, load)
               v_sol_next = self.solve_dense(Y_lin, J_lin, Y_nonlin, J_nonlin, v_sol)
            # # # Compute The Error at the current NR iteration # # #
            # TODO: PART 1, STEP 2.6 - Finish the check_error function which calculates the maximum error, err_max
            #  You need to decide the input arguments and return values.
            
            # Check if limiting needs to be applied:
            if self.limiting:
                v_sol_next = self.apply_limiting(v_sol_next, v_sol, bus)
            
            diff = np.subtract(v_sol_next,v_sol)
            
            err_max = self.check_error(diff)
            v_sol = v_sol_next

            # # # Compute The Error at the current NR iteration # # #
            # TODO: PART 2, STEP 1 - Develop the apply_limiting function which implements voltage and reactive power
            #  limiting. Also, complete the else condition. Do not complete this step until you've finished Part 1.
            #  You need to decide the input arguments and return values.

            #print(v_sol)
            print("\tFinished Iter: {} with error {}".format(NR_count+1,err_max))
            NR_count += 1
        # determine if the NR converged
        if (err_max <= tol) and (NR_count <= self.NR_max_iters):
            converge = True
            print("Solution interation: {}".format(NR_count))
        else:
            converge = False
            print("PF Diverged!!!!")
        #print(v_sol)
        
        return v_sol,converge
    
    
    def init_tx(self, slack, generator, bus):
        v_init = np.zeros((self.size_Y,1))  # create a solution vector filled with zeros of size_Y
        # Set the nodes of each slack or generator
        for ele in bus:
            #Slack or PQ Bus
            v_init[ele.node_Vr] = 1
            v_init[ele.node_Vi] = .1
            if ele.Type == 2:
                v_init[ele.node_Q] = 1e-1
        for ele in generator:
            #Slack or PQ Bus
            v_init[ele.bus.node_Vr] = np.sqrt(2)/2 * ele.Vset
            v_init[ele.bus.node_Vi] = np.sqrt(2)/2 * ele.Vset
            if ele.gen_type == 2:
                v_init[ele.bus.node_Q] = 1e-1
        for ele in slack:
            # PV Bus
            #v_init[ele.bus.node_Vr_Slack] = np.sqrt(2)/2 * ele.Vset
            #v_init[ele.bus.node_Vi_Slack] = np.sqrt(2)/2 * ele.Vset
            v_init[ele.node_Vr_Slack] = np.sqrt(2)/2 * ele.Vr_set
            v_init[ele.node_Vi_Slack] = np.sqrt(2)/2 * ele.Vi_set
            
        return v_init
    
    def run_tx_stepping(self, SETTINGS, bus, slack, generator, transformer, branch, shunt, load ):
        # Read other TX settings to create the starting V & Gamma
        tx_step = 1
        v_init = self.init_tx(slack, generator,bus)
        # Create the TX Branches as copy of branch
        tx_branch = branch.copy()
        # Create the TX Transformers as copy of transformer
        tx_transformer = transformer.copy()
        tx_converged = False
        # Magnitude to decrease losses
        tx_gamma = SETTINGS["TX-scaling"]
        # While it has yet to converge try and make it even smaller
        while (tx_converged == False) and (tx_step <= SETTINGS["TX-max_steps"]):
            # tx_v will shrink exponentially according to agressiveness
            # a larger value a more agressive shrink
            tx_v = 1-((100 - SETTINGS["TX-agressiveness"])/100)**tx_step
            print("Shorting iter: {}, tx_v: {}".format(tx_step, tx_v))
            
            for ele in tx_branch:
                ele.set_tx(tx_v, tx_gamma)
            
            for ele in tx_transformer:
                ele.set_tx(tx_v, tx_gamma)
            
            # Run a power flow with shorted values
            tx_sol, tx_success = self.run_powerflow(v_init, bus, slack, generator, tx_transformer, tx_branch, shunt, load)
            if tx_success == False:
                tx_step += 1

            else:
                tx_converged = True
        if tx_converged:
            print("TX Stepping converged, Starting to back off")
            # With a converged trivial solution try and step it up to original
            recover = False
            exit = False
            recover_step = 1
            recover_sol = np.copy(tx_sol)
            tx_v_sol = tx_v
            step_lin = (tx_v_sol)/SETTINGS["TX-max_steps"]
            print("Backing off in {} steps, starting tx_v: {}, step: {}".format(SETTINGS["TX-max_steps"], tx_v_sol, step_lin))
            #while (recover == False) and (recover_step <= SETTINGS["TX-max_steps"]):
            while (recover_step <= SETTINGS["TX-max_steps"]) and (exit == False):
                
                # tx_v will recover from the converged point linearly in max steps steps
                # a larger value a more agressive shrink
                
                # Linear
                tx_v = tx_v_sol - recover_step*step_lin
                
                #exponential
                #tx_v = tx_v_sol*()

                print("Backing off iter: {}, tx_v: {}".format(recover_step, tx_v))
                # Refresh the values
                for ele in tx_branch:
                    ele.set_tx(tx_v, tx_gamma)
                
                for ele in tx_transformer:
                    ele.set_tx(tx_v, tx_gamma)
                
                # Run a power flow with increase
                recover_sol, recover = self.run_powerflow(recover_sol, bus, slack, generator, transformer, branch, shunt, load)
                
                if(recover==False):
                    # use the last TX convergence and start with half the step size
                    exit = True
                    recover_step = -1
                    recover_tx_v_div = tx_v + recover_step*step_lin # Last one to converge
                recover_step += 1
                
            # Try again from last as a second chance
            # calculate new step 
            step_lin = (recover_tx_v_div)/SETTINGS["TX-max_steps"]
            print("Backing off in {} steps, starting tx_v: {}, step: {}".format(SETTINGS["TX-max_steps"], recover_tx_v_div, step_lin))
            while (recover_step <= SETTINGS["TX-max_steps"]) and (exit == True):
                
                # tx_v will recover from the converged point linearly in max steps steps
                # a larger value a more agressive shrink
                
                # Linear
                tx_v = recover_tx_v_div - recover_step*step_lin
                
                #exponential
                #tx_v = tx_v_sol*()

                print("Backing off iter: {}, tx_v: {}".format(recover_step, tx_v))
                # Refresh the values
                for ele in tx_branch:
                    ele.set_tx(tx_v, tx_gamma)
                
                for ele in tx_transformer:
                    ele.set_tx(tx_v, tx_gamma)
                
                # Run a power flow with increase
                recover_sol, recover = self.run_powerflow(recover_sol, bus, slack, generator, transformer, branch, shunt, load)
                
                if(recover==False):
                    # use the last TX convergence and start with half the step size
                    exit = False
                recover_step += 1
                    
        
        if recover:
            # Run PF with v=0
            for ele in tx_branch:
                ele.set_tx(0, tx_gamma)
                
            for ele in tx_transformer:
                ele.set_tx(0, tx_gamma)
            recover_sol, recover = self.run_powerflow(recover_sol, bus, slack, generator, tx_transformer, tx_branch, shunt, load)
            return recover_sol, recover
        
        return None, recover
        
    