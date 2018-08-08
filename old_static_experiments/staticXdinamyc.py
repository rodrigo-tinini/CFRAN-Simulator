import sys
sys.path.insert(0, '/home/hextinini/Área de Trabalho/simulador/CFRAN-Simulator')
import simpy
import functools
import random as np
import time
from enum import Enum
import numpy
from scipy.stats import norm
import matplotlib.pyplot as plt
import batch_teste as lp
import pureBatchILP as plp
import copy
import incrementalWithBatchILP as sim
import static_accounting_base_line as st

number_of_rrhs = 35
total_average_wait_time = []
total_din_average_wait_time = []

#running for the static
util = st.Util()
for i in range(1):
	env = simpy.Environment()
	cp = st.Control_Plane(env, util)
	st.rrhs = util.createRRHs(number_of_rrhs, env, st.service_time, cp)
	#for i in rrhs:
	#	print(i.rrhs_matrix)
	np.shuffle(st.rrhs)
	t = st.Traffic_Generator(env, st.distribution, st.service_time, cp, util)
	print("Begin at "+str(env.now))
	print("Running {}th".format(i+1))
	env.run(until = 86401)
	print("End at "+str(env.now))
	#total_average_power.append(power_consumption)
	total_average_wait_time.append(st.avg_hours_wait_time)
	util.resetParams()
wait_time_hour_average = [float(sum(col))/len(col) for col in zip(*total_average_wait_time)]
print(wait_time_hour_average)

util2 = sim.Util()
for i in range(1):
	print("STARTING INC BATCH SIMULATION---STARTING BATCH SIMULATION---STARTING BATCH SIMULATION---STARTING BATCH SIMULATION---")
	print("Execution # {}".format(i))
	env = simpy.Environment()
	cp = sim.Control_Plane(env, util2, "batch")
	sim.rrhs = util2.createRRHs(number_of_rrhs, env, sim.service_time, cp)
	np.shuffle(sim.rrhs)
	t = sim.Traffic_Generator(env, sim.distribution, sim.service_time, cp)
	print("\Begin at "+str(env.now))
	env.run(until = 86401)
	print("\End at "+str(env.now))
	total_din_average_wait_time.append(sim.avg_batch_rrhs_wait_time)
	util2.resetParams()
din_wait_time_average = [float(sum(col))/len(col) for col in zip(*total_din_average_wait_time)]
print(din_wait_time_average)


#generate the plots for power consumption
plt.plot(wait_time_hour_average, label = "Static Traffic")
plt.plot(din_wait_time_average, label = "Dynamic Traffic")
plt.xticks(numpy.arange(0, 24, 1))
plt.yticks(numpy.arange(-1, max(max(wait_time_hour_average), max(din_wait_time_average)),100))
plt.ylabel('Average Waiting Time')
plt.xlabel("Time of the day")
plt.legend()
plt.grid()
plt.savefig('/home/hextinini/Área de Trabalho/waitTime_staticXDynamic.png'.format(number_of_rrhs), bbox_inches='tight')
#plt.show()
plt.clf()