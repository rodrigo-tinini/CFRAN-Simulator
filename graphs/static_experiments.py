import importlib
import simpy
import functools
import random
import time
from enum import Enum
import numpy as np
from scipy.stats import norm
import scipy as sp
import scipy.stats
import matplotlib.pyplot as plt
import copy
import graph as g

#log variables
power_consumption = []
execution_time = []

#Assign VPON Heuristic simulations
#add 5 rrhs per execution
#5 rrhs
g.rrhs_amount = 5
#fog nodes amount
gp = g.createGraph()
g.createRRHs()
print(len(g.rrhs))
#for i in rrhs:
#  print(i.id)
g.addFogNodes(gp, 5)
g.addRRHs(gp, 0, 1, "0")
g.addRRHs(gp, 1, 2, "1")
g.addRRHs(gp, 2, 3, "2")
g.addRRHs(gp, 3, 4, "3")
g.addRRHs(gp, 4, 5, "4")
#turn the rrhs on
for i in range(len(g.rrhs)):
	g.startNode(gp, "RRH{}".format(i))
	g.actives_rrhs.append("RRH{}".format(i))
#for i in range(len(g.rrhs)):
#	print(gp["s"]["RRH{}".format(i)]["capacity"])
g.assignVPON(gp)
start_time = g.time.clock()
mincostFlow = g.nx.max_flow_min_cost(gp, "s", "d")
execution_time.append(g.time.clock() - start_time)
power_consumption.append(g.overallPowerConsumption(gp))
importlib.reload(g)

#10 rrhs
g.rrhs_amount = 10
#fog nodes amount
gp = g.createGraph()
g.createRRHs()
print(len(g.rrhs))
#for i in rrhs:
#  print(i.id)
g.addFogNodes(gp, 5)
g.addRRHs(gp, 0, 2, "0")
g.addRRHs(gp, 2, 4, "1")
g.addRRHs(gp, 4, 6, "2")
g.addRRHs(gp, 6, 8, "3")
g.addRRHs(gp, 8, 10, "4")
#turn the rrhs on
for i in range(len(g.rrhs)):
  g.startNode(gp, "RRH{}".format(i))
  g.actives_rrhs.append("RRH{}".format(i))
#for i in range(len(g.rrhs)):
#	print(gp["s"]["RRH{}".format(i)]["capacity"])
g.assignVPON(gp)
start_time = g.time.clock()
mincostFlow = g.nx.max_flow_min_cost(gp, "s", "d")
execution_time.append(g.time.clock() - start_time)
power_consumption.append(g.overallPowerConsumption(gp))
importlib.reload(g)

#15 rrhs
g.rrhs_amount = 15
#fog nodes amount
gp = g.createGraph()
g.createRRHs()
print(len(g.rrhs))
#for i in rrhs:
#  print(i.id)
g.addFogNodes(gp, 5)
g.addRRHs(gp, 0, 3, "0")
g.addRRHs(gp, 3, 6, "1")
g.addRRHs(gp, 6, 9, "2")
g.addRRHs(gp, 9, 12, "3")
g.addRRHs(gp, 12, 15, "4")
#turn the rrhs on
for i in range(len(g.rrhs)):
  g.startNode(gp, "RRH{}".format(i))
  g.actives_rrhs.append("RRH{}".format(i))
#for i in range(len(g.rrhs)):
#	print(gp["s"]["RRH{}".format(i)]["capacity"])
g.assignVPON(gp)
start_time = g.time.clock()
mincostFlow = g.nx.max_flow_min_cost(gp, "s", "d")
execution_time.append(g.time.clock() - start_time)
power_consumption.append(g.overallPowerConsumption(gp))
importlib.reload(g)

