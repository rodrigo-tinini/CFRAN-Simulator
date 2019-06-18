import simpy
import functools
import random
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
import builtins#all n=built-in python methods
import operator
import simulator as sim

number_of_runs = 2
current_module = sys.modules[__name__]

batch_power_consumption = []
batch_blocking = []
time_b = []
incremental_power_consumption = []
inc_blocking = []
time_inc = []

def checkNodeCapacity(node, n_state):
	#print("Checking node {}".format(node))
	#print(node)
	#print(n_state.du_processing[node])
	if sum(n_state.du_processing[node]) > 0:
		return True
	else:
		#print("Node {} is empty".format(node))
		return False

def checkNodesLambda(node, n_state):
	if n_state.nodes_lambda[node]:
		return True
	else:
		return False

def getFirstFitVPON(node, n_state):
	for w in n_state.nodes_lambda[node]:
		if checkLambdaCapacity(w, n_state):
			return w

def checkLambdaCapacity(aLambda, n_state):
	if n_state.wavelength_capacity[aLambda] >= n_state.RRHband:
		return True
	else:
		return False

#check if a lambda is free to be allocated on a given node
def checkLambdaNode(node, wavelength, n_state):
	if n_state.lambda_node[wavelength][node] == 1:
		return True
	else:
		return False

#this heuristic must decrease both the VPONs used and the switch intercommunications delay, so, it must minimize the number of active VPONs and VDUs in a processing node
#it has to place as many as possible RRHs into the same VPON and same VDU
def minAll(rrh, solution, n_state):
	blocked_rrhs = []
	for i in solution.var_x:
		#print(n_state.wavelength_capacity)
		#get the RRH and the node, lambda and vdu returned on the relaxation
		r = rrh[i[0]]
		r_node = i[1]
		r_lambda = i[2]
		du = getVarU(i, solution)
		r_du = du[2]
		#print("Solution VPON of RRH {} is {}".format(r.id, r_lambda))
		#allocate the node
		if checkNodeCapacity(r_node, n_state):
			r.node = r_node
		elif checkNodeCapacity(r.fog, n_state):
			r.node = r.fog
		#print("RRH {} has node {}".format(r.id, r.node))
		if r.node == None:
			#print("RRH {} no node".format(r.id))
			r.blocked = True
		#if RRH was not blocked, allocates the VPON
		#now, allocate the VPON minimizing the lambdas used
		if r.blocked == False:
			if not checkNodesLambda(r.node, n_state):
				#take the one in the solution
				if checkLambdaNode(r.node, r_lambda, n_state):
					#use this one
					r.wavelength = r_lambda
				else:
					#take a free vpon
					#if no VPON was found 'til here, get one that is non-allocated
					vpon = getFreeVPON(n_state)
					if vpon != None:
						r.wavelength = vpon
			#if it has, get the first one that can handle the RRH
			else:
				vpon = getFirstFitVPON(r.node, n_state)
				#if a lambda was found, allocate to the RRH
				if vpon != None:
					r.wavelength = vpon
				else:
					#if no VPON was found 'til here, get one that is non-allocated
					vpon = getFreeVPON(n_state)
					if vpon != None:
						r.wavelength = vpon
			if r.wavelength == None:
				r.blocked = True
		#now, allocate the VDU minimizing the VDUs in the node
		if r.blocked == False:
			pass

