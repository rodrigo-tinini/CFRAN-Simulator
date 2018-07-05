import networkx as nx
import matplotlib.pyplot as plt

G = nx.DiGraph()
power_cost = 0
#cpri line rate
cpri_line = 614.4
#fog capacity
fog_capacity = 5 * cpri_line
#cloud capacity
cloud_capacity = 25 *cpri_line
#node power costs
costs = {}
costs["f1"] = 300
costs["f2"] = 300
costs["c"] = 600
#nodes capacities
capacities = {}
capacities["f1"] = fog_capacity
capacities["f2"] = fog_capacity
capacities["c"] = cloud_capacity

#rrh
class RRH(object):
    def __init__(cpri_line):
        self.cpri_line = cpri_line

#create graph
G.add_edges_from([("s", "v1", {'capacity': 614, 'weight': 0}),
                    ("s", "v2", {'capacity': 614, 'weight': 0}),
                    ("v1", "f1", {'capacity': fog_capacity, 'weight': 300}),
                   ("v1", "bridge", {'capacity': 10000, 'weight': 0}),
                   ("bridge", "c", {'capacity': cloud_capacity, 'weight': 0}),
                   ("v2", "f2", {'capacity': fog_capacity, 'weight': 300}),
                   ("v2", "bridge", {'capacity': 10000, 'weight': 0}),
                   ("f1", "d", {'capacity': 10000, 'weight': 0}),
                   ("f2", "d", {'capacity': 10000, 'weight': 0}),
                   ("c", "d", {'capacity': cloud_capacity, 'weight': 0}),
                   ])

mincostFlow = nx.max_flow_min_cost(G, "s", "d")
#print(mincostFlow)

def getPowerConsumption():
    power_cost = 0
    for i in mincostFlow:
        print("{}: {}".format(i, mincostFlow[i]))
        for j in mincostFlow[i]:
            if j == "d" and mincostFlow[i][j] > 0:
                print(i)
                #print("Node {}: Flow: {}".format(j,mincostFlow[i][j]))
                print("{} put traffic on d".format(i))
                power_cost += costs[i]
    return power_cost
power_cost = getPowerConsumption()
print(power_cost)
#mincost = nx.cost_of_flow(G, mincostFlow)
#mincost
#from networkx.algorithms.flow import maximum_flow
#maxFlow = maximum_flow(G, 1, 7)[1]
#nx.cost_of_flow(G, maxFlow) >= mincost
#mincostFlowValue = (sum((mincostFlow[u][7] for u in G.predecessors(7)))
#                     - sum((mincostFlow[7][v] for v in G.successors(7))))
#print(mincostFlowValue == nx.maximum_flow_value(G, 1, 7))
#nx.draw(G)
#plt.show()

'''
G = nx.DiGraph()
G.add_node('v1', demand = -614)
G.add_node('v2', demand = -614)
G.add_node('d', demand = 1228)
G.add_edge('v1', 'f1', weight = 500, capacity = 10000)
G.add_edge('f1', 'd', weight = 0, capacity = 10000)
G.add_edge('v1', 'bridge', weight = 600, capacity = 10000)
G.add_edge('v2', 'bridge', weight = 600, capacity = 10000)
G.add_edge('bridge', 'd', weight = 600, capacity = 10000)
G.add_edge('v2', 'f2', weight = 500, capacity = 10000)
G.add_edge('f2', 'd', weight = 0, capacity = 10000)
flowCost, flowDict = nx.capacity_scaling(G)
for i in flowDict:
    print("{}: {}".format(i, flowDict[i]))
'''