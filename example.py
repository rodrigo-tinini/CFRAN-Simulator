import simpy
import functools
import random as np
import time
from enum import Enum
import numpy
from scipy.stats import norm
import scipy as sp
import scipy.stats
import matplotlib.pyplot as plt
import batch_teste as lp
import pureBatchILP as plp
import copy
import incrementalWithBatchILP as sim

total_inc_power = []
total_batch_power = []
total_inc_batch = []

util = sim.Util()
sim.load_threshold = 15
#incremental simulation

number_of_rrhs = 20

for i in range(10):
	print("STARTING INCREMENTAL SIMULATION---STARTING INCREMENTAL SIMULATION---STARTING INCREMENTAL SIMULATION---STARTING INCREMENTAL SIMULATION---")
	print("Execution # {}".format(i))
	env = simpy.Environment()
	cp = sim.Control_Plane(env, util, "inc")
	sim.rrhs = util.createRRHs(number_of_rrhs, env, sim.service_time, cp)
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

for i in range(10):
	print("STARTING INC BATCH SIMULATION---STARTING BATCH SIMULATION---STARTING BATCH SIMULATION---STARTING BATCH SIMULATION---")
	print("Execution # {}".format(i))
	env = simpy.Environment()
	cp = sim.Control_Plane(env, util, "inc_batch")
	sim.rrhs = util.createRRHs(number_of_rrhs, env, sim.service_time, cp)
	np.shuffle(sim.rrhs)
	t = sim.Traffic_Generator(env, sim.distribution, sim.service_time, cp)
	print("\Begin at "+str(env.now))
	env.run(until = 86401)
	print("\End at "+str(env.now))
	print("#|#|#|#|#|#|#|#|#|#|#|#|#|#|#|#|#|#|#|#|#|#|#|#|##|#|#|#|")
	print(sim.inc_batch_average_consumption)
	print("-------------------------------------")
	print(len(sim.inc_batch_average_consumption))
	print("#|#|#|#|#|#|#|#|#|#|#|#|#|#|#|#|#|#|#|#|#|#|#|#|##|#|#|#|")
	total_batch_power.append(sim.inc_batch_average_consumption)
	util.resetParams()

	#batch simulation

for i in range(10):
	print("STARTING INC BATCH SIMULATION---STARTING BATCH SIMULATION---STARTING BATCH SIMULATION---STARTING BATCH SIMULATION---")
	print("Execution # {}".format(i))
	env = simpy.Environment()
	cp = sim.Control_Plane(env, util, "batch")
	sim.rrhs = util.createRRHs(number_of_rrhs, env, sim.service_time, cp)
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
	total_inc_batch.append(sim.batch_average_consumption)
	util.resetParams()

def mean_confidence_interval(data, confidence=0.95):
    a = 1.0*numpy.array(data)
    n = len(a)
    m, se = numpy.mean(a), scipy.stats.sem(a)
    h = se * sp.stats.t._ppf((1+confidence)/2., n-1)
    return m, m-h, m+h


ci = [mean_confidence_interval(col, confidence = 0.95) for col in zip(*total_inc_power)]
print("CI for INC")
print(ci)
print("--------------------------------------------------------------------------------")
ci2 = [mean_confidence_interval(col, confidence = 0.95) for col in zip(*total_batch_power)]
print("CI for Batch")
print(ci2)
'''
#standard deviations
inc_standard_deviations = [numpy.std(col) for col in zip(*total_inc_power)]
batch_standard_deviations = [numpy.std(col) for col in zip(*total_batch_power)]
print("STD---------------")
print(inc_standard_deviations)
#print(batch_standard_deviations)
print("STD---------------")
'''
#means
total_average_inc_power = [float(sum(col))/len(col) for col in zip(*total_inc_power)]
total_average_batch_power = [float(sum(col))/len(col) for col in zip(*total_batch_power)]
total_average_inc_batch_power = [float(sum(col))/len(col) for col in zip(*total_inc_batch)]
print(total_average_inc_power)
print(total_average_batch_power)


#print("Total blocking for Incremental {}".format(sim.total_inc_blocking))
#print("Total blocking for Batch {}".format(sim.total_batch_blocking))

#generate the plots for power consumption
plt.plot(total_average_inc_power, label = "Incremental ILP")
plt.plot(total_average_batch_power, label = "Batch ILP Threshold = {}".format(sim.load_threshold))
plt.plot(total_average_inc_batch_power, label = "Pure Batch ILP")
plt.xticks(numpy.arange(0, 24, 1))
plt.yticks(numpy.arange(0, 3000,300))
plt.ylabel('Power Consumption')
plt.xlabel("Time of the day")
plt.legend()
plt.grid()
plt.savefig('/home/hextinini/Área de Trabalho/dinamycInc_batchXinc{}.png'.format(number_of_rrhs), bbox_inches='tight')
#plt.show()
plt.clf()

#generate the plots for power consumption
plt.plot(sim.total_inc_blocking, label = "Incremental ILP")
plt.plot(sim.total_batch_blocking, label = "Batch ILP Threshold = {}".format(sim.load_threshold))
plt.xticks(numpy.arange(0, 24, 1))
plt.yticks(numpy.arange(0, 500,10))
plt.ylabel('Blocking of RRHs')
plt.xlabel("Time of the day")
plt.legend()
plt.grid()
plt.savefig('/home/hextinini/Área de Trabalho/IncBatchblocking{}.png'.format(number_of_rrhs), bbox_inches='tight')
#plt.show()
plt.clf()
