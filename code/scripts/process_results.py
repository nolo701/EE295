import numpy as np
import matplotlib.pyplot as plt


def process_results(V_waveform, devices, SETTINGS, inv_node_dict, desiredVoltages, desiredCurrents):
    # get number of plots assuming all nodes are to be visible
    num_waves = np.shape(V_waveform)[1]
    num_samples = np.shape(V_waveform)[0]
    # create the time vector
    x = np.linspace(0, SETTINGS["Simulation Time"], num=num_samples)
    # Figure 1: Node voltages
    plt.figure(1)
    plt.title("Node Voltages")
    fig1_legend = []
    # Figure 2: VSource Currents
    plt.figure(2)
    plt.title("Voltage Source Currents")
    fig2_legend = []

    # Plot the waves
    for Y in range((num_waves)):
        node = inv_node_dict[Y]
        wave = V_waveform[:,Y]
        # check to see if it belongs to the desired Voltages
        for desired in desiredVoltages: 
            if(node == desired):
                plt.figure(1)
                plt.plot(x,wave)
                fig1_legend.append(node)
        # check to see if it belongs to the desired Currents
        for desired in desiredCurrents:
            if(node == desired):
                plt.figure(2)
                plt.plot(x,wave)
                fig2_legend.append("Current:" + str(node))
    # Add the legends & grids
    plt.figure(1)
    plt.legend(fig1_legend, loc=1)
    plt.grid()
    plt.figure(2)
    plt.legend(fig2_legend, loc=1)
    plt.grid()
    
    
    pass



