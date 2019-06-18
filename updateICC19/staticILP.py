import simpy
import functools
import random as np
import time
from enum import Enum
import numpy
from scipy.stats import norm
import matplotlib.pyplot as plt
#import batch_teste as lp
import pureBatchILP as plp
import copy
import sys
import pdb#debugging module
import importlib#to reload modules
import incrementalWithBatchILP as sim

#initial number of RRHs
minimum_rrhs = 5
number_of_rrhs = 5
#increment of each run
rrhs_increment = 5
#number of executions
exec_number = 2
#down time of live migration
lm_downtime = 1.5
#array of RRHs to be solved
rrhs_array = []
for i in range(42):
	rrhs_array.append(i)
#for i in range(exec_number):
#	rrhs_array.append(number_of_rrhs)
#	number_of_rrhs += rrhs_increment
#number_of_rrhs -= rrhs_increment
#for i in range(exec_number):
#	if number_of_rrhs > rrhs_array[0] :
#		number_of_rrhs -= rrhs_increment
#		rrhs_array.append(number_of_rrhs)
#print(rrhs_array)

#numbers of executions
amount_exec = 7

#metrics for the average calculation of the static case
power_static = []
execution_static = []
redirected_static = []
activated_nodes_static = []
activated_lambdas_static = []
activated_dus_static = []
activated_switches_static = []
cloud_use_static = []
fog_use_static = []
usage_lambda = []
usage_du = []

#metrics
power = []
redirected = []
external_migrations = 0
migrations = []
total_vm_migrations_time = {}
total_down_time = {}
lambda_usage = []
proc_usage = []
execution_time = []
activated_nodes = []
activated_lambdas = []
activated_dus = []
activated_switchs = []
cloud_use = []
fog_use = []
act_cloud = 0
act_fog = 0
#util class
util = plp.Util()

#log the results
def logResults(dest_file):
	with open(dest_file,'w') as filehandle:  
		filehandle.write("Power\n\n")
		filehandle.writelines("%s\n" % p for p in average_batch_power)
		filehandle.write("\n")
		filehandle.write("Redirected\n\n")
		filehandle.writelines("%s\n" % p for p in average_redirected)
		filehandle.write("\n")   
		filehandle.write("Activated nodes\n\n")
		filehandle.writelines("%s\n" % p for p in average_act_nodes)
		filehandle.write("\n")
		filehandle.write("Activated lambdas\n\n")
		filehandle.writelines("%s\n" % p for p in average_act_lambdas)
		filehandle.write("\n")
		filehandle.write("Activated dus\n\n")
		filehandle.writelines("%s\n" % p for p in average_act_dus)
		filehandle.write("\n")
		filehandle.write("Activated switches\n\n")
		filehandle.writelines("%s\n" % p for p in average_act_switches)
		filehandle.write("\n")
		filehandle.write("Cloud use\n\n")
		filehandle.writelines("%s\n" % p for p in average_cloud_use)
		filehandle.write("\n")
		filehandle.write("Fog use\n\n")
		filehandle.writelines("%s\n" % p for p in average_fog_use)
		filehandle.write("\n")
		filehandle.write("Lamba usage\n\n")
		filehandle.writelines("%s\n" % p for p in average_lambda_usage)
		filehandle.write("\n")
		filehandle.write("VDUs usage\n\n")
		filehandle.writelines("%s\n" % p for p in average_du_usage)
		filehandle.write("\n")
		filehandle.write("Execution time\n\n")
		filehandle.writelines("%s\n" % p for p in average_execution_time)
		filehandle.write("\n")

def countNodes(ilp):
	global act_cloud, act_fog
	for i in range(len(ilp.nodeState)):
		if ilp.nodeState[i] == 1:
			if i == 0:
				act_cloud += 1
			else:
				act_fog += 1

#calculate the usage of each processing node
def getProcUsage(ilp):
	total_dus_capacity = sum(sim.dus_capacity)
	du_usage = 0
	#counts the active DUs
	for i in range(len(ilp.du_state)):
		du_usage += sum(ilp.du_state[i])#*sim.dus_capacity[i]
	#print("Active DUs {}".format(plp.du_state))
	#print("Processing Usage {}".format(du_usage))
	return du_usage/total_dus_capacity

