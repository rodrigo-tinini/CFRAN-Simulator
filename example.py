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
total_inc_batch3 = []
total_inc_batch4 = []

#lists of activated nodes means
total_inc_nodes = []
total_batch_nodes = []
total_inc_batch_nodes = []
total_inc_batch_nodes2 = []
total_inc_batch_nodes3 = []
total_inc_batch_nodes4 = []

#lists of activated DUs means
total_inc_DUs = []
total_batch_DUs = []
total_inc_batch_DUs = []
total_inc_batch_DUs2 = []
total_inc_batch_DUs3 = []
total_inc_batch_DUs4 = []

#lists of activated switches means
total_inc_switches = []
total_batch_switches = []
total_inc_batch_switches = []
total_inc_batch_switches2 = []
total_inc_batch_switches3 = []
total_inc_batch_switches4 = []

#lists of activated lambdas means
total_inc_lambdas = []
total_batch_lambdas = []
total_inc_batch_lambdas = []
total_inc_batch_lambdas2 = []
total_inc_batch_lambdas3 = []
total_inc_batch_lambdas4 = []

#lists of redirectes RRHs means
total_inc_redir = []
total_batch_redir = []
total_inc_batch_redir = []
total_inc_batch_redir2 = []
total_inc_batch_redir3 = []
total_inc_batch_redir4 = []

#lists of blocked RRHs means
total_inc_blocked = []
total_batch_blocked = []
total_inc_batch_blocked = []
total_inc_batch_blocked2 = []
total_inc_batch_blocked3 = []
total_inc_batch_blocked4 = []

#lists of solutions time means
total_inc_time = []
total_batch_time = []
total_inc_batch_time = []
total_inc_batch_time2 = []
total_inc_batch_time3 = []
total_inc_batch_time4 = []

#lists of external migrations means
total_inc_migrations = []
total_batch_migrations = []
total_inc_batch_migrations = []
total_inc_batch_migrations2 = []
total_inc_batch_migrations3 = []
total_inc_batch_migrations4 = []

#lists of bandwidth usage
total_inc_lambda_usage = []
total_batch_lambda_usage = []
total_inc_batch_lambda_usage = []
total_inc_batch_lambda_usage2 = []
total_inc_batch_lambda_usage3 = []
total_inc_batch_lambda_usage4 = []

#lists of proc usage
total_inc_proc_usage = []
total_batch_proc_usage = []
total_inc_batch_proc_usage = []
total_inc_batch_proc_usage2 = []
total_inc_batch_proc_usage3 = []
total_inc_batch_proc_usage4 = []

#lists
exec_number = 10
util = sim.Util()
#sim.load_threshold = 10
#incremental simulation

number_of_rrhs = sim.rrhs_quantity

for i in range(exec_number):
	print("STARTING BATCH SIMULATION---STARTING BATCH SIMULATION---STARTING BATCH SIMULATION---STARTING BATCH SIMULATION---")
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
	total_batch_migrations.append(sim.avg_external_migrations)
	total_batch_lambda_usage.append(sim.avg_lambda_usage)
	total_batch_proc_usage.append(sim.avg_proc_usage)
	util.resetParams()

for i in range(exec_number):
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
	total_inc_migrations.append(sim.avg_external_migrations)
	total_inc_lambda_usage.append(sim.avg_lambda_usage)
	total_inc_proc_usage.append(sim.avg_proc_usage)
	util.resetParams()

#batch simulation

for i in range(exec_number):
	print("STARTING INC BATCH SIMULATION 1 ---STARTING BATCH SIMULATION 1 ---STARTING BATCH SIMULATION---STARTING BATCH SIMULATION---")
	print("Execution # {}".format(i))
	env = simpy.Environment()
	cp = sim.Control_Plane(env, util, "load_inc_batch")
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
	total_inc_batch_migrations.append(sim.avg_external_migrations)
	total_inc_batch_lambda_usage.append(sim.avg_lambda_usage)
	total_inc_batch_proc_usage.append(sim.avg_proc_usage)
	util.resetParams()

	#batch simulation
