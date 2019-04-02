from docplex.mp.model import Model
import simpy
import functools
import random
import time
import copy
import operator
import numpy as np
from enum import Enum
from scipy.stats import norm
import matplotlib.pyplot as plt
import relaxation_test as rlx
import builtins#all n=built-in python methods
import pdb#debugger module

#returns the most loaded VDU in a processing node
def getMostLoadedVDU(node, n_state):
	vdus_copy = copy.deepcopy(n_state.du_processing[node])
	vdus = np.array(vdus_copy)
	v = np.min(vdus[np.nonzero(vdus)])
	print(v)
	print(n_state.du_processing[node].index(v))
	return n_state.du_processing[node].index(v)
	#vdus = copy.deepcopy(n_state.du_processing[node])
	#while vdus:
	#	v = min(n_state.du_processing[node])
	#	if v == 0:
	#		print(vdus)
	#		del vdus[vdus.index(v)]
	#	else:
	#		return vdus.index(v)

#returns the least loaded VDU in a processing node
def getLeastLoadedVDU(node, n_state):
	vdus_copy = copy.deepcopy(n_state.du_processing[node])
	vdus = np.array(vdus_copy)
	v = np.max(vdus[np.nonzero(vdus)])
	print(v)
	print(n_state.du_processing[node].index(v))
	return n_state.du_processing[node].index(v)
	#vdus = copy.deepcopy(n_state.du_processing[node])
	#while vdus:
	#	v = max(n_state.du_processing[node])
	#	if v == 0:
	#		del vdus[vdus.index(v)]
	#	else:
	#		return vdus.index(v)

#returns the most loaded VPON in a processing node
def getMostLoadedVPON(node, n_state):
	vpons = copy.deepcopy(n_state.nodes_vpons_capacity[node])
	while vpons:
		mostLoaded = max(vpons, key = vpons.__getitem__)
		if vpons[mostLoaded] >= n_state.RRHband:
			return mostLoaded
		else:
			del vpons[mostLoaded]

#returns the least loaded VPON in a processing node
def getLeastLoadedVPON(node, n_state):
	vpons = copy.deepcopy(n_state.nodes_vpons_capacity[node])
	while vpons:
		mostLoaded = min(vpons, key = vpons.__getitem__())
		if vpons[mostLoaded] >= n_state.RRHband:
			return mostLoaded
		else:
			del vpons[mostLoaded]

#test
#nodes_vpons_capacity = {}
#for i in range(3):
#	nodes_vpons_capacity[i] = {}
#RRHband = 2001
#nodes_vpons_capacity[0][0] = 2001
#nodes_vpons_capacity[0][1] = 2000
#v = getMostLoadedVPON(0)
#print(v)
#print(nodes_vpons_capacity)

#this method returns the u variable given the RRH index
def getVarU(aIndex, solution):
	for i in solution.var_u:
		if i[0] == aIndex[0]:
			return i


#allocate a VPON to a RRH and its node and update VPON state
def updateVponState(rrh, vpon, n_state):
	#n_state.wavelength = vpon
	rrh.wavelength = vpon
	n_state.wavelength_capacity[rrh.wavelength] -= n_state.RRHband
	if not vpon in n_state.nodes_lambda[rrh.node]:
		n_state.nodes_lambda[rrh.node].append(rrh.wavelength)
	if n_state.lambda_state[rrh.wavelength] == 0:
		n_state.lambda_state[rrh.wavelength] = 1
		n_state.lc_cost[rrh.wavelength] = 0
	n_state.nodes_vpons_capacity[rrh.node][vpon] = n_state.wavelength_capacity[vpon]
	blockLambda(rrh.wavelength, rrh.node, n_state)

#block an already allocated lambda in other nodes
def blockLambda(wavelength, node, n_state):
	ln = n_state.lambda_node[wavelength]
	for i in range(len(ln)):
		if i != node:
			ln[i] = 0

#check if node has at least one activated VPON
def checkNodeVPON(node, n_state):
	if n_state.nodes_lambda[node]:
		return True
	else:
		return False

#get any non-allocated VPON
def getFreeVPON(rrh, n_state):
	for j in range(len(n_state.lambda_state)):
		if n_state.lambda_state[j] == 0: #this lambda is available
			updateVponState(rrh, j, n_state)
			blockLambda(rrh.wavelength, rrh.node, n_state)
			return True

#new method to get the first free VPON in a node
#this method check if there is an already allocated VPON in a node and returns it 
def getRelaxNodeFirstFitVPON(node, i, n_state):
	#get the first VPON created on node that has capacity
	#get the vpons of node
	n_vpons = n_state.nodes_lambda[node]
	#now, gets the first that has enough capacity
	for j in n_vpons:
		print(n_vpons)
		#print("CHECKED IS {} AND RELAX IS {}".format(j, i[2]))
		if n_state.checkLambdaCapacity(j):
			return j
		#print("BAD CHECKED IS {} AND RELAX IS {}".format(j, i[2]))
	return -1
	
#new method to get the first free VPON in a node
#this method check if there is an already allocated VPON in a node and returns it ONLY IF IT IS DIFFERENT from the one returned on the relaxation
def getNodeFirstFitVPON(node, i, n_state):
	#get the first VPON created on node that has capacity
	#get the vpons of node
	n_vpons = n_state.nodes_lambda[node]
	#now, gets the first that has enough capacity
	for j in n_vpons:
		print(n_vpons)
		#print("CHECKED IS {} AND RELAX IS {}".format(j, i[2]))
		if n_state.checkLambdaCapacity(j) and j != i[2] :
			return j
		#print("BAD CHECKED IS {} AND RELAX IS {}".format(j, i[2]))
	return -1

#get the first available VPON in a node
def getFirstFreeVPON(rrh, i, n_state):
	for j in range(len(n_state.lambda_node)):
		print("Verifying lambda {} with relaxed lambda {}".format(j,i[2]))
		if n_state.lambda_node[j][rrh.node] == 1:
			print("Node {} has lambda {}".format(rrh.node, j))
			print("Lambda node is {}".format(n_state.lambda_node))
		#another lambda is allocated on the node
		if n_state.lambda_node[j][rrh.node] == 1 and n_state.lambda_node[j][rrh.node] != i[2]:
			#check if it has capacity
			if n_state.checkLambdaCapacity(j):
				print("yeeeeees")
				return j
	print("LAMBDAS IN NODES ",n_state.nodes_lambda)
	print("VPONS CAPACITY IN NODES ",n_state.nodes_vpons_capacity)
	return -1

#free node resources
def freeNodeResources(rrh, node, n_state, node_allocated):
	rrh.node = None
	#print(node)
	#print(rrh.node)
	if node_allocated:
		n_state.rrhs_on_nodes[node] -= 1
		#turn the node on if it is not
		if n_state.rrhs_on_nodes[node] == 0:
			#not activated, updates costs
			if node == 0:
				n_state.nodeCost[node] = 0.0
			else:
				n_state.nodeCost[node] = 300.0
			n_state.nodeState[node] = 0

#update the node state after an allocation
def updateNode(rrh, n_state):
	if rrh.node != None:
		n_state.rrhs_on_nodes[rrh.node] += 1
		#turn the node on if it is not
		if n_state.nodeState[rrh.node] == 0:
			#not activated, updates costs
			n_state.nodeCost[rrh.node] = 0
			n_state.nodeState[rrh.node] = 1

#returns the capacity of a VDU in a given node
def getVduCapacity(node, vdu, n_state):
	return n_state.du_processing[node][vdu]

#check VDU capacity
def checkVduCapacity(vdu, node, n_state):
	if n_state.du_processing[node][vdu] > 0:
		return True
	else:
		return False

#this class represents a blocked RRH
class BlockedRRH(object):
	def __init__(self, aId):
		self.id = aId

#this method clears all RRH attributes
def clearRRH(r):
	r.wavelength = None
	r.du = None
	r.node = None
	r.var_x = None
	r.var_u = None
	r.enabled = False

