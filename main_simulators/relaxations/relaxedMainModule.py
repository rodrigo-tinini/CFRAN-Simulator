from docplex.mp.model import Model
import simpy
import functools
import random as np
import time
import copy
import operator
from enum import Enum
from scipy.stats import norm
import matplotlib.pyplot as plt
import relaxation_test as rlx

#returns the most loaded VDU in a processing node
def getMostLoadedVDU(node, n_state):
	vdus = copy.deepcopy(n_state.du_processing[node])
	while vdus:
		v = min(n_state.du_processing[node])
		if v == 0:
			del vdus[vdus.index(v)]
		else:
			return lista.index(v)

#returns the least loaded VDU in a processing node
def getLeastLoadedVDU(node, n_state):
	vdus = copy.deepcopy(n_state.du_processing[node])
	while vdus:
		v = max(n_state.du_processing[node])
		if v == 0:
			del vdus[vdus.index(v)]
		else:
			return lista.index(v)

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
		if i[0] == aIndex:
			return i


#allocate a VPON to a RRH and its node and update VPON state
def updateVponState(rrh, vpon, n_state):
	n_state.wavelength = vpon
	n_state.wavelength_capacity[rrh.wavelength] -= n_state.RRHband
	if n_state.lambda_state[rrh.wavelength] == 0:
		n_state.lambda_state[rrh.wavelength] = 1
		n_state.lc_cost[rrh.wavelength] = 0
	n_state.nodes_vpons_capacity[rrh.node][vpon] = n_state.wavelength_capacity[vpon]
	blockLambda(rrh.wavelength, rrh.node)

#get any non-allocated VPON
def getFreeVPON(rrh, vpon, n_state):
	for j in range(len(n_state.lambda_state)):
		if n_state.lambda_state[j] == 0: #this lambda is available
			updateVponState(rrh, vpon)
			blockLambda(rrh.wavelength, rrh.node)
			return True
	return False

#get the first available VPON in a node
def getFirstFreeVPON(rrh, n_state):
	for j in range(len(n_state.lambda_node)):
		#another lambda is allocated on the node
		if n_state.lambda_node[j][rrh.node] == 1 and n_state.lambda_node[j][rrh.node] != i[2]:
			#check if it has capacity
			if checkLambdaCapacity(j):
				return j
				break
	return False

#free node resources
def freeNodeResources(rrh, node, n_state):
	rrh.node = None
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

#This method tries to use the first fit VPON in a node, and then, the one with most probability use returned on the solution and then, the first fit that was not allocated to any node
#regarding the node, it tries the one with the most probability, then, the other available node (it will be always cloud or fog)
#regarding the VDU, it consider the one with the most probability returned on the solution, then take the first fit available VDU in the node (it does not aim to reduce swtich delay)
def FirstFitRelaxMinVPON(rrh, solution, n_state):
	#iterate over each RRH on the solution
	#general rule for RRHs (var x and u): index [0] is the RRH, index [1] is the node, [2] is the wavelength/DU
	for i in solution.var_x:
		#the node has capacity on its VDUs?
		if i[1] == 0 and rlx.checkNodeCapacity(i[1]):
			#it has, allocate the node to the RRH
			rrh[i[0]].var_x = i#talvez eu tire essa linha depois
			rrh[i[0]].node = i[1]
		else:
			if rlx.checkNodeCapacity(rrh[i[0]].fog):
					rrh[i[0]].node = rrh[i[0]].fog
		#update the node cost, number of allocated RRHs and capacity
		if rrh[i[0]].node != None:
			updateNode(rrh[i[0]])
		#if no node was allocated, blocks the requisition
		else:
			rrh[i[0]].blocked = True
		#now, if a node was found for the RRH, tries to allocate the VPON
		if rrh[i[0]].blocked == False:
			#verifies if the node has an activate VPON
			if rlx.checkNodeVPON(rrh[i[0]].node):#has active VPONs
				#if it has, gets the first free VPON
				vpon = getFirstFreeVPON(rrh[i[0]])
				#check if there is capacity on this VPON
				if vpon:#allocate the RRH on this VPON
					updateVponState(rrh[i[0]], vpon)
			#if not, take the VPON returned on the solution
			#check if the VPON returned on the solution has capacity to support the RRH
			elif checkLambdaNode(rrh[i[0]].node,i[2]) and checkLambdaCapacity(i[2]):
				#allocate the VPON to the RRH and its node and update its state
				updateVponState(rrh[i[0]], i[2])
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
			if checkAvailabilityVDU(vdu, rrh[i[0]].node, rrh[i[0]].wavelength) == 1:
				#allocates this VDU on the RRH and did not use the switch
				rrh[i[0]].du = vdu
				updateVDU(vdu, rrh[i[0]].node)
			elif checkAvailabilityVDU(vdu, rrh[i[0]].node, rrh[i[0]].wavelength) == 0:
				#allocates the VDU and activates the ethernet switch
				rrh[i[0]].du = vdu
				updateSwitch(rrh[i[0]].node)
			elif not checkAvailabilityVDU(vdu, rrh[i[0]].node, rrh[i[0]].wavelength):
				#the VDU or the switch has no free capacity, so, get the first fit VDU different from the returned on the solution
				for d in range(len(n_state.du_processing[rrh[i[0]].node])):
					if not checkSwitchUse:
						if rlx.checkCapacityDU(rrh[i[0]].node, d):
							rrh[i[0]].du = d
							updateSwitch(rrh[i[0]].node)
							break
					if rlx.checkCapacityDU(rrh[i[0]].node, d):
						if checkSwitchUse(d, rrh[i[0]].wavelength) and checkSwitchCapacity(rrh[i[0]].node):
							rrh[i[0]].du = d
							updateSwitch(rrh[i[0]].node)
							break
		if rrh[i[0]].du == None:
			rrh[i[0]].blocked = True
			freeNodeResources()