#this heuristic tries to reduce the switch intercommunication delay, the idea is that it behaves just like the minRedir case
def reduceDelay(rrh, solution, n_state):
	blocked_rrhs = []
	for i in solution.var_x:
		#print(n_state.wavelength_capacity)
		#get the RRH and the node, lambda and vdu returned on the relaxation
		r = rrh[i[0]]
		r_node = i[1]
		r_lambda = i[2]
		du = getVarU(i, solution)
		r_du = du[2]
		#print("Solution VPON of RRH {} is {}".format(r.id, r_lambda))
		#allocate the node
		if checkNodeCapacity(r_node, n_state):
			r.node = r_node
		elif checkNodeCapacity(r.fog, n_state):
			r.node = r.fog
		#print("RRH {} has node {}".format(r.id, r.node))
		if r.node == None:
			#print("RRH {} no node".format(r.id))
			r.blocked = True
		#if RRH was not blocked, allocates the VPON
		#now, tries to allocate the VDU in the solution
		if r.blocked == False:
			#first, tries to allocate the VDU on the solution
			if checkVduCapacity(r_du, r.node, n_state):
				#if the vdu has capacity, check if the switch needs to be used
				if checkSwitch(r_du, r.wavelength):
					#updates the switch capacity and cost
					r.du = r_du
					updateSwitch(r.node, n_state)
				else:
					r.du = r_du
			else:
				r_du = None
				#take a random DU and verify if it the switch is needed
				random_du = getRandomVDU(r.node, n_state, r)
				if type(random_du) is tuple:
					#use the switch
					r.du = random_du[0]
					updateSwitch(r.node, n_state)
				#else:
				elif random_du != None:
					r.du = random_du
				else:
					print("pau aqui1 {} {}".format(random_du, r.du))
			if r.du == None:
				r.blocked = True
				print("pau aqui2")
			else:
				print("r du {}".format(r.du))
		#now, tries to allocate the lambda that equals the VDU allocated to the RRH
		if r.blocked == False:
			if checkVPON(r.du, r.node, n_state):
				if checkLambdaCapacity(r.du, n_state):	
					r.wavelength = r.du
			else:
				#tries to allocate this VPON on the node
				if checkLambdaNode(r.node, r.du, n_state):
					r.wavelength = r.du
				else:
					#the VPON equal to the VDU is not available, tries to allocate any available VPON in the node (if the ndoe has VPONs)
					if not checkNodesLambda(r.node, n_state):
						vpon = getFreeVPON(n_state)
						if vpon != None:
							r.wavelength = vpon
							updateSwitch(r.node, n_state)
					else:
						vpon = getFirstFitVPON(r.node, n_state)
						if vpon != None:
							r.wavelength = vpon
							updateSwitch(r.node, n_state)
			if r.wavelength == None:
				#print("no lambda")
				r.blocked = True
		if r.blocked:
			#print("bloqueou")
			blocked_rrhs.append(r)
		else:
			updateVDU(r.du, r.node, n_state)
			updateVponState(r.node, r.wavelength, n_state)
			updateNode(r.node, n_state)
	return blocked_rrhs

#check if the VPON is allocated on a node
def checkVPON(vpon, node, n_state):
	if vpon in n_state.nodes_lambda[node]:
		return True
	else:
		return False

