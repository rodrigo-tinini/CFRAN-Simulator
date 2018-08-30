import networkx as nx
import matplotlib.pyplot as plt
import math
import time
import random

G = nx.DiGraph()
#number of RRHs
rrhs_amount = 160
#consumption of a line card + a DU
line_card_consumption = 20
#keeps the power cost
power_cost = 0
#cpri line rate - it is round to 614 because float 614.4 was unexplained causing no flow to be found (even with as free capacity as needed)
cpri_line = 614
#capacity of a vopn
lambda_capacity = 16 * cpri_line
#fog capacity
fog_capacity = 30 * cpri_line
#cloud capacity
cloud_capacity = 159 *cpri_line
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
available_vpons = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19]
#available_vpons = [0,1,2,3,4,5,6,7,8,9]
#list of allocated vpons
allocated_vpons = []
#capacity of vpons
vpons_capacity = {}
for i in range(20):
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
#keeps the ratio between activated nodes and available bandwidth for the fog nodes
fog_nodes_ratio_act_band = {}
for i in range(fogs):
  fog_nodes_ratio_act_band["fog{}".format(i)] = 0.0
#keeps the delay costs of each processing node
#considering a propagation time of 2*10^8 m/s and a core of mm 50µm
fog_delay = 0.0000980654
cloud_delay = 0.0001961308
delay_costs = {}
delay_costs["cloud"] = cloud_delay
for i in range(fogs):
  delay_costs["fog{}".format(i)] = fog_delay
#keeps the cloud and fog links to random VPON assignment
random_nodes = []
random_nodes.append("cloud")
for i in range(fogs):
  random_nodes.append("fog{}".format(i))

#rrh
class RRH(object):
    def __init__(self, cpri_line, rrhId):
        self.cpri_line = cpri_line
        self.id = "RRH{}".format(rrhId)

#update the ratio between activate nodes and available link band
def updateActRatio(graph):
  for i in range(fogs):
    #if the fog node has active RRHs but no midhaul bandwidth, put a infinity value to it
    if fog_activated_rrhs[getFogBridge(graph, "fog{}".format(i))] > 0 and getFogBandwidth(graph, "fog{}".format(i)) == 0:
      fog_nodes_ratio_act_band["fog{}".format(i)] = float("inf")
    elif fog_activated_rrhs[getFogBridge(graph, "fog{}".format(i))] == 0 and getFogBandwidth(graph, "fog{}".format(i)) == 0:
      fog_nodes_ratio_act_band["fog{}".format(i)] = 0
    else:
      node_ratio = fog_activated_rrhs[getFogBridge(graph, "fog{}".format(i))]/getFogBandwidth(graph, "fog{}".format(i))
      fog_nodes_ratio_act_band["fog{}".format(i)] = node_ratio

#get the biggest loaded node in function of the ratio between activated nodes and available bandwidth
def getBigActBandRatio():
  big_ratio = sorted(fog_nodes_ratio_act_band, key = fog_nodes_ratio_act_band.__getitem__)
  return big_ratio

#get the smallest loaded node in function of the ratio between activated nodes and available bandwidth
def getSmallActBandRatio():
  small_ratio = sorted(fog_nodes_ratio_act_band, key = fog_nodes_ratio_act_band.__getitem__)
  small_ratio.reverse()
  return small_ratio

##############################################################################################################################################
#HEURISTICS

