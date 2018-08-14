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
#general variables
rrhs_amount = 160
#fog nodes amount
gp = g.createGraph()
g.createRRHs()
print(len(g.rrhs))
#for i in rrhs:
#  print(i.id)
g.addFogNodes(gp, 5)
g.addRRHs(gp, 0, 32, "0")
g.addRRHs(gp, 32, 64, "1")
g.addRRHs(gp, 64, 96, "2")
g.addRRHs(gp, 96, 128, "3")
g.addRRHs(gp, 128, 160, "4")
#turn the rrhs on
for i in range(len(g.rrhs)):
  g.startNode(gp, "RRH{}".format(i))
  g.actives_rrhs.append("RRH{}".format(i))
#for i in range(len(g.rrhs)):
#	print(gp["s"]["RRH{}".format(i)]["capacity"])
g.assignVPON(gp)
start_time = g.time.clock()
mincostFlow = g.nx.max_flow_min_cost(gp, "s", "d")
exec_time = g.time.clock() - start_time
print(g.overallPowerConsumption(gp))
#print(g.getPowerConsumption(mincostFlow))
print(exec_time)
#print(mincostFlow["s"])