#count external migration for only batch case - this method considers each vBBU migrated to account
def extSingleMigrations(ilp_module, copy_state, run):
	global external_migrations
	external_migrations = 0
	migrating_vpons = 10000
	for i in ilp_module.nodes:
		print(i)
		#print(copy_state[i])
		#print(ilp_module.rrhs_on_nodes[i])
		if copy_state[i] > ilp_module.rrhs_on_nodes[i] and copy_state[0] < ilp_module.rrhs_on_nodes[0]:
			#print(copy_state[i])
			#print(ilp_module.rrhs_on_nodes[i])
			diff = copy_state[i] - ilp_module.rrhs_on_nodes[i]
			total_down_time[run].append(diff*lm_downtime)
			external_migrations += diff
			total_vm_migrations_time[run].append((diff*614.4)/migrating_vpons)
			#print("paaa", diff)
			#print(total_down_time)
	migrations.append(external_migrations)

network_copy = None
cloud_before = []
cloud_after = []
nodes_before = {}
nodes_after = {}
#for i in plp.nodes:
#	nodes_before[i] = []
#	nodes_after[i] = []
count = 1

#set the maximum load for a simulated scenario given the vdus capacity and the lambdas
def setMaximumLoad(cloud_vdu, fog_vdu, number_of_fogs, number_of_lambdas):
	total_fog = fog_vdu*number_of_lambdas*number_of_fogs
	total_vdus_load = total_fog+(cloud_vdu*number_of_lambdas)
	return total_vdus_load

#keep results of each iteration
pwr = []
redir = []
exec_t = []
c_nodes = []
c_lambdas = []
c_dus = []
c_switches = []
l_usage = []
d_usage = []
a_cloud = []
a_fog = []

#begin the simulations varying number of fog nodes
#initial amount of resources
for e in range(exec_number):
	power = []
	redirected = []
	lambda_usage = []
	proc_usage = []
	execution_time = []
	activated_nodes = []
	activated_lambdas = []
	activated_dus = []
	activated_switchs = []
	cloud_use = []
	fog_use = []
	print("Primal Execution # {}".format(e))
	number_of_nodes = 2
	number_of_lambdas = 3
	for m in range(amount_exec):
		#count lambdas and VDUs
		count_lambdas = 0
		count_dus = 0
		count_nodes = 0
		count_switches = 0
		rrhs_amount = setMaximumLoad(3, 1, number_of_nodes-1, number_of_lambdas)
		solution = None
		antenas = util.newCreateRRHs(rrhs_amount, number_of_nodes)
		plp.setInputParameters(number_of_nodes, number_of_lambdas, plp.cloud_du_capacity, 
		plp.fog_du_capacity, plp.cloud_cost, plp.fog_cost, plp.line_card_cost, plp.switchCost, plp.switch_band, plp.wavelengthCapacity)
		print("Execution of {} RRHs {} Nodes and {} Lambdas".format(rrhs_amount, number_of_nodes, number_of_lambdas))
		#print("DUs", plp.du_processing)
		#print("Lambdas", plp.wavelength_capacity)
		ilp = plp.ILP(antenas, range(len(antenas)), plp.nodes, plp.lambdas)
		solution = ilp.run()
		if solution != None:
			solution_values = ilp.return_solution_values()
			ilp.updateValues(solution_values)
			#if count > 1:
			#	print("hi", plp.du_processing)
			#	extSingleMigrations(plp, network_copy, i)
			cost = util.getPowerConsumption()
			power.append(cost)
			execution_time.append(solution.solve_details.time)
			print("Time: {}".format(solution.solve_details.time))
			countNodes(plp)
			if solution_values.var_k:
				redirected.append(len(solution_values.var_k))
			else:
				redirected.append(0)
			for i in plp.nodeState:
				if i == 1:
					count_nodes += 1
			activated_nodes.append(count_nodes)
			for i in plp.lambda_state:
				if i == 1:
					count_lambdas += 1
			activated_lambdas.append(count_lambdas)
			for i in plp.du_state:
				for j in i:
					if j == 1:
						count_dus += 1
			activated_dus.append(count_dus)
			for i in plp.switch_state:
				if i == 1:
					count_switches += 1
			activated_switchs.append(count_switches)
			#count DUs and lambdas usage
			if count_lambdas > 0:
				lambda_usage.append((number_of_rrhs*614.4)/(count_lambdas*10000.0))
			if count_dus > 0:
				proc_usage.append(number_of_rrhs/getProcUsage(plp))
			if act_cloud:
				cloud_use.append(act_cloud)
			else:
				cloud_use.append(0)
			act_cloud = 0
			if act_fog:
				fog_use.append(act_fog)
			else:
				fog_use.append(0)
			act_fog = 0
			
			#print(total_down_time)
			#number_of_rrhs += rrhs_increment
			network_copy = copy.copy(plp.rrhs_on_nodes)
			importlib.reload(plp)
			count += 1
			number_of_nodes += 1
			number_of_lambdas += 1
	power_static.append(copy.copy(power))
	execution_static.append(copy.copy(execution_time))
	redirected_static.append(copy.copy(redirected))
	activated_nodes_static.append(copy.copy(activated_nodes))
	activated_lambdas_static.append(copy.copy(activated_lambdas))
	activated_dus_static.append(copy.copy(activated_dus))
	activated_switches_static.append(copy.copy(activated_switchs))
	cloud_use_static.append(copy.copy(cloud_use))
	fog_use_static.append(copy.copy(fog_use))
	usage_lambda.append(copy.copy(lambda_usage))
	usage_du.append(copy.copy(proc_usage))
	print("exec {} {}".format(m,power_static))