#cloud first and fog on sort of the nodes with greatest ratio between activated RRHs and available midhaul bandwidth
def assignBigRatioVPON(graph):
  updateActRatio(graph)
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
      pass
  elif traffic > graph["cloud"]["d"]["capacity"]:
    if available_vpons:
      #print("Putting VPONs on Fronthaul and Fog")
      #calculate the amount necessary on VPONs and put the maximum on the cloud and the rest on the fogs
      num_vpons = 0
      num_vpons = math.ceil(traffic/lambda_capacity)
      while graph["bridge"]["cloud"]["capacity"] < graph["cloud"]["d"]["capacity"] :
        if available_vpons:
          graph["bridge"]["cloud"]["capacity"] += 9824
          cloud_vpons.append(available_vpons.pop())
          num_vpons -= 1
        else:
            print("No VPON available!")
      #calculate the total available bandwidth
      total_bd = getTotalBandwidth(graph)
      #First-Fit Fog VPON Allocation - When there is VPON and traffic is greater than the total available bandwidth, put it on the next Fog Node
      #place VPONs on fogs following least-activated RRHs order
      big_ratio_fogs = getBigActBandRatio()
      #print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
      #print("Actives {}".format(fog_activated_rrhs))
      #print("Ratio {}".format(fog_nodes_ratio_act_band))
      #print("Fogs {}".format(big_ratio_fogs))
      while traffic > total_bd:
        if available_vpons:
          fog = big_ratio_fogs.pop()
          #print("Took {}".format(fog))
          bridge = getFogBridge(graph, fog)
          if graph[bridge][fog]["capacity"] < graph[fog]["d"]["capacity"]:
            graph[bridge][fog]["capacity"] += 9824
            fogs_vpons[fog].append(available_vpons.pop())
            num_vpons -= 1
            total_bd = getTotalBandwidth(graph)
        else:
              print("No VPON available!")
    #else: print('No available VPONs')
  #return traffic
  #print(fog_nodes_ratio_act_band)
  #print("Cloud VPONs: {}".format(cloud_vpons))
  #print("Fogs VPONs: {}".format(fogs_vpons))
  #print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")

#cloud first and fog on sort of the nodes with greatest ratio between activated RRHs and available midhaul bandwidth
def assignSmallRatioVPON(graph):
  updateActRatio(graph)
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
      pass
  elif traffic > graph["cloud"]["d"]["capacity"]:
    if available_vpons:
      #print("Putting VPONs on Fronthaul and Fog")
      #calculate the amount necessary on VPONs and put the maximum on the cloud and the rest on the fogs
      num_vpons = 0
      num_vpons = math.ceil(traffic/lambda_capacity)
      while graph["bridge"]["cloud"]["capacity"] < graph["cloud"]["d"]["capacity"] :
        if available_vpons:
          graph["bridge"]["cloud"]["capacity"] += 9824
          cloud_vpons.append(available_vpons.pop())
          num_vpons -= 1
        else:
            print("No VPON available!")
      #calculate the total available bandwidth
      total_bd = getTotalBandwidth(graph)
      #First-Fit Fog VPON Allocation - When there is VPON and traffic is greater than the total available bandwidth, put it on the next Fog Node
      #place VPONs on fogs following least-activated RRHs order
      small_ratio_fogs = getSmallActBandRatio()
      #print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
      #print("Actives {}".format(fog_activated_rrhs))
      #print("Ratio {}".format(fog_nodes_ratio_act_band))
      #print("Fogs {}".format(small_ratio_fogs))
      while traffic > total_bd:
        if available_vpons:
          fog = small_ratio_fogs.pop()
          #print("Took {}".format(fog))
          bridge = getFogBridge(graph, fog)
          if graph[bridge][fog]["capacity"] < graph[fog]["d"]["capacity"]:
            graph[bridge][fog]["capacity"] += 9824
            fogs_vpons[fog].append(available_vpons.pop())
            num_vpons -= 1
            total_bd = getTotalBandwidth(graph)
        else:
              print("No VPON available!")
    #else: print('No available VPONs')
  #return traffic
  #print(fog_nodes_ratio_act_band)
  #print("Cloud VPONs: {}".format(cloud_vpons))
  #print("Fogs VPONs: {}".format(fogs_vpons))
  #print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")

##############################################################################################################################################

#gets a random node
def getRandomNode():
  return random_nodes[random.choice(range(len(random_nodes)))]