def firstFitVPON(rrh, solution, n_state):
	blocked_rrhs = []
	#tries to allocate each RRH in the solution
	for i in solution.var_x:
		#print(n_state.wavelength_capacity)
		#get the RRH and the node, lambda and vdu returned on the relaxation
		r = rrh[i[0]]
		r_node = i[1]
		r_lambda = i[2]
		du = getVarU(i, solution)
		r_du = du[2]
		if r.node != None or r.wavelength != None or r.du != None:
			pass
			#print("Already allocated {} ndoe {} lambda {} du {} ".format(r.id, r.node, r.wavelength, r.du))
		else:
			pass
			#print("RRH {} free".format(r.id))
		#print("Solution VPON of RRH {} is {}".format(r.id, r_lambda))
		#allocate the node
		if checkNodeCapacity(r_node, n_state):
			r.node = r_node
		elif checkNodeCapacity(r.fog, n_state):
			r.node = r.fog
		#print("RRH {} has node {}".format(r.id, r.node))
		if r.node == None:
			#print("RRH {} no node".format(r.id))
			r.blocked = True
		#if RRH was not blocked, allocates the VPON
		#first, verify if the node does not have at least one VPON
		if r.blocked == False:
			#print("Checking lambda for RRH {} has node {}".format(r.id, r.node))
			if not checkNodesLambda(r.node, n_state):
				#print("Node {} do not have lambda".format(r.node))
				#take the one in the solution
				if checkLambdaNode(r.node, r_lambda, n_state):
					#use this one
					r.wavelength = r_lambda
					#print("Allocating RRH {} in the solution VPON {}".format(r.id, r_lambda))
				else:
					#take a free vpon
					#if no VPON was found 'til here, get one that is non-allocated
					vpon = getFreeVPON(n_state)
					if vpon != None:
						r.wavelength = vpon
						#print("Allocating RRH {} in the free VPON {}".format(r.id, vpon))
			#if it has, get the first one that can handle the RRH
			else:
				vpon = getFirstFitVPON(r.node, n_state)
				#if a lambda was found, allocate to the RRH
				if vpon != None:
					r.wavelength = vpon
					#print("Allocating RRH {} in the FF VPON {}".format(r.id, vpon))
				else:
					#if no VPON was found 'til here, get one that is non-allocated
					vpon = getFreeVPON(n_state)
					if vpon != None:
						r.wavelength = vpon
						#print("Allocating RRH {} in the free VPON {}".format(r.id, vpon))
			if r.wavelength == None:
				r.blocked = True
		#so far so good, now, write the code to allocate the VDU completely guided by the relaxation solution
		#take the du returned by the relaxation, if it has not capacity, get one randomly
		if r.blocked == False:
			if checkVduCapacity(r_du, r.node, n_state):
				#if the vdu has capacity, check if the switch needs to be used
				if checkSwitch(r_du, r.wavelength):
					#updates the switch capacity and cost
					r.du = r_du
					updateSwitch(r.node, n_state)
				else:
					r.du = r_du
			else:
				#take a random DU and verify if it the switch is needed
				random_du = getRandomVDU(r.node, n_state, r)
				if type(random_du) is tuple:
					#use the switch
					r.du = random_du[0]
					updateSwitch(r.node, n_state)
					if random_du[0] == None:
						print("Tuple none")
				elif random_du != None:
				#else:
					r.du = random_du
					if random_du == None:
						print("Random none")
			if r.du == None:
				r.blocked = True
		if r.blocked:
			blocked_rrhs.append(r)
		else:
			if r.du == None:
				print("Alocando errado o rrh {} com du {}".format(r.id, r.du))
			updateVDU(r.du, r.node, n_state)
			updateVponState(r.node, r.wavelength, n_state)
			updateNode(r.node, n_state)
	if blocked_rrhs:
		pass
		#print("Active is ",len(sim.actives))
		#print("Off is ", len(sim.rrhs))
		#print("Node is",n_state.du_processing)
		#print("Wavelength in node", n_state.nodes_lambda)
		#print("Wavelength capacity", n_state.wavelength_capacity)
		#print("Blocked is RRH {} LAMBDA {} NODE {} DU {} MAT {}".format(r.id,r.wavelength,r.node,r.du, r.rrhs_matrix))
		#verifyDup(r, rrh)
		#for i in rrh:
		#	print("RRH {} NODE {} MAT {}".format(i.id, i.node, i.rrhs_matrix))
		#print("Actives:")
		#for i in rrh:
		#	print("RRH {} NODE {} MAT {}".format(i.id, i.node, i.rrhs_matrix))
		#print("Turned off:")
		#for i in sim.rrhs:
		#	print("RRH {} NODE {} MAT {}".format(i.id, i.node, i.rrhs_matrix))
	return blocked_rrhs

def updateVDU(vdu, node, n_state):
	n_state.du_processing[node][vdu] -= 1
	if n_state.du_state[node][vdu] == 0:
		#du was deactivated - activates it
		n_state.du_state[node][vdu] = 1
		n_state.du_cost[node][vdu] = 0.0

def getRandomVDU(node, n_state, rrh):
	#copy the dus list
	du_copy = copy.copy(n_state.du_processing[node])
	random.shuffle(du_copy)
	for i in range(len(du_copy)):
		#test the vdu
		if checkVduCapacity(i, node, n_state):
			if checkSwitch(i, rrh.wavelength):
				return (i, True)
			else:
				return i

def verifyDup(r, rrh):
	for i in rrh:
		if i.id == r.id:
			print("RRH {} is duplicated".format(r.id))

def updateSwitch(node, n_state):
	n_state.switchBandwidth[node] -= n_state.RRHband
	if n_state.switch_state[node] == 0:
		n_state.switch_state[node] = 1
		n_state.switch_cost[node] = 0.0

def checkVduCapacity(vdu, node, n_state):
	if n_state.du_processing[node][vdu] > 0:
		return True
	else:
		return False

def checkSwitch(vdu, vpon):
	if vdu == vpon:
		return False
	else:
		return True

