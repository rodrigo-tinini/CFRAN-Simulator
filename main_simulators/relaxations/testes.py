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

#general tests
number_of_rrhs = 33
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
blocked = reduceDelay(rrhs, solution_values, plp)
print(len(blocked))
#for i in blocked:
#	print("RRH {} is blocked? {}".format(i.id, i.blocked))
print(plp.du_processing)
print(plp.wavelength_capacity)
print(plp.nodes_lambda)