#This method tries to use the first fit VPON in a node, and then, the one with most probability use returned on the solution and then, the first fit that was not allocated to any node
#regarding the node, it tries the one with the most probability, then, the other available node (it will be always cloud or fog)
#regarding the VDU, it consider the one with the most probability returned on the solution, then take the first fit available VDU in the node (it does not aim to reduce swtich delay)
#Everytime that any resource can not be allocated, -1 is returned and the RRH
def firstFitRelaxMinVPON(rrh, solution, n_state):
	#keep a list of blocked RRHs
	blocked_rrhs = []
	#iterate over each RRH on the solution
	#general rule for RRHs (var x and u): index [0] is the RRH, index [1] is the node, [2] is the wavelength/DU
	for i in solution.var_x:
		alloc_vpon = False
		print("Solution for RRH {} - {} in N State {}".format(rrh[i[0]].id, i[0], n_state.aId))
		print("Current DUs are {}".format(n_state.du_processing))
		#print("ELEMENT {}".format(n_state.nodes_lambda))
		#pdb.set_trace()#debugging breakpoint
		#print(n_state.nodes_lambda)
		#the node has capacity on its VDUs?
		if i[1] == 0 and n_state.checkNodeCapacity(i[1]):
			#it has, allocate the node to the RRH
			rrh[i[0]].var_x = i#talvez eu tire essa linha depois
			rrh[i[0]].node = i[1]
		else:
			if n_state.checkNodeCapacity(rrh[i[0]].fog):
					rrh[i[0]].node = rrh[i[0]].fog
		#update the node cost, number of allocated RRHs and capacity
		if rrh[i[0]].node != None:
			updateNode(rrh[i[0]], n_state)
			#print("found node")
		#if no node was allocated, blocks the requisition
		else:
			rrh[i[0]].blocked = True
			#put the blocked RRH into a list
			#clearRRH(rrh[i[0]])
			#blocked_rrhs.append(rrh[i[0]])
			#return -1
		#now, if a node was found for the RRH, tries to allocate the VPON
		if rrh[i[0]].blocked == False:
			#print("não ta bloqueado")
			#verifies if the node has an activate VPON
			if checkNodeVPON(rrh[i[0]].node, n_state):#has active VPONs
				#print("NODE VERIFIED IS {}".format(rrh[i[0]].node))
				#print(n_state.lambda_node)
				print("AQUI")
				#print(n_state.nodes_lambda)
				#print(i[2])
				#print("*********")
				#if it has, gets the first free VPON
				vpon = getRelaxNodeFirstFitVPON(rrh[i[0]].node, i, n_state)
				#vpon = getFirstFreeVPON(rrh[i[0]], i, n_state)#ELE NAO ESTÁ PEGANDO O VPON CORRETO, QUANDO JÁ TEM ALGUM VPON, ELE RETORNA -1, ARRUMAR ISSO
				#print("hi",vpon)
				#check if there is capacity on this VPON
				if vpon != -1:#allocate the RRH on this VPON
					#print("FOI!!!!", vpon)
					updateVponState(rrh[i[0]], vpon, n_state)
					#print("Aq1 ELEMENT {}".format(n_state.nodes_lambda))
					alloc_vpon = True
			#if not, take the VPON returned on the solution
			#check if the VPON returned on the solution has capacity to support the RRH
			elif n_state.checkLambdaNode(rrh[i[0]].node,i[2]) and n_state.checkLambdaCapacity(i[2]):
				print("AQUI2")
				#print(n_state.nodes_lambda)
				#print(i[2])
				#print("*********")
				#allocate the VPON to the RRH and its node and update its state
				updateVponState(rrh[i[0]], i[2], n_state)
				alloc_vpon = True
				#print("Aq2 ELEMENT {}".format(n_state.nodes_lambda))
				#print("NODE IS {} LAMBDA IS {} FOR RRH {}".format(rrh[i[0]].node, rrh[i[0]].wavelength, rrh[i[0]].id))
			elif not alloc_vpon:
				#if neither an already allocated VPON or the returned one has capacity, take another one that is free
				if getFreeVPON(rrh[i[0]], n_state):
					print("AQUI3")
					alloc_vpon = True
					#print("Aq3 ELEMENT {}".format(n_state.nodes_lambda))
					#print(n_state.nodes_lambda)
					#print(i[2])
					#print("*********")
					pass
			if not alloc_vpon:
				print("Foi bloqueado22...")
				print(n_state.wavelength_capacity)
				rrh[i[0]].blocked = True
				freeNodeResources(rrh[i[0]], rrh[i[0]].node, n_state, True)
				clearRRH(rrh[i[0]])
				blocked_rrhs.append(rrh[i[0]])
				#print(n_state.nodes_lambda)
			#if neither an already allocated VPON or the returned one has capacity, take another one that is free
			#elif getFreeVPON(rrh[i[0]], n_state):
			#	print("AQUI3")
				#print(n_state.nodes_lambda)
				#print(i[2])
				#print("*********")
			#	pass
			#no free non-allocated was found, then blocks the requisition and reverts the allocation done in the processing node
		else:
			print("RRH {} of Node {} is Blocked? {}".format(rrh[i[0]].id, rrh[i[0]].rrhs_matrix, rrh[i[0]].blocked))
			freeNodeResources(rrh[i[0]], rrh[i[0]].node, n_state, False)
			clearRRH(rrh[i[0]])
			blocked_rrhs.append(rrh[i[0]])
		#if until this moment RRH was not blocked, tries to allocate the VDU
		#get var_u - which contains the VDU
		#print("IS BLOCKED?? ",rrh[i[0]].wavelength)
		var_u = getVarU(i, solution)
		#gets the VDU returned on the solution
		vdu = var_u[2]
		if rrh[i[0]].blocked != True:
			#check if the VDU returned has capacity and if the switch will be used
			#print("NODE IS {} LAMBDA IS {} FOR RRH {}".format(rrh[i[0]].node, rrh[i[0]].wavelength, rrh[i[0]].id))
			if checkAvailabilityVDU(vdu, rrh[i[0]].node, rrh[i[0]].wavelength, n_state) == 1:
				#print("SEM SWITCH")
				#allocates this VDU on the RRH and did not use the switch
				rrh[i[0]].du = vdu
				updateVDU(vdu, rrh[i[0]].node, n_state)
				print("SEM SWITCH DU {} e VPON {} in Node {}".format(vdu, rrh[i[0]].wavelength, rrh[i[0]].node))
			elif checkAvailabilityVDU(vdu, rrh[i[0]].node, rrh[i[0]].wavelength, n_state) == 0:
				print("COM SWITCH DU {} e VPON {} in Node {}".format(vdu, rrh[i[0]].wavelength, rrh[i[0]].node))
				#allocates the VDU and activates the ethernet switch
				rrh[i[0]].du = vdu
				updateVDU(vdu, rrh[i[0]].node, n_state)
				updateSwitch(rrh[i[0]].node, n_state)
				print(n_state.du_processing)
			elif checkAvailabilityVDU(vdu, rrh[i[0]].node, rrh[i[0]].wavelength, n_state) == -1:
				print("DU RELAX IS {} AND ALL IS {}".format(vdu, n_state.du_processing))
				print("problem here")
				#the VDU or the switch has no free capacity, so, get the first fit VDU different from the returned on the solution
				for d in range(len(n_state.du_processing[rrh[i[0]].node])):
					if not checkSwitch(d, rrh[i[0]].wavelength):
						print("nao precisa")
						if n_state.checkCapacityDU(rrh[i[0]].node, d):
							rrh[i[0]].du = d
							updateVDU(d, rrh[i[0]].node, n_state)
							print("Put DU {} to RRH {}".format(d, rrh[i[0]].id))
							#updateSwitch(rrh[i[0]].node, n_state)
							break
						else:
							print(n_state.du_processing)
							print("DU is {} and RELAXED is {}".format(d, vdu))
							print("Hello darkness my old friend... RRH {}".format(rrh[i[0]].id))
							#pdb.set_trace()#debugging breakpoint
					elif n_state.checkCapacityDU(rrh[i[0]].node, d):
						if checkSwitch(d, rrh[i[0]].wavelength) and checkSwitchCapacity(rrh[i[0]].node, n_state):
							print("precisa")
							rrh[i[0]].du = d
							updateVDU(d, rrh[i[0]].node, n_state)
							updateSwitch(rrh[i[0]].node, n_state)
							print(n_state.du_processing)
							print("Put DU {} to RRH {}".format(d, rrh[i[0]].id))
							#pdb.set_trace()#debugging breakpoint
							break
						else:
							#blocks
							print("NO SWITCH CAPACITY {} for RRH {}".format(n_state.du_processing, rrh[i[0]].id))
					else:
						#blocks
						print("NO CAPACITY ON DUS {} for RRH {}".format(n_state.du_processing, rrh[i[0]].id))
				if rrh[i[0]].du == None:
					print("BLOKEADO {}".format(rrh[i[0]].id))
					#print(n_state.wavelength_capacity)
					rrh[i[0]].blocked = True
					freeNodeResources(rrh[i[0]], rrh[i[0]].node, n_state, True)
					clearRRH(rrh[i[0]])
					blocked_rrhs.append(rrh[i[0]])
	return blocked_rrhs
			#return -1

















