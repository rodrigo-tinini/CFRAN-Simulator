import networkx as nx
import matplotlib.pyplot as plt
import math
import time
import random

G = nx.DiGraph()
#number of RRHs
rrhs_amount = 100
#consumption of a line card + a DU
line_card_consumption = 25
#keeps the power cost
power_cost = 0
#cpri line rate - it is round to 614 because float 614.4 was unexplained causing no flow to be found (even with as free capacity as needed)
cpri_line = 614
#capacity of a vopn
lambda_capacity = 16 * cpri_line
#fog capacity
fog_capacity = 16 * cpri_line
#cloud capacity
cloud_capacity = 80 *cpri_line
#node power costs
fog_cost = 300
cloud_cost = 1
#number of fogs
fogs = 5
#nodes costs
costs = {}
for i in range(fogs):
  costs["fog{}".format(i)] = 300
costs["cloud"] = 600
#nodes capacities
capacities = {}
for i in range(fogs):
  capacities["fog{}".format(i)] = fog_capacity
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
#this dictionary keeps the rrhs indexed by its fog node
fog_rrhs = {}
#this dictionary keeps the amount of activated RRHs on each fog node
fog_activated_rrhs = {}
#initialize the lists
for i in range(fogs):
  fog_rrhs["fog_bridge{}".format(i)] = []
for i in range(fogs):
  fog_activated_rrhs["fog_bridge{}".format(i)] = 0
#this list keeps the amount of 
#dict that keeps the fog of each RRH
rrhs_fog = {}
#dict that keeps the processing node of each RRH
rrhs_proc_node = {}
for i in range(rrhs_amount):
  rrhs_proc_node["RRH{}".format(i)] = None
#this dictionary keeps track of bandwidth (vpons) allocated to each fog node
fogs_vpons = {}
for i in range(fogs):
  fogs_vpons["fog{}".format(i)] = []
#this list keeps track of the vpons allocated to the cloud
cloud_vpons = []
#this dict keeps the load on each processing node
load_node = {}
load_node["cloud"] = 0.0
for i in range(fogs):
  load_node["fog_bridge{}".format(i)] = 0.0
#keeps the cost of the nodes
nodes_costs = {}
nodes_costs["cloud"] = cloud_cost
for i in range(fogs):
  nodes_costs["fog{}".format(i)] = fog_cost
#keeps the ratio between power consumption and activated RRHs on each processing node
nodes_ratio_cost_rrhs = {}
nodes_ratio_cost_rrhs["cloud"] = 0.0
for i in range(fogs):
  nodes_ratio_cost_rrhs["fog{}".format(i)] = 0.0

#rrh
class RRH(object):
    def __init__(self, cpri_line, rrhId):
        self.cpri_line = cpri_line
        self.id = "RRH{}".format(rrhId)

#update the amount of activated RRHs attached to a fog node
def addActivated(rrh):
  fog_activated_rrhs[rrhs_fog[rrh]] += 1

#update the amount of activated RRHs attached to a fog node
def minusActivated(rrh):
  if fog_activated_rrhs[rrhs_fog[rrh]] > 0:
    fog_activated_rrhs[rrhs_fog[rrh]] -= 1

#update load on processing node
def update_node_load(node, load):
  load_node[node] += load
  load_node[node] = round(load_node[node],1)

#create rrhs
def createRRHs():
  for i in range(rrhs_amount):
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
    indexRRH(node, fog_bridge)

#index RRH to each correspondent fog node
def indexRRH(node, fog_bridge):
  fog_rrhs["fog_bridge{}".format(fog_bridge)].append(node)    

def addFogNodes(graph, fogs):
    for i in range(fogs):
      graph.add_edges_from([("fog_bridge{}".format(i), "fog{}".format(i), {'capacity': 0, 'weight':fog_cost}),
                          ("fog{}".format(i), "d", {'capacity': fog_capacity, 'weight':0}),
                          ])

def addRRHs(graph, bottom, rrhs, fog):
    for i in range(bottom,rrhs):
      addNodesEdgesSet(graph, "RRH{}".format(i), "{}".format(fog))
      rrhs_fog["RRH{}".format(i)] = "fog_bridge{}".format(fog)

def addRRH(graph, rrh, fog):
    addNodesEdgesSet(graph, rrh, fog)

def startNode(graph, node):
  graph["s"][node]["capacity"] = cpri_line