sim.network_threshold = 0.6
sim.count_rrhs = 0
old_th = 0.8
#sim.load_threshold = 5
for i in range(exec_number):
	print("STARTING INC BATCH SIMULATION 2---STARTING BATCH SIMULATION 2---STARTING BATCH SIMULATION---STARTING BATCH SIMULATION---")
	print("Execution # {}".format(i))
	env = simpy.Environment()
	cp = sim.Control_Plane(env, util, "load_inc_batch")
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
	total_inc_batch_migrations2.append(sim.avg_external_migrations)
	total_inc_batch_lambda_usage2.append(sim.avg_lambda_usage)
	total_inc_batch_proc_usage2.append(sim.avg_proc_usage)
	util.resetParams()

sim.network_threshold = 0.4
sim.count_rrhs = 0
old_th2 = 0.6
#sim.load_threshold = 5
for i in range(exec_number):
	print("STARTING INC BATCH SIMULATION 2---STARTING BATCH SIMULATION 2---STARTING BATCH SIMULATION---STARTING BATCH SIMULATION---")
	print("Execution # {}".format(i))
	env = simpy.Environment()
	cp = sim.Control_Plane(env, util, "load_inc_batch")
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
	total_inc_batch3.append(sim.inc_batch_average_consumption)
	total_inc_batch_nodes3.append(sim.inc_batch_average_act_nodes)
	total_inc_batch_DUs3.append(sim.inc_batch_average_act_dus)
	total_inc_batch_lambdas3.append(sim.inc_batch_average_act_lambdas)
	total_inc_batch_redir3.append(sim.inc_batch_average_redir_rrhs)
	total_inc_batch_switches3.append(sim.inc_batch_average_act_switch)
	total_inc_batch_blocked3.append(sim.total_inc_batch_blocking)
	total_inc_batch_time3.append(sim.avg_time_inc_batch)
	total_inc_batch_migrations3.append(sim.avg_external_migrations)
	total_inc_batch_lambda_usage3.append(sim.avg_lambda_usage)
	total_inc_batch_proc_usage3.append(sim.avg_proc_usage)
	util.resetParams()