def OldfirstFitRelaxMinVPON(rrh, solution, n_state):
	#keep a list of blocked RRHs
	blocked_rrhs = []
	#iterate over each RRH on the solution
	#general rule for RRHs (var x and u): index [0] is the RRH, index [1] is the node, [2] is the wavelength/DU
	for i in solution.var_x:
		alloc_vpon = False
		print("Solution for RRH {} - {} in N State {}".format(rrh[i[0]].id, i[0], n_state.aId))
		print("ELEMENT {}".format(n_state.nodes_lambda))
		#pdb.set_trace()#debugging breakpoint
		#print(n_state.nodes_lambda)
		#the node has capacity on its VDUs?
		if i[1] == 0 and n_state.checkNodeCapacity(i[1]):
			#it has, allocate the node to the RRH
			rrh[i[0]].var_x = i#talvez eu tire essa linha depois
			rrh[i[0]].node = i[1]
		else:
			if n_state.checkNodeCapacity(rrh[i[0]].fog):
					rrh[i[0]].node = rrh[i[0]].fog
		#update the node cost, number of allocated RRHs and capacity
		if rrh[i[0]].node != None:
			updateNode(rrh[i[0]], n_state)
			#print("found node")
		#if no node was allocated, blocks the requisition
		else:
			rrh[i[0]].blocked = True
			#put the blocked RRH into a list
			clearRRH(rrh[i[0]])
			blocked_rrhs.append(rrh[i[0]])
			#return -1
		#now, if a node was found for the RRH, tries to allocate the VPON
		if rrh[i[0]].blocked == False:
			#print("não ta bloqueado")
			#verifies if the node has an activate VPON
			if checkNodeVPON(rrh[i[0]].node, n_state):#has active VPONs
				print("NODE VERIFIED IS {}".format(rrh[i[0]].node))
				#print(n_state.lambda_node)
				print("AQUI")
				#print(n_state.nodes_lambda)
				#print(i[2])
				#print("*********")
				#if it has, gets the first free VPON
				vpon = getNodeFirstFitVPON(rrh[i[0]].node, i, n_state)
				#vpon = getFirstFreeVPON(rrh[i[0]], i, n_state)#ELE NAO ESTÁ PEGANDO O VPON CORRETO, QUANDO JÁ TEM ALGUM VPON, ELE RETORNA -1, ARRUMAR ISSO
				#print("hi",vpon)
				#check if there is capacity on this VPON
				if vpon != -1:#allocate the RRH on this VPON
					print("FOI!!!!", vpon)
					updateVponState(rrh[i[0]], vpon, n_state)
					alloc_vpon = True
				else:
					print(vpon)
					print("------NODE IS {} LAMBDA IS {} FOR RRH {}------".format(rrh[i[0]].node, rrh[i[0]].wavelength, rrh[i[0]].id))
					clearRRH(rrh[i[0]])
					blocked_rrhs.append(rrh[i[0]])
					print("******NODE IS {} LAMBDA IS {} FOR RRH {}******".format(rrh[i[0]].node, rrh[i[0]].wavelength, rrh[i[0]].id))
					#pass
					#return -1
					#print("eh -1")
			#if not, take the VPON returned on the solution
			#check if the VPON returned on the solution has capacity to support the RRH
			elif n_state.checkLambdaNode(rrh[i[0]].node,i[2]) and n_state.checkLambdaCapacity(i[2]):
				print("AQUI2")
				#print(n_state.nodes_lambda)
				#print(i[2])
				#print("*********")
				#allocate the VPON to the RRH and its node and update its state
				updateVponState(rrh[i[0]], i[2], n_state)
				print("NODE IS {} LAMBDA IS {} FOR RRH {}".format(rrh[i[0]].node, rrh[i[0]].wavelength, rrh[i[0]].id))
				#print(n_state.nodes_lambda)
			#if neither an already allocated VPON or the returned one has capacity, take another one that is free
			elif getFreeVPON(rrh[i[0]], n_state):
				print("AQUI3")
				#print(n_state.nodes_lambda)
				#print(i[2])
				#print("*********")
				pass
			#no free non-allocated was found, then blocks the requisition and reverts the allocation done in the processing node
			else:
				print("Foi bloqueado...")
				rrh[i[0]].blocked = True
				freeNodeResources(rrh[i[0]], rrh[i[0]].node, n_state)
				clearRRH(rrh[i[0]])
				blocked_rrhs.append(rrh[i[0]])
				#return -1
		else:
			print(rrh[i[0]].blocked)
		#if until this moment RRH was not blocked, tries to allocate the VDU
		#get var_u - which contains the VDU
		#print("IS BLOCKED?? ",rrh[i[0]].wavelength)
		var_u = getVarU(i, solution)
		#gets the VDU returned on the solution
		vdu = var_u[2]
		if rrh[i[0]].blocked != True:
			#check if the VDU returned has capacity and if the switch will be used
			#print("NODE IS {} LAMBDA IS {} FOR RRH {}".format(rrh[i[0]].node, rrh[i[0]].wavelength, rrh[i[0]].id))
			if checkAvailabilityVDU(vdu, rrh[i[0]].node, rrh[i[0]].wavelength, n_state) == 1:
				#print("SEM SWITCH")
				#allocates this VDU on the RRH and did not use the switch
				rrh[i[0]].du = vdu
				updateVDU(vdu, rrh[i[0]].node, n_state)
			elif checkAvailabilityVDU(vdu, rrh[i[0]].node, rrh[i[0]].wavelength, n_state) == 0:
				#print("COM SWITCH DU {} e VPON {}".format(vdu, rrh[i[0]].wavelength))
				#allocates the VDU and activates the ethernet switch
				rrh[i[0]].du = vdu
				updateVDU(vdu, rrh[i[0]].node, n_state)
				updateSwitch(rrh[i[0]].node, n_state)
			elif checkAvailabilityVDU(vdu, rrh[i[0]].node, rrh[i[0]].wavelength, n_state) == -1:
				print("problem here")
				#the VDU or the switch has no free capacity, so, get the first fit VDU different from the returned on the solution
				for d in range(len(n_state.du_processing[rrh[i[0]].node])):
					if not checkSwitch(d, rrh[i[0]].wavelength):
						print("nao precisa")
						if n_state.checkCapacityDU(rrh[i[0]].node, d):
							rrh[i[0]].du = d
							updateVDU(d, rrh[i[0]].node, n_state)
							#updateSwitch(rrh[i[0]].node, n_state)
							break
					elif n_state.checkCapacityDU(rrh[i[0]].node, d):
						if checkSwitch(d, rrh[i[0]].wavelength) and checkSwitchCapacity(rrh[i[0]].node, n_state):
							print("precisa")
							rrh[i[0]].du = d
							updateVDU(d, rrh[i[0]].node, n_state)
							updateSwitch(rrh[i[0]].node, n_state)
							break
		if rrh[i[0]].du == None:
			print("BLOKEADO {}".format(rrh[i[0]].node))
			#print(n_state.wavelength_capacity)
			rrh[i[0]].blocked = True
			freeNodeResources(rrh[i[0]], rrh[i[0]].node, n_state)
			clearRRH(rrh[i[0]])
			blocked_rrhs.append(rrh[i[0]])
	return blocked_rrhs
			#return -1


#This method tries to use the first fit VPON in a node, and then, the one with most probability use returned on the solution and then, the first fit that was not allocated to any node
#regarding the node, it tries the one with the most probability, then, the other available node (it will be always cloud or fog)
#regarding the VDU, it consider the one with the most probability returned on the solution only
def naiveVDUFirstFitRelaxMinVPON(rrh, solution, n_state):
	#iterate over each RRH on the solution
	#general rule for RRHs (var x and u): index [0] is the RRH, index [1] is the node, [2] is the wavelength/DU
	for i in solution.var_x:
		#the node has capacity on its VDUs?
		if i[1] == 0 and n_state.checkNodeCapacity(i[1]):
			#it has, allocate the node to the RRH
			rrh[i[0]].var_x = i#talvez eu tire essa linha depois
			rrh[i[0]].node = i[1]
		else:
			if n_state.checkNodeCapacity(rrh[i[0]].fog):
					rrh[i[0]].node = rrh[i[0]].fog
		#update the node cost, number of allocated RRHs and capacity
		if rrh[i[0]].node != None:
			updateNode(rrh[i[0]], n_state)
		#if no node was allocated, blocks the requisition
		else:
			rrh[i[0]].blocked = True
		#now, if a node was found for the RRH, tries to allocate the VPON
		if rrh[i[0]].blocked == False:
			#verifies if the node has an activate VPON
			if checkNodeVPON(rrh[i[0]].node, n_state):#has active VPONs
				#if it has, gets the first free VPON
				vpon = getFirstFreeVPON(rrh[i[0]], i, n_state)
				#check if there is capacity on this VPON
				if vpon != -1:#allocate the RRH on this VPON
					updateVponState(rrh[i[0]], vpon, n_state)
			#if not, take the VPON returned on the solution
			#check if the VPON returned on the solution has capacity to support the RRH
			elif n_state.checkLambdaNode(rrh[i[0]].node,i[2]) and n_state.checkLambdaCapacity(i[2]):
				#allocate the VPON to the RRH and its node and update its state
				updateVponState(rrh[i[0]], i[2], n_state)
			#if neither an already allocated VPON or the returned one has capacity, take another one that is free
			elif getFreeVPON():
				pass
			#no free non-allocated was found, then blocks the requisition and reverts the allocation done in the processing node
			else:
				rrh[i[0]].blocked = True
				freeNodeResources()
		#if until this moment RRH was not blocked, tries to allocate the VDU
		#get var_u - which contains the VDU
		var_u = getVarU(i, solution)
		#gets the VDU returned on the solution
		vdu = var_u[2]
		if rrh[i[0]].blocked != True:
			#check if the VDU returned has capacity and if the switch will be used
			if checkAvailabilityVDU(vdu, rrh[i[0]].node, rrh[i[0]].wavelength, n_state) == 1:
				#allocates this VDU on the RRH and did not use the switch
				rrh[i[0]].du = vdu
				updateVDU(vdu, rrh[i[0]].node, n_state)
			elif checkAvailabilityVDU(vdu, rrh[i[0]].node, rrh[i[0]].wavelength, n_state) == 0:
				#allocates the VDU and activates the ethernet switch
				rrh[i[0]].du = vdu
				updateVDU(vdu, rrh[i[0]].node, n_state)
				updateSwitch(rrh[i[0]].node, n_state)
			#if rrh[i[0]].du == None:
			#	rrh[i[0]].blocked = True
		if rrh[i[0]].du == None:
			rrh[i[0]].blocked = True
			freeNodeResources()