#check switch capacity
def checkSwitchCapacity(node, n_state):
	if n_state.switchBandwidth[node] >= n_state.RRHband:
		return True
	else:
		return False

def blockLambda(wavelength, node, n_state):
	ln = n_state.lambda_node[wavelength]
	for i in range(len(ln)):
		if i != node:
			ln[i] = 0

def updateVponState(node, vpon, n_state):
	#n_state.wavelength = vpon
	n_state.wavelength_capacity[vpon] -= n_state.RRHband
	if not vpon in n_state.nodes_lambda[node]:
		n_state.nodes_lambda[node].append(vpon)
	if n_state.lambda_state[vpon] == 0:
		n_state.lambda_state[vpon] = 1
		n_state.lc_cost[vpon] = 0
	n_state.nodes_vpons_capacity[node][vpon] = n_state.wavelength_capacity[vpon]
	blockLambda(vpon, node, n_state)

def updateNode(node, n_state):
	#increase the number of RRHs being processed
	n_state.rrhs_on_nodes[node] += 1
	#turn the node on if it is not
	if n_state.nodeState[node] == 0:
		#not activated, updates costs
		n_state.nodeCost[node] = 0
		n_state.nodeState[node] = 1

def getFreeVPON(n_state):
	for j in range(len(n_state.lambda_state)):
		if n_state.lambda_state[j] == 0: #this lambda is available
			return j

#this method returns the u variable given the RRH index
def getVarU(aIndex, solution):
	for i in solution.var_u:
		if i[0] == aIndex[0]:
			return i

#this method runs a batch incrementally - it differs from inc_batch, as, we have a batch to process, but runs the relaxation to it element of the batch
def incrementalRelaxedBatch(rrhs_batch, relaxHeuristic, postProcessingHeuristic, ilp_module, metric, method):
	for r in range(len(rrhs_batch)):
		runIncSched(relaxHeuristic, postProcessingHeuristic, ilp_module, metric, method, rrhs_batch[r])
		del rrhs_batch[r]


#this is the method invoked by the simulator to call the relaxed version of the incremental ILP algorithm
def runIncSched(relaxHeuristic, postProcessingHeuristic, ilp_module, metric, method, r):
	solution_time = 0
	solutions_list = []
	semi_solutions = []
	#create the network states
	for e in range(number_of_runs):
		relaxSol = rm.NetworkState(ilp_module, e)
		solutions_list.append(relaxSol)
	for e in solutions_list:
		print()
		r_copy = None
		r_copy = copy.deepcopy(r)
		antenas = []
		antenas.append(r_copy)
		start = time.time()
		ilp = ilp_module.ILP(antenas, range(len(antenas)), ilp_module.nodes, ilp_module.lambdas, True)
		solution = ilp.run()
		if solution != None:
			solution_values = ilp.return_decision_variables()
			postMethod = getattr(rlx, postProcessingHeuristic)
			postMethod(solution_values, ilp, e)
			relaxMethod = getattr(current_module, relaxHeuristic)
			blocked_rrh = []
			blocked_rrh = relaxMethod(antenas, solution_values, e)
			if blocked_rrh:
				foundSolution = False
				#print("Blocked!",r.id)
			else:
				foundSolution = True
				semi_solutions.append(e)
				e.setMetric("solution_values", solution_values)
				e.setMetric("execution_time", solution.solve_details.time)
				e.setMetric("power", getPowerConsumption(e))
				end = time.time()
				solution_time += end - start
				e.relaxTime = solution_time
	if foundSolution == True:
		#sucs_reqs += 1
		all_solutions = rm.NetworkStateCollection(semi_solutions)
		bestSolution = all_solutions.getBestNetworkState(metric, method)
		#now, updates the main network state (so far I am using the on plp file, which is the ILP module file)
		rm.updateRealNetworkState(bestSolution, ilp_module)
		#updates the execution time of this solution, which is the relaxed ILP solving time + the relaxation scheduling updating procedure
		#solution_time += bestSolution.execution_time
		time_inc.append(solution_time)
		#r.updateWaitTime(env.now)
		#for i in antenas:
		#	env.process(i.run())
		#	actives.append(i)
		#	antenas.remove(i)
		incremental_power_consumption.append(getPowerConsumption(ilp_module))
		#countNodes(ilp_module)
		#URGENTE - MEU ALGORITMO DE PÓS PROCESSAMENTO NÃO FAZ NADA COM ESSA VARIÁVEL, LOGO, ELA SEMPRE ESTARÁ VAZIA
		#ASSIM, PRECISO CRIAR UM MÉTODO PARA VERIFICAR REDIRECIONAMENTO DE DUS E CASO OUTRA VARIÁVEL FIQUE VAZIA PELO
		#ALGORITMO DE PÓS PROCESSAMENTO, CRIAR MÉTODOS PARA CONTABILIZÁ-LA TB
		'''
		if solution_values.var_k:
			redirected_rrhs.append(len(solution_values.var_k))
		else:
			redirected_rrhs.append(0)
		for i in bestSolution.nodeState:
			if i == 1:
				count_nodes += 1
		activated_nodes.append(count_nodes)
		for i in bestSolution.lambda_state:
			if i == 1:
				count_lambdas += 1
		activated_lambdas.append(count_lambdas)
		for i in bestSolution.du_state:
			for j in i:
				if j == 1:
					count_dus += 1
		activated_dus.append(count_dus)
		for i in bestSolution.switch_state:
			if i == 1:
				count_switches += 1
		activated_switchs.append(count_switches)
		#count DUs and lambdas usage
		if count_lambdas > 0:
			lambda_usage.append((len(actives)*614.4)/(count_lambdas*10000.0))
		if count_dus > 0:
			proc_usage.append(len(actives)/self.getProcUsage(bestSolution))
		'''
		return True
	else:
		inc_blocking.append(1)
		incremental_power_consumption.append(getPowerConsumption(ilp_module))
		return False

