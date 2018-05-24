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

#lists of power consumptions means
total_inc_power = []
total_batch_power = []
total_inc_batch = []
total_inc_batch2 = []

#lists of activated nodes means
total_inc_nodes = []
total_batch_nodes = []
total_inc_batch_nodes = []
total_inc_batch_nodes2 = []

#lists of activated DUs means
total_inc_DUs = []
total_batch_DUs = []
total_inc_batch_DUs = []
total_inc_batch_DUs2 = []

#lists of activated switches means
total_inc_switches = []
total_batch_switches = []
total_inc_batch_switches = []
total_inc_batch_switches2 = []

#lists of activated lambdas means
total_inc_lambdas = []
total_batch_lambdas = []
total_inc_batch_lambdas = []
total_inc_batch_lambdas2 = []

#lists of redirectes RRHs means
total_inc_redir = []
total_batch_redir = []
total_inc_batch_redir = []
total_inc_batch_redir2 = []

#lists of blocked RRHs means
total_inc_blocked = []
total_batch_blocked = []
total_inc_batch_blocked = []
total_inc_batch_blocked2 = []

#lists of solutions time means
total_inc_time = []
total_batch_time = []
total_inc_batch_time = []
total_inc_batch_time2 = []

#lists

util = sim.Util()
sim.load_threshold = 10
#incremental simulation

number_of_rrhs = 25

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
	total_inc_nodes.append(sim.average_act_nodes)
	total_inc_DUs.append(sim.average_act_dus)
	total_inc_lambdas.append(sim.average_act_lambdas)
	total_inc_redir.append(sim.average_redir_rrhs)
	total_inc_switches.append(sim.average_act_switch)
	total_inc_blocked.append(sim.total_inc_blocking)
	total_inc_time.append(sim.avg_time_inc)
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
	total_inc_batch.append(sim.inc_batch_average_consumption)
	total_inc_batch_nodes.append(sim.inc_batch_average_act_nodes)
	total_inc_batch_DUs.append(sim.inc_batch_average_act_dus)
	total_inc_batch_lambdas.append(sim.inc_batch_average_act_lambdas)
	total_inc_batch_redir.append(sim.inc_batch_average_redir_rrhs)
	total_inc_batch_switches.append(sim.inc_batch_average_act_switch)
	total_inc_batch_blocked.append(sim.total_inc_batch_blocking)
	total_inc_batch_time.append(sim.avg_time_inc_batch)
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
	total_batch_power.append(sim.batch_average_consumption)
	total_batch_nodes.append(sim.b_average_act_nodes)
	total_batch_DUs.append(sim.b_average_act_dus)
	total_batch_lambdas.append(sim.b_average_act_lambdas)
	total_batch_redir.append(sim.b_average_redir_rrhs)
	total_batch_switches.append(sim.b_average_act_switch)
	total_batch_blocked.append(sim.total_batch_blocking)
	total_batch_time.append(sim.avg_time_b)
	util.resetParams()

old_th = 10
sim.load_threshold = 5
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
	total_inc_batch2.append(sim.inc_batch_average_consumption)
	total_inc_batch_nodes2.append(sim.inc_batch_average_act_nodes)
	total_inc_batch_DUs2.append(sim.inc_batch_average_act_dus)
	total_inc_batch_lambdas2.append(sim.inc_batch_average_act_lambdas)
	total_inc_batch_redir2.append(sim.inc_batch_average_redir_rrhs)
	total_inc_batch_switches2.append(sim.inc_batch_average_act_switch)
	total_inc_batch_blocked2.append(sim.total_inc_batch_blocking)
	total_inc_batch_time2.append(sim.avg_time_inc_batch)

	util.resetParams()

def mean_confidence_interval(data, confidence=0.95):
    a = 1.0*numpy.array(data)
    n = len(a)
    m, se = numpy.mean(a), scipy.stats.sem(a)
    h = se * sp.stats.t._ppf((1+confidence)/2., n-1)
    #return m, m-h, m+h
    return h


#print("CI for Batch")
#print(ci2)
'''
#standard deviations
inc_standard_deviations = [numpy.std(col, ddof=1) for col in zip(*total_inc_power)]
batch_standard_deviations = [numpy.std(col,ddof=1) for col in zip(*total_batch_power)]
print("STD INC---------------")
print(inc_standard_deviations)
print("CI for INC")
print(ci)
print("############################################")
print("STD Batch---------------")
print(batch_standard_deviations)
'''