#this method first try the probabilities of the solution and then, the most loaded VPONs and VDUs and then, another one free
def relaxUpdateMostLoaded(rrh, solution, n_state):
	#iterate over each RRH on the solution
	#general rule for RRHs (var x and u): index [0] is the RRH, index [1] is the node, [2] is the wavelength/DU
	for i in solution.var_x:
		#the node has capacity on its VDUs?
		if i[1] == 0 and n_state.checkNodeCapacity(i[1]):
			#it has, allocate the node to the RRH
			rrh[i[0]].var_x = i#talvez eu tire essa linha depois
			rrh[i[0]].node = i[1]
		else:
			if n_state.checkNodeCapacity(rrh[i[0]].fog):
					rrh[i[0]].node = rrh[i[0]].fog
		#update the node cost, number of allocated RRHs and capacity
		if rrh[i[0]].node != None:
			updateNode(rrh[i[0]], n_state)
		#if no node was allocated, blocks the requisition
		else:
			rrh[i[0]].blocked = True
		#now, if a node was found for the RRH, tries to allocate the VPON
		if rrh[i[0]].blocked == False:
			if n_state.checkLambdaNode(rrh[i[0]].node,i[2]) and n_state.checkLambdaCapacity(i[2]):
				#allocate the VPON to the RRH and its node and update its state
				updateVponState(rrh[i[0]], i[2], n_state)
			#if the VPON of the solution has no capacity, tries the most loaded on the node
			elif checkNodeVPON(rrh[i[0]].node, n_state):#has active VPONs
				#if it has, gets the most loaded VPON
				vpon = getMostLoadedVPON(rrh[i[0]], n_state)
				#check if there is capacity on this VPON
				if vpon != -1:#allocate the RRH on this VPON
					updateVponState(rrh[i[0]], vpon, n_state)
			#if there is no available VPON, take another one free
			elif getFreeVPON():
				pass
			#no free non-allocated was found, then blocks the requisition and reverts the allocation done in the processing node
			else:
				rrh[i[0]].blocked = True
				freeNodeResources()
		#if until this moment RRH was not blocked, tries to allocate the VDU
		#get var_u - which contains the VDU
		var_u = getVarU(i, solution)
		#gets the VDU returned on the solution
		vdu = var_u[2]
		if rrh[i[0]].blocked != True:
			break
		else:
			#check if the VDU returned has capacity and if the switch will be used
			if checkAvailabilityVDU(vdu, rrh[i[0]].node, rrh[i[0]].wavelength, n_state) == 1:
				#allocates this VDU on the RRH and did not use the switch
				rrh[i[0]].du = vdu
				updateVDU(vdu, rrh[i[0]].node, n_state)
			elif checkAvailabilityVDU(vdu, rrh[i[0]].node, rrh[i[0]].wavelength, n_state) == 0:
				#allocates the VDU and activates the ethernet switch
				rrh[i[0]].du = vdu
				updateVDU(vdu, rrh[i[0]].node, n_state)
				updateSwitch(rrh[i[0]].node, n_state)
			#if the returned VDU or the switch has no capacity, tries the most loaded
			if rrh[i[0]].du == None:
				most_vdu = getMostLoadedVDU(rrh[i[0]].node, n_state)
				if checkAvailabilityVDU(most_vdu, rrh[i[0]].node, rrh[i[0]].wavelength, n_state) == 1:
					rrh[i[0]].du = most_vdu
					updateVDU(most_vdu, rrh[i[0]].node, n_state)
				elif checkAvailabilityVDU(most_vdu, rrh[i[0]].node, rrh[i[0]].wavelength, n_state) == 0:
					#allocates the VDU and activates the ethernet switch
					rrh[i[0]].du = most_vdu
					updateVDU(most_vdu, rrh[i[0]].node, n_state)
					updateSwitch(rrh[i[0]].node, n_state)
				elif checkAvailabilityVDU(most_vdu, rrh[i[0]].node, rrh[i[0]].wavelength, n_state) == -1:
					#the VDU or the switch has no free capacity, so, get the first fit VDU different from the returned on the solution
					for d in range(len(n_state.du_processing[rrh[i[0]].node])):
						if not checkSwitch(d, rrh[i[0]].wavelength):
							if n_state.checkCapacityDU(rrh[i[0]].node, d):
								rrh[i[0]].du = d
								updateVDU(d, rrh[i[0]].node, n_state)
								updateSwitch(rrh[i[0]].node, n_state)
								break
						elif n_state.checkCapacityDU(rrh[i[0]].node, d):
							if checkSwitch(d, rrh[i[0]].wavelength) and checkSwitchCapacity(rrh[i[0]].node):
								rrh[i[0]].du = d
								updateVDU(d, rrh[i[0]].node, n_state)
								updateSwitch(rrh[i[0]].node, n_state)
								break
			#if rrh[i[0]].du == None:
			#	rrh[i[0]].blocked = True
		if rrh[i[0]].du == None:
			rrh[i[0]].blocked = True
			freeNodeResources()

#this method first try the probabilities of the solution and then, the least loaded VPONs and VDUs and then, another one free
def relaxUpdateLeastLoaded(rrh, solution, n_state):
	#iterate over each RRH on the solution
	#general rule for RRHs (var x and u): index [0] is the RRH, index [1] is the node, [2] is the wavelength/DU
	for i in solution.var_x:
		#the node has capacity on its VDUs?
		if i[1] == 0 and n_state.checkNodeCapacity(i[1]):
			#it has, allocate the node to the RRH
			rrh[i[0]].var_x = i#talvez eu tire essa linha depois
			rrh[i[0]].node = i[1]
		else:
			if n_state.checkNodeCapacity(rrh[i[0]].fog):
					rrh[i[0]].node = rrh[i[0]].fog
		#update the node cost, number of allocated RRHs and capacity
		if rrh[i[0]].node != None:
			updateNode(rrh[i[0]], n_state)
		#if no node was allocated, blocks the requisition
		else:
			rrh[i[0]].blocked = True
		#now, if a node was found for the RRH, tries to allocate the VPON
		if rrh[i[0]].blocked == False:
			if n_state.checkLambdaNode(rrh[i[0]].node,i[2]) and n_state.checkLambdaCapacity(i[2]):
				#allocate the VPON to the RRH and its node and update its state
				updateVponState(rrh[i[0]], i[2], n_state)
			#if the VPON of the solution has no capacity, tries the most loaded on the node
			elif checkNodeVPON(rrh[i[0]].node, n_state):#has active VPONs
				#if it has, gets the most loaded VPON
				vpon = getLeastLoadedVPON(rrh[i[0]], n_state)
				#check if there is capacity on this VPON
				if vpon != -1:#allocate the RRH on this VPON
					updateVponState(rrh[i[0]], vpon, n_state)
			#if there is no available VPON, take another one free
			elif getFreeVPON():
				pass
			#no free non-allocated was found, then blocks the requisition and reverts the allocation done in the processing node
			else:
				rrh[i[0]].blocked = True
				freeNodeResources()
		#if until this moment RRH was not blocked, tries to allocate the VDU
		#get var_u - which contains the VDU
		var_u = getVarU(i, solution)
		#gets the VDU returned on the solution
		vdu = var_u[2]
		if rrh[i[0]].blocked != True:
			break
		else:
			#check if the VDU returned has capacity and if the switch will be used
			if checkAvailabilityVDU(vdu, rrh[i[0]].node, rrh[i[0]].wavelength, n_state) == 1:
				#allocates this VDU on the RRH and did not use the switch
				rrh[i[0]].du = vdu
				updateVDU(vdu, rrh[i[0]].node)
			elif checkAvailabilityVDU(vdu, rrh[i[0]].node, rrh[i[0]].wavelength, n_state) == 0:
				#allocates the VDU and activates the ethernet switch
				rrh[i[0]].du = vdu
				updateVDU(vdu, rrh[i[0]].node)
				updateSwitch(rrh[i[0]].node)
			#if the returned VDU or the switch has no capacity, tries the most loaded
			if rrh[i[0]].du == None:
				most_vdu = getLeastLoadedVDU(rrh[i[0]].node, n_state)
				if checkAvailabilityVDU(most_vdu, rrh[i[0]].node, rrh[i[0]].wavelength, n_state) == 1:
					rrh[i[0]].du = most_vdu
					updateVDU(most_vdu, rrh[i[0]].node)
				elif checkAvailabilityVDU(most_vdu, rrh[i[0]].node, rrh[i[0]].wavelength, n_state) == 0:
					#allocates the VDU and activates the ethernet switch
					rrh[i[0]].du = most_vdu
					updateVDU(most_vdu, rrh[i[0]].node)
					updateSwitch(rrh[i[0]].node)
				elif checkAvailabilityVDU(most_vdu, rrh[i[0]].node, rrh[i[0]].wavelength, n_state) == -1:
					#the VDU or the switch has no free capacity, so, get the first fit VDU different from the returned on the solution
					for d in range(len(n_state.du_processing[rrh[i[0]].node])):
						if not checkSwitch(d, rrh[i[0]].wavelength):
							if n_state.checkCapacityDU(rrh[i[0]].node, d):
								rrh[i[0]].du = d
								updateVDU(d, rrh[i[0]].node)
								#updateSwitch(rrh[i[0]].node)
								break
						elif n_state.checkCapacityDU(rrh[i[0]].node, d):
							if checkSwitch(d, rrh[i[0]].wavelength) and checkSwitchCapacity(rrh[i[0]].node):
								rrh[i[0]].du = d
								updateVDU(d, rrh[i[0]].node)
								updateSwitch(rrh[i[0]].node)
								break
			#if rrh[i[0]].du == None:
			#	rrh[i[0]].blocked = True
		if rrh[i[0]].du == None:
			rrh[i[0]].blocked = True
			freeNodeResources()

#this method only considers the probabilities of both nodes, VPON and VDU for the RRHs
#if any of those has not free capacity, it will not seek for another resource and will block the requisition
def naiveRelaxUpdate(rrh, solution, n_state):
	#iterate over each RRH on the solution
	#general rule for RRHs (var x and u): index [0] is the RRH, index [1] is the node, [2] is the wavelength/DU
	for i in solution.var_x:
		#the node has capacity on its VDUs?
		if i[1] == 0 and n_state.checkNodeCapacity(i[1]):
			#it has, allocate the node to the RRH
			rrh[i[0]].var_x = i#talvez eu tire essa linha depois
			rrh[i[0]].node = i[1]
		else:
			if n_state.checkNodeCapacity(rrh[i[0]].fog):
					rrh[i[0]].node = rrh[i[0]].fog
		#update the node cost, number of allocated RRHs and capacity
		if rrh[i[0]].node != None:
			updateNode(rrh[i[0]], n_state)
		#if no node was allocated, blocks the requisition
		else:
			rrh[i[0]].blocked = True
		#now, if a node was found for the RRH, tries to allocate the VPON
		if rrh[i[0]].blocked == False:
			if n_state.checkLambdaNode(rrh[i[0]].node,i[2]) and n_state.checkLambdaCapacity(i[2]):
				#allocate the VPON to the RRH and its node and update its state
				updateVponState(rrh[i[0]], i[2], n_state)
			#no free non-allocated was found, then blocks the requisition and reverts the allocation done in the processing node
			else:
				rrh[i[0]].blocked = True
				freeNodeResources()
		#if until this moment RRH was not blocked, tries to allocate the VDU
		#get var_u - which contains the VDU
		var_u = getVarU(i, solution)
		#gets the VDU returned on the solution
		vdu = var_u[2]
		if rrh[i[0]].blocked != True:
			break
		else:
			#check if the VDU returned has capacity and if the switch will be used
			if checkAvailabilityVDU(vdu, rrh[i[0]].node, rrh[i[0]].wavelength, n_state) == 1:
				#allocates this VDU on the RRH and did not use the switch
				rrh[i[0]].du = vdu
				updateVDU(vdu, rrh[i[0]].node)
			elif checkAvailabilityVDU(vdu, rrh[i[0]].node, rrh[i[0]].wavelength, n_state) == 0:
				#allocates the VDU and activates the ethernet switch
				rrh[i[0]].du = vdu
				updateVDU(vdu, rrh[i[0]].node)
				updateSwitch(rrh[i[0]].node)
			#if rrh[i[0]].du == None:
			#	rrh[i[0]].blocked = True
		if rrh[i[0]].du == None:
			rrh[i[0]].blocked = True
			freeNodeResources()

