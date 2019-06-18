import simpy
import functools
import random as np
import time
from enum import Enum
import numpy
from scipy.stats import norm
import matplotlib.pyplot as plt
#import batch_teste as lp
import static_relaxILP as plp
import relaxation_module as rlx
import relaxedMainModule as rm
import copy
import sys
import pdb#debugging module
import importlib#to reload modules
#import relaxAlgs as ra

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
amount_exec = 5

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

#post processing method
postProcessingHeuristic = "mostProbability"
#post processing heuristic
relaxHeuristic = "firstFitVPON"
#number of repetitions of the relaxation
relax_amount = 2




logResults('/home/tinini/Área de Trabalho/logsTeseILP/relaxStatic/outputs.txt')