#This method tries to use the first fit VPON in a node, and then, the one with most probability use returned on the solution and then, the first fit that was not allocated to any node
#regarding the node, it tries the one with the most probability, then, the other available node (it will be always cloud or fog)
#regarding the VDU, it consider the one with the most probability returned on the solution only
def NaiveVDUFirstFitRelaxMinVPON(rrh, solution, n_state):
	#iterate over each RRH on the solution
	#general rule for RRHs (var x and u): index [0] is the RRH, index [1] is the node, [2] is the wavelength/DU
	for i in solution.var_x:
		#the node has capacity on its VDUs?
		if i[1] == 0 and rlx.checkNodeCapacity(i[1]):
			#it has, allocate the node to the RRH
			rrh[i[0]].var_x = i#talvez eu tire essa linha depois
			rrh[i[0]].node = i[1]
		else:
			if rlx.checkNodeCapacity(rrh[i[0]].fog):
					rrh[i[0]].node = rrh[i[0]].fog
		#update the node cost, number of allocated RRHs and capacity
		if rrh[i[0]].node != None:
			updateNode(rrh[i[0]])
		#if no node was allocated, blocks the requisition
		else:
			rrh[i[0]].blocked = True
		#now, if a node was found for the RRH, tries to allocate the VPON
		if rrh[i[0]].blocked == False:
			#verifies if the node has an activate VPON
			if rlx.checkNodeVPON(rrh[i[0]].node):#has active VPONs
				#if it has, gets the first free VPON
				vpon = getFirstFreeVPON(rrh[i[0]])
				#check if there is capacity on this VPON
				if vpon:#allocate the RRH on this VPON
					updateVponState(rrh[i[0]], vpon)
			#if not, take the VPON returned on the solution
			#check if the VPON returned on the solution has capacity to support the RRH
			elif checkLambdaNode(rrh[i[0]].node,i[2]) and checkLambdaCapacity(i[2]):
				#allocate the VPON to the RRH and its node and update its state
				updateVponState(rrh[i[0]], i[2])
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
			if checkAvailabilityVDU(vdu, rrh[i[0]].node, rrh[i[0]].wavelength) == 1:
				#allocates this VDU on the RRH and did not use the switch
				rrh[i[0]].du = vdu
				updateVDU(vdu, rrh[i[0]].node)
			elif checkAvailabilityVDU(vdu, rrh[i[0]].node, rrh[i[0]].wavelength) == 0:
				#allocates the VDU and activates the ethernet switch
				rrh[i[0]].du = vdu
				updateSwitch(rrh[i[0]].node)
			#if rrh[i[0]].du == None:
			#	rrh[i[0]].blocked = True
		if rrh[i[0]].du == None:
			rrh[i[0]].blocked = True
			freeNodeResources()