#this method tries to allocate vBBUs in the most loaded VPON in a node and in the VDU with most probability, then in the VPON with most probability, then in another one available
def mostLoadedVPON(rrh, solution, n_state):
	#iterate over each RRH on the solution
	#general rule for RRHs (var x and u): index [0] is the RRH, index [1] is the node, [2] is the wavelength/DU
	for i in solution.var_x:
		#the node has capacity on its VDUs?
		if i[1] == 0 and n_state.checkNodeCapacity(i[1]):
			#it has, allocate the node to the RRH
			rrh[i[0]].var_x = i#talvez eu tire essa linha depois
			rrh[i[0]].node = i[1]
		else:
			if n_state.checkNodeCapacity(rrh[i[0]].fog):
					rrh[i[0]].node = rrh[i[0]].fog
		#update the node cost, number of allocated RRHs and capacity
		if rrh[i[0]].node != None:
			updateNode(rrh[i[0]], n_state)
		#if no node was allocated, blocks the requisition
		else:
			rrh[i[0]].blocked = True
		#now, if a node was found for the RRH, tries to allocate the VPON
		if rrh[i[0]].blocked == False:
			#verifies if the node has an activate VPON
			if checkNodeVPON(rrh[i[0]].node, n_state):#has active VPONs
				#if it has, gets the most loaded VPON
				vpon = getMostLoadedVPON(rrh[i[0]], n_state)
				#check if there is capacity on this VPON
				if vpon != -1:#allocate the RRH on this VPON
					updateVponState(rrh[i[0]], vpon, n_state)
			#if not, take the VPON returned on the solution
			#check if the VPON returned on the solution has capacity to support the RRH
			elif n_state.checkLambdaNode(rrh[i[0]].node,i[2]) and n_state.checkLambdaCapacity(i[2]):
				#allocate the VPON to the RRH and its node and update its state
				updateVponState(rrh[i[0]], i[2], n_state)
			#if neither an already allocated VPON or the returned one has capacity, take another one that is free
			elif getFreeVPON():
				pass
			#no free non-allocated was found, then blocks the requisition and reverts the allocation done in the processing node
			else:
				rrh[i[0]].blocked = True
				freeNodeResources()
		#if until this moment RRH was not blocked, tries to allocate the VDU
		#get var_u - which contains the VDU
		var_u = getVarU(i, solution)
		#gets the VDU returned on the solution
		vdu = var_u[2]
		if rrh[i[0]].blocked != True:
			#check if the VDU returned has capacity and if the switch will be used
			if checkAvailabilityVDU(vdu, rrh[i[0]].node, rrh[i[0]].wavelength, n_state) == 1:
				#allocates this VDU on the RRH and did not use the switch
				rrh[i[0]].du = vdu
				updateVDU(vdu, rrh[i[0]].node)
			elif checkAvailabilityVDU(vdu, rrh[i[0]].node, rrh[i[0]].wavelength, n_state) == 0:
				#allocates the VDU and activates the ethernet switch
				rrh[i[0]].du = vdu
				updateVDU(vdu, rrh[i[0]].node, n_state)
				updateSwitch(rrh[i[0]].node, n_state)
			elif heckAvailabilityVDU(vdu, rrh[i[0]].node, rrh[i[0]].wavelength, n_state) == -1:
				#the VDU or the switch has no free capacity, so, get the first fit VDU different from the returned on the solution
				for d in range(len(n_state.du_processing[rrh[i[0]].node])):
					if not checkSwitch(d, rrh[i[0]].wavelength):
						if n_state.checkCapacityDU(rrh[i[0]].node, d):
							rrh[i[0]].du = d
							updateVDU(vdu, rrh[i[0]].node, n_state)
							#updateSwitch(rrh[i[0]].node, n_state)
							break
					elif n_state.checkCapacityDU(rrh[i[0]].node, d):
						if checkSwitch(d, rrh[i[0]].wavelength) and checkSwitchCapacity(rrh[i[0]].node):
							rrh[i[0]].du = d
							updateVDU(vdu, rrh[i[0]].node, n_state)
							updateSwitch(rrh[i[0]].node, n_state)
							break
		if rrh[i[0]].du == None:
			rrh[i[0]].blocked = True
			freeNodeResources()

#this method reduces the VPONs and VDUs used in a node
#it will always try to allocate the most loaded VPON in a node and the most loaded VDU
def mostLoadedVponVDU(rrh, solution, n_state):
	#general rule for RRHs (var x and u): index [0] is the RRH, index [1] is the node, [2] is the wavelength/DU
	for i in solution.var_x:
		#the node has capacity on its VDUs?
		if i[1] == 0 and n_state.checkNodeCapacity(i[1]):
			#it has, allocate the node to the RRH
			rrh[i[0]].var_x = i#talvez eu tire essa linha depois
			rrh[i[0]].node = i[1]
		else:
			if n_state.checkNodeCapacity(rrh[i[0]].fog):
					rrh[i[0]].node = rrh[i[0]].fog
		#update the node cost, number of allocated RRHs and capacity
		if rrh[i[0]].node != None:
			updateNode(rrh[i[0]], n_state)
		#if no node was allocated, blocks the requisition
		else:
			rrh[i[0]].blocked = True
		#now, if a node was found for the RRH, tries to allocate the VPON
		if rrh[i[0]].blocked == False:
			#verifies if the node has an activate VPON
			if checkNodeVPON(rrh[i[0]].node, n_state):#has active VPONs
				#if it has, gets the most loaded VPON
				vpon = getMostLoadedVPON(rrh[i[0]], n_state)
				#check if there is capacity on this VPON
				if vpon != -1:#allocate the RRH on this VPON
					updateVponState(rrh[i[0]], vpon, n_state)
			#if not, take the VPON returned on the solution
			#check if the VPON returned on the solution has capacity to support the RRH
			elif n_state.checkLambdaNode(rrh[i[0]].node,i[2]) and n_state.checkLambdaCapacity(i[2]):
				#allocate the VPON to the RRH and its node and update its state
				updateVponState(rrh[i[0]], i[2], n_state)
			#if neither an already allocated VPON or the returned one has capacity, take another one that is free
			elif getFreeVPON():
				pass
			#no free non-allocated was found, then blocks the requisition and reverts the allocation done in the processing node
			else:
				rrh[i[0]].blocked = True
				freeNodeResources()
		#if until this moment RRH was not blocked, tries to allocate the VDU
		#get var_u - which contains the VDU
		var_u = getVarU(i, solution)
		#gets the VDU returned on the solution
		vdu = var_u[2]
		if rrh[i[0]].blocked != True:
			#tries to allocate on the most loaded VDU
			most_vdu = getMostLoadedVDU(rrh[i[0]].node, n_state)
			if checkAvailabilityVDU(most_vdu, rrh[i[0]].node, rrh[i[0]].wavelength, n_state) == 1:
				rrh[i[0]].du = most_vdu
				updateVDU(most_vdu, rrh[i[0]].node)
			elif checkAvailabilityVDU(most_vdu, rrh[i[0]].node, rrh[i[0]].wavelength, n_state) == 0:
				#allocates the VDU and activates the ethernet switch
				rrh[i[0]].du = most_vdu
				updateVDU(most_vdu, rrh[i[0]].node, n_state)
				updateSwitch(rrh[i[0]].node, n_state)
			elif checkAvailabilityVDU(most_vdu, rrh[i[0]].node, rrh[i[0]].wavelength, n_state) == -1:
				#if the most loaded VDU or the switch has no free capacity, tries to get the returned on the solution and then, another one free
				if vdu != most_vdu:
					if checkAvailabilityVDU(vdu, rrh[i[0]].node, rrh[i[0]].wavelength, n_state) == 1:
						rrh[i[0]].du = vdu
						updateVDU(vdu, rrh[i[0]].node, n_state)
					elif checkAvailabilityVDU(vdu, rrh[i[0]].node, rrh[i[0]].wavelength, n_state) == 0:
						#allocates the VDU and activates the ethernet switch
						rrh[i[0]].du = vdu
						updateVDU(vdu, rrh[i[0]].node, n_state)
						updateSwitch(rrh[i[0]].node, n_state)
				if rrh[i[0]].du == None:
				#elif not checkAvailabilityVDU(vdu, rrh[i[0]].node, rrh[i[0]].wavelength):
					#the most loaded VDU or the switch has no free capacity, so, get the first fit VDU different from the returned on the solution
					for d in range(len(n_state.du_processing[rrh[i[0]].node])):
						if not checkSwitch(d, rrh[i[0]].wavelength):
							if n_state.checkCapacityDU(rrh[i[0]].node, d):
								rrh[i[0]].du = d
								updateVDU(d, rrh[i[0]].node)
								break
						elif n_state.checkCapacityDU(rrh[i[0]].node, d):
							if checkSwitch(d, rrh[i[0]].wavelength) and checkSwitchCapacity(rrh[i[0]].node):
								rrh[i[0]].du = d
								updateVDU(d, rrh[i[0]].node)
								updateSwitch(rrh[i[0]].node)
								break
		if rrh[i[0]].du == None:
			rrh[i[0]].blocked = True
			freeNodeResources()

