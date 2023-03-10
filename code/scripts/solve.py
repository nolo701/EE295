from lib.parse_json import parse_json
from lib.assign_node_indexes import assign_node_indexes
from lib.initialize import initialize
from scripts.run_time_domain_simulation import run_time_domain_simulation
from scripts.process_results import process_results
import numpy as np

def solve(TESTCASE, SETTINGS, desiredVoltages, desiredCurrents):
    """Run the time-domain solver.
    Args:
        TESTCASE (str): A string with the path to the network json file.
        SETTINGS (dict): Contains all the solver settings in a dictionary.
    Returns:
        None
    """
    # TODO: STEP 0 - Initialize all the model classes in the models directory (models/) and familiarize
    #  yourself with the parameters of each model.
    from classes import Nodes as Nodes
    from classes import Resistors
    from classes import Capacitors
    from classes import Inductors
    from classes import VoltageSources
    from classes import Switches
    # # # Parse the test case data # # #
    case_name = TESTCASE
    devices = parse_json(case_name)

    # # # Unpack parsed device objects in case you need them # # #
    nodes = devices['nodes']
    voltage_sources = devices['voltage_sources']
    resistors = devices['resistors']
    capacitors = devices['capacitors']
    inductors = devices['inductors']
    switches = devices['switches']
    induction_motors = devices['induction_motors']

    # # # Solver settings # # #
    t_final = SETTINGS['Simulation Time']
    tol = SETTINGS['Tolerance']  # NR solver tolerance
    max_iters = SETTINGS['Max Iters']  # maximum NR iterations

    # # # Assign system nodes # # #
    # We assign a node index for every node in our Y matrix and J vector.
    # In addition to voltages, nodes track currents of voltage sources and
    # other state variables needed for companion models or the model of the 
    # induction motor.
    # You can determine the size of the Y matrix by looking at the total
    # number of nodes in the system.
    node_dict={}
    size_Y = assign_node_indexes(devices,node_dict)
    # create an inverse dictionary to allow the process_waves to have a way
    # to create a legend from the index of the nodes
    inv_node_dict=dict(map(reversed, node_dict.items()))

 
    # # # Initialize solution vector # # #
    # TODO: STEP 1 - Complete the function to find your state vector at time t=0.
    V_init = initialize(devices, size_Y, node_dict, SETTINGS)
    
    # increase size_Y to account for matrix sizing starting at 1 not 0
    #size_Y += 1

    # TODO: STEP 2 - Run the time domain simulation and return an array that contains
    #                time domain waveforms of all the state variables # # #
    V_waveform = run_time_domain_simulation(devices, V_init, size_Y, SETTINGS)

    # # # Process Results # # #
    # TODO: PART 1, STEP 3 - Write a process results function to compute the relevant results (voltage and current
    # waveforms, steady state values, etc.), plot them, and compare your output to the waveforms produced by Simulink
    process_results(V_waveform, devices, SETTINGS, inv_node_dict, desiredVoltages, desiredCurrents)