#get the fog from RRHs connected bridge
def getBridgeFog(graph, bridge):
  return next(iter(graph[bridge]))


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
#Totally random heuristic
def allRandomVPON(graph):
  #take the traffic, calculate how many VPONs are necessary and random allocate them on the links of the network
  traffic = getIncomingTraffic()
  total_bd = getTotalBandwidth(graph)
  while traffic > total_bd:
    #print("INFINITE LOOP ALLLL")
    #random get a processing node
    node = getRandomNode()
    if node == "cloud":
      if available_vpons:
        graph["bridge"][node]["capacity"] += 9824
        cloud_vpons.append(available_vpons.pop())
        total_bd = getTotalBandwidth(graph)
      else:
        break
        #print("PUT VPON IN CLOUD")
    else:
      bridge = getFogBridge(graph, node)
      if available_vpons:
        graph[bridge][node]["capacity"] += 9824
        fogs_vpons[node].append(available_vpons.pop())
        total_bd = getTotalBandwidth(graph)
      else:
        break
        #print("PUT VPON IN {}".format(node))
  #print("Cloud VPONs: {}".format(cloud_vpons))
  #print("Fogs VPONs: {}".format(fogs_vpons))

#Totally random remove VPONs
def randomRemoveVPONs(graph):
  #gets the traffic
  traffic = getIncomingTraffic()
  total_bd = getTotalBandwidth(graph)
  need_vpons = math.ceil(traffic/lambda_capacity)
  current_vpons = round(total_bd/lambda_capacity)
  #now, removes the VPONs until the available bandwidth is equal to
  while current_vpons > need_vpons:
    #print("Try to remove")
    node = getRandomNode()
    if node == "cloud":
      if graph["bridge"]["cloud"]["capacity"] > 0:
        graph["bridge"]["cloud"]["capacity"] -= 9824
        available_vpons.append(cloud_vpons.pop())
        total_bd = getTotalBandwidth(graph)
        current_vpons = round(total_bd/lambda_capacity)
        #print("Removing {}".format(node))
    else:
      bridge = getFogBridge(graph, node)
      if graph[bridge][node]["capacity"] > 0:
        graph[bridge][node]["capacity"] -= 9824
        available_vpons.append(fogs_vpons[node].pop())
        total_bd = getTotalBandwidth(graph)
        current_vpons = round(total_bd/lambda_capacity)
        #print("Removing {}".format(node))