#it will always try to allocate the least loaded VPON in a node and the least loaded VDU
def leastLoadedVponVDU(rrh, solution, n_state):
	#general rule for RRHs (var x and u): index [0] is the RRH, index [1] is the node, [2] is the wavelength/DU
	for i in solution.var_x:
		#the node has capacity on its VDUs?
		if i[1] == 0 and n_state.checkNodeCapacity(i[1]):
			#it has, allocate the node to the RRH
			rrh[i[0]].var_x = i#talvez eu tire essa linha depois
			rrh[i[0]].node = i[1]
		else:
			if n_state.checkNodeCapacity(rrh[i[0]].fog):
					rrh[i[0]].node = rrh[i[0]].fog
		#update the node cost, number of allocated RRHs and capacity
		if rrh[i[0]].node != None:
			updateNode(rrh[i[0]], n_state)
		#if no node was allocated, blocks the requisition
		else:
			rrh[i[0]].blocked = True
		#now, if a node was found for the RRH, tries to allocate the VPON
		if rrh[i[0]].blocked == False:
			#verifies if the node has an activate VPON
			if checkNodeVPON(rrh[i[0]].node, n_state):#has active VPONs
				#if it has, gets the most loaded VPON
				vpon = getLeastLoadedVPON(rrh[i[0]], n_state)
				#check if there is capacity on this VPON
				if vpon != -1:#allocate the RRH on this VPON
					updateVponState(rrh[i[0]], vpon, n_state)
			#if not, take the VPON returned on the solution
			#check if the VPON returned on the solution has capacity to support the RRH
			elif n_state.checkLambdaNode(rrh[i[0]].node,i[2]) and n_state.checkLambdaCapacity(i[2]):
				#allocate the VPON to the RRH and its node and update its state
				updateVponState(rrh[i[0]], i[2], n_state)
			#if neither an already allocated VPON or the returned one has capacity, take another one that is free
			elif getFreeVPON():
				pass
			#no free non-allocated was found, then blocks the requisition and reverts the allocation done in the processing node
			else:
				rrh[i[0]].blocked = True
				freeNodeResources()
		#if until this moment RRH was not blocked, tries to allocate the VDU
		#get var_u - which contains the VDU
		var_u = getVarU(i, solution)
		#gets the VDU returned on the solution
		vdu = var_u[2]
		if rrh[i[0]].blocked != True:
			#tries to allocate on the most loaded VDU
			least_vdu = getLeastLoadedVDU(rrh[i[0]].node, n_state)
			if checkAvailabilityVDU(least_vdu, rrh[i[0]].node, rrh[i[0]].wavelength, n_state) == 1:
				rrh[i[0]].du = least_vdu
				updateVDU(least_vdu, rrh[i[0]].node, n_state)
			elif checkAvailabilityVDU(least_vdu, rrh[i[0]].node, rrh[i[0]].wavelength, n_state) == 0:
				#allocates the VDU and activates the ethernet switch
				rrh[i[0]].du = least_vdu
				updateVDU(least_vdu, rrh[i[0]].node, n_state)
				updateSwitch(rrh[i[0]].node, n_state)
			elif checkAvailabilityVDU(least_vdu, rrh[i[0]].node, rrh[i[0]].wavelength, n_state) == -1:
				#if the most loaded VDU or the switch has no free capacity, tries to get the returned on the solution and then, another one free
				if vdu != least_vdu:
					if checkAvailabilityVDU(vdu, rrh[i[0]].node, rrh[i[0]].wavelength, n_state) == 1:
						rrh[i[0]].du = vdu
						updateVDU(vdu, rrh[i[0]].node, n_state)
					elif checkAvailabilityVDU(vdu, rrh[i[0]].node, rrh[i[0]].wavelength, n_state) == 0:
						#allocates the VDU and activates the ethernet switch
						rrh[i[0]].du = vdu
						updateVDU(vdu, rrh[i[0]].node, n_state)
						updateSwitch(rrh[i[0]].node, n_state)
				if rrh[i[0]].du == None:
				#elif not checkAvailabilityVDU(vdu, rrh[i[0]].node, rrh[i[0]].wavelength):
					#the most loaded VDU or the switch has no free capacity, so, get the first fit VDU different from the returned on the solution
					for d in range(len(n_state.du_processing[rrh[i[0]].node])):
						if not checkSwitch(d, rrh[i[0]].wavelength):
							if n_state.checkCapacityDU(rrh[i[0]].node, d):
								rrh[i[0]].du = d
								updateVDU(d, rrh[i[0]].node, n_state)
								break
						elif n_state.checkCapacityDU(rrh[i[0]].node, d):
							if checkSwitch(d, rrh[i[0]].wavelength) and checkSwitchCapacity(rrh[i[0]].node):
								rrh[i[0]].du = d
								updateVDU(d, rrh[i[0]].node, n_state)
								updateSwitch(rrh[i[0]].node, n_state)
								break
		if rrh[i[0]].du == None:
			rrh[i[0]].blocked = True
			freeNodeResources()

#this method reduces the VPONs and VDUs used in a node
#it will always try to allocate the most loaded VPON in a node and the most loaded VDU that matches the VPONs allocated firstly
def mostLoadedEqualVponVDU(rrh, solution, n_state):
	pass

#this method allocates the vBBU in the least loaded VPON in a node, then in the one returned on the solution, then, in another one available
def leastLoadedVPON(rrh, solution, n_state):
	#iterate over each RRH on the solution
	for i in solution.var_x:
		#the node has capacity on its VDUs?
		if i[1] == 0 and n_state.checkNodeCapacity(i[1]):
			#it has, allocate the node to the RRH
			rrh[i[0]].var_x = i#talvez eu tire essa linha depois
			rrh[i[0]].node = i[1]
		else:
			if n_state.checkNodeCapacity(rrh[i[0]].fog):
					rrh[i[0]].node = rrh[i[0]].fog
		#update the node cost, number of allocated RRHs and capacity
		if rrh[i[0]].node != None:
			updateNode(rrh[i[0]], n_state)
		#if no node was allocated, blocks the requisition
		else:
			rrh[i[0]].blocked = True
		#now, if a node was found for the RRH, tries to allocate the VPON
		if rrh[i[0]].blocked == False:
			#verifies if the node has an activate VPON
			if checkNodeVPON(rrh[i[0]].node, n_state):#has active VPONs
				#if it has, gets the most loaded VPON
				vpon = getLeastLoadedVPON(rrh[i[0]], n_state)
				#check if there is capacity on this VPON
				if vpon != -1:#allocate the RRH on this VPON
					updateVponState(rrh[i[0]], vpon, n_state)
			#if not, take the VPON returned on the solution
			#check if the VPON returned on the solution has capacity to support the RRH
			elif n_state.checkLambdaNode(rrh[i[0]].node,i[2]) and n_state.checkLambdaCapacity(i[2]):
				#allocate the VPON to the RRH and its node and update its state
				updateVponState(rrh[i[0]], i[2], n_state)
			#if neither an already allocated VPON or the returned one has capacity, take another one that is free
			elif getFreeVPON():
				pass
			#no free non-allocated was found, then blocks the requisition and reverts the allocation done in the processing node
			else:
				rrh[i[0]].blocked = True
				freeNodeResources()
		#if until this moment RRH was not blocked, tries to allocate the VDU
		#get var_u - which contains the VDU
		var_u = getVarU(i, solution)
		#gets the VDU returned on the solution
		vdu = var_u[2]
		if rrh[i[0]].blocked != True:
			#check if the VDU returned has capacity and if the switch will be used
			if checkAvailabilityVDU(vdu, rrh[i[0]].node, rrh[i[0]].wavelength, n_state) == 1:
				#allocates this VDU on the RRH and did not use the switch
				rrh[i[0]].du = vdu
				updateVDU(vdu, rrh[i[0]].node)
			elif checkAvailabilityVDU(vdu, rrh[i[0]].node, rrh[i[0]].wavelength, n_state) == 0:
				#allocates the VDU and activates the ethernet switch
				rrh[i[0]].du = vdu
				updateVDU(vdu, rrh[i[0]].node, n_state)
				updateSwitch(rrh[i[0]].node, n_state)
			elif checkAvailabilityVDU(vdu, rrh[i[0]].node, rrh[i[0]].wavelength, n_state) == -1:
				#the VDU or the switch has no free capacity, so, get the first fit VDU different from the returned on the solution
				for d in range(len(n_state.du_processing[rrh[i[0]].node])):
					if not checkSwitch(d, rrh[i[0]].wavelength):
						if n_state.checkCapacityDU(rrh[i[0]].node, d):
							rrh[i[0]].du = d
							updateVDU(d, rrh[i[0]].node, n_state)
							#updateSwitch(rrh[i[0]].node, n_state)
							break
					elif n_state.checkCapacityDU(rrh[i[0]].node, d):
						if checkSwitch(d, rrh[i[0]].wavelength) and checkSwitchCapacity(rrh[i[0]].node):
							rrh[i[0]].du = d
							updateVDU(d, rrh[i[0]].node, n_state)
							updateSwitch(rrh[i[0]].node, n_state)
							break
		if rrh[i[0]].du == None:
			rrh[i[0]].blocked = True
			freeNodeResources()

#this naive most loaded VPON heuristic allocates the most loaded VPON and on the returned VDU only and no other else
def naiveMostLoadedVPON(rrh, solution, n_state):
	#iterate over each RRH on the solution
	#general rule for RRHs (var x and u): index [0] is the RRH, index [1] is the node, [2] is the wavelength/DU
	for i in solution.var_x:
		#the node has capacity on its VDUs?
		if i[1] == 0 and n_state.checkNodeCapacity(i[1]):
			#it has, allocate the node to the RRH
			rrh[i[0]].var_x = i#talvez eu tire essa linha depois
			rrh[i[0]].node = i[1]
		else:
			if n_state.checkNodeCapacity(rrh[i[0]].fog):
					rrh[i[0]].node = rrh[i[0]].fog
		#update the node cost, number of allocated RRHs and capacity
		if rrh[i[0]].node != None:
			updateNode(rrh[i[0]], n_state)
		#if no node was allocated, blocks the requisition
		else:
			rrh[i[0]].blocked = True
		#now, if a node was found for the RRH, tries to allocate the VPON
		if rrh[i[0]].blocked == False:
			#verifies if the node has an activate VPON
			if checkNodeVPON(rrh[i[0]].node, n_state):#has active VPONs
				#if it has, gets the most loaded VPON
				vpon = getMostLoadedVPON(rrh[i[0]], n_state)
				#check if there is capacity on this VPON
				if vpon != -1:#allocate the RRH on this VPON
					updateVponState(rrh[i[0]], vpon, n_state)
			else:
				rrh[i[0]].blocked = True
				freeNodeResources()
		#if until this moment RRH was not blocked, tries to allocate the VDU
		#get var_u - which contains the VDU
		var_u = getVarU(i, solution)
		#gets the VDU returned on the solution
		vdu = var_u[2]
		if rrh[i[0]].blocked != True:
			#check if the VDU returned has capacity and if the switch will be used
			if checkAvailabilityVDU(vdu, rrh[i[0]].node, rrh[i[0]].wavelength, n_state) == 1:
				#allocates this VDU on the RRH and did not use the switch
				rrh[i[0]].du = vdu
				updateVDU(vdu, rrh[i[0]].node, n_state)
			elif checkAvailabilityVDU(vdu, rrh[i[0]].node, rrh[i[0]].wavelength, n_state) == 0:
				#allocates the VDU and activates the ethernet switch
				rrh[i[0]].du = vdu
				updateVDU(vdu, rrh[i[0]].node, n_state)
				updateSwitch(rrh[i[0]].node, n_state)
		if rrh[i[0]].du == None:
			rrh[i[0]].blocked = True
			freeNodeResources()

