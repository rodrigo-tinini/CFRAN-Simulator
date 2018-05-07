#running incremental ILP for incremental number of RRHs
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
import simDynamicTemporalRRH as sim

#util class
util = sim.Util()
#keep the power consumption
power_consumption = []
inc_power_consumption = []
#to count the activated resources
activated_nodes, activated_lambdas, activated_dus, activated_switchs, redirected = ([] for i in range(5))
#to count the activated resources
inc_activated_nodes, inc_activated_lambdas, inc_activated_dus, inc_activated_switchs, inc_redirected = ([] for i in range(5))
#to control the number of RRHs in each run
r = range(1,50)

#method of the batch sequential scheduling
def seqBatch():
	count_nodes, count_lambdas, count_dus, count_switches = (0 for i in range(4))
	#list of RRHs to be scheduled
	rrhs = []
	#create the RRHs
	for i in r:
		rrhs.append(util.createRRHs(i,[],[],[]))
	#calls the ILP for each set of RRHs
	for i in rrhs:
		ilp = plp.ILP(i, range(len(i)), plp.nodes, plp.lambdas)
		s = ilp.run()
		#print(lp.nodeState)
		if s != None:
			#print("Optimal solution is: {}".format(s.objective_value))
			sol = ilp.return_solution_values()
			ilp.updateValues(sol)
			if redirected:
				redirected.append(sum((redirected[-1], len(sol.var_k))))
			else:
				redirected.append(len(sol.var_k))
			power_consumption.append(util.getPowerConsumption(plp))
			#counts the current activated nodes, lambdas, DUs and switches
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
			ilp.resetValues()
			count_nodes = 0
			count_lambdas = 0
			count_dus = 0
			count_switches = 0
	ilp.resetValues()

#method for the sequential incremental
def seqInc():
	count_nodes, count_lambdas, count_dus, count_switches = (0 for i in range(4))
	rrhs = util.createRRHs(max(r),[],[],[])
	np.shuffle(rrhs)
	#calls the ilp for each rrh on rrhs
	for i in rrhs:
		rrh_list = []
		rrh_list.append(i)
		#print("Matrix is {}".format(i.rrhs_matrix))
		ilp = plp.ILP(rrh_list, range(0,1), plp.nodes, plp.lambdas)
		s = ilp.run()
		if s != None:
			#print("Optimal solution is: {}".format(s.objective_value))
			sol = ilp.return_solution_values()
			ilp.updateValues(sol)
			if inc_redirected:
				inc_redirected.append(sum((inc_redirected[-1], len(sol.var_k))))
			else:
				inc_redirected.append(len(sol.var_k))
			inc_power_consumption.append(util.getPowerConsumption(plp))
			#counts the current activated nodes, lambdas, DUs and switches
			for i in plp.nodeState:
				if i == 1:
					count_nodes += 1
			inc_activated_nodes.append(count_nodes)
			for i in plp.lambda_state:
				if i == 1:
					count_lambdas += 1
			inc_activated_lambdas.append(count_lambdas)
			for i in plp.du_state:
				for j in i:
					if j == 1:
						count_dus += 1
			inc_activated_dus.append(count_dus)
			for i in plp.switch_state:
				if i == 1:
					count_switches += 1
			inc_activated_switchs.append(count_switches)
			count_nodes = 0
			count_lambdas = 0
			count_dus = 0
			count_switches = 0
		else:
			print("noooo")

seqBatch()
seqInc()
print(redirected)
print(inc_redirected)
min_power = min(min(power_consumption), min(inc_power_consumption))
max_power = max(max(power_consumption), max(inc_power_consumption))
min_lambdas = min(min(activated_lambdas), min(inc_activated_lambdas))
max_lambdas = max(max(activated_lambdas), max(inc_activated_lambdas))
min_nodes = min(min(activated_nodes), min(inc_activated_nodes))
max_nodes = max(max(activated_nodes), max(inc_activated_nodes))
min_dus = min(min(activated_dus), min(inc_activated_dus))
max_dus = max(max(activated_dus), max(inc_activated_dus))
min_switch = min(min(activated_switchs), min(inc_activated_switchs))
max_switch = max(max(activated_switchs), max(inc_activated_switchs))
min_redirected = min(min(redirected), min(inc_redirected))
max_redirected = max(max(redirected), max(inc_redirected))