#Fog-First heuristic - Put one VPON per fog first and, if the fogs capacities are exhausted, put other VPONs on the cloud
def fogFirst(graph):
  traffic = 0
  #calculate the total incoming traffic
  traffic = len(actives_rrhs) * cpri_line
  #calculate the amount necessary on VPONs and put the maximum on the cloud and the rest on the fogs
  num_vpons = 0
  num_vpons = math.ceil(traffic/lambda_capacity)
  #check each fog node and put VPON on it if it has traffic - Use the cloud only when the fog is exhausted
  for i in range(fogs):
    fog_traffic = getRRHsFogLoad(graph, "fog{}".format(i))
    #print("FT {}".format(fog_traffic))
    if (fog_traffic > 0 and fog_traffic > graph[getFogBridge(graph, "fog{}".format(i))]["fog{}".format(i)]["capacity"] 
      and graph[getFogBridge(graph, "fog{}".format(i))]["fog{}".format(i)]["capacity"] < graph["fog{}".format(i)]["d"]["capacity"]) :
      #print("AQUIII")
      if available_vpons:
        graph[getFogBridge(graph, "fog{}".format(i))]["fog{}".format(i)]["capacity"] += 9824
        num_vpons -= 1
        fogs_vpons["fog{}".format(i)].append(available_vpons.pop())
      else:
        print("No VPON available")
  total_bd = getTotalBandwidth(graph)
  #print("TOTAL BD {}".format(total_bd))
  while traffic > total_bd:
    if available_vpons:
      if graph["bridge"]["cloud"]["capacity"] < graph["cloud"]["d"]["capacity"]:
        graph["bridge"]["cloud"]["capacity"] += 9824
        cloud_vpons.append(available_vpons.pop())
        num_vpons -= 1
        total_bd = getTotalBandwidth(graph)
  #print("Cloud VPONs: {}".format(cloud_vpons))
  #print("Fogs VPONs: {}".format(fogs_vpons))

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
      #calculate the amount necessary on VPONs and put the maximum on the cloud and the rest on the fogs
      num_vpons = 0
      num_vpons = math.ceil(traffic/lambda_capacity)
      #print("Putting VPONs on Fronthaul and Fog")
      if graph["bridge"]["cloud"]["capacity"] < graph["cloud"]["d"]["capacity"]:
        while graph["bridge"]["cloud"]["capacity"] < graph["cloud"]["d"]["capacity"] :
          if available_vpons:
            graph["bridge"]["cloud"]["capacity"] += 9824
            cloud_vpons.append(available_vpons.pop())
            num_vpons -= 1
          else:
              print("No VPON available!")
      #Random Fog VPON Allocation - When there is VPON and traffic is greater than the total available bandwidth, put it on a random fog node
      #calculate the total available bandwidth
      total_bd = getTotalBandwidth(graph)
      #First-Fit Fog VPON Allocation - When there is VPON and traffic is greater than the total available bandwidth, put it on the next Fog Node
      #take a list of the fog nodes (using getMostActivatedRRHsFog method, but as I am going to take a random fog, this method or the most loaded fog does not make difference)
      least_fogs = getMostActivatedRRHsFog()
      #print("TRAFFIC IS {} TOTAL BD IS {}".format(traffic,total_bd))
      while traffic > total_bd:
        if available_vpons:
          #choose a random fog node
          bridge = least_fogs[random.choice(range(len(least_fogs)))]
          fog = getBridgeFog(graph, bridge)
          #print(least_fogs)
          #print(fog)
          graph[bridge][fog]["capacity"] += 9824
          fogs_vpons[fog].append(available_vpons.pop())
          num_vpons -= 1
          total_bd = getTotalBandwidth(graph)
        else:
              print("No VPON available!")
  #print("Cloud VPONs: {}".format(cloud_vpons))
  #print("Fogs VPONs: {}".format(fogs_vpons))

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
      #calculate the amount necessary on VPONs and put the maximum on the cloud and the rest on the fogs
      num_vpons = 0
      num_vpons = math.ceil(traffic/lambda_capacity)
      while graph["bridge"]["cloud"]["capacity"] < graph["cloud"]["d"]["capacity"] :
        if available_vpons:
          graph["bridge"]["cloud"]["capacity"] += 9824
          cloud_vpons.append(available_vpons.pop())
          num_vpons -= 1
        else:
            print("No VPON available!")
      #First-Fit Fog VPON Allocation - When there is VPON and traffic is greater than the total available bandwidth, put it on the next Fog Node
      while available_vpons:
        for i in range(fogs):#this is the First-Fit Fog VPON Allocation
          if available_vpons:
            graph["fog_bridge{}".format(i)]["fog{}".format(i)]["capacity"] += 9824 
            fogs_vpons["fog{}".format(i)].append(available_vpons.pop())
            num_vpons -= 1
          else:
              print("No VPON available!")
    #else: print('No available VPONs')
  #return traffic
  #print("Cloud VPONs: {}".format(cloud_vpons))
  #print("Fogs VPONs: {}".format(fogs_vpons))

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
      pass
  elif traffic > graph["cloud"]["d"]["capacity"]:
    if available_vpons:
      #print("Putting VPONs on Fronthaul and Fog")
      #calculate the amount necessary on VPONs and put the maximum on the cloud and the rest on the fogs
      num_vpons = 0
      num_vpons = math.ceil(traffic/lambda_capacity)
      while graph["bridge"]["cloud"]["capacity"] < graph["cloud"]["d"]["capacity"] :
        if available_vpons:
          graph["bridge"]["cloud"]["capacity"] += 9824
          cloud_vpons.append(available_vpons.pop())
          num_vpons -= 1
        else:
            print("No VPON available!")
      #calculate the total available bandwidth
      total_bd = getTotalBandwidth(graph)
      #First-Fit Fog VPON Allocation - When there is VPON and traffic is greater than the total available bandwidth, put it on the next Fog Node
      #place VPONs on fogs following least-activated RRHs order
      least_fogs = getMostActivatedRRHsFog()
      while traffic > total_bd:
        if available_vpons:
          bridge = least_fogs.pop()
          fog = getBridgeFog(graph, bridge)
          graph[bridge][fog]["capacity"] += 9824
          fogs_vpons[fog].append(available_vpons.pop())
          num_vpons -= 1
          total_bd = getTotalBandwidth(graph)
        else:
              print("No VPON available!")
    #else: print('No available VPONs')
  #return traffic
  #print("Cloud VPONs: {}".format(cloud_vpons))
  #print("Fogs VPONs: {}".format(fogs_vpons))

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
      #print("Putting VPONs on Fronthaul and Fog")
      #calculate the amount necessary on VPONs and put the maximum on the cloud and the rest on the fogs
      num_vpons = 0
      num_vpons = math.ceil(traffic/lambda_capacity)
      while graph["bridge"]["cloud"]["capacity"] < graph["cloud"]["d"]["capacity"] :
        if available_vpons:
          graph["bridge"]["cloud"]["capacity"] += 9824
          cloud_vpons.append(available_vpons.pop())
          num_vpons -= 1
        else:
            print("No VPON available!")
      #calculate the total available bandwidth
      total_bd = getTotalBandwidth(graph)
      #First-Fit Fog VPON Allocation - When there is VPON and traffic is greater than the total available bandwidth, put it on the next Fog Node
      #place VPONs on fogs following least-activated RRHs order
      least_fogs = getLeastActivatedRRHsFog()
      while traffic > total_bd:
        if available_vpons:
          bridge = least_fogs.pop()
          fog = getBridgeFog(graph, bridge)
          graph[bridge][fog]["capacity"] += 9824
          fogs_vpons[fog].append(available_vpons.pop())
          num_vpons -= 1
          total_bd = getTotalBandwidth(graph)
        else:
              print("No VPON available!")
  #print("Cloud VPONs: {}".format(cloud_vpons))
  #print("Fogs VPONs: {}".format(fogs_vpons))
    #else: print('No available VPONs')
  #return traffic