def endNode(graph, node):
  graph["s"][node]["capacity"] = 0.0

def updateCapacity(graph, node1, node2, value):
  graph[node1][node2]["capacity"] = value

#clear the load on nodes after traffic change
def clearLoad():
  global load_node
  for i in load_node:
    load_node[i] = 0.0

#remove traffic from RRH from its processing node
def removeRRHNode(rrh):
  global load_node, rrhs_proc_node
  load_node[rrhs_proc_node[rrh]] -= cpri_line
  rrhs_proc_node[rrh] = None

############################################################################################
#The following heuristics are all Cloud-First and then have different policies to put VPONs on the Fog
#Regardless of the cost of the Fog, all of them put VPONs first on the cloud
#Cloud-First and Random Fog VPON Assignment
def randomFogVPON(graph):
  traffic = 0
  #calculate the total incoming traffic
  traffic = len(actives_rrhs) * cpri_line
  #verify if the cloud alone can support this traffic
  if traffic <= graph["cloud"]["d"]["capacity"]:
    #print("Cloud Can Handle It!")
    #verify if the fronthaul has lambda. If so, does nothing, otherwise, put the necessary vpons
    if graph["bridge"]["cloud"]["capacity"] == 0 or traffic > graph["bridge"]["cloud"]["capacity"]:
      #print("Putting VPONs on Fronthaul")
      #calculate the VPONs necessaries and put them on the fronthaul
      #num_vpons = 0
      #num_vpons = math.ceil(traffic/lambda_capacity)
      #for i in range(num_vpons):
      #  graph["bridge"]["cloud"]["capacity"] += 9824
      #  allocated_vpons.append(available_vpons.pop())
      #this ways seems better than the above method
      while graph["bridge"]["cloud"]["capacity"] < traffic:
        if available_vpons:
          graph["bridge"]["cloud"]["capacity"] += 9824
          cloud_vpons.append(available_vpons.pop())
        else:
          print("No VPON available!")
    else:
      pass#print("OKKKK")
  elif traffic > graph["cloud"]["d"]["capacity"]:
    if available_vpons:
      print("Putting VPONs on Fronthaul and Fog")
      #calculate the amount necessary on VPONs and put the maximum on the cloud and the rest on the fogs
      num_vpons = 0
      num_vpons = math.ceil(traffic/lambda_capacity)
      while graph["bridge"]["cloud"]["capacity"] < graph["cloud"]["d"]["capacity"] :
        if available_vpons:
          graph["bridge"]["cloud"]["capacity"] += 9824
          cloud_vpons.append(available_vpons.pop())
          num_vpons -= num_vpons
        else:
            print("No VPON available!")
      #Random Fog VPON Allocation - When there is VPON and traffic is greater than the total available bandwidth, put it on a random fog node
      #calculate the total available bandwidth
      total_bd = getTotalBandwidth(graph)
      #First-Fit Fog VPON Allocation - When there is VPON and traffic is greater than the total available bandwidth, put it on the next Fog Node
      #take a list of the fog nodes (using getMostActivatedRRHsFog method, but as I am going to take a random fog, this method or the most loaded fog does not make difference)
      least_fogs = getMostActivatedRRHsFog(graph)
      while traffic < total_bd:
        if available_vpons:
          #choose a random fog node
          f = least_fogs[random.choice(range(len(least_fogs)))]
          bridge = getFogBridge(graph, f)
          graph[bridge][fog]["capacity"] += 9824
          fogs_vpons[f].append(available_vpons.pop())
          num_vpons -= num_vpons
          total_bd = getTotalBandwidth(graph)
        else:
              print("No VPON available!")