average_batch_power = [float(sum(col))/len(col) for col in zip(*power_static)]
average_execution_time = [float(sum(col))/len(col) for col in zip(*execution_static)]
average_redirected = [float(sum(col))/len(col) for col in zip(*redirected_static)]
average_act_nodes = [float(sum(col))/len(col) for col in zip(*activated_nodes_static)]
average_act_lambdas = [float(sum(col))/len(col) for col in zip(*activated_lambdas_static)]
average_act_dus = [float(sum(col))/len(col) for col in zip(*activated_dus_static)]
average_act_switches = [float(sum(col))/len(col) for col in zip(*activated_switches_static)]
average_cloud_use = [float(sum(col))/len(col) for col in zip(*cloud_use_static)]
average_fog_use = [float(sum(col))/len(col) for col in zip(*fog_use_static)]
average_lambda_usage = [float(sum(col))/len(col) for col in zip(*usage_lambda)]
average_du_usage = [float(sum(col))/len(col) for col in zip(*usage_du)]

print(average_batch_power)

'''
#executions that goes up and then goes down in the number of RRHs
#start executions
for i in range(amount_exec):
	for i in range(len(rrhs_array)):
		#migrations[i] = []
		total_vm_migrations_time[i] = []
		total_down_time[i] = []
		#to keep the network state of the last solution in order to account the migrations
		#global act_cloud, act_fog
		#count lambdas and VDUs
		count_lambdas = 0
		count_dus = 0
		count_nodes = 0
		count_switches = 0
		#to keep the variables of the ILP solution
		solution = None
		antenas = util.newCreateRRHs(rrhs_array[i])
		print("Execution of {} RRHs".format(rrhs_array[i]))
		#for i in antenas:
		#	print(i.rrhs_matrix)
		#for i in range(len(antenas)):
		#	print(antenas[i].rrhs_matrix)
		np.shuffle(antenas)
		ilp = plp.ILP(antenas, range(len(antenas)), plp.nodes, plp.lambdas)
		solution = ilp.run()
		if solution != None:
			solution_values = ilp.return_solution_values()
			ilp.updateValues(solution_values)
			if count > 1:
				extSingleMigrations(plp, network_copy, i)
			cost = util.getPowerConsumption()
			power.append(cost)
			execution_time.append(solution.solve_details.time)
			print("Time: {}".format(solution.solve_details.time))
			countNodes(plp)
			if solution_values.var_k:
				redirected.append(len(solution_values.var_k))
			else:
				redirected.append(0)
			for i in plp.nodeState:
				if i == 1:
					count_nodes += 1
			activated_nodes.append(count_nodes)
			for i in plp.lambda_state:
				if i == 1:
					count_lambdas += 1
			activated_lambdas.append(count_lambdas)
			for i in plp.du_state:
				for j in i:
					if j == 1:
						count_dus += 1
			activated_dus.append(count_dus)
			for i in plp.switch_state:
				if i == 1:
					count_switches += 1
			activated_switchs.append(count_switches)
			#count DUs and lambdas usage
			if count_lambdas > 0:
				lambda_usage.append((number_of_rrhs*614.4)/(count_lambdas*10000.0))
			if count_dus > 0:
				proc_usage.append(number_of_rrhs/getProcUsage(plp))
			if act_cloud:
				cloud_use.append(act_cloud)
			else:
				cloud_use.append(0)
			act_cloud = 0
			if act_fog:
				fog_use.append(act_fog)
			else:
				fog_use.append(0)
			act_fog = 0
			power_static.append(copy.copy(power))
			execution_static.append(copy.copy(execution_time))
			redirected_static.append(copy.copy(redirected))
			activated_nodes_static.append(copy.copy(activated_nodes))
			activated_lambdas_static.append(copy.copy(activated_lambdas))
			activated_dus_static.append(copy.copy(activated_dus))
			activated_switches_static.append(copy.copy(activated_switchs))
			cloud_use_static.append(copy.copy(cloud_use))
			fog_use_static.append(copy.copy(fog_use))
			#print(total_down_time)
			#number_of_rrhs += rrhs_increment
			network_copy = copy.copy(plp.rrhs_on_nodes)
			importlib.reload(plp)
			count += 1
'''