################################################################################################################

#get the load of the activated RRHs on a fog
def getRRHsFogLoad(graph, fog):
  fog_load = fog_activated_rrhs[getFogBridge(graph, fog)]
  return fog_load * cpri_line

#get the fog's available bandwidth
def getFogBandwidth(graph, fog):
  return graph[getFogBridge(graph, fog)][fog]["capacity"]

#get the fronthaul bandwidth
def getFronthaulBandwidth(graph):
  return graph["bridge"]["cloud"]["capacity"]

#get the total bandwidth of the fog nodes
def getMidhaulBandiwdth(graph):
  midhaul_band = {}
  for i in range(fogs):
    midhaul_band["fog{}".format(i)] = graph[getFogBridge(graph, "fog{}".format(i))]["fog{}".format(i)]["capacity"]
  return midhaul_band

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
  least_cost.reverse()
  return least_cost

#sort and get nodes sorted by least ratio between node cost and activated RRHs
def getLeastActCost():
  least_cost = sorted(nodes_ratio_cost_rrhs, key = nodes_ratio_cost_rrhs.__getitem__)
  return least_cost

#The following heuristic puts the VPONs on the least cost node, regardless if it is the cloud or the fogs
#it sorts the nodes in ascending order of costs and then assign the VPONs until the demanded traffic is less or equal than the available bandwidth
def leastCostNodeVPON(graph):
  updateRatio()
  least_cost = getLeastCostNodes()
  traffic = getIncomingTraffic()
  total_bd = getTotalBandwidth(graph)
  #verify if there is the need for VPONs to support the traffic demand
  num_vpons = 0
  num_vpons = math.ceil(traffic/lambda_capacity)
  while traffic > total_bd:
    #print("TRAFFIC IS {} TOTAL BD IS {}".format(traffic,total_bd))
    if available_vpons:
      fog = least_cost.pop()
      bridge = getFogBridge(graph, fog)
      if fog == "cloud":
        if graph["bridge"]["cloud"]["capacity"] < graph["cloud"]["d"]["capacity"]:
          graph["bridge"]["cloud"]["capacity"] += 9824
          cloud_vpons.append(available_vpons.pop())
          num_vpons -= 1
          total_bd = getTotalBandwidth(graph)
      else: # it is a fog node
        #print(graph[bridge][fog]["capacity"])
        #print(graph[fog]["d"]["capacity"])
        if graph[bridge][fog]["capacity"] < graph[fog]["d"]["capacity"]:
          graph[bridge][fog]["capacity"] += 9824
          fogs_vpons[fog].append(available_vpons.pop())
          num_vpons -= 1
          total_bd = getTotalBandwidth(graph)
          #print("PUT VPON ON FOG and NOW TRAFFIC IS {} TOTAL BD IS {}".format(traffic,total_bd))
      total_bd = getTotalBandwidth(graph)
  #print("Cloud VPONs: {}".format(cloud_vpons))
  #print("Fogs VPONs: {}".format(fogs_vpons))