sim.network_threshold = 0.2
sim.count_rrhs = 0
old_th3 = 0.4
#sim.load_threshold = 5
for i in range(exec_number):
	print("STARTING INC BATCH SIMULATION 2---STARTING BATCH SIMULATION 2---STARTING BATCH SIMULATION---STARTING BATCH SIMULATION---")
	print("Execution # {}".format(i))
	env = simpy.Environment()
	cp = sim.Control_Plane(env, util, "load_inc_batch")
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
	total_inc_batch4.append(sim.inc_batch_average_consumption)
	total_inc_batch_nodes4.append(sim.inc_batch_average_act_nodes)
	total_inc_batch_DUs4.append(sim.inc_batch_average_act_dus)
	total_inc_batch_lambdas4.append(sim.inc_batch_average_act_lambdas)
	total_inc_batch_redir4.append(sim.inc_batch_average_redir_rrhs)
	total_inc_batch_switches4.append(sim.inc_batch_average_act_switch)
	total_inc_batch_blocked4.append(sim.total_inc_batch_blocking)
	total_inc_batch_time4.append(sim.avg_time_inc_batch)
	total_inc_batch_migrations4.append(sim.avg_external_migrations)
	total_inc_batch_lambda_usage4.append(sim.avg_lambda_usage)
	total_inc_batch_proc_usage4.append(sim.avg_proc_usage)
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
#lambdas usage
avg_total_inc_lambda_usage = [float(sum(col))/len(col) for col in zip(*total_inc_lambda_usage)]
avg_total_batch_lambda_usage = [float(sum(col))/len(col) for col in zip(*total_batch_lambda_usage)]
avg_total_inc_batch_lambda_usage = [float(sum(col))/len(col) for col in zip(*total_inc_batch_lambda_usage)]
avg_total_inc_batch_lambda_usage2 = [float(sum(col))/len(col) for col in zip(*total_inc_batch_lambda_usage2)]
avg_total_inc_batch_lambda_usage3 = [float(sum(col))/len(col) for col in zip(*total_inc_batch_lambda_usage3)]
avg_total_inc_batch_lambda_usage4 = [float(sum(col))/len(col) for col in zip(*total_inc_batch_lambda_usage4)]
#procs usage
avg_total_inc_proc_usage = [float(sum(col))/len(col) for col in zip(*total_inc_proc_usage)]
avg_total_batch_proc_usage = [float(sum(col))/len(col) for col in zip(*total_batch_proc_usage)]
avg_total_inc_batch_proc_usage = [float(sum(col))/len(col) for col in zip(*total_inc_batch_proc_usage)]
avg_total_inc_batch_proc_usage2 = [float(sum(col))/len(col) for col in zip(*total_inc_batch_proc_usage2)]
avg_total_inc_batch_proc_usage3 = [float(sum(col))/len(col) for col in zip(*total_inc_batch_proc_usage3)]
avg_total_inc_batch_proc_usage4 = [float(sum(col))/len(col) for col in zip(*total_inc_batch_proc_usage4)]
#migrations
avg_total_inc_migrations = [float(sum(col))/len(col) for col in zip(*total_inc_migrations)]
avg_total_batch_migrations = [float(sum(col))/len(col) for col in zip(*total_batch_migrations)]
avg_total_inc_batch_migrations = [float(sum(col))/len(col) for col in zip(*total_inc_batch_migrations)]
avg_total_inc_batch_migrations2 = [float(sum(col))/len(col) for col in zip(*total_inc_batch_migrations2)]
avg_total_inc_batch_migrations3 = [float(sum(col))/len(col) for col in zip(*total_inc_batch_migrations3)]
avg_total_inc_batch_migrations4 = [float(sum(col))/len(col) for col in zip(*total_inc_batch_migrations4)]
#power
total_average_inc_power = [float(sum(col))/len(col) for col in zip(*total_inc_power)]
total_average_batch_power = [float(sum(col))/len(col) for col in zip(*total_batch_power)]
total_average_inc_batch_power = [float(sum(col))/len(col) for col in zip(*total_inc_batch)]
total_average_inc_batch_power2 = [float(sum(col))/len(col) for col in zip(*total_inc_batch2)]
total_average_inc_batch_power3 = [float(sum(col))/len(col) for col in zip(*total_inc_batch3)] 
total_average_inc_batch_power4 = [float(sum(col))/len(col) for col in zip(*total_inc_batch4)]  
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
#inc_batch3
inc_batch_nodes_mean3 = [float(sum(col))/len(col) for col in zip(*total_inc_batch_nodes3)]
inc_batch_dus_mean3=	[float(sum(col))/len(col) for col in zip(*total_inc_batch_DUs3)]
inc_batch_lambdas_mean3=	[float(sum(col))/len(col) for col in zip(*total_inc_batch_lambdas3)]
inc_batch_redir_mean3=	[float(sum(col))/len(col) for col in zip(*total_inc_batch_redir3)]
inc_batch_switches_mean3=	[float(sum(col))/len(col) for col in zip(*total_inc_batch_switches3)]
inc_batch_blocked_mean3=	[float(sum(col))/len(col) for col in zip(*total_inc_batch_blocked3)]
inc_batch_time_mean3=	[float(sum(col))/len(col) for col in zip(*total_inc_batch_time3)]
#inc_batch4
inc_batch_nodes_mean4 = [float(sum(col))/len(col) for col in zip(*total_inc_batch_nodes4)]
inc_batch_dus_mean4=	[float(sum(col))/len(col) for col in zip(*total_inc_batch_DUs4)]
inc_batch_lambdas_mean4=	[float(sum(col))/len(col) for col in zip(*total_inc_batch_lambdas4)]
inc_batch_redir_mean4=	[float(sum(col))/len(col) for col in zip(*total_inc_batch_redir4)]
inc_batch_switches_mean4=	[float(sum(col))/len(col) for col in zip(*total_inc_batch_switches4)]
inc_batch_blocked_mean4=	[float(sum(col))/len(col) for col in zip(*total_inc_batch_blocked4)]
inc_batch_time_mean4=	[float(sum(col))/len(col) for col in zip(*total_inc_batch_time4)]