#this method only considers the probabilities of both nodes, VPON and VDU for the RRHs
#if any of those has not free capacity, it will not seek for another resource and will block the requisition
def naiveRelaxUpdate(solution, n_state):
	#iterate over each RRH on the solution
	#general rule for RRHs (var x and u): index [0] is the RRH, index [1] is the node, [2] is the wavelength/DU
	for i in solution.var_x:
		#the node has capacity on its VDUs?
		if i[1] == 0 and rlx.checkNodeCapacity(i[1]):
			#it has, allocate the node to the RRH
			rrh[i[0]].var_x = i#talvez eu tire essa linha depois
			rrh[i[0]].node = i[1]
		else:
			if rlx.checkNodeCapacity(rrh[i[0]].fog):
					rrh[i[0]].node = rrh[i[0]].fog
		#update the node cost, number of allocated RRHs and capacity
		if rrh[i[0]].node != None:
			updateNode(rrh[i[0]])
		#if no node was allocated, blocks the requisition
		else:
			rrh[i[0]].blocked = True
		#now, if a node was found for the RRH, tries to allocate the VPON
		if rrh[i[0]].blocked == False:
			if checkLambdaNode(rrh[i[0]].node,i[2]) and checkLambdaCapacity(i[2]):
				#allocate the VPON to the RRH and its node and update its state
				updateVponState(rrh[i[0]], i[2])
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
			if checkAvailabilityVDU(vdu, rrh[i[0]].node, rrh[i[0]].wavelength) == 1:
				#allocates this VDU on the RRH and did not use the switch
				rrh[i[0]].du = vdu
				updateVDU(vdu, rrh[i[0]].node)
			elif checkAvailabilityVDU(vdu, rrh[i[0]].node, rrh[i[0]].wavelength) == 0:
				#allocates the VDU and activates the ethernet switch
				rrh[i[0]].du = vdu
				updateSwitch(rrh[i[0]].node)
			#if rrh[i[0]].du == None:
			#	rrh[i[0]].blocked = True
		if rrh[i[0]].du == None:
			rrh[i[0]].blocked = True
			freeNodeResources()

#this method tries to allocate vBBUs in the most loaded VPON in a node and in the VDU with most probability, then in the VPON with most probability, then in another one available
def mostLoadedVPON(solution, n_state):
	#iterate over each RRH on the solution
	#general rule for RRHs (var x and u): index [0] is the RRH, index [1] is the node, [2] is the wavelength/DU
	for i in solution.var_x:
		#the node has capacity on its VDUs?
		if i[1] == 0 and rlx.checkNodeCapacity(i[1]):
			#it has, allocate the node to the RRH
			rrh[i[0]].var_x = i#talvez eu tire essa linha depois
			rrh[i[0]].node = i[1]
		else:
			if rlx.checkNodeCapacity(rrh[i[0]].fog):
					rrh[i[0]].node = rrh[i[0]].fog
		#update the node cost, number of allocated RRHs and capacity
		if rrh[i[0]].node != None:
			updateNode(rrh[i[0]])
		#if no node was allocated, blocks the requisition
		else:
			rrh[i[0]].blocked = True
		#now, if a node was found for the RRH, tries to allocate the VPON
		if rrh[i[0]].blocked == False:
			#verifies if the node has an activate VPON
			if rlx.checkNodeVPON(rrh[i[0]].node):#has active VPONs
				#if it has, gets the most loaded VPON
				vpon = getMostLoadedVPON(rrh[i[0]], n_state)
				#check if there is capacity on this VPON
				if vpon:#allocate the RRH on this VPON
					updateVponState(rrh[i[0]], vpon)
			#if not, take the VPON returned on the solution
			#check if the VPON returned on the solution has capacity to support the RRH
			elif checkLambdaNode(rrh[i[0]].node,i[2]) and checkLambdaCapacity(i[2]):
				#allocate the VPON to the RRH and its node and update its state
				updateVponState(rrh[i[0]], i[2])
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
			if checkAvailabilityVDU(vdu, rrh[i[0]].node, rrh[i[0]].wavelength) == 1:
				#allocates this VDU on the RRH and did not use the switch
				rrh[i[0]].du = vdu
				updateVDU(vdu, rrh[i[0]].node)
			elif checkAvailabilityVDU(vdu, rrh[i[0]].node, rrh[i[0]].wavelength) == 0:
				#allocates the VDU and activates the ethernet switch
				rrh[i[0]].du = vdu
				updateSwitch(rrh[i[0]].node)
			elif not checkAvailabilityVDU(vdu, rrh[i[0]].node, rrh[i[0]].wavelength):
				#the VDU or the switch has no free capacity, so, get the first fit VDU different from the returned on the solution
				for d in range(len(n_state.du_processing[rrh[i[0]].node])):
					if not checkSwitchUse:
						if rlx.checkCapacityDU(rrh[i[0]].node, d):
							rrh[i[0]].du = d
							updateSwitch(rrh[i[0]].node)
							break
					if rlx.checkCapacityDU(rrh[i[0]].node, d):
						if checkSwitchUse(d, rrh[i[0]].wavelength) and checkSwitchCapacity(rrh[i[0]].node):
							rrh[i[0]].du = d
							updateSwitch(rrh[i[0]].node)
							break
		if rrh[i[0]].du == None:
			rrh[i[0]].blocked = True
			freeNodeResources()

