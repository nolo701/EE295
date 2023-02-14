import numpy as np

def run_time_domain_simulation(devices, V_init, size_Y, SETTINGS):
    # for t=0: run from init conditions
    t = 0
    count = 0
    Y = np.zeros((size_Y, size_Y))
    J = np.zeros(size_Y, )
    
    
    
    # create a matrix for the results of each time step
    # and fill in the known value for init
    samples = int(1 + np.ceil( [SETTINGS["Simulation Time"]/SETTINGS["Time Step"]]))
    #print(samples)
    V_waveform = np.zeros((samples,size_Y))
    V_waveform[0,:] = V_init.T
    #print(V_waveform)
    # Stamp all the Resistors into the matrix
    for R in devices["resistors"]:
        R.stamp_dense(Y)
    
    # Stamp all the Voltage sources into the matrix
    for VS in devices["voltage_sources"]:
        VS.stamp_dense(Y, V_init, t)
        
    # Stamp all the Inductors into the matrix
    for L in devices["inductors"]:
        L.stamp_dense(Y,J,V_init,t,SETTINGS)
    
    result_t = np.linalg.solve(Y,V_init)
    
    t += SETTINGS["Time Step"]
    count += 1
    
    while(t<=SETTINGS["Simulation Time"]):
        # Create the empty dense matricies
        Y = np.zeros((size_Y, size_Y))
        J = np.zeros(size_Y, )
        
        # Stamp all the Resistors into the matrix
        for R in devices["resistors"]:
            R.stamp_dense(Y)
        
        # Stamp all the Voltage sources into the matrix
        for VS in devices["voltage_sources"]:
            VS.stamp_dense(Y, J, t)
            
        # Stamp all the Inductors into the matrix
        for L in devices["inductors"]:
            L.stamp_dense(Y,J,result_t,t,SETTINGS)
        
        result_t = np.linalg.solve(Y,J)
        #print(count, "t=", t)
        #print(result_t)
        V_waveform[count,:] = result_t
        count += 1
        t += SETTINGS["Time Step"]
    

    return V_waveform