#this is the method invoked by the simulator to call the relaxed ILP for the batch algorithm - It is expected to block no RRH at all
#it works only with copies of the data structures
def runBatchRelaxed(relaxHeuristic, postProcessingHeuristic, ilp_module, metric, method, r = None):
	solution_time = 0
	solutions_list = []
	#run each execution and copy the result to a list containing network states
	for e in range(number_of_runs):
		print("Execution # {}".format(e))
		#make deep copies of lists and objects that will be modified
		r_copy = None
		actives_copy = []
		actives_copy = copy.deepcopy(actives)
		if r != None:
			r_copy = copy.deepcopy(r)
			actives_copy.append(r_copy)
		#take a snapshot of the network and its elements state
		network_copy = copy.copy(ilp_module.rrhs_on_nodes)
		cp_l =  copy.copy(ilp_module.lambda_node)
		cp_d = copy.copy(ilp_module.du_processing)
		importlib.reload(ilp_module)
		start = time.time()
		ilp = ilp_module.ILP(actives_copy, range(len(actives_copy)), ilp_module.nodes, ilp_module.lambdas, True)
		solution = ilp.run()
		#verifies if a solution was found and, if so, updates this auxiliary network state
		if solution != None:
			foundSolution = True
			solution_values = ilp.return_decision_variables()
			postMethod = getattr(rlx, postProcessingHeuristic)
			postMethod(solution_values, ilp, ilp_module)
			relaxMethod = getattr(current_module, relaxHeuristic)
			blocked_rrhs = None
			blocked_rrhs = relaxMethod(actives_copy, solution_values, ilp_module)
			blk = copy.deepcopy(blocked_rrhs)
			#PUT TREATMENT WHEN BLOCK OCCURS IN BATCH? IT SHOULD NEVER OCCURS IN BATCH
			end = time.time()
			solution_time += end - start
			relaxSol = rm.NetworkState(ilp_module, e)
			relaxSol.relaxTime = solution_time
			relaxSol.setMetric("solution_values", solution_values)
			relaxSol.setMetric("execution_time", solution.solve_details.time)
			relaxSol.setMetric("power", getPowerConsumption(ilp_module))
			relaxSol.actives = copy.deepcopy(actives_copy)
			solutions_list.append(relaxSol)
	if foundSolution == True:
		#sucs_reqs += 1
		all_solutions = rm.NetworkStateCollection(solutions_list)
		bestSolution = all_solutions.getBestNetworkState(metric, method)
		#now, updates the main network state (so far I am using the on plp file, which is the ILP module file)
		rm.updateRealNetworkState(bestSolution, ilp_module)
		#solution_time += bestSolution.execution_time
		#if r != None:
		#	r.updateWaitTime(self.env.now+solution.solve_details.time)
		#print("Gen is {} ".format(r.generationTime))
		#print("NOW {} ".format(r.waitingTime))
		#if r!= None:
		#	actives.append(r)
		#	self.env.process(r.run())
		#copy the state of the RRHs of the copied list to the original actives list
		actives = copy.deepcopy(bestSolution.actives)
		batch_power_consumption.append(util.getPowerConsumption(bestSolution))
		#batch_rrhs_wait_time.append(averageWaitingTime(actives))
		#batch_blocking.append(len(bestSolution.relax_blocked))
		time_b.append(bestSolution.execution_time)
		#time_b.append(bestSolution.execution_time)
		#URGENTE - MEU ALGORITMO DE PÓS PROCESSAMENTO NÃO FAZ NADA COM ESSA VARIÁVEL, LOGO, ELA SEMPRE ESTARÁ VAZIA
		#ASSIM, PRECISO CRIAR UM MÉTODO PARA VERIFICAR REDIRECIONAMENTO DE DUS E CASO OUTRA VARIÁVEL FIQUE VAZIA PELO
		#ALGORITMO DE PÓS PROCESSAMENTO, CRIAR MÉTODOS PARA CONTABILIZÁ-LA TB
		'''
		if solution_values.var_k:
			b_redirected_rrhs.append(len(solution_values.var_k))
		else:
			b_redirected_rrhs.append(0)
		#counts the current activated nodes, lambdas, DUs and switches
		self.countNodes(ilp_module)
		#counting each single vBBU migration - new method - Updated 2/12/2018
		self.extSingleMigrations(bestSolution, bestSolution.old_network_state)
		#count migration only when all load from fog ndoe is migrated - old method
		#self.extMigrations(ilp_module, copy_state)
		for i in bestSolution.nodeState:
			if i == 1:
				count_nodes += 1
		b_activated_nodes.append(count_nodes)
		for i in bestSolution.lambda_state:
			if i == 1:
				count_lambdas += 1
		b_activated_lambdas.append(count_lambdas)
		for i in bestSolution.du_state:
			for j in i:
				if j == 1:
					count_dus += 1
		b_activated_dus.append(count_dus)
		for i in ilp_module.switch_state:
			if i == 1:
				count_switches += 1
		b_activated_switchs.append(count_switches)
		#count DUs and lambdas usage
		if count_lambdas > 0:
			lambda_usage.append((len(actives)*614.4)/(count_lambdas*10000.0))
		if count_dus > 0:
			proc_usage.append(len(actives)/self.getProcUsage(bestSolution))
		#print("Found the best solution for {} actives RRHs".format(len(actives)))
		'''
		return solution
	else:
		print("No Solution")
		#print(plp.du_processing)
		#if r != None:
		#	rrhs.append(r)
		#	np.shuffle(rrhs)
		batch_power_consumption.append(self.util.getPowerConsumption(ilp_module))
		batch_blocking.append(1)

