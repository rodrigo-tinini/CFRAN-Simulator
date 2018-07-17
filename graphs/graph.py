import networkx as nx
import matplotlib.pyplot as plt
import math
import time

G = nx.DiGraph()
#keeps the power cost
power_cost = 0
#cpri line rate
cpri_line = 614.4
#capacity of a vopn
lambda_capacity = 16 * cpri_line
#fog capacity
fog_capacity = 16 * cpri_line
#cloud capacity
cloud_capacity = 80 *cpri_line
#node power costs
fog_cost = 300
cloud_cost = 0
#nodes costs
costs = {}
costs["fog0"] = 300
costs["fog1"] = 300
costs["fog2"] = 300
costs["fog3"] = 300
costs["fog4"] = 300
costs["cloud"] = 600
#nodes capacities
capacities = {}
capacities["fog0"] = fog_capacity
capacities["fog1"] = fog_capacity
capacities["fog2"] = fog_capacity
capacities["fog3"] = fog_capacity
capacities["fog4"] = fog_capacity
capacities["cloud"] = cloud_capacity
#list of all rrhs
rrhs = []
#list of actives rrhs on the graph
actives_rrhs =[]
#list of available VPONs
available_vpons = [0,1,2,3,4,5,6,7,8,9]
#list of allocated vpons
allocated_vpons = []
#capacity of vpons
vpons_capacity = {}
for i in range(10):
  vpons_capacity[i] = 10000

#rrh
class RRH(object):
    def __init__(self, cpri_line, rrhId):
        self.cpri_line = cpri_line
        self.id = "RRH{}".format(rrhId)

#create rrhs
def createRRHs(amount):
  for i in range(amount):
    rrhs.append(RRH(cpri_line, i))

#create graph
G.add_edges_from([("bridge", "cloud", {'capacity': 0, 'weight': cloud_cost}),
                    ("cloud", "d", {'capacity': cloud_capacity, 'weight': 0}),
                   ])

def createGraph():
    G = nx.DiGraph()
    G.add_edges_from([("bridge", "cloud", {'capacity': 0, 'weight': cloud_cost}),
                    ("cloud", "d", {'capacity': cloud_capacity, 'weight': 0}),
                   ])
    return G

def addNodesEdgesSet(graph, node, fog_bridge):
    graph.add_edges_from([("s", node, {'capacity': 0, 'weight': 0}),
      (node, "fog_bridge{}".format(fog_bridge), { 'weight': 0}),
      (node, "bridge", { 'weight': 0}),
      ])

def addFogNodes(graph, fogs):
    for i in range(fogs):
      graph.add_edges_from([("fog_bridge{}".format(i), "fog{}".format(i), {'capacity': 0, 'weight':fog_cost}),
                          ("fog{}".format(i), "d", {'capacity': fog_capacity, 'weight':0}),
                          ])

def addRRHs(graph, bottom, rrhs, fog):
    for i in range(bottom,rrhs):
      addNodesEdgesSet(graph, "RRH{}".format(i), "{}".format(fog))

def addRRH(graph, rrh, fog):
    addNodesEdgesSet(graph, rrh, fog)

def startNode(graph, node):
  graph["s"][node]["capacity"] = cpri_line

def endNode(graph, node):
  graph["s"][node]["capacity"] = 0

def updateCapacity(graph, node1, node2, value):
  graph[node1][node2]["capacity"] = value

#heuristic to assign VPONs to nodes- cloud first
def assignVPON(graph):
      traffic = 0
      #calculate the total incoming traffic
      traffic = len(actives_rrhs) * cpri_line
      #verify if the cloud alone can support this traffic
      if traffic <= graph["cloud"]["d"]["capacity"]:
        #verify if the fronthaul has lambda. If so, does nothing, otherwise, put the necessary vpons
        if graph["bridge"]["cloud"]["capacity"] == 0 or traffic > graph["bridge"]["cloud"]["capacity"]:
          print("Putting VPONs on Fronthaul")
          #calculate the VPONs necessaries and put them on the fronthaul
          #num_vpons = 0
          #num_vpons = math.ceil(traffic/lambda_capacity)
          #for i in range(num_vpons):
          #  graph["bridge"]["cloud"]["capacity"] += 9830.4
          #  allocated_vpons.append(available_vpons.pop())
          #this ways seems better than the above method
          while graph["bridge"]["cloud"]["capacity"] < traffic:
            if available_vpons:
              graph["bridge"]["cloud"]["capacity"] += 9830.4
              allocated_vpons.append(available_vpons.pop())
            else:
              print("No VPON available!")
      else:
        print("Putting VPONs on Fronthaul and Fog")
        #calculate the amount necessary on VPONs and put the maximum on the cloud and the rest on the fogs
        num_vpons = 0
        num_vpons = math.ceil(traffic/lambda_capacity)
        while graph["bridge"]["cloud"]["capacity"] < graph["cloud"]["d"]["capacity"] :
          if available_vpons:
            graph["bridge"]["cloud"]["capacity"] += 9830.4
            allocated_vpons.append(available_vpons.pop())
            num_vpons -= num_vpons
          else:
              print("No VPON available!")
        #First-Fit Fog VPON Allocation - When there is VPON, put it on the next Fog Node
        while available_vpons:
          for i in range(fogs):#this is the First-Fit Fog VPON Allocation
            if available_vpons:
              graph["fog_bridge{}".format(i)]["fog{}".format(i)]["capacity"] += 9830.4 
              allocated_vpons.append(available_vpons.pop())
              num_vpons -= num_vpons
            else:
                print("No VPON available!")
      #return traffic

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


#testes
'''
createRRHs(10)
for i in rrhs:
  print(i.id)
addFogNodes(G, 1)
addRRHs(G,12,14,0)
print([i for i in nx.edges(G)])
#G["s"]["RRH0"]["capacity"] = 10
#print(G["s"])
#startNode(G, "RRH11")
start_time = time.clock()
#mincostFlow = nx.max_flow_min_cost(G, "s", "d")
#print(mincostFlow)
#for i in mincostFlow:
#  print(i, mincostFlow[i])
#print("Time lapsed: {}".format(time.clock() - start_time))

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

#power_cost = getPowerConsumption()
#print(power_cost)

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
