from scripts.solve import solve

# path to the grid network RAW file
#casename = 'testcases/GS-4_prior_solution.RAW'
casename = 'testcases/IEEE-14_prior_solution.RAW'

# the settings for the solver
settings = {
    "Tolerance": 1E-05,
    "Max Iters": 10,
    "Limiting":  False,
    "Sparse": True,
    "case_name": casename
}

# run the solver
solve(casename, settings)