#this method reduces the VPONs and VDUs used in a node
#it will always try to allocate the most loaded VPON in a node and the most loaded VDU
def mostLoadedVponVDU(solution, n_state):
	#general rule for RRHs (var x and u): index [0] is the RRH, index [1] is the node, [2] is the wavelength/DU
	for i in solution.var_x:
		#the node has capacity on its VDUs?
		if i[1] == 0 and rlx.checkNodeCapacity(i[1]):
			#it has, allocate the node to the RRH
			rrh[i[0]].var_x = i#talvez eu tire essa linha depois
			rrh[i[0]].node = i[1]
		else:
			if rlx.checkNodeCapacity(rrh[i[0]].fog):
					rrh[i[0]].node = rrh[i[0]].fog
		#update the node cost, number of allocated RRHs and capacity
		if rrh[i[0]].node != None:
			updateNode(rrh[i[0]])
		#if no node was allocated, blocks the requisition
		else:
			rrh[i[0]].blocked = True
		#now, if a node was found for the RRH, tries to allocate the VPON
		if rrh[i[0]].blocked == False:
			#verifies if the node has an activate VPON
			if rlx.checkNodeVPON(rrh[i[0]].node):#has active VPONs
				#if it has, gets the most loaded VPON
				vpon = getMostLoadedVPON(rrh[i[0]], n_state)
				#check if there is capacity on this VPON
				if vpon:#allocate the RRH on this VPON
					updateVponState(rrh[i[0]], vpon)
			#if not, take the VPON returned on the solution
			#check if the VPON returned on the solution has capacity to support the RRH
			elif checkLambdaNode(rrh[i[0]].node,i[2]) and checkLambdaCapacity(i[2]):
				#allocate the VPON to the RRH and its node and update its state
				updateVponState(rrh[i[0]], i[2])
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
			if checkAvailabilityVDU(most_vdu, rrh[i[0]].node, rrh[i[0]].wavelength) == 1
				rrh[i[0]].du = most_vdu
				updateVDU(most_vdu, rrh[i[0]].node)
			elif checkAvailabilityVDU(most_vdu, rrh[i[0]].node, rrh[i[0]].wavelength) == 0:
				#allocates the VDU and activates the ethernet switch
				rrh[i[0]].du = most_vdu
				updateVDU(most_vdu, rrh[i[0]].node)
				updateSwitch(rrh[i[0]].node)
			elif not checkAvailabilityVDU(most_vdu, rrh[i[0]].node, rrh[i[0]].wavelength):
				#if the most loaded VDU or the switch has no free capacity, tries to get the returned on the solution and then, another one free
				if vdu != most_vdu:
					if checkAvailabilityVDU(vdu, rrh[i[0]].node, rrh[i[0]].wavelength) == 1
						rrh[i[0]].du = vdu
						updateVDU(vdu, rrh[i[0]].node)
					elif checkAvailabilityVDU(vdu, rrh[i[0]].node, rrh[i[0]].wavelength) == 0:
						#allocates the VDU and activates the ethernet switch
						rrh[i[0]].du = vdu
						updateVDU(vdu, rrh[i[0]].node)
						updateSwitch(rrh[i[0]].node)
				if rrh[i[0]].du == None:
				#elif not checkAvailabilityVDU(vdu, rrh[i[0]].node, rrh[i[0]].wavelength):
					#the most loaded VDU or the switch has no free capacity, so, get the first fit VDU different from the returned on the solution
					for d in range(len(n_state.du_processing[rrh[i[0]].node])):
						if not checkSwitchUse:
							if rlx.checkCapacityDU(rrh[i[0]].node, d):
								rrh[i[0]].du = d
								updateVDU(d, rrh[i[0]].node)
								break
						if rlx.checkCapacityDU(rrh[i[0]].node, d):
							if checkSwitchUse(d, rrh[i[0]].wavelength) and checkSwitchCapacity(rrh[i[0]].node):
								rrh[i[0]].du = d
								updateVDU(d, rrh[i[0]].node)
								updateSwitch(rrh[i[0]].node)
								break
		if rrh[i[0]].du == None:
			rrh[i[0]].blocked = True
			freeNodeResources()