#confidence intervals
inc_ci = [mean_confidence_interval(col, confidence = 0.95) for col in zip(*total_inc_power)]
batch_ci = [mean_confidence_interval(col, confidence = 0.95) for col in zip(*total_batch_power)]
inc_batch_ci = [mean_confidence_interval(col, confidence = 0.95) for col in zip(*total_inc_batch)]
inc_batch_ci2 = [mean_confidence_interval(col, confidence = 0.95) for col in zip(*total_inc_batch2)]

x = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23]
#print("Total blocking for Incremental {}".format(sim.total_inc_blocking))
#print("Total blocking for Batch {}".format(sim.total_batch_blocking))

#mins and max for the plots
#power consumption
min_power = []
min_power.append(total_average_inc_power)
min_power.append(total_average_batch_power)
min_power.append(total_average_inc_batch_power)
min_power.append(total_average_inc_batch_power2)
max_power= []
max_power.append(total_average_inc_power)
max_power.append(total_average_batch_power)
max_power.append(total_average_inc_batch_power)
max_power.append(total_average_inc_batch_power2)
power_min = min(min_power)
power_max = max(max_power)

#plot for lambdas usage
plt.plot(avg_total_inc_lambda_usage,marker='o', label = "No-nfvLB")
plt.plot(avg_total_inc_batch_lambda_usage,marker='v', label = "nfvLB Threshold = {}".format(old_th))
plt.plot(avg_total_inc_batch_lambda_usage2,marker='v', label = "nfvLB Threshold = {}".format(old_th2))
plt.plot(avg_total_inc_batch_lambda_usage3,marker='v', label = "nfvLB Threshold = {}".format(old_th3))
plt.plot(avg_total_inc_batch_lambda_usage4,marker='v', label = "nfvLB Threshold = {}".format(sim.network_threshold))
plt.plot(avg_total_batch_lambda_usage,marker='^', label = "PureBatch-nfvLB ")
plt.ylabel('Bandwidth Usage')
plt.xlabel("Time of the day")
plt.legend(loc="upper left",prop={'size': 8})
plt.grid()
plt.savefig('/home/hextinini/Área de Trabalho/nfv_cp/lambda_usage{}.png'.format(number_of_rrhs), bbox_inches='tight')
#plt.show()
plt.clf()

#plot for DUs usage
plt.plot(avg_total_inc_proc_usage,marker='o', label = "No-nfvLB")
plt.plot(avg_total_inc_batch_proc_usage,marker='v', label = "nfvLB Threshold = {}".format(old_th))
plt.plot(avg_total_inc_batch_proc_usage2,marker='v', label = "nfvLB Threshold = {}".format(old_th2))
plt.plot(avg_total_inc_batch_proc_usage3,marker='v', label = "nfvLB Threshold = {}".format(old_th3))
plt.plot(avg_total_inc_batch_proc_usage4,marker='v', label = "nfvLB Threshold = {}".format(sim.network_threshold))
plt.plot(avg_total_batch_proc_usage,marker='^', label = "PureBatch-nfvLB ")
plt.ylabel('Virtualized DUs Usage')
plt.xlabel("Time of the day")
plt.legend(loc="upper left",prop={'size': 8})
plt.grid()
plt.savefig('/home/hextinini/Área de Trabalho/nfv_cp/procs_usage{}.png'.format(number_of_rrhs), bbox_inches='tight')
#plt.show()
plt.clf()

