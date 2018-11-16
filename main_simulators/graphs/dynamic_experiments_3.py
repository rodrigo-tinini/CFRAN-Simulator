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
import simulator as sim
import graph as g

#auxiliar list that keeps the plot markers and colors
markers = ['o', 'v', '^', '<', '>', 's', 'p', 'h', 'H', '+', '<','>']
colors = ['b','g','r','c','m', 'y', 'k', 'r', 'b', 'g', 'r', 'c']

#reset markers and colors
def resetMarkers():
	global markers, colors
	markers = ['o', 'v', '^', '<', '>', 's', 'p', 'h', 'H', '+', '<','>']
	colors = ['b','g','r','c','m', 'y', 'k', 'r', 'b', 'g', 'r', 'c']

#get the blocking probability from the blocked packets and the total generated packets
def calcBlocking(blocked, generated):
	blocking_probability = []
	#iterate over the collection of values in both lists
	for i in range(len(generated)):
		block_list = blocked[i]
		gen_list = generated[i]
		#now, iterate over the lists and calculates the blocking probability
		for j in range(len(gen_list)):
			if gen_list[j] == 0:
				blocking_probability.append(0.0)
			else:
				blocking_probability.append(block_list[j]/gen_list[j])
	return blocking_probability

#Logging
#generate logs
def genLogs(removeHeuristic):
	#iterate over each scheduling policy
	for i in sched_pol:
		#power consumption
		with open('/home/tinini/Área de Trabalho/sbrcLogs/power/power_consumption_{}_{}_{}.txt'.format(i,removeHeuristic, g.rrhs_amount),'a') as filehandle:  
		    filehandle.write("{}\n\n".format(i))
		    filehandle.writelines("%s\n" % p for p in total_power_mean["{}".format(i)])
		    filehandle.write("\n")
		    filehandle.write("\n")
		#blocked
		with open('/home/tinini/Área de Trabalho/sbrcLogs/blocked/blocked_{}_{}_{}.txt'.format(i,removeHeuristic, g.rrhs_amount),'a') as filehandle:  
		    filehandle.write("{}\n\n".format(i))
		    filehandle.writelines("%s\n" % p for p in total_blocking_mean["{}".format(i)])
		    filehandle.write("\n")
		    filehandle.write("\n")
	    #blocking probability
		with open('/home/tinini/Área de Trabalho/sbrcLogs/blocking/blocking_probability_{}_{}_{}.txt'.format(i,removeHeuristic, g.rrhs_amount),'a') as filehandle:  
		    filehandle.write("{}\n\n".format(i))
		    filehandle.writelines("%s\n" % p for p in total_blocking_prob_mean["{}".format(i)])
		    filehandle.write("\n")
		    filehandle.write("\n")
		#execution times
		with open('/home/tinini/Área de Trabalho/sbrcLogs/exec/exec_times_{}_{}_{}.txt'.format(i,removeHeuristic, g.rrhs_amount),'a') as filehandle:  
		    filehandle.write("{}\n\n".format(i))
		    filehandle.writelines("%s\n" % p for p in total_exec_time_mean["{}".format(i)])
		    filehandle.write("\n")
		    filehandle.write("\n")

		#confidence interval
		with open('/home/tinini/Área de Trabalho/sbrcLogs/confidence/power_{}_{}_{}.txt'.format(i,removeHeuristic, g.rrhs_amount),'a') as filehandle:  
		    filehandle.write("{}\n\n".format(i))
		    filehandle.writelines("%s\n" % p for p in power_ci["{}".format(i)])
		    filehandle.write("\n")
		    filehandle.write("\n")
		with open('/home/tinini/Área de Trabalho/sbrcLogs/confidence/blocking_{}_{}_{}.txt'.format(i,removeHeuristic, g.rrhs_amount),'a') as filehandle:  
		    filehandle.write("{}\n\n".format(i))
		    filehandle.writelines("%s\n" % p for p in blocking_ci["{}".format(i)])
		    filehandle.write("\n")
		    filehandle.write("\n")
		with open('/home/tinini/Área de Trabalho/sbrcLogs/confidence/exec_{}_{}_{}.txt'.format(i,removeHeuristic, g.rrhs_amount),'a') as filehandle:  
		    filehandle.write("{}\n\n".format(i))
		    filehandle.writelines("%s\n" % p for p in exec_ci["{}".format(i)])
		    filehandle.write("\n")
		    filehandle.write("\n")

