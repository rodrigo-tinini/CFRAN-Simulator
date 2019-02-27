from docplex.mp.model import Model
import simpy
import functools
import random as np
import time
from enum import Enum
from scipy.stats import norm
import matplotlib.pyplot as plt
import relaxation_test as rlx

#this method returns the u variable given the RRH index
def getVarU(aIndex, solution):
	for i in solution.var_u:
		if i[0] == aIndex:
			return i


#allocate a VPON to a RRH and its node and update VPON state
def updateVponState(rrh, vpon):
	rrh.wavelength = vpon
	rlx.wavelength_capacity[rrh.wavelength] -= rlx.RRHband
	if rlx.lambda_state[rrh.wavelength] == 0:
		rlx.lambda_state[rrh.wavelength] = 1
		rlx.lc_cost[rrh.wavelength] = 0
	rlx.nodes_vpons_capacity[rrh.node][vpon] = rlx.wavelength_capacity[vpon]
	blockLambda(rrh.wavelength, rrh.node)

#get any non-allocated VPON
def getFreeVPON(rrh, vpon):
	for j in range(len(rlx.lambda_state)):
		if rlx.lambda_state[j] == 0: #this lambda is available
			updateVponState(rrh, vpon)
			blockLambda(rrh.wavelength, rrh.node)
			return True
	return False

#get the first available VPON in a node
def getFirstFreeVPON(rrh):
	for j in range(len(rlx.lambda_node)):
		#another lambda is allocated on the node
		if rlx.lambda_node[j][rrh.node] == 1 and rlx.lambda_node[j][rrh.node] != i[2]:
			#check if it has capacity
			if checkLambdaCapacity(j):
				return j
				break
	return False

#free node resources
def freeNodeResources(rrh, node):
	rrh.node = None
	rlx.rrhs_on_nodes[node] -= 1
	#turn the node on if it is not
	if rlx.rrhs_on_nodes[node] == 0:
		#not activated, updates costs
		if node == 0:
			rlx.nodeCost[node] = 0.0
		else:
			rlx.nodeCost[node] = 300.0
		rlx.nodeState[node] = 0

#update the node state after an allocation
def updateNode(rrh):
	if rrh.node != None:
		rlx.rrhs_on_nodes[rrh.node] += 1
		#turn the node on if it is not
		if rlx.nodeState[rrh.node] == 0:
			#not activated, updates costs
			rlx.nodeCost[rrh.node] = 0
			rlx.nodeState[rrh.node] = 1

#returns the capacity of a VDU in a given node
def getVduCapacity(node, vdu):
	return rlx.du_processing[node][vdu]

#check VDU capacity
def checkVduCapacity(vdu, node):
	if rlx.du_processing[node][vdu] > 0:
		return True
	else:
		return False

#update VDU state
def updateVDU(vdu, node):
	pass


#This method tries to use the first fit VPON in a node, and then, the one with most probability use returned on the solution and then, the first fit that was not allocated to any node
#regarding the node, it tries the one with the most probability, then, the other available node (it will be always cloud or fog)
#regarding the VDU, it consider the one with the most probability returned on the solution, then take the first fit available VDU in the node (it does not aim to reduce swtich delay)
def FirstFitRelaxMinVPON(rrh, solution):
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
				#if it has, gets the first free VPON - MODIFY THIS TO TAKE THE VPON MOST LOADED
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
			elif not checkAvailabilityVDU(vdu, rrh[i[0]].node, rrh[i[0]].wavelength):
				#the VDU or the switch has no free capacity, so, get the first fit VDU different from the returned on the solution
				for d in range(len(rlx.du_processing[rrh[i[0]].node])):
					if not checkSwitchUse:
						if rlx.checkCapacityDU(rrh[i[0]].node, d):
							rrh[i[0]].du = d
							updateSwitch(rrh[i[0]].node)
					if rlx.checkCapacityDU(rrh[i[0]].node, d):
						if checkSwitchUse(d, rrh[i[0]].wavelength) and checkSwitchCapacity(rrh[i[0]].node):
							rrh[i[0]].du = d
							updateSwitch(rrh[i[0]].node)


#This method tries to use the first fit VPON in a node, and then, the one with most probability use returned on the solution and then, the first fit that was not allocated to any node
#regarding the node, it tries the one with the most probability, then, the other available node (it will be always cloud or fog)
#regarding the VDU, it consider the one with the most probability returned on the solution only
def NaiveVDUFirstFitRelaxMinVPON(rrh, solution):
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
				#if it has, gets the first free VPON - MODIFY THIS TO TAKE THE VPON MOST LOADED
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
			if rrh[i[0]].du == None:
				rrh[i[0]].blocked = True

#this method only consider the probabilities of both nodes, VPON and VDU for the RRHs
#if any of those has not free capacity, it will not seek for another resource and will block the requisition
def naiveRelaxUpdate(solution):
	pass

#this method reduces the VPONs and VDUs used in a node
#it will always try to allocate the most loaded VPON in a node and the most loaded VDU
def mostLoadedVponVDU(solution):
	pass

#this method reduces the VPONs and VDUs used in a node
#it will always try to allocate the most loaded VPON in a node and the most loaded VDU that matches the VPONs allocated firstly
def mostLoadedEqualVponVDU(solution):
	pass

#update VDU capacity, state and cost
def updateVDU(vdu, node):
	rlx.du_processing[node][vdu] -= 1
	if rlx.du_state[node][vdu] == 0:
		#du was deactivated - activates it
		rlx.du_state[node][vdu] = 1
		rlx.du_cost[node][vdu] = 0.0

#check if a VDU will require the ethernet switch activation
def checkSwitchUse(vdu, vpon):
	if vdu == vpon:
		return False
	else:
		return True

#check switch capacity
def checkSwitchCapacity(node):
	if rlx.switchBandwidth[node] >= rlx.RRHband:
		return True
	else:
		return False

#check if a VDU can be used by checking its capacity and the capacity of the ethernet switch, if it will be activated
#if it is not necessary to use the switch (VDU and VPONs are in the same LC), return 1
#if VDU and VPONs are in different LCs and both the VDU and the Switch has capacity, return 0
#if the VDU or the siwtch, in any case has not free capacity, return False
def checkAvailabilityVDU(vdu, node, vpon):
	#first, check if the VDU has free capacity
	if not rlx.checkCapacityDU(node, vdu):
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
def updateSwitch(node):
	rlx.switchBandwidth -= rlx.RRHband
	if switch_state[self.rrh[i[0]].node] == 0:
		switch_state[self.rrh[i[0]].node] = 1
		switch_cost[self.rrh[i[0]].node] = 0.0