#it will always try to allocate the least loaded VPON in a node and the least loaded VDU
def leastLoadedVponVDU(solution, n_state):
	#general rule for RRHs (var x and u): index [0] is the RRH, index [1] is the node, [2] is the wavelength/DU
	for i in solution.var_x:
		#the node has capacity on its VDUs?
		if i[1] == 0 and rlx.checkNodeCapacity(i[1]):
			#it has, allocate the node to the RRH
			rrh[i[0]].var_x = i#talvez eu tire essa linha depois
			rrh[i[0]].node = i[1]
		else:
			if rlx.checkNodeCapacity(rrh[i[0]].fog):
					rrh[i[0]].node = rrh[i[0]].fog
		#update the node cost, number of allocated RRHs and capacity
		if rrh[i[0]].node != None:
			updateNode(rrh[i[0]])
		#if no node was allocated, blocks the requisition
		else:
			rrh[i[0]].blocked = True
		#now, if a node was found for the RRH, tries to allocate the VPON
		if rrh[i[0]].blocked == False:
			#verifies if the node has an activate VPON
			if rlx.checkNodeVPON(rrh[i[0]].node):#has active VPONs
				#if it has, gets the most loaded VPON
				vpon = getLeastLoadedVPON(rrh[i[0]], n_state)
				#check if there is capacity on this VPON
				if vpon:#allocate the RRH on this VPON
					updateVponState(rrh[i[0]], vpon)
			#if not, take the VPON returned on the solution
			#check if the VPON returned on the solution has capacity to support the RRH
			elif checkLambdaNode(rrh[i[0]].node,i[2]) and checkLambdaCapacity(i[2]):
				#allocate the VPON to the RRH and its node and update its state
				updateVponState(rrh[i[0]], i[2])
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
			if checkAvailabilityVDU(least_vdu, rrh[i[0]].node, rrh[i[0]].wavelength) == 1
				rrh[i[0]].du = least_vdu
				updateVDU(least_vdu, rrh[i[0]].node)
			elif checkAvailabilityVDU(least_vdu, rrh[i[0]].node, rrh[i[0]].wavelength) == 0:
				#allocates the VDU and activates the ethernet switch
				rrh[i[0]].du = least_vdu
				updateVDU(least_vdu, rrh[i[0]].node)
				updateSwitch(rrh[i[0]].node)
			elif not checkAvailabilityVDU(least_vdu, rrh[i[0]].node, rrh[i[0]].wavelength):
				#if the most loaded VDU or the switch has no free capacity, tries to get the returned on the solution and then, another one free
				if vdu != least_vdu:
					if checkAvailabilityVDU(vdu, rrh[i[0]].node, rrh[i[0]].wavelength) == 1
						rrh[i[0]].du = vdu
						updateVDU(vdu, rrh[i[0]].node)
					elif checkAvailabilityVDU(vdu, rrh[i[0]].node, rrh[i[0]].wavelength) == 0:
						#allocates the VDU and activates the ethernet switch
						rrh[i[0]].du = vdu
						updateVDU(vdu, rrh[i[0]].node)
						updateSwitch(rrh[i[0]].node)
				if rrh[i[0]].du == None:
				#elif not checkAvailabilityVDU(vdu, rrh[i[0]].node, rrh[i[0]].wavelength):
					#the most loaded VDU or the switch has no free capacity, so, get the first fit VDU different from the returned on the solution
					for d in range(len(n_state.du_processing[rrh[i[0]].node])):
						if not checkSwitchUse:
							if rlx.checkCapacityDU(rrh[i[0]].node, d):
								rrh[i[0]].du = d
								updateVDU(d, rrh[i[0]].node)
								break
						if rlx.checkCapacityDU(rrh[i[0]].node, d):
							if checkSwitchUse(d, rrh[i[0]].wavelength) and checkSwitchCapacity(rrh[i[0]].node):
								rrh[i[0]].du = d
								updateVDU(d, rrh[i[0]].node)
								updateSwitch(rrh[i[0]].node)
								break
		if rrh[i[0]].du == None:
			rrh[i[0]].blocked = True
			freeNodeResources()