#The following heuristic puts the VPONs on the least cost node order, considering the ratio between cost and actives RRHs connected to it
#It also re-assign VPONs if the costs changes or if the number of active RRHs on each fog node changes
def leastCostLoadedVPON(graph):
  least_cost = getLeastActCost()
  traffic = getIncomingTraffic()
  total_bd = getTotalBandwidth(graph)
  #verify if there is the need for VPONs to support the traffic demand
  num_vpons = 0
  num_vpons = math.ceil(traffic/lambda_capacity)
  while traffic > total_bd:
    #print("TRAFFIC IS {} TOTAL BD IS {}".format(traffic,total_bd))
    if available_vpons:
      fog = least_cost.pop()
      bridge = getFogBridge(graph, fog)
      if fog == "cloud":
        if graph["bridge"]["cloud"]["capacity"] < graph["cloud"]["d"]["capacity"]:
          graph["bridge"]["cloud"]["capacity"] += 9824
          cloud_vpons.append(available_vpons.pop())
          num_vpons -= 1
          total_bd = getTotalBandwidth(graph)
      else: # it is a fog node
        #print(graph[bridge][fog]["capacity"])
        #print(graph[fog]["d"]["capacity"])
        if graph[bridge][fog]["capacity"] < graph[fog]["d"]["capacity"]:
          graph[bridge][fog]["capacity"] += 9824
          fogs_vpons[fog].append(available_vpons.pop())
          num_vpons -= 1
          total_bd = getTotalBandwidth(graph)
          #print("PUT VPON ON FOG and NOW TRAFFIC IS {} TOTAL BD IS {}".format(traffic,total_bd))
      total_bd = getTotalBandwidth(graph)
  #print("Cloud VPONs: {}".format(cloud_vpons))
  #print("Fogs VPONs: {}".format(fogs_vpons))

  #Versions of Least and Most loaded heuristics that considers the bandwidth on each fog node
  #Most-Loaded Fog VPON Allocation
def assignMostLoadedVPONBand(graph):
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
      pass
  elif traffic > graph["cloud"]["d"]["capacity"]:
    if available_vpons:
      #print("Putting VPONs on Fronthaul and Fog")
      #calculate the amount necessary on VPONs and put the maximum on the cloud and the rest on the fogs
      num_vpons = 0
      num_vpons = math.ceil(traffic/lambda_capacity)
      while graph["bridge"]["cloud"]["capacity"] < graph["cloud"]["d"]["capacity"] :
        if available_vpons:
          graph["bridge"]["cloud"]["capacity"] += 9824
          cloud_vpons.append(available_vpons.pop())
          num_vpons -= 1
        else:
            print("No VPON available!")
      #calculate the total available bandwidth
      total_bd = getTotalBandwidth(graph)
      #First-Fit Fog VPON Allocation - When there is VPON and traffic is greater than the total available bandwidth, put it on the next Fog Node
      #place VPONs on fogs following least-activated RRHs order
      least_fogs = getMostActivatedRRHsFog()
      while traffic > total_bd:
        if available_vpons:
          bridge = least_fogs.pop()
          fog = getBridgeFog(graph, bridge)
          if graph[bridge][fog]["capacity"] < graph[fog]["d"]["capacity"]:
            graph[bridge][fog]["capacity"] += 9824
            fogs_vpons[fog].append(available_vpons.pop())
            num_vpons -= 1
            total_bd = getTotalBandwidth(graph)
        else:
              print("No VPON available!")
    #else: print('No available VPONs')
  #return traffic
  #print("Cloud VPONs: {}".format(cloud_vpons))
  #print("Fogs VPONs: {}".format(fogs_vpons))