'''
#executions that goes up and then goes down in the number of RRHs
#start executions
for i in range(len(rrhs_array)):
	#migrations[i] = []
	total_vm_migrations_time[i] = []
	total_down_time[i] = []
	#to keep the network state of the last solution in order to account the migrations
	#global act_cloud, act_fog
	#count lambdas and VDUs
	count_lambdas = 0
	count_dus = 0
	count_nodes = 0
	count_switches = 0
	#to keep the variables of the ILP solution
	solution = None
	antenas = util.newCreateRRHs(rrhs_array[i])
	print("Execution of {} RRHs".format(rrhs_array[i]))
	#for i in antenas:
	#	print(i.rrhs_matrix)
	#for i in range(len(antenas)):
	#	print(antenas[i].rrhs_matrix)
	np.shuffle(antenas)
	ilp = plp.ILP(antenas, range(len(antenas)), plp.nodes, plp.lambdas)
	solution = ilp.run()
	if solution != None:
		solution_values = ilp.return_solution_values()
		ilp.updateValues(solution_values)
		if count > 1:
			extSingleMigrations(plp, network_copy, i)
		cost = util.getPowerConsumption()
		power.append(cost)
		execution_time.append(solution.solve_details.time)
		print("Time: {}".format(solution.solve_details.time))
		countNodes(plp)
		if solution_values.var_k:
			redirected.append(len(solution_values.var_k))
		else:
			redirected.append(0)
		for i in plp.nodeState:
			if i == 1:
				count_nodes += 1
		activated_nodes.append(count_nodes)
		for i in plp.lambda_state:
			if i == 1:
				count_lambdas += 1
		activated_lambdas.append(count_lambdas)
		for i in plp.du_state:
			for j in i:
				if j == 1:
					count_dus += 1
		activated_dus.append(count_dus)
		for i in plp.switch_state:
			if i == 1:
				count_switches += 1
		activated_switchs.append(count_switches)
		#count DUs and lambdas usage
		if count_lambdas > 0:
			lambda_usage.append((number_of_rrhs*614.4)/(count_lambdas*10000.0))
		if count_dus > 0:
			proc_usage.append(number_of_rrhs/getProcUsage(plp))
		if act_cloud:
			cloud_use.append(act_cloud)
		else:
			cloud_use.append(0)
		act_cloud = 0
		if act_fog:
			fog_use.append(act_fog)
		else:
			fog_use.append(0)
		act_fog = 0
		#print(total_down_time)
		#number_of_rrhs += rrhs_increment
		network_copy = copy.copy(plp.rrhs_on_nodes)
		importlib.reload(plp)
		count += 1
'''
#for i in migrations:
#	print(migrations[i])
#print(plp.du_processing)
#print(plp.lambda_node)
	#print(dus_total_capacity)
#print(migrations)
logResults('/home/tinini/Área de Trabalho/logsTeseILP/outputsMinRedir.txt')