#this method reduces the VPONs and VDUs used in a node
#it will always try to allocate the most loaded VPON in a node and the most loaded VDU that matches the VPONs allocated firstly
def mostLoadedEqualVponVDU(solution, n_state):
	pass

#this method allocates the vBBU in the least loaded VPON in a node, then in the one returned on the solution, then, in another one available
def leastLoadedVPON(solution, n_state):
	#iterate over each RRH on the solution
	for i in solution.var_x:
		#the node has capacity on its VDUs?
		if i[1] == 0 and rlx.checkNodeCapacity(i[1]):
			#it has, allocate the node to the RRH
			rrh[i[0]].var_x = i#talvez eu tire essa linha depois
			rrh[i[0]].node = i[1]
		else:
			if rlx.checkNodeCapacity(rrh[i[0]].fog):
					rrh[i[0]].node = rrh[i[0]].fog
		#update the node cost, number of allocated RRHs and capacity
		if rrh[i[0]].node != None:
			updateNode(rrh[i[0]])
		#if no node was allocated, blocks the requisition
		else:
			rrh[i[0]].blocked = True
		#now, if a node was found for the RRH, tries to allocate the VPON
		if rrh[i[0]].blocked == False:
			#verifies if the node has an activate VPON
			if rlx.checkNodeVPON(rrh[i[0]].node):#has active VPONs
				#if it has, gets the most loaded VPON
				vpon = getLeastLoadedVPON(rrh[i[0]], n_state)
				#check if there is capacity on this VPON
				if vpon:#allocate the RRH on this VPON
					updateVponState(rrh[i[0]], vpon)
			#if not, take the VPON returned on the solution
			#check if the VPON returned on the solution has capacity to support the RRH
			elif checkLambdaNode(rrh[i[0]].node,i[2]) and checkLambdaCapacity(i[2]):
				#allocate the VPON to the RRH and its node and update its state
				updateVponState(rrh[i[0]], i[2])
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
			if checkAvailabilityVDU(vdu, rrh[i[0]].node, rrh[i[0]].wavelength) == 1:
				#allocates this VDU on the RRH and did not use the switch
				rrh[i[0]].du = vdu
				updateVDU(vdu, rrh[i[0]].node)
			elif checkAvailabilityVDU(vdu, rrh[i[0]].node, rrh[i[0]].wavelength) == 0:
				#allocates the VDU and activates the ethernet switch
				rrh[i[0]].du = vdu
				updateSwitch(rrh[i[0]].node)
			elif not checkAvailabilityVDU(vdu, rrh[i[0]].node, rrh[i[0]].wavelength):
				#the VDU or the switch has no free capacity, so, get the first fit VDU different from the returned on the solution
				for d in range(len(n_state.du_processing[rrh[i[0]].node])):
					if not checkSwitchUse:
						if rlx.checkCapacityDU(rrh[i[0]].node, d):
							rrh[i[0]].du = d
							updateSwitch(rrh[i[0]].node)
							break
					if rlx.checkCapacityDU(rrh[i[0]].node, d):
						if checkSwitchUse(d, rrh[i[0]].wavelength) and checkSwitchCapacity(rrh[i[0]].node):
							rrh[i[0]].du = d
							updateSwitch(rrh[i[0]].node)
							break
		if rrh[i[0]].du == None:
			rrh[i[0]].blocked = True
			freeNodeResources()