#heuristic to assign VPONs to nodes- cloud first and all fogs
def assignVPON(graph):
  traffic = 0
  #calculate the total incoming traffic
  traffic = len(actives_rrhs) * cpri_line
  #verify if the cloud alone can support this traffic
  if traffic <= graph["cloud"]["d"]["capacity"]:
    #print("Cloud Can Handle It!")
    #verify if the fronthaul has lambda. If so, does nothing, otherwise, put the necessary vpons
    if graph["bridge"]["cloud"]["capacity"] == 0 or traffic > graph["bridge"]["cloud"]["capacity"]:
      #print("Putting VPONs on Fronthaul")
      #calculate the VPONs necessaries and put them on the fronthaul
      #num_vpons = 0
      #num_vpons = math.ceil(traffic/lambda_capacity)
      #for i in range(num_vpons):
      #  graph["bridge"]["cloud"]["capacity"] += 9824
      #  allocated_vpons.append(available_vpons.pop())
      #this ways seems better than the above method
      while graph["bridge"]["cloud"]["capacity"] < traffic:
        if available_vpons:
          graph["bridge"]["cloud"]["capacity"] += 9824
          cloud_vpons.append(available_vpons.pop())
        else:
          print("No VPON available!")
    else:
      pass#print("OKKKK")
  elif traffic > graph["cloud"]["d"]["capacity"]:
    if available_vpons:
      print("Putting VPONs on Fronthaul and Fog")
      #calculate the amount necessary on VPONs and put the maximum on the cloud and the rest on the fogs
      num_vpons = 0
      num_vpons = math.ceil(traffic/lambda_capacity)
      while graph["bridge"]["cloud"]["capacity"] < graph["cloud"]["d"]["capacity"] :
        if available_vpons:
          graph["bridge"]["cloud"]["capacity"] += 9824
          cloud_vpons.append(available_vpons.pop())
          num_vpons -= num_vpons
        else:
            print("No VPON available!")
      #First-Fit Fog VPON Allocation - When there is VPON and traffic is greater than the total available bandwidth, put it on the next Fog Node
      while available_vpons:
        for i in range(fogs):#this is the First-Fit Fog VPON Allocation
          if available_vpons:
            graph["fog_bridge{}".format(i)]["fog{}".format(i)]["capacity"] += 9824 
            fogs_vpons["fog{}".format(i)].append(available_vpons.pop())
            num_vpons -= num_vpons
          else:
              print("No VPON available!")
    #else: print('No available VPONs')
  #return traffic

#Most-Loaded Fog VPON Allocation
def assignMostLoadedVPON(graph):
  traffic = 0
  #calculate the total incoming traffic
  traffic = len(actives_rrhs) * cpri_line
  #verify if the cloud alone can support this traffic
  if traffic <= graph["cloud"]["d"]["capacity"]:
    #print("Cloud Can Handle It!")
    #verify if the fronthaul has lambda. If so, does nothing, otherwise, put the necessary vpons
    if graph["bridge"]["cloud"]["capacity"] == 0 or traffic > graph["bridge"]["cloud"]["capacity"]:
      #print("Putting VPONs on Fronthaul")
      #calculate the VPONs necessaries and put them on the fronthaul
      #num_vpons = 0
      #num_vpons = math.ceil(traffic/lambda_capacity)
      #for i in range(num_vpons):
      #  graph["bridge"]["cloud"]["capacity"] += 9824
      #  allocated_vpons.append(available_vpons.pop())
      #this ways seems better than the above method
      while graph["bridge"]["cloud"]["capacity"] < traffic:
        if available_vpons:
          graph["bridge"]["cloud"]["capacity"] += 9824
          cloud_vpons.append(available_vpons.pop())
        else:
          print("No VPON available!")
    else:
      pass#print("OKKKK")
  elif traffic > graph["cloud"]["d"]["capacity"]:
    if available_vpons:
      print("Putting VPONs on Fronthaul and Fog")
      #calculate the amount necessary on VPONs and put the maximum on the cloud and the rest on the fogs
      num_vpons = 0
      num_vpons = math.ceil(traffic/lambda_capacity)
      while graph["bridge"]["cloud"]["capacity"] < graph["cloud"]["d"]["capacity"] :
        if available_vpons:
          graph["bridge"]["cloud"]["capacity"] += 9824
          cloud_vpons.append(available_vpons.pop())
          num_vpons -= num_vpons
        else:
            print("No VPON available!")
      #calculate the total available bandwidth
      total_bd = getTotalBandwidth(graph)
      #First-Fit Fog VPON Allocation - When there is VPON and traffic is greater than the total available bandwidth, put it on the next Fog Node
      #place VPONs on fogs following least-activated RRHs order
      least_fogs = getMostActivatedRRHsFog(graph)
      while traffic < total_bd:
        if available_vpons:
          f = least_fogs.pop()
          bridge = getFogBridge(graph, f)
          graph[bridge][fog]["capacity"] += 9824
          fogs_vpons[f].append(available_vpons.pop())
          num_vpons -= num_vpons
          total_bd = getTotalBandwidth(graph)
        else:
              print("No VPON available!")
    #else: print('No available VPONs')
  #return traffic

