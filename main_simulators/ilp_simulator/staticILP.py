import simpy
import functools
import random as np
import time
from enum import Enum
import numpy
from scipy.stats import norm
import matplotlib.pyplot as plt
#import batch_teste as lp
import icc19ILP as plp
import copy
import sys
import pdb#debugging module
import importlib#to reload modules
import simulator as sim

#log the results
def logResults(dest_file):
	with open(dest_file,'w') as filehandle:  
		filehandle.write("Power\n\n")
		filehandle.writelines("%s\n" % p for p in power)
		filehandle.write("\n")
		filehandle.write("Redirected\n\n")
		filehandle.writelines("%s\n" % p for p in redirected)
		filehandle.write("\n")   
		filehandle.write("Lambda usage\n\n")
		filehandle.writelines("%s\n" % p for p in lambda_usage)
		filehandle.write("\n")
		filehandle.write("VDUs usage\n\n")
		filehandle.writelines("%s\n" % p for p in proc_usage)
		filehandle.write("\n")
		filehandle.write("Execution time\n\n")
		filehandle.writelines("%s\n" % p for p in execution_time)
		filehandle.write("\n")
		filehandle.write("Activated nodes\n\n")
		filehandle.writelines("%s\n" % p for p in activated_nodes)
		filehandle.write("\n")
		filehandle.write("Activated lambdas\n\n")
		filehandle.writelines("%s\n" % p for p in activated_lambdas)
		filehandle.write("\n")
		filehandle.write("Activated dus\n\n")
		filehandle.writelines("%s\n" % p for p in activated_dus)
		filehandle.write("\n")
		filehandle.write("Activated switches\n\n")
		filehandle.writelines("%s\n" % p for p in activated_switchs)
		filehandle.write("\n")
		filehandle.write("Cloud use\n\n")
		filehandle.writelines("%s\n" % p for p in cloud_use)
		filehandle.write("\n")
		filehandle.write("Fog use\n\n")
		filehandle.writelines("%s\n" % p for p in fog_use)
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
	du_usage = 0
	#counts the active DUs
	for i in range(len(ilp.du_state)):
		du_usage += sum(ilp.du_state[i])*sim.dus_capacity[i]
	#print("Active DUs {}".format(plp.du_state))
	#print("Processing Usage {}".format(du_usage))
	return du_usage

#initial number of RRHs
number_of_rrhs = 5
#increment of each run
rrhs_increment = 5
#number of executions
exec_number = 12

#metrics
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
act_cloud = 0
act_fog = 0
#util class
util = plp.Util()
#start executions
for i in range(exec_number):
	print("Execution {} of {} RRHs".format(i, number_of_rrhs))
	#global act_cloud, act_fog
	#count lambdas and VDUs
	count_lambdas = 0
	count_dus = 0
	count_nodes = 0
	count_switches = 0
	#to keep the variables of the ILP solution
	solution = None
	antenas = util.newCreateRRHs(number_of_rrhs)
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
		cost = util.getPowerConsumption()
		power.append(cost)
		execution_time.append(solution.solve_details.time)
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
		number_of_rrhs += rrhs_increment
		importlib.reload(plp)
#print(plp.du_processing)
#print(plp.lambda_node)
	#print(dus_total_capacity)
	
logResults('/home/tinini/Área de Trabalho/logsElsevier/staticMinRedir/outputs.txt')