#this naive most loaded VPON heuristic allocates the most loaded VPON and on the returned VDU only and no other else
def naiveMostLoadedVPON(solution, n_state):
	#iterate over each RRH on the solution
	#general rule for RRHs (var x and u): index [0] is the RRH, index [1] is the node, [2] is the wavelength/DU
	for i in solution.var_x:
		#the node has capacity on its VDUs?
		if i[1] == 0 and rlx.checkNodeCapacity(i[1]):
			#it has, allocate the node to the RRH
			rrh[i[0]].var_x = i#talvez eu tire essa linha depois
			rrh[i[0]].node = i[1]
		else:
			if rlx.checkNodeCapacity(rrh[i[0]].fog):
					rrh[i[0]].node = rrh[i[0]].fog
		#update the node cost, number of allocated RRHs and capacity
		if rrh[i[0]].node != None:
			updateNode(rrh[i[0]])
		#if no node was allocated, blocks the requisition
		else:
			rrh[i[0]].blocked = True
		#now, if a node was found for the RRH, tries to allocate the VPON
		if rrh[i[0]].blocked == False:
			#verifies if the node has an activate VPON
			if rlx.checkNodeVPON(rrh[i[0]].node):#has active VPONs
				#if it has, gets the most loaded VPON
				vpon = getMostLoadedVPON(rrh[i[0]], n_state)
				#check if there is capacity on this VPON
				if vpon:#allocate the RRH on this VPON
					updateVponState(rrh[i[0]], vpon)
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
			if checkAvailabilityVDU(vdu, rrh[i[0]].node, rrh[i[0]].wavelength) == 1:
				#allocates this VDU on the RRH and did not use the switch
				rrh[i[0]].du = vdu
				updateVDU(vdu, rrh[i[0]].node)
			elif checkAvailabilityVDU(vdu, rrh[i[0]].node, rrh[i[0]].wavelength) == 0:
				#allocates the VDU and activates the ethernet switch
				rrh[i[0]].du = vdu
				updateVDU(vdu, rrh[i[0]].node)
				updateSwitch(rrh[i[0]].node)
		if rrh[i[0]].du == None:
			rrh[i[0]].blocked = True
			freeNodeResources()

#this naive least loaded VPON heuristic allocates the least loaded VPON only and the VDU of the solution and no other else
def naiveLeastLoadedVPON(solution, n_state):
	#iterate over each RRH on the solution
	#general rule for RRHs (var x and u): index [0] is the RRH, index [1] is the node, [2] is the wavelength/DU
	for i in solution.var_x:
		#the node has capacity on its VDUs?
		if i[1] == 0 and rlx.checkNodeCapacity(i[1]):
			#it has, allocate the node to the RRH
			rrh[i[0]].var_x = i#talvez eu tire essa linha depois
			rrh[i[0]].node = i[1]
		else:
			if rlx.checkNodeCapacity(rrh[i[0]].fog):
					rrh[i[0]].node = rrh[i[0]].fog
		#update the node cost, number of allocated RRHs and capacity
		if rrh[i[0]].node != None:
			updateNode(rrh[i[0]])
		#if no node was allocated, blocks the requisition
		else:
			rrh[i[0]].blocked = True
		#now, if a node was found for the RRH, tries to allocate the VPON
		if rrh[i[0]].blocked == False:
			#verifies if the node has an activate VPON
			if rlx.checkNodeVPON(rrh[i[0]].node):#has active VPONs
				#if it has, gets the most loaded VPON
				vpon = getLeastLoadedVPON(rrh[i[0]], n_state)
				#check if there is capacity on this VPON
				if vpon:#allocate the RRH on this VPON
					updateVponState(rrh[i[0]], vpon)
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
			if checkAvailabilityVDU(vdu, rrh[i[0]].node, rrh[i[0]].wavelength) == 1:
				#allocates this VDU on the RRH and did not use the switch
				rrh[i[0]].du = vdu
				updateVDU(vdu, rrh[i[0]].node)
			elif checkAvailabilityVDU(vdu, rrh[i[0]].node, rrh[i[0]].wavelength) == 0:
				#allocates the VDU and activates the ethernet switch
				rrh[i[0]].du = vdu
				updateVDU(vdu, rrh[i[0]].node)
				updateSwitch(rrh[i[0]].node)
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
def checkSwitchUse(vdu, vpon):
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
	if not n_state.checkCapacityDU(node, vdu):
		return False
	else:
		#verify if it is necessary to use the switch
		if not checkSwitch(vdu, vpon):
			return 1
		else:
			#check switch capacity
			if not checkSwitchCapacity(node):
				return False
			else:
				return 0

#update switch
def updateSwitch(node, n_state):
	n_state.switchBandwidth -= n_state.RRHband
	if n_state.switch_state[node] == 0:
		n_state.switch_state[node] = 1
		n_state.switch_cost[node] = 0.0

