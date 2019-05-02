import simpy
import functools
import random
import time
from enum import Enum
import numpy
from scipy.stats import norm
import matplotlib.pyplot as plt
#import batch_teste as lp
import relaxation_test as plp
import relaxation_module as rlx
import relaxedMainModule as rm
import copy
import sys
import pdb#debugging module
import importlib#to reload modules
import builtins#all n=built-in python methods
import operator
import simulator as sim

def checkNodeCapacity(node, n_state):
	#print("Checking node {}".format(node))
	if sum(n_state.du_processing[node]) > 0:
		return True
	else:
		print("Node {} is empty".format(node))
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
				#take a random DU and verify if it the switch is needed
				random_du = getRandomVDU(r.node, n_state, r)
				if type(random_du) is tuple:
					#use the switch
					r.du = random_du[0]
					updateSwitch(r.node, n_state)
				else:
					r.du = random_du
			if r.du == None:
				r.blocked = True
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
				r.blocked = True
		if r.blocked:
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
			print("Checking lambda for RRH {} has node {}".format(r.id, r.node))
			if not checkNodesLambda(r.node, n_state):
				print("Node {} do not have lambda".format(r.node))
				#take the one in the solution
				if checkLambdaNode(r.node, r_lambda, n_state):
					#use this one
					r.wavelength = r_lambda
					print("Allocating RRH {} in the solution VPON {}".format(r.id, r_lambda))
				else:
					#take a free vpon
					#if no VPON was found 'til here, get one that is non-allocated
					vpon = getFreeVPON(n_state)
					if vpon != None:
						r.wavelength = vpon
						print("Allocating RRH {} in the free VPON {}".format(r.id, vpon))
			#if it has, get the first one that can handle the RRH
			else:
				vpon = getFirstFitVPON(r.node, n_state)
				#if a lambda was found, allocate to the RRH
				if vpon != None:
					r.wavelength = vpon
					print("Allocating RRH {} in the FF VPON {}".format(r.id, vpon))
				else:
					#if no VPON was found 'til here, get one that is non-allocated
					vpon = getFreeVPON(n_state)
					if vpon != None:
						r.wavelength = vpon
						print("Allocating RRH {} in the free VPON {}".format(r.id, vpon))
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
				else:
					r.du = random_du
			if r.du == None:
				r.blocked = True
		if r.blocked:
			blocked_rrhs.append(r)
		else:
			updateVDU(r.du, r.node, n_state)
			updateVponState(r.node, r.wavelength, n_state)
			updateNode(r.node, n_state)
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
def incrementalRelaxedBatch(self, rrhs_batch, relaxHeuristic, postProcessingHeuristic, ilp_module, metric, method):
	for r in range(len(rrhs_batch)):
		runIncSched(relaxHeuristic, postProcessingHeuristic, ilp_module, metric, method, rrhs_batch[r])
		del rrhs_batch[r]


#this is the method invoked by the simulator to call the relaxed version of the incremental ILP algorithm
def runIncSched(self, relaxHeuristic, postProcessingHeuristic, ilp_module, metric, method, r):
	solution_list = []
	semi_solutions = []
	#create the network states
	for e in range(self.number_of_runs):
		relaxSol = rm.NetworkState(ilp_module)
		solutions_list.append(relaxSol)
	for e in solution_list:
		r_copy = None
		r_copy = copy.deepcopy(r)
		antenas = []
		antenas.append(r_copy)
		start = time.time()
		self.ilp = ilp_module.ILP(antenas, range(len(antenas)), ilp_module.nodes, ilp_module.lambdas, True)
		solution = self.ilp.run()
		if solution != None:
			solution_values = self.ilp.return_decision_variables()
			postMethod = getattr(rlx, self.postProcessingHeuristic)
			postMethod(solution_values, self.ilp, e)
			relaxMethod = getattr(rm, self.relaxHeuristic)
			blocked_rrh = []
			blocked_rrh = relaxMethod(antenas, solution_values, e)
			if blocked_rrh:
				foundSolution = False
				print("Blocked!",r.id)
			else:
				foundSolution = True
				semi_solutions.append(e)
				e.setMetric("solution_values", solution_values)
				e.setMetric("execution_time", solution.solve_details.time)
				e.setMetric("power", self.util.getPowerConsumption(e))
				end = time.time()
				solution_time += end - start
				e.relaxTime = solution_time
	if foundSolution == True:
		sucs_reqs += 1
		bestSolution = self.relaxSolutions.getBestNetworkState(self.metric, self.method)
		#now, updates the main network state (so far I am using the on plp file, which is the ILP module file)
		rm.updateRealNetworkState(bestSolution, ilp_module)
		#updates the execution time of this solution, which is the relaxed ILP solving time + the relaxation scheduling updating procedure
		#solution_time += bestSolution.execution_time
		time_inc.append(solution_time)
		r.updateWaitTime(self.env.now)
		for i in antenas:
			self.env.process(i.run())
			actives.append(i)
			antenas.remove(i)
		incremental_power_consumption.append(self.util.getPowerConsumption(ilp_module))
		self.countNodes(ilp_module)
		#URGENTE - MEU ALGORITMO DE PÓS PROCESSAMENTO NÃO FAZ NADA COM ESSA VARIÁVEL, LOGO, ELA SEMPRE ESTARÁ VAZIA
		#ASSIM, PRECISO CRIAR UM MÉTODO PARA VERIFICAR REDIRECIONAMENTO DE DUS E CASO OUTRA VARIÁVEL FIQUE VAZIA PELO
		#ALGORITMO DE PÓS PROCESSAMENTO, CRIAR MÉTODOS PARA CONTABILIZÁ-LA TB
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
		return True
	else:
		print("Incremental Blocking")
		#verifies if it is the nfv control plane
		if self.type == "load_inc_batch":
			inc_blocking.append(1)
		else:
			rrhs.append(r)
			np.shuffle(rrhs)
			antenas = []
			#print("Incremental Blocking")
			inc_blocking.append(1)
			incremental_power_consumption.append(self.util.getPowerConsumption(ilp_module))
			return False