#number of executions
execution_times = 60
#scheduling policies
sched_pol = []
sched_pol.append("all_random")
sched_pol.append("cloud_first_all_fogs")
sched_pol.append("cloud_first_random_fogs")
sched_pol.append("fog_first")
sched_pol.append("most_loaded")
sched_pol.append("least_loaded")
sched_pol.append("least_cost")
sched_pol.append("least_cost_active_ratio")
sched_pol.append("most_loaded_bandwidth")
sched_pol.append("least_loaded_bandwidth")
#sched_pol.append("all_random")
sched_pol.append("big_ratio")
sched_pol.append("small_ratio")
#vpon removing policies
remove_pol = []
remove_pol.append("fog_first")
remove_pol.append("cloud_first")
remove_pol.append("random_remove")

#create the lists to keep the results from
average_power = {}
average_blocking = {}
total_reqs = {}
exec_times = {}
blocking_prob = {}
for i in sched_pol:
	average_power["{}".format(i)] = []
	average_blocking["{}".format(i)] = []
	total_reqs["{}".format(i)] = []
	exec_times["{}".format(i)] = []
	blocking_prob["{}".format(i)] = []

#resets the lists
def resetLists():
	global average_power, average_blocking, total_reqs, exec_times
	#create the lists to keep the results from
	average_power = {}
	average_blocking = {}
	total_reqs = {}
	exec_times = {}
	blocking_pro = {}
	for i in sched_pol:
		average_power["{}".format(i)] = []
		average_blocking["{}".format(i)] = []
		total_reqs["{}".format(i)] = []
		exec_times["{}".format(i)] = []
		blocking_prob["{}".format(i)] = []

#this function reloads the graph module
def reloadGraphModule():
    importlib.reload(g)

#general function to reload modules
def reloadModule(aModule):
    importlib.reload(aModule)

for i in sched_pol:
	print("Executions of heuristic {}".format(i))
	#begin the experiments
	for j in range(execution_times):
		print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
		print("Execution #{} of heuristic {}".format(j,i))
		print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
		#simulation environment
		env = simpy.Environment()
		#create the graph
		gp = g.createGraph()
		#create the control plane
		cp = sim.Control_Plane(env, "Graph", gp, i, "fog_first")
		#traffic generator
		tg = sim.Traffic_Generator(env,sim.distribution, None, cp)
		#create the rrhs
		cp.createRRHs(g.rrhs_amount,env)
		random.shuffle(g.rrhs)
		#create fog nodes
		g.addFogNodes(gp, g.fogs)
		#add RRHs to the graph
		#10 rrhs per fog node
		g.addRRHs(gp, 0, 32, "0")
		g.addRRHs(gp, 32, 64, "1")
		g.addRRHs(gp, 64, 96, "2")
		g.addRRHs(gp, 96, 128, "3")
		g.addRRHs(gp, 128, 160, "4")
		#print(g.rrhs_fog)
		#starts the simulation
		env.run(until = 86401)
		average_power["{}".format(i)].append(sim.average_power_consumption)
		average_blocking["{}".format(i)].append(sim.average_blocking_prob)
		total_reqs["{}".format(i)].append(sim.total_requested)
		exec_times["{}".format(i)].append(sim.average_execution_time)
		blocking_prob["{}".format(i)].append(calcBlocking(average_blocking["{}".format(i)], total_reqs["{}".format(i)]))
		reloadGraphModule()
		reloadModule(sim)

#to calculate the confidence interval
def mean_confidence_interval(data, confidence=0.95):
    a = 1.0*numpy.array(data)
    n = len(a)
    m, se = numpy.mean(a), scipy.stats.sem(a)
    h = se * sp.stats.t._ppf((1+confidence)/2., n-1)
    #return m, m-h, m+h
    return h