#plot for external migrations
plt.plot(avg_total_inc_migrations,marker='o', label = "No-nfvLB")
plt.plot(avg_total_inc_batch_migrations,marker='v', label = "nfvLB Threshold = {}".format(old_th))
plt.plot(avg_total_inc_batch_migrations2,marker='v', label = "nfvLB Threshold = {}".format(old_th2))
plt.plot(avg_total_inc_batch_migrations3,marker='v', label = "nfvLB Threshold = {}".format(old_th3))
plt.plot(avg_total_inc_batch_migrations4,marker='v', label = "nfvLB Threshold = {}".format(sim.network_threshold))
plt.plot(avg_total_batch_migrations,marker='^', label = "PureBatch-nfvLB ")
plt.ylabel('Inter Node Service Interruption Probability')
plt.xlabel("Time of the day")
plt.legend(loc="upper left",prop={'size': 6})
plt.grid()
plt.savefig('/home/hextinini/Área de Trabalho/nfv_cp/migrations{}.png'.format(number_of_rrhs), bbox_inches='tight')
#plt.show()
plt.clf()


#generate the plots for power consumption
plt.plot(total_average_inc_power,marker='o', label = "No-nfvLB")
plt.plot(total_average_inc_batch_power,marker='v', label = "nfvLB Threshold = {}".format(old_th))
plt.plot(total_average_inc_batch_power2,marker='h', label = "nfvLB Threshold = {}".format(old_th2))
plt.plot(total_average_inc_batch_power3,marker='v', label = "nfvLB Threshold = {}".format(old_th3))
plt.plot(total_average_inc_batch_power4,marker='v', label = "nfvLB Threshold = {}".format(sim.network_threshold))
plt.plot(total_average_batch_power,marker='^', label = "PureBatch-nfvLB ")
#plt.errorbar(x, total_average_inc_batch_power, yerr=batch_ci, fmt='none')
#plt.errorbar(x, total_average_inc_power, yerr=inc_ci, fmt='none')
#plt.xticks(numpy.arange(0, 24, 1))
#plt.yticks(numpy.arange(0, 3000,300))
plt.ylabel('Power Consumption')
plt.xlabel("Time of the day")
plt.legend(loc="upper left",prop={'size': 6})
plt.grid()
plt.savefig('/home/hextinini/Área de Trabalho/nfv_cp/power{}.png'.format(number_of_rrhs), bbox_inches='tight')
#plt.show()
plt.clf()

#Logging
#power consumption
with open('/home/hextinini/Área de Trabalho/nfv_cp/logs/power_consumption{}.txt'.format(number_of_rrhs),'w') as filehandle:  
    filehandle.write("Batch\n\n")
    filehandle.writelines("%s\n" % p for p in total_average_batch_power)
    filehandle.write("\n")
    filehandle.write("Inc\n\n")
    filehandle.writelines("%s\n" % p for p in total_average_inc_power)
    filehandle.write("\n")
    filehandle.write("LoadInc Threshold {}\n\n".format(old_th))
    filehandle.writelines("%s\n" % p for p in total_average_inc_batch_power)
    filehandle.write("\n")
    filehandle.write("LoadInc Threshold {}\n\n".format(old_th2))
    filehandle.writelines("%s\n" % p for p in total_average_inc_batch_power2)
    filehandle.write("\n")
    filehandle.write("LoadInc Threshold {}\n\n".format(old_th3))
    filehandle.writelines("%s\n" % p for p in total_average_inc_batch_power3)
    filehandle.write("\n")
    filehandle.write("LoadInc Threshold {}\n\n".format(sim.network_threshold))
    filehandle.writelines("%s\n" % p for p in total_average_inc_batch_power4)
    filehandle.write("\n")

