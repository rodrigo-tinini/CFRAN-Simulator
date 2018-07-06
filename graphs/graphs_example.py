import networkx as nx
import matplotlib.pyplot as plt
import time

G = nx.DiGraph()
power_cost = 0
#cpri line rate
cpri_line = 614
#fog capacity
fog_capacity = 5 * cpri_line
#cloud capacity
cloud_capacity = 25 *cpri_line
#node power costs
fog_cost = 300
cloud_cost = 0
costs = {}
costs["f1"] = 300
costs["f2"] = 300
costs["f3"] = 300
costs["f4"] = 300
costs["c"] = 600
#nodes capacities
capacities = {}
capacities["f1"] = fog_capacity
capacities["f2"] = fog_capacity
capacities["f3"] = fog_capacity
capacities["f4"] = fog_capacity
capacities["c"] = cloud_capacity

#rrh
class RRH(object):
    def __init__(cpri_line):
        self.cpri_line = cpri_line

#create graph
G.add_edges_from([("s", "r1", {'capacity': 614, 'weight': 0}),
                  ("s", "r2", {'capacity': 614, 'weight': 0}),
                  ("s", "r3", {'capacity': 614, 'weight': 0}),
                  ("s", "r4", {'capacity': 614, 'weight': 0}),
                  ("r1", "f1", {'capacity': 0, 'weight': fog_cost}),
                  ("r2", "f1", {'capacity': 0, 'weight': fog_cost}),
                  ("r3", "f1", {'capacity': 0, 'weight': fog_cost}),
                  ("r4", "f1", {'capacity': 0, 'weight': fog_cost}),
                  ("r1", "b", { 'weight': cloud_cost}),
                  ("r2", "b", { 'weight': cloud_cost}),
                  ("r3", "b", { 'weight': cloud_cost}),
                  ("r4", "b", { 'weight': cloud_cost}),
                  ("b", "c", {'capacity': 18420, 'weight': 0}),
                  ("c", "d", {'capacity': 18420, 'weight': 0}),
                  ("f1", "d", {'capacity': 6144, 'weight': 0}),
                  ("f2", "d", {'capacity': 6144, 'weight': 0}),
                  ("f3", "d", {'capacity': 6144, 'weight': 0}),
                  ("f4", "d", {'capacity': 6144, 'weight': 0}),
                  ("s", "r5", {'capacity': 614, 'weight': 0}),
                  ("r5", "f1", {'capacity': 0, 'weight': fog_cost}),
                  ("r5", "b", { 'weight': 0}),
                  ("s", "r6", {'capacity': 614, 'weight': 0}),
                  ("r6", "f1", {'capacity': 0, 'weight': fog_cost}),
                  ("r6", "b", { 'weight': 0}),
                  ("s", "r7", {'capacity': 614, 'weight': 0}),
                  ("r7", "f1", {'capacity': 0, 'weight': fog_cost}),
                  ("r7", "b", { 'weight': 0}),
                  ("s", "r8", {'capacity': 614, 'weight': 0}),
                  ("r8", "f1", {'capacity': 0, 'weight': fog_cost}),
                  ("r8", "b", { 'weight': 0}),
                  ("s", "r9", {'capacity': 614, 'weight': 0}),
                  ("r9", "f1", {'capacity': 0, 'weight': fog_cost}),
                  ("r9", "b", { 'weight': 0}),
                  ("s", "r10", {'capacity': 614, 'weight': 0}),
                  ("r10", "f1", {'capacity': 0, 'weight': fog_cost}),
                  ("r10", "b", { 'weight': 0}),
                  
                  ("s", "r11", {'capacity': 614, 'weight': 0}),
                  ("r11", "f2", {'capacity': 0, 'weight': fog_cost}),
                  ("r11", "b", { 'weight': 0}),
                  ("s", "r12", {'capacity': 614, 'weight': 0}),
                  ("r12", "f2", {'capacity': 0, 'weight': fog_cost}),
                  ("r12", "b", { 'weight': 0}),
                  ("s", "r13", {'capacity': 614, 'weight': 0}),
                  ("r13", "f2", {'capacity': 0, 'weight': fog_cost}),
                  ("r13", "b", { 'weight': 0}),
                  ("s", "r14", {'capacity': 614, 'weight': 0}),
                  ("r14", "f2", {'capacity': 0, 'weight': fog_cost}),
                  ("r14", "b", { 'weight': 0}),
                    ("s", "r15", {'capacity': 614, 'weight': 0}),
                  ("r15", "f2", {'capacity': 0, 'weight': fog_cost}),
                  ("r15", "b", { 'weight': 0}),
                    ("s", "r16", {'capacity': 614, 'weight': 0}),
                  ("r16", "f2", {'capacity': 0, 'weight': fog_cost}),
                  ("r16", "b", { 'weight': 0}),
                    ("s", "r17", {'capacity': 614, 'weight': 0}),
                  ("r17", "f2", {'capacity': 0, 'weight': fog_cost}),
                  ("r17", "b", { 'weight': 0}),
                  ("s", "r18", {'capacity': 614, 'weight': 0}),
                  ("r18", "f2", {'capacity': 0, 'weight': fog_cost}),
                  ("r18", "b", { 'weight': 0}),
                  ("s", "r19", {'capacity': 614, 'weight': 0}),
                  ("r19", "f2", {'capacity': 0, 'weight': fog_cost}),
                  ("r19", "b", { 'weight': 0}),
                  ("s", "r20", {'capacity': 614, 'weight': 0}),
                  ("r20", "f2", {'capacity': 0, 'weight': fog_cost}),
                  ("r20", "b", { 'weight': 0}),

                    ("s", "r21", {'capacity': 614, 'weight': 0}),
                  ("r21", "f3", {'capacity': 0, 'weight': fog_cost}),
                  ("r21", "b", { 'weight': 0}),
                  ("s", "r22", {'capacity': 614, 'weight': 0}),
                  ("r22", "f3", {'capacity': 0, 'weight': fog_cost}),
                  ("r22", "b", { 'weight': 0}),
                  ("s", "r23", {'capacity': 614, 'weight': 0}),
                  ("r23", "f3", {'capacity': 0, 'weight': fog_cost}),
                  ("r23", "b", { 'weight': 0}),
                  ("s", "r24", {'capacity': 614, 'weight': 0}),
                  ("r24", "f3", {'capacity': 0, 'weight': fog_cost}),
                  ("r24", "b", { 'weight': 0}),
                    ("s", "r25", {'capacity': 614, 'weight': 0}),
                  ("r25", "f3", {'capacity': 0, 'weight': fog_cost}),
                  ("r25", "b", { 'weight': 0}),
                    ("s", "r26", {'capacity': 614, 'weight': 0}),
                  ("r26", "f3", {'capacity': 0, 'weight': fog_cost}),
                  ("r26", "b", { 'weight': 0}),
                    ("s", "r27", {'capacity': 614, 'weight': 0}),
                  ("r27", "f3", {'capacity': 0, 'weight': fog_cost}),
                  ("r27", "b", { 'weight': 0}),
                  ("s", "r28", {'capacity': 614, 'weight': 0}),
                  ("r28", "f3", {'capacity': 0, 'weight': fog_cost}),
                  ("r28", "b", { 'weight': 0}),
                  ("s", "r29", {'capacity': 614, 'weight': 0}),
                  ("r29", "f3", {'capacity': 0, 'weight': fog_cost}),
                  ("r29", "b", { 'weight': 0}),
                  ("s", "r30", {'capacity': 614, 'weight': 0}),
                  ("r30", "f3", {'capacity': 0, 'weight': fog_cost}),
                  ("r30", "b", { 'weight': 0}),

                       ("s", "r31", {'capacity': 614, 'weight': 0}),
                  ("r31", "f4", {'capacity': 6144, 'weight': fog_cost}),
                  ("r31", "b", { 'weight': 0}),
                  ("s", "r32", {'capacity': 614, 'weight': 0}),
                  ("r32", "f4", {'capacity': 6144, 'weight': fog_cost}),
                  ("r32", "b", { 'weight': 0}),
                  ("s", "r33", {'capacity': 614, 'weight': 0}),
                  ("r33", "f4", {'capacity': 6144, 'weight': fog_cost}),
                  ("r33", "b", { 'weight': 0}),
                  ("s", "r34", {'capacity': 614, 'weight': 0}),
                  ("r34", "f4", {'capacity': 6144, 'weight': fog_cost}),
                  ("r34", "b", { 'weight': 0}),
                    ("s", "r35", {'capacity': 614, 'weight': 0}),
                  ("r35", "f4", {'capacity': 6144, 'weight': fog_cost}),
                  ("r35", "b", { 'weight': 0}),
                    ("s", "r36", {'capacity': 614, 'weight': 0}),
                  ("r36", "f4", {'capacity': 6144, 'weight': fog_cost}),
                  ("r36", "b", { 'weight': 0}),
                    ("s", "r37", {'capacity': 614, 'weight': 0}),
                  ("r37", "f4", {'capacity': 6144, 'weight': fog_cost}),
                  ("r37", "b", { 'weight': 0}),
                  ("s", "r38", {'capacity': 614, 'weight': 0}),
                  ("r38", "f4", {'capacity': 6144, 'weight': fog_cost}),
                  ("r38", "b", { 'weight': 0}),
                  ("s", "r39", {'capacity': 614, 'weight': 0}),
                  ("r39", "f4", {'capacity': 6144, 'weight': fog_cost}),
                  ("r39", "b", { 'weight': 0}),
                  ("s", "r40", {'capacity': 614, 'weight': 0}),
                  ("r40", "f4", {'capacity': 6144, 'weight': fog_cost}),
                  ("r40", "b", { 'weight': 0}),


                   ])
start_time = time.clock()
mincostFlow = nx.max_flow_min_cost(G, "s", "d")
#print(mincostFlow)
for i in mincostFlow:
  print(i, mincostFlow[i])
print("Time lapsed: {}".format(time.clock() - start_time))

def getPowerConsumption():
    power_cost = 0
    for i in mincostFlow:
        #print("{}: {}".format(i, mincostFlow[i]))
        for j in mincostFlow[i]:
            if j == "d" and mincostFlow[i][j] > 0:
                power_cost += costs[i]
            #if mincostFlow[i][j] == 0 and i != "s" and i != "c" and i != "b":
                  #print(i)
                  #print("Node {}: Flow: {}".format(j,mincostFlow[i][j]))
              #print("{} put traffic on {}".format(i,j))
    return power_cost

power_cost = getPowerConsumption()
print(power_cost)
#example of modifying edge attribute
#print(nx.edges(G,["d"]))
#print(G["s"]["r1"]['capacity'])
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