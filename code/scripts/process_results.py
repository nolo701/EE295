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
    print("Inv. Node dict")
    print(inv_node_dict)
    print("Num waves:")
    print(num_waves)
    print("Num samples:")
    print(num_samples)
    
    # Change these lists to select which voltages and which currents to plot
    # Three phase RL
    #desiredVoltages = ["n3_a","n3_b","n3_c"]
    #desiredCurrents = ["vs_v_a","vs_v_b","vs_v_c"]
    # Single Phase RL
    #desiredVoltages = ["n1_a","n2_a"]
    #desiredCurrents = ["vs_v_a"]
    # Single Phase RL-L
    desiredVoltages = ["n1_a","n2_a","n3_a"]
    desiredCurrents = ["vs_v_a"]
    
    # Works for single Phase
    for Y in range((num_waves)):
        node = inv_node_dict[Y]
        wave = V_waveform[:,Y]
        # check to see if it belongs to the desired Voltages
        for desired in desiredVoltages:
            
            if(node == desired):
                print("Voltage found")
                plt.figure(1)
                plt.plot(x,wave)
                fig1_legend.append(node)
        # check to see if it belongs to the desired Currents
        for desired in desiredCurrents:
            
            if(node == desired):
                print("Current Found")
                plt.figure(2)
                plt.plot(x,wave)
                fig2_legend.append("Current:" + str(node))
        

    plt.figure(1)
    plt.legend(fig1_legend, loc=1)
    plt.figure(2)
    plt.legend(fig2_legend, loc=1)
    
    
    pass




def process_resultsIncomplete(V_waveform, devices, SETTINGS, inv_node_dict):
    # get number of plots assuming all nodes are to be visible
    num_waves = np.shape(V_waveform)[1]
    num_samples = np.shape(V_waveform)[0]
    # create the time vector
    x = np.linspace(0, SETTINGS["Simulation Time"], num=num_samples)
    # parse to find number of phases
    phaseDict={}
    for nodes in devices["nodes"]:
        if nodes.phase != "N":
            phaseDict[nodes.phase] = nodes.phase
    # correct the phase dict for letter->num
    count = 1
    for p, val in phaseDict.items():
        phaseDict[p] = count
        count = count + 2
    phases = len(phaseDict)
    print("Phases:")
    print(phases)
    print(phaseDict)
    # Create an int to follow number of nessecary figures
    # # of plots = (# of phases) * 2 (1 for currents, 1 for voltages)
    numPlots = phases * 2
    
    # Instantiate plots & legends
    legends = []
    for i in range((numPlots)):
        legends.append([])
        plt.figure(i)
        if (i % 2) == 0:
            plt.title("Currents")
        else:
            plt.title("Node Voltages")
    # go through all the waves and add them to the corresponding plot
    # - lines up phase & measurment type
    for Y in range((num_waves)):
        node = inv_node_dict[Y]
        wave = V_waveform[:,Y]
        # check phase
        print("Node:")
        print(node)
        print("Node Length")
        print(len(node))
        wave_phase = phaseDict[str(node[len(node)-1]).capitalize()]
        print("Wave Phase")
        print(wave_phase)
        fig_num = wave_phase
        if (node[0]=="n"):
            plt.figure(fig_num)
            plt.plot(x,wave)
            legends[fig_num].append(node)
        elif (node[0]+node[1]=="vs") :
            plt.figure(fig_num+1)
            plt.plot(x,wave)
            legends[fig_num].append("Current:" + str(node))
            
    # add the legends
    inv_phase_dict=dict(map(reversed, phaseDict.items()))
    for i in range((numPlots)):
        plt.figure(i)
        plt.legend(legends[i-1], loc=1)
        if (i % 2) == 0:
            plt.title("Currents - Phase "+inv_phase_dict(np.ceil(i/2)+(np.ceil(i/2)-1)))
        else:
            plt.title("Node Voltages - Phase "+inv_phase_dict(np.ceil(i/2)+(np.ceil(i/2)-1)))
    '''
    # Figure 1: Node voltages
    plt.figure(1)
    plt.title("Node Voltages")
    fig1_legend = []
    # Figure 2: VSource Currents
    plt.figure(2)
    plt.title("Voltage Source Currents")
    fig2_legend = []
    print("Inv. Node dict")
    print(inv_node_dict)
    print("Num waves:")
    print(num_waves)
    print("Num samples:")
    print(num_samples)
    
    # Works for single Phase
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
    '''
    pass
    