import numpy as np
import matplotlib.pyplot as plt


def process_results(V_waveform, devices, SETTINGS, inv_node_dict):
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
    
    print(inv_node_dict)
    
    for Y in range((num_waves)):
        node = inv_node_dict[Y]
        wave = V_waveform[:,Y]
        if (node[0]=="n"):
            plt.figure(1)
            plt.plot(x,wave)
            fig1_legend.append(node)
        elif (node[0]+node[1]=="vs") :
            plt.figure(2)
            plt.plot(x,wave)
            fig2_legend.append("Current:" + str(node))

    plt.figure(1)
    plt.legend(fig1_legend, loc=1)
    plt.figure(2)
    plt.legend(fig2_legend, loc=1)
    
    pass
    