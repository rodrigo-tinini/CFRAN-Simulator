import simpy
import functools
import random as np
import time
from enum import Enum
from scipy.stats import norm
import matplotlib.pyplot as plt
import cfran_batch_ilp as lp

#to generate the traffic load of each timestamp
loads = []
#number of timestamps of load changing
stamps = 24
for i in range(stamps):
	x = norm.pdf(i, 10, 4)
	x *= 1000
	x= round(x,0)
	loads.append(x)
loads.reverse()
rrhs = []
for i in range(0,100):
	r = lp.RRH(i, [1,1,0,0,0,0,0,0,0,0])
	rrhs.append(r)
for period in loads:


	