#this naive least loaded VPON heuristic allocates the least loaded VPON only and the VDU of the solution and no other else
def naiveLeastLoadedVPON(rrh, solution, n_state):
	#iterate over each RRH on the solution
	#general rule for RRHs (var x and u): index [0] is the RRH, index [1] is the node, [2] is the wavelength/DU
	for i in solution.var_x:
		#the node has capacity on its VDUs?
		if i[1] == 0 and n_state.checkNodeCapacity(i[1]):
			#it has, allocate the node to the RRH
			rrh[i[0]].var_x = i#talvez eu tire essa linha depois
			rrh[i[0]].node = i[1]
		else:
			if n_state.checkNodeCapacity(rrh[i[0]].fog):
					rrh[i[0]].node = rrh[i[0]].fog
		#update the node cost, number of allocated RRHs and capacity
		if rrh[i[0]].node != None:
			updateNode(rrh[i[0]], n_state)
		#if no node was allocated, blocks the requisition
		else:
			rrh[i[0]].blocked = True
		#now, if a node was found for the RRH, tries to allocate the VPON
		if rrh[i[0]].blocked == False:
			#verifies if the node has an activate VPON
			if checkNodeVPON(rrh[i[0]].node, n_state):#has active VPONs
				#if it has, gets the most loaded VPON
				vpon = getLeastLoadedVPON(rrh[i[0]], n_state)
				#check if there is capacity on this VPON
				if vpon != -1:#allocate the RRH on this VPON
					updateVponState(rrh[i[0]], vpon, n_state)
			else:
				rrh[i[0]].blocked = True
				freeNodeResources()
		#if until this moment RRH was not blocked, tries to allocate the VDU
		#get var_u - which contains the VDU
		var_u = getVarU(i, solution)
		#gets the VDU returned on the solution
		vdu = var_u[2]
		if rrh[i[0]].blocked != True:
			#check if the VDU returned has capacity and if the switch will be used
			if checkAvailabilityVDU(vdu, rrh[i[0]].node, rrh[i[0]].wavelength, n_state) == 1:
				#allocates this VDU on the RRH and did not use the switch
				rrh[i[0]].du = vdu
				updateVDU(vdu, rrh[i[0]].node, n_state)
			elif checkAvailabilityVDU(vdu, rrh[i[0]].node, rrh[i[0]].wavelength, n_state) == 0:
				#allocates the VDU and activates the ethernet switch
				rrh[i[0]].du = vdu
				updateVDU(vdu, rrh[i[0]].node, n_state)
				updateSwitch(rrh[i[0]].node, n_state)
		if rrh[i[0]].du == None:
			rrh[i[0]].blocked = True
			freeNodeResources()

#update VDU capacity, state and cost
def updateVDU(vdu, node, n_state):
	n_state.du_processing[node][vdu] -= 1
	if n_state.du_state[node][vdu] == 0:
		#du was deactivated - activates it
		n_state.du_state[node][vdu] = 1
		n_state.du_cost[node][vdu] = 0.0

#check if a VDU will require the ethernet switch activation
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

#check if a VDU can be used by checking its capacity and the capacity of the ethernet switch, if it will be activated
#if it is not necessary to use the switch (VDU and VPONs are in the same LC), return 1
#if VDU and VPONs are in different LCs and both the VDU and the Switch has capacity, return 0
#if the VDU or the siwtch, in any case has not free capacity, return False
def checkAvailabilityVDU(vdu, node, vpon, n_state):
	#first, check if the VDU has free capacity
	#print(n_state.du_processing)
	if not n_state.checkCapacityDU(node, vdu):
		#return False
		return -1
	else:
		#verify if it is necessary to use the switch
		if not checkSwitch(vdu, vpon):
			return 1
		else:
			#check switch capacity
			if not checkSwitchCapacity(node, n_state):
				#return False
				return -1
			else:
				return 0

#update switch
def updateSwitch(node, n_state):
	n_state.switchBandwidth[node] -= n_state.RRHband
	if n_state.switch_state[node] == 0:
		n_state.switch_state[node] = 1
		n_state.switch_cost[node] = 0.0

#update the "real" network state with the best solution found by many iterations of the relaxation (or any other algorithm)
def updateRealNetworkState(auxiliaryNetwork, realNetwork):
	realNetwork.rrhs_on_nodes = auxiliaryNetwork.rrhs_on_nodes
	#to assure that each lamba allocatedto a node can only be used on that node on the incremental execution of the ILP
	realNetwork.lambda_node = auxiliaryNetwork.lambda_node
	#capacity of each VDU
	realNetwork.du_processing = auxiliaryNetwork.du_processing
	#used to calculate the processing usage of the node
	realNetwork.dus_total_capacity = auxiliaryNetwork.dus_total_capacity
	#state of each VDU
	realNetwork.du_state = auxiliaryNetwork.du_state
	#state of each node
	realNetwork.nodeState = auxiliaryNetwork.nodeState
	#power cost of each processing node
	realNetwork.nodeCost = auxiliaryNetwork.nodeCost
	#power cost of each VDu
	realNetwork.du_cost = auxiliaryNetwork.du_cost
	#power cost of each Line Card
	realNetwork.lc_cost = auxiliaryNetwork.lc_cost
	#power cost of the backplane switch
	realNetwork.switch_cost = auxiliaryNetwork.switch_cost
	#bandwidth capacity of the backplane switch
	realNetwork.switchBandwidth =  auxiliaryNetwork.switchBandwidth
	#bandwidth capacity of each wavelength
	realNetwork.wavelength_capacity = auxiliaryNetwork.wavelength_capacity
	#basic CPRI line used
	realNetwork.RRHband = auxiliaryNetwork.RRHband
	#capacity of each VDU on the cloud
	realNetwork.cloud_du_capacity = auxiliaryNetwork.cloud_du_capacity
	#capacity of each VDU in a fog node
	realNetwork.fog_du_capacity = auxiliaryNetwork.fog_du_capacity
	#state of each wavelength/VPON
	realNetwork.lambda_state = auxiliaryNetwork.lambda_state
	#state of the backplane switch in each processing node
	realNetwork.switch_state = auxiliaryNetwork.switch_state
	#other variables
	#lambdas\VPONs in each processing node
	realNetwork.nodes_lambda = auxiliaryNetwork.nodes_lambda
	#current capacity of each VPON of each processing node
	realNetwork.nodes_vpons_capacity = auxiliaryNetwork.nodes_vpons_capacity
	#blocked RRHs
	realNetwork.relax_blocked = auxiliaryNetwork.relax_blocked

