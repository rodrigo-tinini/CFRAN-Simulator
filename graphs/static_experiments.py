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

def genLogs():
	#iterate over each scheduling policy
	for i in sched_pol:
		#power consumption
		with open('/home/tinini/Área de Trabalho/iccSim/CFRAN-Simulator/graphs/static/logs/power_consumption_{}.txt'.format(g.rrhs_amount),'a') as filehandle:  
		    filehandle.write("{}\n\n".format(i))
		    filehandle.writelines("%s\n" % p for p in power_consumption["{}".format(i)])
		    filehandle.write("\n")
		    #filehandle.write("\n")
		with open('/home/tinini/Área de Trabalho/iccSim/CFRAN-Simulator/graphs/static/logs/execution_time_{}.txt'.format(g.rrhs_amount),'a') as filehandle:  
		    filehandle.write("{}\n\n".format(i))
		    filehandle.writelines("%s\n" % p for p in execution_time["{}".format(i)])
		    filehandle.write("\n")
		    #filehandle.write("\n")

#fog nodes amount
fog_amount = 5
#scheduling policies
sched_pol = []
sched_pol.append("all_random")
sched_pol.append("cloud_first_all_fogs")
sched_pol.append("cloud_first_random_fogs")
#sched_pol.append("fog_first")
sched_pol.append("most_loaded")
sched_pol.append("least_loaded")
#sched_pol.append("least_cost")
#sched_pol.append("least_cost_active_ratio")
#sched_pol.append("most_loaded_bandwidth")
#sched_pol.append("least_loaded_bandwidth")
#sched_pol.append("all_random")
#sched_pol.append("big_ratio")
#sched_pol.append("small_ratio")
#log variables
power_consumption = {}
execution_time = {}
average_delay = {}
for i in sched_pol:
	power_consumption["{}".format(i)] = []
	execution_time["{}".format(i)] = []

def setExperiment(gp, rrhs, fogs):
	divided = int(rrhs/fogs)
	g.addRRHs(gp, 0, divided, "0")
	g.addRRHs(gp, divided, divided*2, "1")
	g.addRRHs(gp, divided*2, divided*3, "2")
	g.addRRHs(gp, divided*3, divided*4, "3")
	g.addRRHs(gp, divided*4, divided*5, "4")

#Assign VPON Heuristic simulations
#add 5 rrhs per execution
g.rrhs_amount = 5
rs = g.rrhs_amount
#main loop
for s in sched_pol:
	g.rrhs_amount = 5
	rs = g.rrhs_amount
	print("Executing {}".format(s))
	for i in range(40):
		#print(g.rrhs_amount)
		importlib.reload(g)
		g.rrhs_amount = rs
		gp = g.createGraph()
		g.createRRHs()
		g.addFogNodes(gp, fog_amount)
		setExperiment(gp, g.rrhs_amount, fog_amount)
		for i in range(len(g.rrhs)):
			g.startNode(gp, "RRH{}".format(i))
			g.actives_rrhs.append("RRH{}".format(i))
		if s == "all_random":
			g.allRandomVPON(gp)
		#elif s == "fog_first":
		#	g.fogFirst(gp)
		elif s == "cloud_first_all_fogs":
			g.assignVPON(gp)
		elif s == "cloud_first_random_fogs":
			g.randomFogVPON(gp)
		elif s == "most_loaded":
			g.assignMostLoadedVPON(gp)
		elif s == "least_loaded":
			g.assignLeastLoadedVPON(gp)
		#elif s == "least_cost":
		#	g.leastCostNodeVPON(gp)
		#elif s == "least_cost_active_ratio":
		#	g.leastCostLoadedVPON(gp)
		#most and least loaded that considers the bandwidth available on each node midhaul
		#elif s == "most_loaded_bandwidth":
		#	g.assignMostLoadedVPONBand(gp)
		#elif s == "least_loaded_bandwidth":
		#	g.assignLeastLoadedVPONBand(gp)
		#elif s == "big_ratio":
		#	g.assignBigRatioVPON(gp)
		#elif s == "small_ratio":
		#	g.assignSmallRatioVPON(gp)
		start_time = g.time.clock()
		mincostFlow = g.nx.max_flow_min_cost(gp, "s", "d")
		execution_time[s].append(g.time.clock() - start_time)
		power_consumption[s].append(g.overallPowerConsumption(gp))
		g.rrhs_amount += 5
		rs = g.rrhs_amount
print(power_consumption)
genLogs()


'''
gp = g.createGraph()
g.createRRHs()
#print(len(g.rrhs))
#for i in rrhs:
#  print(i.id)
g.addFogNodes(gp, fog_amount)
setExperiment(gp, g.rrhs_amount, fog_amount)
for i in range(len(g.rrhs)):
	g.startNode(gp, "RRH{}".format(i))
	g.actives_rrhs.append("RRH{}".format(i))

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
'''