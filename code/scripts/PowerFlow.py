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
        self.max_iters = SETTINGS["Max Iters"]
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
        
        Y_r = np.append(Y_lin_r, Y_nonlin_r).flatten()
        #Y_r = np.resize(Y_r, [len(Y_r),1])
        Y_c = np.append(Y_lin_c, Y_nonlin_c).flatten()
        #Y_c = np.resize(Y_c, [len(Y_c),1])
        Y_val = np.append(Y_lin_val, Y_nonlin_val).flatten()
        #Y_val = np.resize(Y_val, [len(Y_val),1])
        
        J_r = np.append(J_lin_r, J_nonlin_r).flatten()
        #J_r = np.resize(J_r, [len(J_r),1])
        J_val = np.append(J_lin_val, J_nonlin_val).flatten()
        #J_val = np.resize(J_val, [len(J_val),1])
        
        J_c = np.zeros([len(J_r),1]).flatten()
        '''
        Y = sparse.csr_matrix((np.asarray(Y_val, dtype=np.float64),
                               np.asarray(Y_r),np.asarray(Y_c)),
                                shape = (self.size_Y, self.size_Y))
        '''
        Y = sparse.csr_matrix((Y_val, (Y_r, Y_c)), 
                          shape = (self.size_Y, self.size_Y))
        J = sparse.csr_matrix((J_val, (J_r, J_c)), 
                          shape = (self.size_Y, 1))
        #J = sparse.csr_matrix(J_val,(J_r,1))
        sol = np.array(sparse.linalg.spsolve(Y,J))

        return sol

    def apply_limiting(self):
        pass

    def check_error(self, step):
        error = max(abs(step))
        #error = np.linalg.norm(sol)
        return error

    def stamp_linear(self, inputBranch, inputSlack, inputShunt, inputTransformer):
        # Init differently if sparse is True or False
        if self.sparse == True:
            Y_lin_r = np.zeros((1,3))
            Y_lin_c = np.zeros((1,3))
            Y_lin_val = np.zeros((1,3))
            J_lin_r = np.zeros((1,3))
            J_lin_val = np.zeros((1,3))
            
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
            Y_nonlin_r = np.zeros((1,3))
            Y_nonlin_c = np.zeros((1,3))
            Y_nonlin_val = np.zeros((1,3))
            J_nonlin_r = np.zeros((1,3))
            J_nonlin_val = np.zeros((1,3))
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
        while (err_max > tol) and (NR_count < self.max_iters):
            print("Started Iter:")
            print(NR_count+1)
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
            diff = np.subtract(v_sol_next,v_sol)
            
            err_max = self.check_error(diff)
            v_sol = v_sol_next

            # # # Compute The Error at the current NR iteration # # #
            # TODO: PART 2, STEP 1 - Develop the apply_limiting function which implements voltage and reactive power
            #  limiting. Also, complete the else condition. Do not complete this step until you've finished Part 1.
            #  You need to decide the input arguments and return values.
            if self.enable_limiting and err_max > tol:
                self.apply_limiting()
            else:
                pass
            #print(v_sol)
            print("Finished Iter:")
            print(NR_count+1)
            print(err_max)
            NR_count += 1

        print("Final Solution found after inter: ")
        print(NR_count)
        #print(v_sol)
        # determine if the NR converged
        if (err_max <= tol) and (NR_count <= self.max_iters):
            converge = True
        else:
            converge = False
        return v_sol,converge