#Cloud-First and Least-Loaded Fog VPON Allocation
def assignLeastLoadedVPON(graph):
  traffic = 0
  #calculate the total incoming traffic
  traffic = len(actives_rrhs) * cpri_line
  #verify if the cloud alone can support this traffic
  if traffic <= graph["cloud"]["d"]["capacity"]:
    #print("Cloud Can Handle It!")
    #verify if the fronthaul has lambda. If so, does nothing, otherwise, put the necessary vpons
    if graph["bridge"]["cloud"]["capacity"] == 0 or traffic > graph["bridge"]["cloud"]["capacity"]:
      #print("Putting VPONs on Fronthaul")
      #calculate the VPONs necessaries and put them on the fronthaul
      #num_vpons = 0
      #num_vpons = math.ceil(traffic/lambda_capacity)
      #for i in range(num_vpons):
      #  graph["bridge"]["cloud"]["capacity"] += 9824
      #  allocated_vpons.append(available_vpons.pop())
      #this ways seems better than the above method
      while graph["bridge"]["cloud"]["capacity"] < traffic:
        if available_vpons:
          graph["bridge"]["cloud"]["capacity"] += 9824
          cloud_vpons.append(available_vpons.pop())
        else:
          print("No VPON available!")
    else:
      pass#print("OKKKK")
  elif traffic > graph["cloud"]["d"]["capacity"]:
    if available_vpons:
      print("Putting VPONs on Fronthaul and Fog")
      #calculate the amount necessary on VPONs and put the maximum on the cloud and the rest on the fogs
      num_vpons = 0
      num_vpons = math.ceil(traffic/lambda_capacity)
      while graph["bridge"]["cloud"]["capacity"] < graph["cloud"]["d"]["capacity"] :
        if available_vpons:
          graph["bridge"]["cloud"]["capacity"] += 9824
          cloud_vpons.append(available_vpons.pop())
          num_vpons -= num_vpons
        else:
            print("No VPON available!")
      #calculate the total available bandwidth
      total_bd = getTotalBandwidth(graph)
      #First-Fit Fog VPON Allocation - When there is VPON and traffic is greater than the total available bandwidth, put it on the next Fog Node
      #place VPONs on fogs following least-activated RRHs order
      least_fogs = getLeastActivatedRRHsFog(graph)
      while traffic < total_bd:
        if available_vpons:
          f = least_fogs.pop()
          bridge = getFogBridge(graph, f)
          graph[bridge][fog]["capacity"] += 9824
          fogs_vpons[f].append(available_vpons.pop())
          num_vpons -= num_vpons
          total_bd = getTotalBandwidth(graph)
        else:
              print("No VPON available!")
    #else: print('No available VPONs')
  #return traffic

################################################################################################################

#updates nodes ratio between cost and activated RRHs
def updateRatio():
  traffic = getIncomingTraffic()
  #updates the ratio of the cloud
  if traffic > 0:
    nodes_ratio_cost_rrhs["cloud"] = nodes_costs["cloud"]/traffic
  for i in range(fogs):
    if fog_activated_rrhs["fog_bridge{}".format(i)] > 0:
      total_fog_traffic = fog_activated_rrhs["fog_bridge{}".format(i)] * cpri_line
      nodes_ratio_cost_rrhs["fog{}".format(i)] = nodes_costs["fog{}".format(i)]/total_fog_traffic

#sort and get nodes by least cost
def getLeastCostNodes():
  least_cost = sorted(nodes_costs, key = nodes_costs.__getitem__)
  return least_cost

#sort and get nodes sorted by least ratio between node cost and activated RRHs
def getLeastActCost():
  least_cost = sorted(nodes_ratio_cost_rrhs, key = nodes_ratio_cost_rrhs.__getitem__)
  return least

#The following heuristic puts the VPONs on the least cost node, regardless if it is the cloud or the fogs
#it sorts the nodes in ascending order of costs and then assign the VPONs until the demanded traffic is less or equal than the available bandwidth
def leastCostNodeVPON(graph):
  #keeps the sorted nodes
  least_cost = sorted(nodes_costs, key = nodes_costs.__getitem__)

#The following heuristic puts the VPONs on the least cost node order, but, it also sorts the fog node considering the number of active RRHs in each fog node
#It also re-assign VPONs if the costs changes or if the number of active RRHs on each fog node changes
def leastCostLoadedVPON(graph):
  pass

#update the cost of a node
def updateNodeCost(node, cost):
  nodes_costs[node] = cost