#generate the plots for power consumption
plt.plot(power_consumption, label = "Batch ILP")
plt.plot(inc_power_consumption, label = "Inc ILP")
plt.xticks(numpy.arange(min(range(len(power_consumption))), max(range(len(power_consumption))), 5))
plt.yticks(numpy.arange(min_power, max_power, 500))
plt.ylabel('Power Consumption')
plt.xlabel("Number of ONUs")
plt.legend()
plt.grid()
plt.savefig('/home/tinini/Área de Trabalho/simQuaseFinal/CFRAN-Simulator/experiments/power_consumption.png', bbox_inches='tight')
plt.clf()

#generate the plots for activated lambdas
plt.plot(activated_lambdas, label = "Batch ILP")
plt.plot(inc_activated_lambdas, label = "Inc ILP")
plt.xticks(numpy.arange(min(r), max(r), 5))
plt.yticks(numpy.arange(min_lambdas, max_lambdas+1, 1))
plt.ylabel('Activated Lambdas')
plt.xlabel("Number of ONUs")
plt.legend()
plt.grid()
plt.savefig('/home/tinini/Área de Trabalho/simQuaseFinal/CFRAN-Simulator/experiments/activated_lambdas.png', bbox_inches='tight')
plt.clf()

#generate the plots for activated nodes
plt.plot(activated_nodes, label = "Batch ILP")
plt.plot(inc_activated_nodes, label = "Inc ILP")
plt.xticks(numpy.arange(min(r), max(r), 5))
plt.yticks(numpy.arange(min_nodes, max_nodes+1, 1))
plt.ylabel('Activated Nodes')
plt.xlabel("Number of ONUs")
plt.legend()
plt.grid()
plt.savefig('/home/tinini/Área de Trabalho/simQuaseFinal/CFRAN-Simulator/experiments/activated_nodes.png', bbox_inches='tight')
plt.clf()

#generate the plots for activated DUs
plt.plot(activated_dus, label = "Batch ILP")
plt.plot(inc_activated_dus, label = "Inc ILP")
plt.xticks(numpy.arange(min(r), max(r), 5))
plt.yticks(numpy.arange(min_dus, max_dus, 5))
plt.ylabel('Activated DUs')
plt.xlabel("Number of ONUs")
plt.legend()
plt.grid()
plt.savefig('/home/tinini/Área de Trabalho/simQuaseFinal/CFRAN-Simulator/experiments/activated_DUs.png', bbox_inches='tight')
plt.clf()

#generate the plots for activated Switches
plt.plot(activated_switchs, label = "Batch ILP")
plt.plot(inc_activated_switchs, label = "Inc ILP")
plt.xticks(numpy.arange(min(r), max(r), 5))
plt.yticks(numpy.arange(min_switch, max_switch+1, 1))
plt.ylabel('Activated Switches')
plt.xlabel("Number of ONUs")
plt.legend()
plt.grid()
plt.savefig('/home/tinini/Área de Trabalho/simQuaseFinal/CFRAN-Simulator/experiments/activated_switches.png', bbox_inches='tight')
plt.clf()

#generate the plots for redirected DUs
plt.plot(redirected, label = "Batch ILP")
plt.plot(inc_redirected, label = "Inc ILP")
plt.xticks(numpy.arange(min(r), max(r), 5))
plt.yticks(numpy.arange(min_redirected, max_redirected, 2))
plt.ylabel('Redirected RRHs')
plt.xlabel("Number of ONUs")
plt.legend()
plt.grid()
plt.savefig('/home/tinini/Área de Trabalho/simQuaseFinal/CFRAN-Simulator/experiments/redirected_rrhs.png', bbox_inches='tight')
plt.clf()