#plot for activated nodes
plt.plot(inc_nodes_mean,marker='o', label = "No-nfvLB")
plt.plot(inc_batch_nodes_mean, marker='v',label = "nfvLB Threshold = {}".format(old_th))
plt.plot(inc_batch_nodes_mean2,marker='h', label = "nfvLB Threshold = {}".format(old_th2))
plt.plot(inc_batch_nodes_mean3,marker='h', label = "nfvLB Threshold = {}".format(old_th3))
plt.plot(inc_batch_nodes_mean4,marker='h', label = "nfvLB Threshold = {}".format(sim.network_threshold))
plt.plot(batch_nodes_mean,marker='^', label = "PureBatch-nfvLB")
#plt.xticks(numpy.arange(0, 24, 1))
#plt.yticks(numpy.arange(0, 4,1))
plt.ylabel('Activated Nodes')
plt.xlabel("Time of the day")
plt.legend(loc="upper left",prop={'size': 6})
plt.grid()
plt.savefig('/home/hextinini/Área de Trabalho/nfv_cp/nodes{}.png'.format(number_of_rrhs), bbox_inches='tight')
#plt.show()
plt.clf()

#plot for activated DUs
plt.plot(inc_dus_mean,marker='o', label = "No-nfvLB")
plt.plot(inc_batch_dus_mean,marker='v', label = "nfvLB Threshold = {}".format(old_th))
plt.plot(inc_batch_dus_mean2,marker='h', label = "nfvLB Threshold = {}".format(old_th2))
plt.plot(inc_batch_dus_mean3,marker='h', label = "nfvLB Threshold = {}".format(old_th3))
plt.plot(inc_batch_dus_mean4,marker='h', label = "nfvLB Threshold = {}".format(sim.network_threshold))
plt.plot(batch_dus_mean,marker='^', label = "PureBatch-nfvLB")
#plt.xticks(numpy.arange(0, 24, 1))
#plt.yticks(numpy.arange(0, 10,1))
plt.ylabel('Activated DUs')
plt.xlabel("Time of the day")
plt.legend(loc="upper left",prop={'size': 6})
plt.grid()
plt.savefig('/home/hextinini/Área de Trabalho/nfv_cp/dus{}.png'.format(number_of_rrhs), bbox_inches='tight')
#plt.show()
plt.clf()

#plot for activated lambdas
plt.plot(inc_lambdas_mean,marker='o', label = "No-nfvLB")
plt.plot(inc_batch_lambdas_mean,marker='v', label = "nfvLB Threshold = {}".format(old_th))
plt.plot(inc_batch_lambdas_mean2,marker='h', label = "nfvLB Threshold = {}".format(old_th2))
plt.plot(inc_batch_lambdas_mean3,marker='h', label = "nfvLB Threshold = {}".format(old_th3))
plt.plot(inc_batch_lambdas_mean4,marker='h', label = "nfvLB Threshold = {}".format(sim.network_threshold))
plt.plot(batch_lambdas_mean,marker='^', label = "PureBatch-nfvLB")
#plt.xticks(numpy.arange(0, 24, 1))
#plt.yticks(numpy.arange(0, 5,1))
plt.ylabel('Activated lambdas')
plt.xlabel("Time of the day")
plt.legend(loc="upper left",prop={'size': 6})
plt.grid()
plt.savefig('/home/hextinini/Área de Trabalho/nfv_cp/lambdas{}.png'.format(number_of_rrhs), bbox_inches='tight')
#plt.show()
plt.clf()

#plot for redirected RRHs
plt.plot(inc_redir_mean,marker='o', label = "No-nfvLB")
plt.plot(inc_batch_redir_mean,marker='v', label = "nfvLB Threshold = {}".format(old_th))
plt.plot(inc_batch_redir_mean2,marker='h', label = "nfvLB Threshold = {}".format(old_th2))
plt.plot(inc_batch_redir_mean3,marker='h', label = "nfvLB Threshold = {}".format(old_th3))
plt.plot(inc_batch_redir_mean4,marker='h', label = "nfvLB Threshold = {}".format(sim.network_threshold))
plt.plot(batch_redir_mean,marker='^', label = "PureBatch-nfvLB")
#plt.xticks(numpy.arange(0, 24, 1))
#plt.yticks(numpy.arange(0, 500,50))
plt.ylabel('Redirected RRHs')
plt.xlabel("Time of the day")
plt.legend(loc="upper left",prop={'size': 6})
plt.grid()
plt.savefig('/home/hextinini/Área de Trabalho/nfv_cp/redirected{}.png'.format(number_of_rrhs), bbox_inches='tight')
#plt.show()
plt.clf()