#Cloud-First and Least-Loaded Fog VPON Allocation
def assignLeastLoadedVPONBand(graph):
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
      pass
  elif traffic > graph["cloud"]["d"]["capacity"]:
    if available_vpons:
      #print("Putting VPONs on Fronthaul and Fog")
      #calculate the amount necessary on VPONs and put the maximum on the cloud and the rest on the fogs
      num_vpons = 0
      num_vpons = math.ceil(traffic/lambda_capacity)
      while graph["bridge"]["cloud"]["capacity"] < graph["cloud"]["d"]["capacity"] :
        if available_vpons:
          graph["bridge"]["cloud"]["capacity"] += 9824
          cloud_vpons.append(available_vpons.pop())
          num_vpons -= 1
        else:
            print("No VPON available!")
      #calculate the total available bandwidth
      total_bd = getTotalBandwidth(graph)
      #First-Fit Fog VPON Allocation - When there is VPON and traffic is greater than the total available bandwidth, put it on the next Fog Node
      #place VPONs on fogs following least-activated RRHs order
      least_fogs = getLeastActivatedRRHsFog()
      while traffic > total_bd:
        if available_vpons:
          bridge = least_fogs.pop()
          fog = getBridgeFog(graph, bridge)
          if graph[bridge][fog]["capacity"] < graph[fog]["d"]["capacity"]:
            graph[bridge][fog]["capacity"] += 9824
            fogs_vpons[fog].append(available_vpons.pop())
            num_vpons -= 1
            total_bd = getTotalBandwidth(graph)
        else:
              print("No VPON available!")
  #print("Cloud VPONs: {}".format(cloud_vpons))
  #print("Fogs VPONs: {}".format(fogs_vpons))
    #else: print('No available VPONs')
  #return traffic

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
          #print("Poping")
          available_vpons.append(fogs_vpons["fog{}".format(i)].pop())
    #release the VPONs of the fronthaul until only the necessary to support current traffic is reached
    num_vpons = 0
    num_vpons = (math.ceil(traffic/lambda_capacity))*9824
    while graph["bridge"]["cloud"]["capacity"] > num_vpons:
      #print("Releasing the cloud")
      graph["bridge"]["cloud"]["capacity"] -= 9824
      available_vpons.append(cloud_vpons.pop())

#remove unnecessary bandwidth first from the cloud and then from the fog nodes - The name of thhis method refers to the name of heuristic fog first
#This method is specific for the Fog First VPON assignment heuristic, as this heuristic considers only 1 vpon per fog node
#so, for another more sophisticated fog first heuristic, a new remove method must be created
def removeFogFirstVPON(graph):
  #get the bandwidth available on midhaul
  traffic = getIncomingTraffic()
  midhaul_bd = 0.0
  md = getMidhaulBandiwdth(graph)
  for i in range(fogs):
    midhaul_bd += md["fog{}".format(i)]
  #check if the midhaul can handle the traffic
  if traffic <= midhaul_bd:
    #turn the VPONs of cloud off
    while graph["bridge"]["cloud"]["capacity"] > 0:
      graph["bridge"]["cloud"]["capacity"] -= 9824
      available_vpons.append(cloud_vpons.pop())
      #print("CLEANING CLOUD")
  #now, check if some fog node must be turned off
  for i in range(fogs):
    fog_traffic = getRRHsFogLoad(graph, "fog{}".format(i))
    if fog_traffic == 0 and graph[getFogBridge(graph, "fog{}".format(i))]["fog{}".format(i)]["capacity"] > 0:
      #print("CLEANING FOG{}".format(i))
      graph[getFogBridge(graph, "fog{}".format(i))]["fog{}".format(i)]["capacity"] = 0
      available_vpons.append(fogs_vpons["fog{}".format(i)].pop())

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
    #print("Inserted on fog")
    return True
  elif mincostFlow[rrh]["bridge"] != 0:
    update_node_load("cloud", cpri_line)
    rrhs_proc_node[rrh] = "cloud"
    #print("Inserted on cloud")
    return True
  else:
    return False
  #print(mincostFlow[actives_rrhs[i]]["bridge"])

#get the amount of activated RRHs on each fog node
def activatedFogRRHs():
  return fog_activated_rrhs