#20 rrhs
g.rrhs_amount = 20
#fog nodes amount
gp = g.createGraph()
g.createRRHs()
print(len(g.rrhs))
#for i in rrhs:
#  print(i.id)
g.addFogNodes(gp, 5)
g.addRRHs(gp, 0, 4, "0")
g.addRRHs(gp, 4, 8, "1")
g.addRRHs(gp, 8, 12, "2")
g.addRRHs(gp, 12, 16, "3")
g.addRRHs(gp, 16, 20, "4")
#turn the rrhs on
for i in range(len(g.rrhs)):
  g.startNode(gp, "RRH{}".format(i))
  g.actives_rrhs.append("RRH{}".format(i))
#for i in range(len(g.rrhs)):
#	print(gp["s"]["RRH{}".format(i)]["capacity"])
g.assignVPON(gp)
start_time = g.time.clock()
mincostFlow = g.nx.max_flow_min_cost(gp, "s", "d")
execution_time.append(g.time.clock() - start_time)
power_consumption.append(g.overallPowerConsumption(gp))
importlib.reload(g)

#25 rrhs
g.rrhs_amount = 25
#fog nodes amount
gp = g.createGraph()
g.createRRHs()
print(len(g.rrhs))
#for i in rrhs:
#  print(i.id)
g.addFogNodes(gp, 5)
g.addRRHs(gp, 0, 5, "0")
g.addRRHs(gp, 5, 10, "1")
g.addRRHs(gp, 10, 15, "2")
g.addRRHs(gp, 15, 20, "3")
g.addRRHs(gp, 20, 25, "4")
#turn the rrhs on
for i in range(len(g.rrhs)):
  g.startNode(gp, "RRH{}".format(i))
  g.actives_rrhs.append("RRH{}".format(i))
#for i in range(len(g.rrhs)):
#	print(gp["s"]["RRH{}".format(i)]["capacity"])
g.assignVPON(gp)
start_time = g.time.clock()
mincostFlow = g.nx.max_flow_min_cost(gp, "s", "d")
execution_time.append(g.time.clock() - start_time)
power_consumption.append(g.overallPowerConsumption(gp))
importlib.reload(g)

#30 rrhs
g.rrhs_amount = 30
#fog nodes amount
gp = g.createGraph()
g.createRRHs()
print(len(g.rrhs))
#for i in rrhs:
#  print(i.id)
g.addFogNodes(gp, 5)
g.addRRHs(gp, 0, 6, "0")
g.addRRHs(gp, 6, 12, "1")
g.addRRHs(gp, 12, 18, "2")
g.addRRHs(gp, 18, 24, "3")
g.addRRHs(gp, 24, 30, "4")
#turn the rrhs on
for i in range(len(g.rrhs)):
  g.startNode(gp, "RRH{}".format(i))
  g.actives_rrhs.append("RRH{}".format(i))
#for i in range(len(g.rrhs)):
#	print(gp["s"]["RRH{}".format(i)]["capacity"])
g.assignVPON(gp)
start_time = g.time.clock()
mincostFlow = g.nx.max_flow_min_cost(gp, "s", "d")
execution_time.append(g.time.clock() - start_time)
power_consumption.append(g.overallPowerConsumption(gp))
importlib.reload(g)

#35 rrhs
g.rrhs_amount = 35
#fog nodes amount
gp = g.createGraph()
g.createRRHs()
print(len(g.rrhs))
#for i in rrhs:
#  print(i.id)
g.addFogNodes(gp, 5)
g.addRRHs(gp, 0, 7, "0")
g.addRRHs(gp, 7, 14, "1")
g.addRRHs(gp, 14, 21, "2")
g.addRRHs(gp, 21, 28, "3")
g.addRRHs(gp, 28, 35, "4")
#turn the rrhs on
for i in range(len(g.rrhs)):
  g.startNode(gp, "RRH{}".format(i))
  g.actives_rrhs.append("RRH{}".format(i))
#for i in range(len(g.rrhs)):
#	print(gp["s"]["RRH{}".format(i)]["capacity"])
g.assignVPON(gp)
start_time = g.time.clock()
mincostFlow = g.nx.max_flow_min_cost(gp, "s", "d")
execution_time.append(g.time.clock() - start_time)
power_consumption.append(g.overallPowerConsumption(gp))
importlib.reload(g)

print(power_consumption)
print(execution_time)