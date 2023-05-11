from scripts.SolveFeasibility import solve_feasibility
from models.global_vars import global_vars

# path to the grid network RAW file
#casename = 'testcases/IEEE-118_prior_solution.RAW' 
casename = 'testcases/GS-4_stressed.RAW'
#casename = 'testcases/GS-4_prior_solution.RAW'
#casename = 'testcases/IEEE-14_stressed_1.RAW' 
#casename = 'testcases/IEEE-14_stressed2_fixed.RAW' 
# the settings for the solver
settings = {
    "Tolerance": 1E-03,
    "Max Iters": 100,
    "Limiting":  False
}

# run the solver
solve_feasibility(casename, settings)