#compute the power consumption at the moment
def getPowerConsumption(ilp_module):
	netCost = 0.0
	#compute all activated nodes
	for i in range(len(ilp_module.nodeState)):
		if ilp_module.nodeState[i] == 1:
			if i == 0:
				netCost += 600.0
			else:
				netCost += 500.0
		#compute activated DUs
		for j in range(len(ilp_module.du_state[i])):
			if ilp_module.du_state[i][j] == 1:
				if i == 0:
					netCost += 100.0
				else:
					netCost += 50.0
	#compute lambda and switch costs
	for w in ilp_module.lambda_state:
		if w == 1:
			netCost += 20.0
	for s in ilp_module.switch_state:
		if s == 1:
			netCost += 15.0
	return netCost

#set the maximum load for a simulated scenario given the vdus capacity and the lambdas
def setMaximumLoad(cloud_vdu, fog_vdu, number_of_fogs, number_of_lambdas):
	total_fog = fog_vdu*number_of_lambdas*number_of_fogs
	total_vdus_load = total_fog+(cloud_vdu*number_of_lambdas)
	return total_vdus_load




#ALL BELOW WILL BE MOVED TO staticRelax FILE-----------------------------------------

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


#to keep values of each solution in order to calculate the averages
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

metric = "power"
method = "min"