#get the cost of a node
def getNodeCost(node):
  return nodes_costs[node]

#get the fog bridge of a fog node
def getFogBridge(graph, fog):
  for i in range(fogs):
    if next(iter(graph["fog_bridge{}".format(i)])) == fog:
      return "fog_bridge{}".format(i)

#simple function that allocates VPONs on the fronthaul
def vponFronthaul(graph, traffic):
  while graph["bridge"]["cloud"]["capacity"] < traffic:
          if available_vpons:
            graph["bridge"]["cloud"]["capacity"] += 9824
            cloud_vpons.append(available_vpons.pop())
          else:
            print("No VPON available!")

#remove unnecessary bandwidth(VPONs) from the links (fronthaul and fog nodes)
def removeVPON(graph):
  #first, verify if the traffic can be handled only by the cloud
  #if fog has VPONs, deallocate them
  traffic = len(actives_rrhs) * cpri_line
  if traffic <= graph["cloud"]["d"]["capacity"] and traffic <= graph["bridge"]["cloud"]["capacity"]:
    #cloud can handle the traffic, if there are VPONs on fogs, release them
    for i in range(fogs):
      if graph["fog_bridge{}".format(i)]["fog{}".format(i)]["capacity"] > 0:
        graph["fog_bridge{}".format(i)]["fog{}".format(i)]["capacity"] = 0
        while fogs_vpons["fog{}".format(i)]:
          print("Poping")
          available_vpons.append(fogs_vpons["fog{}".format(i)].pop())
    #release the VPONs of the fronthaul until only the necessary to support current traffic is reached
    num_vpons = 0
    num_vpons = (math.ceil(traffic/lambda_capacity))*9824
    while graph["bridge"]["cloud"]["capacity"] > num_vpons:
      print("Releasing the cloud")
      graph["bridge"]["cloud"]["capacity"] -= 9824
      available_vpons.append(cloud_vpons.pop())

#return the total available bandwidth on all network links
def getTotalBandwidth(graph):
  total = 0.0
  total += graph["bridge"]["cloud"]["capacity"]
  for i in range(fogs):
    total += graph["fog_bridge{}".format(i)]["fog{}".format(i)]["capacity"]
  return total

#check in which node the rrhs is being processed
def getProcessingNodes(graph, mincostFlow, rrh):
  #now, iterate over the flow of each neighbor of the RRH
  if mincostFlow[rrh][rrhs_fog[rrh]] != 0:
    update_node_load(rrhs_fog[rrh], cpri_line)
    rrhs_proc_node[rrh] = rrhs_fog[rrh]
    print("Inserted on fog")
  elif mincostFlow[rrh]["bridge"] != 0:
    update_node_load("cloud", cpri_line)
    rrhs_proc_node[rrh] = "cloud"
    print("Inserted on cloud")
  #print(mincostFlow[actives_rrhs[i]]["bridge"])


##get the amount of activated RRHs on each fog node
def activatedFogRRHs(graph):
  #verify the RRHs that are
  for i in range(len(rrhs)):
    if graph["s"]["RRH{}".format(i)]["capacity"] != 0:
      fog_activated_rrhs[rrhs_fog["RRH{}".format(i)]] += 1
  return fog_activated_rrhs

#sort the fogs from ascendenting number of activated RRHs
def getLeastActivatedRRHsFog(graph):
  activated = activatedFogRRHs(graph)
  activated_sorted = sorted(activated, key = activated.__getitem__)
  activated_sorted.reverse()
  return activated_sorted

#sort the fogs from descendenting number of activated RRHs
def getMostActivatedRRHsFog(graph):
  activated = activatedFogRRHs(graph)
  activated_sorted = sorted(activated, key = activated.__getitem__)
  return activated_sorted

def OLDgetProcessingNodes(graph, mincostFlow):
  #check the outcoming flow of each RRH and where it is put (bridge or fog bridge)
  for i in range(len(actives_rrhs)):
    #now, iterate over the flow of each neighbor of the RRH
    if mincostFlow[actives_rrhs[i]][rrhs_fog[actives_rrhs[i]]] != 0:
      update_node_load(rrhs_fog[actives_rrhs[i]], cpri_line)
      rrhs_proc_node[actives_rrhs[i]] = rrhs_fog[actives_rrhs[i]]
    elif mincostFlow[actives_rrhs[i]]["bridge"] != 0:
      update_node_load("cloud", cpri_line)
      rrhs_proc_node[actives_rrhs[i]] = "cloud"
    #print(mincostFlow[actives_rrhs[i]]["bridge"])

