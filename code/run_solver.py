from scripts.solve import solve

# path to the grid network RAW file
#casename = 'testcases/single_phase_RC_circuit.json'
#casename = 'testcases/single_phase_R_circuit.json'
#casename = 'testcases/single_phase_RL_circuit.json'
#casename = 'testcases/single_phase_RL_RL_circuit.json'
casename = 'testcases/single_phase_R_SW_circuit.json'
#casename = 'testcases/RL_circuit.json'
#casename = 'testcases/RLC_circuit.json'

# the settings for the solver
settings = {
	"Tolerance": 1E-05, # Tolerance for Newton-Raphson
	"Max Iters": 5, # Maximum number of newton iterations for non-linear loop at given time step
    "Simulation Time": .25, # Total time to simulate: [0, tf]
    "Sparse": False, # Use sparse matrix formulation
    "Time Step": 1E-4
    
}

# these are the desired nodes to plot
# Change these lists to select which voltages and which currents to plot
# Three phase RL
#desiredVoltages = ["n3_a","n3_b","n3_c"]
#desiredCurrents = ["vs_v_a","vs_v_b","vs_v_c"]
# Single Phase RL
#desiredVoltages = ["n1_a","n2_a"]
#desiredCurrents = ["vs_v_a"]
# Single Phase RL-L - This is my custom JSON
#desiredVoltages = ["n1_a","n2_a","n3_a"]
#desiredCurrents = ["vs_v_a"]
# Three phase RLC
#desiredVoltages = ["n4_a","n4_b","n4_c"]
#desiredCurrents = ["vs_c1_a","vs_c1_b","vs_c1_c"]
# Single Phase R_SW
desiredVoltages = ["n1_a","n2_a"]
desiredCurrents = ["vs_v_a"]

# run the solver
solve(casename, settings, desiredVoltages, desiredCurrents)