#plot for activated switches
plt.plot(inc_switches_mean,marker='o', label = "No-nfvLB")
plt.plot(inc_batch_switches_mean,marker='v', label = "nfvLB Threshold = {}".format(old_th))
plt.plot(inc_batch_switches_mean2,marker='h', label = "nfvLB Threshold = {}".format(old_th2))
plt.plot(inc_batch_switches_mean3,marker='h', label = "nfvLB Threshold = {}".format(old_th3))
plt.plot(inc_batch_switches_mean4,marker='h', label = "nfvLB Threshold = {}".format(sim.network_threshold))
plt.plot(batch_switches_mean,marker='^', label = "PureBatch-nfvLB")
#plt.xticks(numpy.arange(0, 24, 1))
#plt.yticks(numpy.arange(0, 5,0.5))
plt.ylabel('Activated Switches')
plt.xlabel("Time of the day")
plt.legend(loc="upper left",prop={'size': 6})
plt.grid()
plt.savefig('/home/hextinini/Área de Trabalho/nfv_cp/switches{}.png'.format(number_of_rrhs), bbox_inches='tight')
#plt.show()
plt.clf()

#plot for blocked RRHs
plt.plot(inc_blocked_mean,marker='o', label = "No-nfvLB")
plt.plot(inc_batch_blocked_mean,marker='v', label = "nfvLB Threshold = {}".format(old_th))
plt.plot(inc_batch_blocked_mean2,marker='h', label = "nfvLB Threshold = {}".format(old_th2))
plt.plot(inc_batch_blocked_mean3,marker='h', label = "nfvLB Threshold = {}".format(old_th3))
plt.plot(inc_batch_blocked_mean4,marker='h', label = "nfvLB Threshold = {}".format(sim.network_threshold))
plt.plot(batch_blocked_mean,marker='^', label = "PureBatch-nfvLB")
#plt.xticks(numpy.arange(0, 24, 1))
#plt.yticks(numpy.arange(0, 30,5))
plt.ylabel('Blocked RRHs')
plt.xlabel("Time of the day")
plt.legend(loc="upper left",prop={'size': 6})
plt.grid()
plt.savefig('/home/hextinini/Área de Trabalho/nfv_cp/blocked{}.png'.format(number_of_rrhs), bbox_inches='tight')
#plt.show()
plt.clf()

#plot for solution times
plt.plot(inc_time_mean,marker='o', label = "No-nfvLB")
plt.plot(inc_batch_time_mean,marker='v', label = "nfvLB Threshold = {}".format(old_th))
plt.plot(inc_batch_time_mean2,marker='h', label = "nfvLB Threshold = {}".format(old_th2))
plt.plot(inc_batch_time_mean3,marker='h', label = "nfvLB Threshold = {}".format(old_th3))
plt.plot(inc_batch_time_mean4,marker='h', label = "nfvLB Threshold = {}".format(sim.network_threshold))
plt.plot(batch_time_mean,marker='^', label = "PureBatch-nfvLB")
#plt.xticks(numpy.arange(0, 24, 1))
#plt.yticks(numpy.arange(0, 1, 0.05))
plt.ylabel('Solution Time')
plt.xlabel("Time of the day")
plt.legend(loc="upper left",prop={'size': 6})
plt.grid()
plt.savefig('/home/hextinini/Área de Trabalho/nfv_cp/solution_time{}.png'.format(number_of_rrhs), bbox_inches='tight')
#plt.show()
plt.clf()
print("Redirected")
print(batch_redir_mean)