#this class represents a "virtual" network state, used to keep a solution returned from the relaxation algorithms
#this class will be used to be put on a list with n results drawn from n executions of the relaxations, when the instance with the best result will be used to
#update the "real" network state
class NetworkState(object):
	#constructor 1
	def __init__(self, aId, rrhs_on_nodes = [0,0,0],lambda_node = [[1,1,1],[1,1,1],[1,1,1],[1,1,1],],du_processing = [[8.0, 8.0, 8.0, 8.0],[4.0, 4.0, 4.0, 4.0 ],[4.0, 4.0, 4.0, 4.0 ],],
		dus_total_capacity = [[8.0, 8.0, 8.0, 8.0],[4.0, 4.0, 4.0, 4.0 ],[4.0, 4.0, 4.0, 4.0 ],], du_state = [[0, 0, 0, 0],[0, 0, 0, 0],[0, 0, 0, 0],], nodeState = [0,0,0], 
		nodeCost = [0.0,300.0,300.0,], du_cost = [[100.0, 100.0, 100.0, 100.0],[50.0, 50.0, 50.0, 50.0],[50.0, 50.0, 50.0, 50.0],], lc_cost = [20.0,20.0,20.0,20.0,], 
		switch_cost = [15.0, 15.0, 15.0], switchBandwidth = [10000.0,10000.0,10000.0], wavelength_capacity = [10000.0, 10000.0, 10000.0, 10000.0], RRHband = 614.4, 
		cloud_du_capacity = 9.0, fog_du_capacity = 1.0, lambda_state = [0,0,0,0], switch_state = [0,0,0], delay = None, power = None, lambda_wastage = None, 
		execution_time = None, migration_probability = None , total_migrations = None):
		#Id of this network state
		self.aId = aId
		#to keep the amount of RRHs being processed on each node
		self.rrhs_on_nodes = rrhs_on_nodes
		#to assure that each lamba allocatedto a node can only be used on that node on the incremental execution of the ILP
		self.lambda_node = lambda_node
		#capacity of each VDU
		self.du_processing = du_processing
		#used to calculate the processing usage of the node
		self.dus_total_capacity = dus_total_capacity
		#state of each VDU
		self.du_state = du_state
		#state of each node
		self.nodeState = nodeState
		#power cost of each processing node
		self.nodeCost = nodeCost
		#power cost of each VDu
		self.du_cost = du_cost
		#power cost of each Line Card
		self.lc_cost = lc_cost
		#power cost of the backplane switch
		self.switch_cost = switch_cost
		#bandwidth capacity of the backplane switch
		self.switchBandwidth =  switchBandwidth
		#bandwidth capacity of each wavelength
		self.wavelength_capacity = wavelength_capacity
		#basic CPRI line used
		self.RRHband = RRHband
		#capacity of each VDU on the cloud
		self.cloud_du_capacity = cloud_du_capacity
		#capacity of each VDU in a fog node
		self.fog_du_capacity = fog_du_capacity
		#state of each wavelength/VPON
		self.lambda_state = lambda_state
		#state of the backplane switch in each processing node
		self.switch_state = switch_state
		#metrics obtained on the solution
		self.delay = delay
		self.power = power
		self.lambda_wastage = lambda_wastage
		self.execution_time = execution_time
		self.migration_probability = migration_probability
		self.total_migrations = total_migrations
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
	

#this class encapsulates several network state to get the one with the best metric
class NetworkStateCollection(object):
	#amount is the number of times that the relaxation will be executed, thus, generation an "amoun" number of solutions
	def __init__(self, amount):
		#list of network state objects
		self.network_states = []

	#create the network state objects
	def initStates(self, amount, rrhs_on_nodes, lambda_node, du_processing, dus_total_capacity, du_state, nodeState,
		nodeCost, du_cost, lc_cost, switch_cost, switchBandwidth, wavelength_capacity, RRHband, cloud_du_capacity, 
		fog_du_capacity, lambda_state, switch_state, delay, power, lambda_wastage, execution_time, migration_probability, total_migrations):
		#create a network state object for each relaxation execution
		for i in range(amount):
			ns = NetworkState(i, rrhs_on_nodes, lambda_node, du_processing, dus_total_capacity, du_state, nodeState,
		nodeCost, du_cost, lc_cost, switch_cost, switchBandwidth, wavelength_capacity, RRHband, cloud_du_capacity, 
		fog_du_capacity, lambda_state, switch_state, delay, power, lambda_wastage, execution_time, migration_probability, total_migrations)
			#put the object on the list
			self.network_states.append(ns)

	#get the best solution for a given metric
	def getBestSolution(self, metric, method):
		sol = method(self.network_states, key = operator.attrgetter("metric"))
		return sol.aId