#calculate the confidence interval
#lists to keep confidence interval
power_ci = [mean_confidence_interval(col, confidence = 0.95) for col in zip(*average_power)]
blocking_ci = [mean_confidence_interval(col, confidence = 0.95) for col in zip(*blocking_prob)]
exec_ci = [mean_confidence_interval(col, confidence = 0.95) for col in zip(*exec_times)]

#calculate the means from the executions
#power consumption means
total_power_mean = {}
for i in sched_pol:
	total_power_mean["{}".format(i)] = [float(sum(col))/len(col) for col in zip(*average_power["{}".format(i)])]

#blocking means
total_blocking_mean = {}
for i in sched_pol:
	total_blocking_mean["{}".format(i)] = [float(sum(col))/len(col) for col in zip(*average_blocking["{}".format(i)])]

#execution times means
total_exec_time_mean = {}
for i in sched_pol:
	total_exec_time_mean["{}".format(i)] = [float(sum(col))/len(col) for col in zip(*exec_times["{}".format(i)])]

#blocking probability means
total_blocking_prob_mean = {}
for i in sched_pol:
	total_blocking_prob_mean["{}".format(i)] = [float(sum(col))/len(col) for col in zip(*blocking_prob["{}".format(i)])]

genLogs("remove_fog_first")

#plot results
#generate the plots for power consumption
for i in sched_pol:
	plt.plot(total_power_mean["{}".format(i)], color = '{}'.format(colors.pop()),marker='{}'.format(markers.pop()), label = "{}".format(i))
plt.ylabel('Power Consumption')
plt.xlabel("Time of the day")
plt.legend(loc="upper left",prop={'size': 6})
plt.grid()
plt.savefig('/home/tinini/Área de Trabalho/iccSim/CFRAN-Simulator/graphs/plots/power{}_remove_ff.png'.format(g.rrhs_amount), bbox_inches='tight')
#plt.show()
plt.clf()

resetMarkers()
#generate the plots for blocking 
for i in sched_pol:
	plt.plot(total_blocking_mean["{}".format(i)], color = '{}'.format(colors.pop()), marker='{}'.format(markers.pop()), label = "{}".format(i))
plt.ylabel('Blocking Amount')
plt.xlabel("Time of the day")
plt.legend(loc="upper left",prop={'size': 6})
plt.grid()
plt.savefig('/home/tinini/Área de Trabalho/iccSim/CFRAN-Simulator/graphs/plots/blocking{}__remove_ff.png'.format(g.rrhs_amount), bbox_inches='tight')
#plt.show()
plt.clf()

resetMarkers()
#generate the plots for execution times
for i in sched_pol:
	plt.plot(total_exec_time_mean["{}".format(i)], color = '{}'.format(colors.pop()), marker='{}'.format(markers.pop()), label = "{}".format(i))
plt.ylabel('Execution Time')
plt.xlabel("Time of the day")
plt.legend(loc="upper left",prop={'size': 6})
plt.grid()
plt.savefig('/home/tinini/Área de Trabalho/iccSim/CFRAN-Simulator/graphs/plots/execution_time{}__remove_ff.png'.format(g.rrhs_amount), bbox_inches='tight')
#plt.show()
plt.clf()

resetMarkers()
#generate the plots for blocking probability
for i in sched_pol:
	plt.plot(total_blocking_prob_mean["{}".format(i)], color = '{}'.format(colors.pop()), marker='{}'.format(markers.pop()), label = "{}".format(i))
plt.ylabel('Blocking Probability')
plt.xlabel("Time of the day")
plt.legend(loc="upper left",prop={'size': 6})
plt.grid()
plt.savefig('/home/tinini/Área de Trabalho/iccSim/CFRAN-Simulator/graphs/plots/blocking_probability{}_remove_ff.png'.format(g.rrhs_amount), bbox_inches='tight')
#plt.show()
plt.clf()