#means
#power
total_average_inc_power = [float(sum(col))/len(col) for col in zip(*total_inc_power)]
total_average_batch_power = [float(sum(col))/len(col) for col in zip(*total_batch_power)]
total_average_inc_batch_power = [float(sum(col))/len(col) for col in zip(*total_inc_batch)]
total_average_inc_batch_power2 = [float(sum(col))/len(col) for col in zip(*total_inc_batch2)] 
#inc
inc_nodes_mean = [float(sum(col))/len(col) for col in zip(*total_inc_nodes)]
inc_dus_mean=	[float(sum(col))/len(col) for col in zip(*total_inc_DUs)]
inc_lambdas_mean=	[float(sum(col))/len(col) for col in zip(*total_inc_lambdas)]
inc_redir_mean=	[float(sum(col))/len(col) for col in zip(*total_inc_redir)]
inc_switches_mean=	[float(sum(col))/len(col) for col in zip(*total_inc_switches)]
inc_blocked_mean=	[float(sum(col))/len(col) for col in zip(*total_inc_blocked)]
inc_time_mean=	[float(sum(col))/len(col) for col in zip(*total_inc_time)]
#batch
batch_nodes_mean = [float(sum(col))/len(col) for col in zip(*total_batch_nodes)]
batch_dus_mean=	[float(sum(col))/len(col) for col in zip(*total_batch_DUs)]
batch_lambdas_mean=	[float(sum(col))/len(col) for col in zip(*total_batch_lambdas)]
batch_redir_mean=	[float(sum(col))/len(col) for col in zip(*total_batch_redir)]
batch_switches_mean=	[float(sum(col))/len(col) for col in zip(*total_batch_switches)]
batch_blocked_mean=	[float(sum(col))/len(col) for col in zip(*total_batch_blocked)]
batch_time_mean=	[float(sum(col))/len(col) for col in zip(*total_batch_time)]
#inc_batch
inc_batch_nodes_mean = [float(sum(col))/len(col) for col in zip(*total_inc_batch_nodes)]
inc_batch_dus_mean=	[float(sum(col))/len(col) for col in zip(*total_inc_batch_DUs)]
inc_batch_lambdas_mean=	[float(sum(col))/len(col) for col in zip(*total_inc_batch_lambdas)]
inc_batch_redir_mean=	[float(sum(col))/len(col) for col in zip(*total_inc_batch_redir)]
inc_batch_switches_mean=	[float(sum(col))/len(col) for col in zip(*total_inc_batch_switches)]
inc_batch_blocked_mean=	[float(sum(col))/len(col) for col in zip(*total_inc_batch_blocked)]
inc_batch_time_mean=	[float(sum(col))/len(col) for col in zip(*total_inc_batch_time)]
#inc_batch2
inc_batch_nodes_mean2 = [float(sum(col))/len(col) for col in zip(*total_inc_batch_nodes2)]
inc_batch_dus_mean2=	[float(sum(col))/len(col) for col in zip(*total_inc_batch_DUs2)]
inc_batch_lambdas_mean2=	[float(sum(col))/len(col) for col in zip(*total_inc_batch_lambdas2)]
inc_batch_redir_mean2=	[float(sum(col))/len(col) for col in zip(*total_inc_batch_redir2)]
inc_batch_switches_mean2=	[float(sum(col))/len(col) for col in zip(*total_inc_batch_switches2)]
inc_batch_blocked_mean2=	[float(sum(col))/len(col) for col in zip(*total_inc_batch_blocked2)]
inc_batch_time_mean2=	[float(sum(col))/len(col) for col in zip(*total_inc_batch_time2)]



#confidence intervals
inc_ci = [mean_confidence_interval(col, confidence = 0.95) for col in zip(*total_inc_power)]
batch_ci = [mean_confidence_interval(col, confidence = 0.95) for col in zip(*total_batch_power)]
inc_batch_ci = [mean_confidence_interval(col, confidence = 0.95) for col in zip(*total_inc_batch)]
inc_batch_ci2 = [mean_confidence_interval(col, confidence = 0.95) for col in zip(*total_inc_batch2)]

x = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23]
#print("Total blocking for Incremental {}".format(sim.total_inc_blocking))
#print("Total blocking for Batch {}".format(sim.total_batch_blocking))

#generate the plots for power consumption
plt.plot(total_average_inc_power, label = "Incremental ILP")
plt.plot(total_average_inc_batch_power, label = "Batch ILP Threshold = {}".format(old_th))
plt.plot(total_average_inc_batch_power2, label = "Batch ILP Threshold = {}".format(sim.load_threshold))
plt.plot(total_average_batch_power, label = "Pure Batch ILP")
#plt.errorbar(x, total_average_inc_batch_power, yerr=batch_ci, fmt='none')
#plt.errorbar(x, total_average_inc_power, yerr=inc_ci, fmt='none')
plt.xticks(numpy.arange(0, 24, 1))
plt.yticks(numpy.arange(0, 3000,300))
plt.ylabel('Power Consumption')
plt.xlabel("Time of the day")
plt.legend()
plt.grid()
plt.savefig('/home/hextinini/Área de Trabalho/plots/power{}.png'.format(number_of_rrhs), bbox_inches='tight')
#plt.show()
plt.clf()

#plot for activated nodes
plt.plot(inc_nodes_mean, label = "Incremental ILP")
plt.plot(inc_batch_nodes_mean, label = "Batch ILP Threshold = {}".format(old_th))
plt.plot(inc_batch_nodes_mean2, label = "Batch ILP Threshold = {}".format(sim.load_threshold))
plt.plot(batch_nodes_mean, label = "Pure Batch ILP")
plt.xticks(numpy.arange(0, 24, 1))
plt.yticks(numpy.arange(0, 4,1))
plt.ylabel('Activated Nodes')
plt.xlabel("Time of the day")
plt.legend()
plt.grid()
plt.savefig('/home/hextinini/Área de Trabalho/plots/nodes{}.png'.format(number_of_rrhs), bbox_inches='tight')
#plt.show()
plt.clf()