#general tests
#count lambdas and VDUs
for j in range(5):
	importlib.reload(plp)
	number_of_nodes = 2
	number_of_lambdas = 3
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
	print("Primal execution # {}".format(j))
	for e in range(8):
		count_lambdas = 0
		count_dus = 0
		count_nodes = 0
		count_switches = 0
		util = sim.Util()
		solution_time = 0
		solutions_list = []
		rrhs_amount = setMaximumLoad(3, 1, number_of_nodes-1, number_of_lambdas)
		antenas = util.createRRHs(rrhs_amount, number_of_nodes, None, None, None)
		print("Execution of {} RRHs {} Nodes and {} Lambdas".format(rrhs_amount, number_of_nodes, number_of_lambdas))
		for i in range(2):
			#for i in antenas:
			#	print(i.fog)
			plp.setInputParameters(number_of_nodes, number_of_lambdas, plp.cloud_du_capacity, 
			plp.fog_du_capacity, plp.cloud_cost, plp.fog_cost, plp.line_card_cost, plp.switchCost, plp.switch_band, plp.wavelengthCapacity)
			start = time.time()
			ilp = plp.ILP(antenas, range(len(antenas)), plp.nodes, plp.lambdas, True)
			solution = ilp.run()
			#get the values high probabilities
			solution_values = ilp.return_decision_variables()
			rlx.mostProbability(solution_values, ilp, plp)
			blocked = []
			#blocked = reduceDelay(antenas, solution_values, plp)
			blocked = firstFitVPON(antenas, solution_values, plp)
			#print(len(blocked))
			relaxSol = rm.NetworkState(plp, i)
			relaxSol.relaxTime = solution_time
			relaxSol.setMetric("solution_values", solution_values)
			relaxSol.setMetric("execution_time", solution.solve_details.time)
			relaxSol.setMetric("power", util.getPowerConsumption(plp))
			solutions_list.append(relaxSol)
		#now get the best solution
		all_solutions = rm.NetworkStateCollection(solutions_list)
		bestSolution = all_solutions.getBestNetworkState(metric, method)
		end = time.time()
		solution_time += end - start
		#now, updates the main network state to take the metrics(so far I am using the on plp file, which is the ILP module file)
		rm.updateRealNetworkState(bestSolution, plp)
		power.append(util.getPowerConsumption(plp))
		execution_time.append(solution_time)
		countNodes(plp)
		for a in antenas:
			#count the redirection, if it exists of the allocated RRH
			if a.wavelength != a.du:
				redirected.append(1)
			else:
				redirected.append(0)
		for i in bestSolution.nodeState:
			if i == 1:
				count_nodes += 1
		activated_nodes.append(count_nodes)
		for i in bestSolution.lambda_state:
			if i == 1:
				count_lambdas += 1
		activated_lambdas.append(count_lambdas)
		for i in bestSolution.du_state:
			for j in i:
				if j == 1:
					count_dus += 1
		activated_dus.append(count_dus)
		for i in bestSolution.switch_state:
			if i == 1:
				count_switches += 1
		activated_switchs.append(count_switches)
		#count DUs and lambdas usage
		if count_lambdas > 0:
			lambda_usage.append((len(antenas)*614.4)/(count_lambdas*10000.0))
		if count_dus > 0:
			proc_usage.append(len(antenas)/getProcUsage(bestSolution))
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
print("Time", execution_static)

#for i in blocked:
#	print("RRH {} is blocked? {}".format(i.id, i.blocked))
#print(plp.du_processing)
#print(plp.wavelength_capacity)
#print(plp.nodes_lambda)
#print(s.solve_details.time)

'''
number_of_rrhs = 64
util = sim.Util()
rrhs = util.createRRHs(number_of_rrhs, None, None, None)
rh = rrhs.pop()
#runIncSched("firstFitVPON", "mostProbability", plp, "power", "min", rh)
runBatchRelaxed("firstFitVPON", "mostProbability", plp, "power", "min", rrhs, rh)
print(batch_power_consumption)
print(time_b)
'''