'''
resetMarkers()
resetLists()

for i in sched_pol:
	print("Executions of heuristic {}".format(i))
	#begin the experiments
	for j in range(execution_times):
		print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
		print("Execution #{} of heuristic {}".format(j,i))
		print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
		#simulation environment
		env = simpy.Environment()
		#create the graph
		gp = g.createGraph()
		#create the control plane
		cp = sim.Control_Plane(env, "Graph", gp, i, "cloud_first")
		#traffic generator
		tg = sim.Traffic_Generator(env,sim.distribution, None, cp)
		#create the rrhs
		cp.createRRHs(g.rrhs_amount,env)
		random.shuffle(g.rrhs)
		#create fog nodes
		g.addFogNodes(gp, g.fogs)
		#add RRHs to the graph
		#10 rrhs per fog node
		g.addRRHs(gp, 0, 32, "0")
		g.addRRHs(gp, 32, 64, "1")
		g.addRRHs(gp, 64, 96, "2")
		g.addRRHs(gp, 96, 128, "3")
		g.addRRHs(gp, 128, 160, "4")
		#print(g.rrhs_fog)
		#starts the simulation
		env.run(until = 86401)
		average_power["{}".format(i)].append(sim.average_power_consumption)
		average_blocking["{}".format(i)].append(sim.average_blocking_prob)
		total_reqs["{}".format(i)].append(sim.total_requested)
		exec_times["{}".format(i)].append(sim.average_execution_time)
		blocking_prob["{}".format(i)].append(calcBlocking(average_blocking["{}".format(i)], total_reqs["{}".format(i)]))
		reloadGraphModule()
		reloadModule(sim)

#calculate the means from the executions
#power consumption means
total_power_mean = {}
for i in sched_pol:
	total_power_mean["{}".format(i)] = [float(sum(col))/len(col) for col in zip(*average_power["{}".format(i)])]

#blocking means
total_blocking_mean = {}
for i in sched_pol:
	total_blocking_mean["{}".format(i)] = [float(sum(col))/len(col) for col in zip(*average_blocking["{}".format(i)])]

#execution times means
total_exec_time_mean = {}
for i in sched_pol:
	total_exec_time_mean["{}".format(i)] = [float(sum(col))/len(col) for col in zip(*exec_times["{}".format(i)])]

#blocking probability means
total_blocking_prob_mean = {}
for i in sched_pol:
	total_blocking_prob_mean["{}".format(i)] = [float(sum(col))/len(col) for col in zip(*blocking_prob["{}".format(i)])]

genLogs("remove_cloud_first")

#plot results
#generate the plots for power consumption
for i in sched_pol:
	plt.plot(total_power_mean["{}".format(i)], color = '{}'.format(colors.pop()),marker='{}'.format(markers.pop()), label = "{}".format(i))
plt.ylabel('Power Consumption')
plt.xlabel("Time of the day")
plt.legend(loc="upper left",prop={'size': 6})
plt.grid()
plt.savefig('/home/tinini/Área de Trabalho/iccSim/CFRAN-Simulator/graphs/plots/power{}_remove_cf.png'.format(g.rrhs_amount), bbox_inches='tight')
#plt.show()
plt.clf()

resetMarkers()

#generate the plots for blocking
for i in sched_pol:
	plt.plot(total_blocking_mean["{}".format(i)], color = '{}'.format(colors.pop()), marker='{}'.format(markers.pop()), label = "{}".format(i))
plt.ylabel('Blocking Amount')
plt.xlabel("Time of the day")
plt.legend(loc="upper left",prop={'size': 6})
plt.grid()
plt.savefig('/home/tinini/Área de Trabalho/iccSim/CFRAN-Simulator/graphs/plots/blocking{}_remove_cf.png'.format(g.rrhs_amount), bbox_inches='tight')
#plt.show()
plt.clf()

resetMarkers()
#generate the plots for execution times
for i in sched_pol:
	plt.plot(total_exec_time_mean["{}".format(i)], color = '{}'.format(colors.pop()), marker='{}'.format(markers.pop()), label = "{}".format(i))
plt.ylabel('Execution Time')
plt.xlabel("Time of the day")
plt.legend(loc="upper left",prop={'size': 6})
plt.grid()
plt.savefig('/home/tinini/Área de Trabalho/iccSim/CFRAN-Simulator/graphs/plots/execution_time{}__remove_cf.png'.format(g.rrhs_amount), bbox_inches='tight')
#plt.show()
plt.clf()

resetMarkers()
#generate the plots for blocking probability
for i in sched_pol:
	plt.plot(total_blocking_prob_mean["{}".format(i)], color = '{}'.format(colors.pop()), marker='{}'.format(markers.pop()), label = "{}".format(i))
plt.ylabel('Blocking Probability')
plt.xlabel("Time of the day")
plt.legend(loc="upper left",prop={'size': 6})
plt.grid()
plt.savefig('/home/tinini/Área de Trabalho/iccSim/CFRAN-Simulator/graphs/plots/blocking_probability{}_remove_cf.png'.format(g.rrhs_amount), bbox_inches='tight')
#plt.show()
plt.clf()

resetMarkers()
resetLists()

for i in sched_pol:
	print("Executions of heuristic {}".format(i))
	#begin the experiments
	for j in range(execution_times):
		print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
		print("Execution #{} of heuristic {}".format(j,i))
		print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
		#simulation environment
		env = simpy.Environment()
		#create the graph
		gp = g.createGraph()
		#create the control plane
		cp = sim.Control_Plane(env, "Graph", gp, i, "random_remove")
		#traffic generator
		tg = sim.Traffic_Generator(env,sim.distribution, None, cp)
		#create the rrhs
		cp.createRRHs(g.rrhs_amount,env)
		random.shuffle(g.rrhs)
		#create fog nodes
		g.addFogNodes(gp, g.fogs)
		#add RRHs to the graph
		#10 rrhs per fog node
		g.addRRHs(gp, 0, 32, "0")
		g.addRRHs(gp, 32, 64, "1")
		g.addRRHs(gp, 64, 96, "2")
		g.addRRHs(gp, 96, 128, "3")
		g.addRRHs(gp, 128, 160, "4")
		#print(g.rrhs_fog)
		#starts the simulation
		env.run(until = 86401)
		average_power["{}".format(i)].append(sim.average_power_consumption)
		average_blocking["{}".format(i)].append(sim.average_blocking_prob)
		total_reqs["{}".format(i)].append(sim.total_requested)
		exec_times["{}".format(i)].append(sim.average_execution_time)
		blocking_prob["{}".format(i)].append(calcBlocking(average_blocking["{}".format(i)], total_reqs["{}".format(i)]))
		reloadGraphModule()
		reloadModule(sim)

#calculate the means from the executions
#power consumption means
total_power_mean = {}
for i in sched_pol:
	total_power_mean["{}".format(i)] = [float(sum(col))/len(col) for col in zip(*average_power["{}".format(i)])]

#blocking means
total_blocking_mean = {}
for i in sched_pol:
	total_blocking_mean["{}".format(i)] = [float(sum(col))/len(col) for col in zip(*average_blocking["{}".format(i)])]

#execution times means
total_exec_time_mean = {}
for i in sched_pol:
	total_exec_time_mean["{}".format(i)] = [float(sum(col))/len(col) for col in zip(*exec_times["{}".format(i)])]

#blocking probability means
total_blocking_prob_mean = {}
for i in sched_pol:
	total_blocking_prob_mean["{}".format(i)] = [float(sum(col))/len(col) for col in zip(*blocking_prob["{}".format(i)])]

genLogs("remove_random")

#plot results
#generate the plots for power consumption
for i in sched_pol:
	plt.plot(total_power_mean["{}".format(i)], color = '{}'.format(colors.pop()),marker='{}'.format(markers.pop()), label = "{}".format(i))
plt.ylabel('Power Consumption')
plt.xlabel("Time of the day")
plt.legend(loc="upper left",prop={'size': 6})
plt.grid()
plt.savefig('/home/tinini/Área de Trabalho/iccSim/CFRAN-Simulator/graphs/plots/power{}_remove_random.png'.format(g.rrhs_amount), bbox_inches='tight')
#plt.show()
plt.clf()

resetMarkers()

#generate the plots for blocking 
for i in sched_pol:
	plt.plot(total_blocking_mean["{}".format(i)], color = '{}'.format(colors.pop()), marker='{}'.format(markers.pop()), label = "{}".format(i))
plt.ylabel('Blocking Amount')
plt.xlabel("Time of the day")
plt.legend(loc="upper left",prop={'size': 6})
plt.grid()
plt.savefig('/home/tinini/Área de Trabalho/iccSim/CFRAN-Simulator/graphs/plots/blocking{}_remove_random.png'.format(g.rrhs_amount), bbox_inches='tight')
#plt.show()
plt.clf()

resetMarkers()
#generate the plots for execution times
for i in sched_pol:
	plt.plot(total_exec_time_mean["{}".format(i)], color = '{}'.format(colors.pop()), marker='{}'.format(markers.pop()), label = "{}".format(i))
plt.ylabel('Execution Time')
plt.xlabel("Time of the day")
plt.legend(loc="upper left",prop={'size': 6})
plt.grid()
plt.savefig('/home/tinini/Área de Trabalho/iccSim/CFRAN-Simulator/graphs/plots/execution_time{}__remove_random.png'.format(g.rrhs_amount), bbox_inches='tight')
#plt.show()
plt.clf()

resetMarkers()
#generate the plots for blocking probability
for i in sched_pol:
	plt.plot(total_blocking_prob_mean["{}".format(i)], color = '{}'.format(colors.pop()), marker='{}'.format(markers.pop()), label = "{}".format(i))
plt.ylabel('Blocking Probability')
plt.xlabel("Time of the day")
plt.legend(loc="upper left",prop={'size': 6})
plt.grid()
plt.savefig('/home/tinini/Área de Trabalho/iccSim/CFRAN-Simulator/graphs/plots/blocking_probability{}_remove_random.png'.format(g.rrhs_amount), bbox_inches='tight')
#plt.show()
plt.clf()
'''