#calculate the power consumed by active processing node (if a flow reaches "d" by a node, it is considered active)
def getPowerConsumption(mincostFlow):
    power_cost = 0.0
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

#calculate the power consumed by active VPONs
def getBandwidthPower(graph):
  bandwidth_power = 0.0
  #first get the consumption of the fronthaul
  if graph["bridge"]["cloud"]["capacity"] > 0:
    bandwidth_power += (graph["bridge"]["cloud"]["capacity"] / 9824) * line_card_consumption
  #now, if there are VPONs on the fog nodes, calculates their power consumption
  for i in range(fogs):
    if graph["fog_bridge{}".format(i)]["fog{}".format(i)]["capacity"] > 0:
      bandwidth_power += (graph["fog_bridge{}".format(i)]["fog{}".format(i)]["capacity"] / 9824) * line_card_consumption
  return bandwidth_power

#sort fog nodes by Most Loaded
def sortFogMostLoaded():
 most_loaded = sorted(load_node,key=load_node.__getitem__)
 most_loaded.reverse()
 return most_loaded

#sort fog nodes by Least Loaded
def sortFogLeastLoaded():
 least_loaded = sorted(load_node,key=load_node.__getitem__)
 return least_loaded

#get all incoming traffic
def getIncomingTraffic():
  return cpri_line * (len(actives_rrhs))

#get all transmitted traffic from source to destination
def getTransmittedTraffic(mincostFlow):
  transmitted = 0.0
  transmitted += mincostFlow["cloud"]["d"]
  for i in range(fogs):
    transmitted += mincostFlow["fog{}".format(i)]["d"]
  return transmitted

#get the blocking probability of each executed max flow min cost
def getBlockingProbability(mincostFlow):
  lost_traffic = (len(actives_rrhs)*cpri_line) - getTransmittedTraffic(mincostFlow)
  blocking_probability = lost_traffic/(len(actives_rrhs)*cpri_line)
  return blocking_probability

#verify if there were traffic that could not be allocated to a node
def getTrafficLost(mincostFlow):
  lost_traffic = 0.0
  lost_traffic = (len(actives_rrhs)*cpri_line) - getTransmittedTraffic(mincostFlow)
  return lost_traffic
#testes
'''
g = createGraph()
createRRHs()
#for i in rrhs:
#  print(i.id)
addFogNodes(g, 5)
addRRHs(g, 0, 5, "0")
addRRHs(g, 5, 10, "1")
addRRHs(g, 10, 15, "2")
#addRRHs(g, 5, 10, "1")
#addRRHs(g, 10, 15, "2")
#addRRHs(g, 15, 20, "3")
for i in range(len(rrhs)):
  startNode(g, "RRH{}".format(i))
  actives_rrhs.append("RRH{}".format(i))
#for i in range(len(rrhs)):
#  print(g["s"]["RRH{}".format(i)]["capacity"])
assignVPON(g)
#print(g["bridge"]["cloud"]["capacity"])
#g["bridge"]["cloud"]["capacity"] = 20000.0
#print([i for i in nx.edges(g)])
#G["s"]["RRH0"]["capacity"] = 10
#print(G["s"])
#startNode(G, "RRH11")
start_time = time.clock()
mincostFlow = nx.max_flow_min_cost(g, "s", "d")
#print(mincostFlow)
#print(mincostFlow["cloud"]["d"])
#for i in mincostFlow:
#  print(i, mincostFlow[i])
print("Time lapsed: {}".format(time.clock() - start_time))
for i in range(len(rrhs)):
  getProcessingNodes(g, mincostFlow, "RRH{}".format(i))
activatedFogRRHs(g)
updateRatio()
print(fog_activated_rrhs)
print(getLeastActivatedRRHsFog(g))
updateRatio()
print(nodes_ratio_cost_rrhs)
#sort = sorted(load_node,key=load_node.__getitem__)
#sort.reverse()
#print(sort)
#print(load_node)
#print(sortFogMostLoaded())
#print(sortFogLeastLoaded())
#print(getTransmittedTraffic(mincostFlow))
#print(getBlockingProbability(mincostFlow))
#print(getTrafficLost(mincostFlow))
#print(getFogBridge(g, "fog1"))


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
