
def initialize(Vinit, bus, slack):
    for ele in bus:
        #Slack or PQ Bus
        Vinit[ele.node_Vr] = 1
        Vinit[ele.node_Vi] = 0
        if ele.Type == 2:
            Vinit[ele.node_Q] = 1e-2
    for ele in slack:
        # PV Bus
        Vinit[ele.node_Vr_Slack] = 1e-4
        Vinit[ele.node_Vi_Slack] = 1e-4

    return Vinit