'''
#Logging
#generate logs
def genLogs(removeHeuristic):
	#iterate over each scheduling policy
	for i in sched_pol:
		#power consumption
		with open('/home/tinini/Área de Trabalho/iccSim/CFRAN-Simulator/graphs/logs/power_consumption_{}_{}_{}.txt'.format(i,removeHeuristic, g.rrhs_amount),'a') as filehandle:  
		    filehandle.write("{}\n\n".format(i))
		    filehandle.writelines("%s\n" % p for p in total_power_mean["{}".format(i)])
		    filehandle.write("\n")
		    filehandle.write("\n")
		#blocked
		with open('/home/tinini/Área de Trabalho/iccSim/CFRAN-Simulator/graphs/logs/blocked_{}_{}_{}.txt'.format(i,removeHeuristic, g.rrhs_amount),'a') as filehandle:  
		    filehandle.write("{}\n\n".format(i))
		    filehandle.writelines("%s\n" % p for p in total_blocking_mean["{}".format(i)])
		    filehandle.write("\n")
		    filehandle.write("\n")
	    #blocking probability
		with open('/home/tinini/Área de Trabalho/iccSim/CFRAN-Simulator/graphs/logs/blocking_probability_{}_{}_{}.txt'.format(i,removeHeuristic, g.rrhs_amount),'a') as filehandle:  
		    filehandle.write("{}\n\n".format(i))
		    filehandle.writelines("%s\n" % p for p in total_blocking_prob_mean["{}".format(i)])
		    filehandle.write("\n")
		    filehandle.write("\n")
		#execution times
		with open('/home/tinini/Área de Trabalho/iccSim/CFRAN-Simulator/graphs/logs/exec_times_{}_{}_{}.txt'.format(i,removeHeuristic, g.rrhs_amount),'a') as filehandle:  
		    filehandle.write("{}\n\n".format(i))
		    filehandle.writelines("%s\n" % p for p in total_exec_time_mean["{}".format(i)])
		    filehandle.write("\n")
		    filehandle.write("\n")
'''