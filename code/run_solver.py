from scripts.solve import solve

# path to the grid network RAW file
#casename = 'testcases/GS-4_prior_solution.RAW'
#casename = 'testcases/IEEE-14_prior_solution.RAW'
#casename = 'testcases/IEEE-118_prior_solution.RAW'
casename = 'testcases/PEGASE-9241_flat_start.RAW'
# the settings for the solver
settings = {
    "Tolerance": 1E-5,
    "Max Iters": 50,
    "Limiting":  False,
    "Sparse": True,
    "case_name": casename,
    "TX-Homotopy": False,
    "TX-max_steps": 5,
    "TX-agressiveness": 5, # % loss per tx step
    "TX-scaling": 10 #(Gamma) smaller decimal means it will move faster
    
}

# run the solver
solve(casename, settings)