#this class represents a "virtual" network state, used to keep a solution returned from the relaxation algorithms
#this class will be used to be put on a list with n results drawn from n executions of the relaxations, when the instance with the best result will be used to
#update the "real" network state
class NetworkState(object):
	#constructor 1
	def __init__(self, aId, nodes_amount, rrhs_on_nodes = None,lambda_node = None,du_processing = None,
		dus_total_capacity = None, du_state = None, nodeState = None, 
		nodeCost = None, du_cost = None, lc_cost = None, 
		switch_cost = None, switchBandwidth = None, wavelength_capacity = None, RRHband = None, 
		cloud_du_capacity = None, fog_du_capacity = None, lambda_state = None, switch_state = None, nodes_lambda = None, nodes_vpons_capacity = None):
		#Id of this network state
		self.aId = aId
		#to keep the amount of RRHs being processed on each node
		if rrhs_on_nodes == None:
			self.rrhs_on_nodes = [0,0,0]
		else:	
			self.rrhs_on_nodes = rrhs_on_nodes
		#to assure that each lamba allocatedto a node can only be used on that node on the incremental execution of the ILP
		if lambda_node == None:
			self.lambda_node = [[1,1,1],[1,1,1],[1,1,1],[1,1,1]]
		else:
			self.lambda_node = lambda_node
		#capacity of each VDU
		if du_processing == None:
			self.du_processing = [[1.0, 1.0, 1.0, 1.0],[1.0, 1.0, 1.0, 1.0 ],[1.0, 1.0, 1.0, 1.0 ],]
		else:
			self.du_processing = du_processing
		#used to calculate the processing usage of the node
		if dus_total_capacity == None:
			self.dus_total_capacity = [[8.0, 8.0, 8.0, 8.0],[4.0, 4.0, 4.0, 4.0 ],[4.0, 4.0, 4.0, 4.0 ]]
		else:
			self.dus_total_capacity = dus_total_capacity
		#state of each VDU
		if du_state == None:
			self.du_state = [[0, 0, 0, 0],[0, 0, 0, 0],[0, 0, 0, 0]]
		else:
			self.du_state = du_state
		#state of each node
		if nodeState == None:
			self.nodeState = [0,0,0]
		else:
			self.nodeState = nodeState
		#power cost of each processing node
		if nodeCost == None:
			self.nodeCost = [0.0,300.0,300.0,]
		else:
			self.nodeCost = nodeCost
		#power cost of each VDu
		if du_cost == None:
			self.du_cost = [[100.0, 100.0, 100.0, 100.0],[50.0, 50.0, 50.0, 50.0],[50.0, 50.0, 50.0, 50.0],]
		else:
			self.du_cost = du_cost
		#power cost of each Line Card
		if lc_cost == None:
			self.lc_cost = [20.0,20.0,20.0,20.0,]
		else:
			self.lc_cost = lc_cost
		#power cost of the backplane switch
		if switch_cost == None:
			self.switch_cost = [15.0, 15.0, 15.0]
		else:
			self.switch_cost = switch_cost
		#bandwidth capacity of the backplane switch
		if switchBandwidth == None:
			self.switchBandwidth = [10000.0,10000.0,10000.0]
		else:
			self.switchBandwidth =  switchBandwidth
		#bandwidth capacity of each wavelength
		if wavelength_capacity == None:
			self.wavelength_capacity = [10000.0, 10000.0, 10000.0, 10000.0]
		else:
			self.wavelength_capacity = wavelength_capacity
		#basic CPRI line used
		if RRHband == None:
			self.RRHband = 614.4
		else:
			self.RRHband = RRHband
		#capacity of each VDU on the cloud
		if cloud_du_capacity == None:
			self.cloud_du_capacity = 9.0
		else:
			self.cloud_du_capacity = cloud_du_capacity
		#capacity of each VDU in a fog node
		if fog_du_capacity == None:
			self.fog_du_capacity = 1.0
		else:
			self.fog_du_capacity = fog_du_capacity
		#state of each wavelength/VPON
		if lambda_state == None:
			self.lambda_state = [0,0,0,0]
		else:
			self.lambda_state = lambda_state
		#state of the backplane switch in each processing node
		if switch_state == None:
			self.switch_state = [0,0,0]
		else:
			self.switch_state = switch_state
		#number of nodes
		self.nodes = nodes_amount
		#lambdas in each node
		if nodes_lambda == None:
			self.nodes_lambda = {}
			for i in nodes_amount:
				self.nodes_lambda[i] = []
		else:
			self.nodes_lambda = nodes_lambda
		#capacity of each VPON in each node
		if nodes_vpons_capacity == None:
			self.nodes_vpons_capacity = {}
			for i in nodes_amount:
				self.nodes_vpons_capacity[i] = {}
		else:
			self.nodes_vpons_capacity = nodes_vpons_capacity
		#metrics obtained on the solution
		self.delay = None
		self.power = None
		self.lambda_wastage = None
		self.execution_time = None
		self.migration_probability = None
		self.total_migrations = None
		#to keep blocked RRHs
		self.relax_blocked = None
		#to keep record of an old network state to calculate vBBUs migrations
		self.old_network_state = None
		#metrics of the solution provided by the ILP
		self.solution = None
		self.solution_values = None

	#set the value of any metric
	def setMetric(self, metric, aValue):
		setattr(self, metric, aValue)

	#set the solution variables returned from the ILP
	def setSolutionValues(self, solution, solutionValue):
		self.solution = solution
		self.solution_values = setSolutionValues

	#methods from the ILP class, copied here for availability when the relaxation process is evaluating several solutions
	#check if a DU in some node has free capacity
	def checkCapacityDU(self, node, du):
		if self.du_processing[node][du] > 0:
			return True
		else:
			return False

	#get a DU's capacity
	def getCapacityDU(self, node, du):
		return self.du_processing[node][du]

	#check if a node has free processing capacity, considering all of its DUs
	def checkNodeCapacity(self, node):
		capacity = 0.0
		capacity = sum(self.du_processing[node])
		if capacity > 0:
			return True
		else:
			return False

	#get node free processing capacity
	def getNodeCapacity(self, node):
		capacity = 0.0
		capacity = sum(self.du_processing[node])
		return capacity

	#check if a lambda has capacity for a request
	def checkLambdaCapacity(self, wavelength):
		if self.wavelength_capacity[wavelength] >= 614.4:
			return True
		else:
			return False

	#check if a lambda has capacity for a request
	def checkLambdaCapacityRRH(self, wavelength, bandwdith):
		if self.wavelength_capacity[wavelength] >= bandwdith:
			return True
		else:
			return False

	#get bandwidth capacity of a lambda
	def getLambdaCapacity(self, wavelength):
		return self.wavelength_capacity[wavelength]

	#block an already allocated lambda in other nodes
	def blockLambda(self, wavelength, node):
		ln = self.lambda_node[wavelength]
		for i in range(len(ln)):
			if i != node:
				ln[i] = 0


	#check if a lambda is free to be allocated on a given node
	def checkLambdaNode(self, node, wavelength):
		if self.lambda_node[wavelength][node] == 1:
			return True
		else:
			return False

	#check if node has at least one activated VPON
	def checkNodeVPON(self, node):
		if self.nodes_lambda[node]:
			print(self.nodes_lambda[node])
			return True
		else:
			print("SUHSUSUHS")
			return False

	#get the first available VPON in a node
	def getFirstFreeVPON(self, node):
		if checkNodeVPON(node):
			for i in self.nodes_lambda[node]:
				if getLambdaCapacity(i) >= self.RRHband:
					return i
				else:
					print("NOVPON")
		else:#no VPON here
			return None

	#get the lambda with most allocated RRHs
	def getMaxLoadVPON(self, node):
		vp = max(self.nodes_vpons_capacity[node], key=self.nodes_vpons_capacity[node].get)

	#get the lambda with least allocated RRHs
	def getMinLoadVPON(self, node):
		return min(self.nodes_vpons_capacity[node], key=self.nodes_vpons_capacity[node].get)

	#update the capacity of the vpons allocated in each node:
	def updateNodeVPONsCapacity(self):
		for i in self.nodes_vpons_capacity:
			for j in self.nodes_vpons_capacity[i]:
				self.nodes_vpons_capacity[i][j] = self.wavelength_capacity[j]

	'''
	def __init__(self, aId):
		#Id of this solution
		self.aId = aId
		#to keep the amount of RRHs being processed on each node
		self.rrhs_on_nodes = [0,0,0]
		#to assure that each lamba allocatedto a node can only be used on that node on the incremental execution of the ILP
		self.lambda_node = [[1,1,1],[1,1,1],[1,1,1],[1,1,1],]
		#capacity of each VDU
		self.du_processing = [[8.0, 8.0, 8.0, 8.0],[4.0, 4.0, 4.0, 4.0 ],[4.0, 4.0, 4.0, 4.0 ],]
		#used to calculate the processing usage of the node
		self.dus_total_capacity = [[8.0, 8.0, 8.0, 8.0],[4.0, 4.0, 4.0, 4.0 ],[4.0, 4.0, 4.0, 4.0 ],]
		#state of each VDU
		self.du_state = [[0, 0, 0, 0],[0, 0, 0, 0],[0, 0, 0, 0],]
		#state of each node
		self.nodeState = [0,0,0]
		#power cost of each processing node
		self.nodeCost = [0.0,300.0,300.0,]
		#power cost of each VDu
		self.du_cost = [[100.0, 100.0, 100.0, 100.0],[50.0, 50.0, 50.0, 50.0],[50.0, 50.0, 50.0, 50.0],]
		#power cost of each Line Card
		self.lc_cost = [20.0,20.0,20.0,20.0,]
		#power cost of the backplane switch
		self.switch_cost = [15.0, 15.0, 15.0]
		#bandwidth capacity of the backplane switch
		self.switchBandwidth = [10000.0,10000.0,10000.0]
		#bandwidth capacity of each wavelength
		self.wavelength_capacity = [10000.0, 10000.0, 10000.0, 10000.0]
		#basic CPRI line used
		self.RRHband = 614.4
		#capacity of each VDU on the cloud
		self.cloud_du_capacity = 9.0
		#capacity of each VDU in a fog node
		self.fog_du_capacity = 1.0
		#state of each wavelength/VPON
		self.lambda_state = [0,0,0,0]
		#state of the backplane switch in each processing node
		self.switch_state = [0,0,0]
		#metrics obtained on this solution
		self.delay = None
		self.power = None
		self.lambda_wastage = None
		self.execution_time = None
		self.migration_probability = None
		self.total_migrations = None
	'''
	
#The class below is unutilized in the current version of the simulator
#The methos getBestSolution, getSlutionBestID and getSolutionValuesID were moved to the class NetworkStates
#this class encapsulates several network state to get the one with the best metric
class NetworkStateCollection(object):
	#amount is the number of times that the relaxation will be executed, thus, generates an "amount" number of solutions
	def __init__(self, network_states):
		#list of network state objects
		self.network_states = network_states

	#create the network state objects
	#def initStates(self, amount, rrhs_on_nodes, lambda_node, du_processing, dus_total_capacity, du_state, nodeState,
	#	nodeCost, du_cost, lc_cost, switch_cost, switchBandwidth, wavelength_capacity, RRHband, cloud_du_capacity, 
	#	fog_du_capacity, lambda_state, switch_state, delay, power, lambda_wastage, execution_time, migration_probability, total_migrations):
	#	#create a network state object for each relaxation execution
	#	for i in range(amount):
	#		ns = NetworkState(i, rrhs_on_nodes, lambda_node, du_processing, dus_total_capacity, du_state, nodeState,
	#	nodeCost, du_cost, lc_cost, switch_cost, switchBandwidth, wavelength_capacity, RRHband, cloud_du_capacity, 
	#	fog_du_capacity, lambda_state, switch_state, delay, power, lambda_wastage, execution_time, migration_probability, total_migrations)
	#		#put the object on the list
	#		self.network_states.append(ns)

	#get best network state
	def getBestNetworkState(self, metric, method):
		function = getattr(builtins, method)
		sol = function(self.network_states, key = operator.attrgetter(metric))
		#print("Best solution is {}".format(sol.aId))
		return sol

	#get the best solution for a given metric
	def getBestSolutionID(self, metric, method):
		function = getattr(builtins, method)
		sol = function(self.network_states, key = operator.attrgetter(metric))
		return sol.aId

	#return the ILP solution from the auxiliary network state with best metric found
	def getBestSolution(self, n_state_id):
		for i in self.network_states:
			if i.aId == n_state_id:
				return i.solution

	#return the ILP solution variables from the auxiliary network state with best metric found
	def getSolutionValues(self, n_state_id):
		for i in self.network_states:
			if i.aId == n_state_id:
				return i.solution_values