##get the amount of activated RRHs on each fog node
def static_activatedFogRRHs(graph):#it sums the number of actives rrhs per fog
  #verify the RRHs that are
  for i in range(len(rrhs)):
    if graph["s"]["RRH{}".format(i)]["capacity"] != 0:
      fog_activated_rrhs[rrhs_fog["RRH{}".format(i)]] += 1
  return fog_activated_rrhs

#sort the fogs from ascendenting number of activated RRHs
def getLeastActivatedRRHsFog():
  activated = activatedFogRRHs()
  activated_sorted = sorted(activated, key = activated.__getitem__)
  activated_sorted.reverse()
  return activated_sorted

#sort the fogs from descendenting number of activated RRHs
def getMostActivatedRRHsFog():
  activated = activatedFogRRHs()
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

#calculate the power consumption considering as active every node that has a VPON assigned, regardless if it is transmitting traffic or not
def overallPowerConsumption(graph):
  power_cost = 0.0
  if graph["bridge"]["cloud"]["capacity"] > 0:
    power_cost += costs["cloud"]
  for i in range(fogs):
    if graph["fog_bridge{}".format(i)]["fog{}".format(i)]["capacity"] > 0:
      power_cost += costs["fog{}".format(i)]
  power_cost += getBandwidthPower(graph)
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

#OLD version that takes the average of delay considering the amount of RRHs that generates delay, i.e., are transmitting
#calculate the average delay of the network, counting for each RRH its transmission delay considering its processing node
def OLDoverallDelay(graph):
  total_delay = 0.0
  average_delay = 0.0
  #keep the number of transmitting RRHs to calculate the average delay
  amount = 0
  for i in rrhs_amount:
    if graph["RRH{}".format(i)]["bridge"]["capacity"] > 0:
      total_delay += cloud_delay
      amount += 1
    elif graph["RRH{}".format(i)][rrhs_fog["RRH{}".format(i)]]["capacity"] > 0:
      total_delay = fog_delay
      amount += 1
  if amount > 0:
    average_delay = total_delay/amount
  return average_delay

#calculates the average minimum delay on the network, taking in consider only the delay of the active nodes
def overallDelay(graph):
  total_delay = 0.0
  amount = 0
  if graph["bridge"]["cloud"]["capacity"] > 0:
    total_delay += cloud_delay
    amount += 1
  for i in range(fogs):
    if graph["fog_bridge{}".format(i)]["fog{}".format(i)]["capacity"] > 0:
      total_delay += fog_delay
      amount += 1
  total_delay = (total_delay/amount)
  return total_delay

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
#print(getRandomNode())
g = createGraph()
createRRHs()
#for i in rrhs:
#  print(i.id)
addFogNodes(g, 5)
#addRRHs(g, 0, 5, "0")
#addRRHs(g, 5, 10, "1")
#addRRHs(g, 10, 15, "2")
#addRRHs(g, 5, 10, "1")
#addRRHs(g, 10, 15, "2")
#addRRHs(g, 15, 20, "3")
addRRHs(g, 0, 32, "0")
addRRHs(g, 32, 64, "1")
addRRHs(g, 64, 96, "2")
addRRHs(g, 96, 128, "3")
addRRHs(g, 128, 160, "4")



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
for i in mincostFlow:
  print(i, mincostFlow[i])

'''
'''
#for i in mincostFlow:
#  print(i, mincostFlow[i])
print("Time lapsed: {}".format(time.clock() - start_time))
for i in range(len(rrhs)):
  getProcessingNodes(g, mincostFlow, "RRH{}".format(i))
static_activatedFogRRHs(g)
updateRatio()
updateActRatio(g)
print(fog_nodes_ratio_act_band)
for i in range(fogs):
  print(getFogBandwidth(g, "fog{}".format(i)))
print(fog_activated_rrhs)
#print(getLeastActivatedRRHsFog())
#updateRatio()
#print(nodes_ratio_cost_rrhs)
#print(getBridgeFog(g, "fog_bridge0"))
#print(getFogBridge(g, getBridgeFog(g, "fog_bridge0")))
#print(getRRHsFogLoad(g, "fog1"))
#print(getFogBandwidth(g, "fog1"))
#print(getMidhaulBandiwdth(g))
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
print(overallPowerConsumption(g))

#old/first power consumption calculation I made for testing
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
