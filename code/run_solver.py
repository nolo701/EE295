from scripts.solve import solve

# path to the grid network RAW file
runall = False
#casename = 'testcases/GS-4_prior_solution.RAW'
#casename = 'testcases/IEEE-14_prior_solution.RAW'
#casename = 'testcases/IEEE-118_prior_solution.RAW'
casename = 'testcases/PEGASE-9241_flat_start.RAW'
#casename = 'testcases/PEGASE-13659_flat_start.RAW'

casename1 = 'testcases/GS-4_prior_solution.RAW'
casename2 = 'testcases/IEEE-14_prior_solution.RAW'
casename3 = 'testcases/IEEE-118_prior_solution.RAW'
casename4 = 'testcases/PEGASE-9241_flat_start.RAW'
cases = [casename1,casename2,casename3,casename4]
# the settings for the solver
settings = {
    "Tolerance": 1E-10,
    "NR_max_steps": 25,
    "Limiting":  False,
    "Limiting-limit": 0.1,
    "Sparse": True,
    "case_name": casename,
    "TX-Homotopy": True,
    "TX-max_steps": 10,
    "TX-agressiveness": 5, # % loss per tx step
    "TX-scaling": 5 #(Gamma) smaller decimal means it will move faster
    
}

# run the solver
if runall:
    for case in cases:
        settings.update("case_name",case)
        solve(case, settings)
else:
    solve(casename, settings)