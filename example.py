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

total_inc_power = []
total_batch_power = []

util = sim.Util()
sim.load_threshold = 1
#incremental simulation

for i in range(5):
	print("STARTING INCREMENTAL SIMULATION---STARTING INCREMENTAL SIMULATION---STARTING INCREMENTAL SIMULATION---STARTING INCREMENTAL SIMULATION---")
	print("Execution # {}".format(i))
	env = simpy.Environment()
	cp = sim.Control_Plane(env, util, "inc")
	sim.rrhs = util.createRRHs(25, env, sim.service_time, cp)
	np.shuffle(sim.rrhs)
	t = sim.Traffic_Generator(env, sim.distribution, sim.service_time, cp)
	print("\Begin at "+str(env.now))
	env.run(until = 86401)
	print("\End at "+str(env.now))
	print("#|#|#|#|#|#|#|#|#|#|#|#|#|#|#|#|#|#|#|#|#|#|#|#|##|#|#|#|")
	print(sim.average_power_consumption)
	print("-------------------------------------")
	print(len(sim.average_power_consumption))
	print("#|#|#|#|#|#|#|#|#|#|#|#|#|#|#|#|#|#|#|#|#|#|#|#|##|#|#|#|")
	total_inc_power.append(sim.average_power_consumption)
	util.resetParams()


#batch simulation

for i in range(5):
	print("STARTING INC BATCH SIMULATION---STARTING BATCH SIMULATION---STARTING BATCH SIMULATION---STARTING BATCH SIMULATION---")
	print("Execution # {}".format(i))
	env = simpy.Environment()
	cp = sim.Control_Plane(env, util, "batch")
	sim.rrhs = util.createRRHs(25, env, sim.service_time, cp)
	np.shuffle(sim.rrhs)
	t = sim.Traffic_Generator(env, sim.distribution, sim.service_time, cp)
	print("\Begin at "+str(env.now))
	env.run(until = 86401)
	print("\End at "+str(env.now))
	print("#|#|#|#|#|#|#|#|#|#|#|#|#|#|#|#|#|#|#|#|#|#|#|#|##|#|#|#|")
	print(sim.batch_average_consumption)
	print("-------------------------------------")
	print(len(sim.batch_average_consumption))
	print("#|#|#|#|#|#|#|#|#|#|#|#|#|#|#|#|#|#|#|#|#|#|#|#|##|#|#|#|")
	total_batch_power.append(sim.batch_average_consumption)
	util.resetParams()


total_average_inc_power = [float(sum(col))/len(col) for col in zip(*total_inc_power)]
total_average_batch_power = [float(sum(col))/len(col) for col in zip(*total_batch_power)]
print(total_average_inc_power)
print(total_average_batch_power)

#print("Total blocking for Incremental {}".format(sim.total_inc_blocking))
#print("Total blocking for Batch {}".format(sim.total_batch_blocking))

#generate the plots for power consumption
plt.plot(total_average_inc_power, label = "Incremental ILP")
plt.plot(total_average_batch_power, label = "Batch ILP Threshold = 1")
plt.xticks(numpy.arange(0, 24, 1))
plt.yticks(numpy.arange(0, 3000,300))
plt.ylabel('Power Consumption')
plt.xlabel("Time of the day")
plt.legend()
plt.grid()
plt.savefig('/home/hextinini/Área de Trabalho/dinamyc_batchXinc40_th1.png', bbox_inches='tight')
#plt.show()
plt.clf()

#generate the plots for power consumption
plt.plot(sim.total_inc_blocking, label = "Incremental ILP")
plt.plot(sim.total_batch_blocking, label = "Batch ILP Threshold = 1")
plt.xticks(numpy.arange(0, 24, 1))
plt.yticks(numpy.arange(0, 500,10))
plt.ylabel('Blocking of RRHs')
plt.xlabel("Time of the day")
plt.legend()
plt.grid()
plt.savefig('/home/hextinini/Área de Trabalho/blocking40_th1.png', bbox_inches='tight')
#plt.show()
plt.clf()