#this is the method invoked by the simulator to call the relaxed ILP for the batch algorithm - It is expected to block no RRH at all
#it works only with copies of the data structures
def runBatchRelaxed(self, relaxHeuristic, postProcessingHeuristic, ilp_module, metric, method, r = None):
	solutions_list = []
	#run each execution and copy the result to a list containing network states
	for e in range(self.number_of_runs):
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
		self.ilp = ilp_module.ILP(actives_copy, range(len(actives_copy)), ilp_module.nodes, ilp_module.lambdas, True)
		solution = self.ilp.run()
		#verifies if a solution was found and, if so, updates this auxiliary network state
		if solution != None:
			foundSolution = True
			solution_values = self.ilp.return_decision_variables()
			postMethod = getattr(rlx, self.postProcessingHeuristic)
			postMethod(solution_values, self.ilp, ilp_module)
			relaxMethod = getattr(rm, self.relaxHeuristic)
			blocked_rrhs = None
			blocked_rrhs = relaxMethod(actives_copy, solution_values, ilp_module)
			blk = copy.deepcopy(blocked_rrhs)
			#PUT TREATMENT WHEN BLOCK OCCURS IN BATCH? IT SHOULD NEVER OCCURS IN BATCH
			end = time.time()
			solution_time += end - start
			relaxSol = rm.NetworkState(ilp_module)
			relaxSol.relaxTime = solution_time
			relaxSol .setMetric("solution_values", solution_values)
			relaxSol .setMetric("execution_time", solution.solve_details.time)
			relaxSol .setMetric("power", self.util.getPowerConsumption(ilp_module))
			relaxSol.actives = actives_copy
			solutions_list.append(relaxSol)
	if foundSolution == True:
		sucs_reqs += 1
		all_solutions = rm.NetworkStateCollection(solutions_list)
		bestSolution = self.allSolutions.getBestNetworkState(self.metric, self.method)
		#now, updates the main network state (so far I am using the on plp file, which is the ILP module file)
		rm.updateRealNetworkState(bestSolution, ilp_module)
		#solution_time += bestSolution.execution_time
		if r != None:
			r.updateWaitTime(self.env.now+solution.solve_details.time)
		#print("Gen is {} ".format(r.generationTime))
		#print("NOW {} ".format(r.waitingTime))
		if r!= None:
			actives.append(r)
			self.env.process(r.run())
		#copy the state of the RRHs of the copied list to the original actives list
		actives = copy.deepcopy(bestSolution.actives)
		batch_power_consumption.append(self.util.getPowerConsumption(bestSolution))
		batch_rrhs_wait_time.append(self.averageWaitingTime(actives))
		batch_blocking.append(len(bestSolution.relax_blocked))
		#time_b.append(bestSolution.execution_time)
		time_b.append(bestSolution.execution_time)
		#URGENTE - MEU ALGORITMO DE PÓS PROCESSAMENTO NÃO FAZ NADA COM ESSA VARIÁVEL, LOGO, ELA SEMPRE ESTARÁ VAZIA
		#ASSIM, PRECISO CRIAR UM MÉTODO PARA VERIFICAR REDIRECIONAMENTO DE DUS E CASO OUTRA VARIÁVEL FIQUE VAZIA PELO
		#ALGORITMO DE PÓS PROCESSAMENTO, CRIAR MÉTODOS PARA CONTABILIZÁ-LA TB
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
		return solution
	else:
		print("No Solution")
		#print(plp.du_processing)
		if r != None:
			rrhs.append(r)
			np.shuffle(rrhs)
		batch_power_consumption.append(self.util.getPowerConsumption(ilp_module))
		batch_blocking.append(1)


#general tests
number_of_rrhs = 64
util = sim.Util()
rrhs = util.createRRHs(number_of_rrhs, None, None, None)
#for i in rrhs:
#	print(i.rrhs_matrix)
ilp = plp.ILP(rrhs, range(len(rrhs)), plp.nodes, plp.lambdas, True)
s = ilp.run()
#get the values high probabilities
solution_values = ilp.return_decision_variables()
rlx.mostProbability(solution_values, ilp, plp)
blocked = []
#blocked = reduceDelay(rrhs, solution_values, plp)
blocked = firstFitVPON(rrhs, solution_values, plp)
print(len(blocked))
#for i in blocked:
#	print("RRH {} is blocked? {}".format(i.id, i.blocked))
print(plp.du_processing)
print(plp.wavelength_capacity)
print(plp.nodes_lambda)
print(s.solve_details.time)