#plot for activated DUs
plt.plot(inc_dus_mean, label = "Incremental ILP")
plt.plot(inc_batch_dus_mean, label = "Batch ILP Threshold = {}".format(old_th))
plt.plot(inc_batch_dus_mean2, label = "Batch ILP Threshold = {}".format(sim.load_threshold))
plt.plot(batch_dus_mean, label = "Pure Batch ILP")
plt.xticks(numpy.arange(0, 24, 1))
plt.yticks(numpy.arange(0, 25,1))
plt.ylabel('Activated DUs')
plt.xlabel("Time of the day")
plt.legend()
plt.grid()
plt.savefig('/home/hextinini/Área de Trabalho/plots/dus{}.png'.format(number_of_rrhs), bbox_inches='tight')
#plt.show()
plt.clf()

#plot for activated lambdas
plt.plot(inc_lambdas_mean, label = "Incremental ILP")
plt.plot(inc_batch_lambdas_mean, label = "Batch ILP Threshold = {}".format(old_th))
plt.plot(inc_batch_lambdas_mean2, label = "Batch ILP Threshold = {}".format(sim.load_threshold))
plt.plot(batch_lambdas_mean, label = "Pure Batch ILP")
plt.xticks(numpy.arange(0, 24, 1))
plt.yticks(numpy.arange(0, 10,1))
plt.ylabel('Activated lambdas')
plt.xlabel("Time of the day")
plt.legend()
plt.grid()
plt.savefig('/home/hextinini/Área de Trabalho/plots/lambdas{}.png'.format(number_of_rrhs), bbox_inches='tight')
#plt.show()
plt.clf()

#plot for redirected RRHs
plt.plot(inc_redir_mean, label = "Incremental ILP")
plt.plot(inc_batch_redir_mean, label = "Batch ILP Threshold = {}".format(old_th))
plt.plot(inc_batch_redir_mean2, label = "Batch ILP Threshold = {}".format(sim.load_threshold))
plt.plot(batch_redir_mean, label = "Pure Batch ILP")
plt.xticks(numpy.arange(0, 24, 1))
plt.yticks(numpy.arange(0, 100,1))
plt.ylabel('Redirected RRHs')
plt.xlabel("Time of the day")
plt.legend()
plt.grid()
plt.savefig('/home/hextinini/Área de Trabalho/plots/redirected{}.png'.format(number_of_rrhs), bbox_inches='tight')
#plt.show()
plt.clf()

#plot for activated switches
plt.plot(inc_switches_mean, label = "Incremental ILP")
plt.plot(inc_batch_switches_mean, label = "Batch ILP Threshold = {}".format(old_th))
plt.plot(inc_batch_switches_mean2, label = "Batch ILP Threshold = {}".format(sim.load_threshold))
plt.plot(batch_switches_mean, label = "Pure Batch ILP")
plt.xticks(numpy.arange(0, 24, 1))
plt.yticks(numpy.arange(0, 10,1))
plt.ylabel('Activated Switches')
plt.xlabel("Time of the day")
plt.legend()
plt.grid()
plt.savefig('/home/hextinini/Área de Trabalho/plots/switches{}.png'.format(number_of_rrhs), bbox_inches='tight')
#plt.show()
plt.clf()

#plot for blocked RRHs
plt.plot(inc_blocked_mean, label = "Incremental ILP")
plt.plot(inc_batch_blocked_mean, label = "Batch ILP Threshold = {}".format(old_th))
plt.plot(inc_batch_blocked_mean2, label = "Batch ILP Threshold = {}".format(sim.load_threshold))
plt.plot(batch_blocked_mean, label = "Pure Batch ILP")
plt.xticks(numpy.arange(0, 24, 1))
plt.yticks(numpy.arange(0, 500,20))
plt.ylabel('Blocked RRHs')
plt.xlabel("Time of the day")
plt.legend()
plt.grid()
plt.savefig('/home/hextinini/Área de Trabalho/plots/blocked{}.png'.format(number_of_rrhs), bbox_inches='tight')
#plt.show()
plt.clf()

#plot for solution times
plt.plot(inc_time_mean, label = "Incremental ILP")
plt.plot(inc_batch_time_mean, label = "Batch ILP Threshold = {}".format(old_th))
plt.plot(inc_batch_time_mean2, label = "Batch ILP Threshold = {}".format(sim.load_threshold))
plt.plot(batch_time_mean, label = "Pure Batch ILP")
plt.xticks(numpy.arange(0, 24, 1))
plt.yticks(numpy.arange(0, 0.1,0.01))
plt.ylabel('Solution Time')
plt.xlabel("Time of the day")
plt.legend()
plt.grid()
plt.savefig('/home/hextinini/Área de Trabalho/plots/solution_time{}.png'.format(number_of_rrhs), bbox_inches='tight')
#plt.show()
plt.clf()
