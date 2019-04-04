from docplex.mp.model import Model
import simpy
import functools
import random as np
import time
from enum import Enum
from scipy.stats import norm
import matplotlib.pyplot as plt
import relaxedMainModule as rl
#Main relaxation module
#This ILP does the allocation of batches of RRHs to the processing nodes.
#It considers that each RRH is connected to the cloud and to only one fog node.

#just an id for identification purposes
aId = "Main network state"
#to keep record of blocked RRHs in the relaxation methods
relax_blocked = 0

#some static methods
#check if a DU in some node has free capacity
def checkCapacityDU(node, du):
	if du_processing[node][du] > 0:
		return True
	else:
		return False

#get a DU's capacity
def getCapacityDU(node, du):
	return du_processing[node][du]

#check if a node has free processing capacity, considering all of its DUs
def checkNodeCapacity(node):
	capacity = 0.0
	capacity = sum(du_processing[node])
	if capacity > 0:
		return True
	else:
		return False

#get node free processing capacity
def getNodeCapacity(node):
	capacity = 0.0
	capacity = sum(du_processing[node])
	return capacity

#check if a lambda has capacity for a request
def checkLambdaCapacity(wavelength):
	if wavelength_capacity[wavelength] >= 614.4:
		return True
	else:
		return False

#check if a lambda has capacity for a request
def checkLambdaCapacityRRH(wavelength, bandwdith):
	if wavelength_capacity[wavelength] >= bandwdith:
		return True
	else:
		return False

#get bandwidth capacity of a lambda
def getLambdaCapacity(wavelength):
	return wavelength_capacity[wavelength]

#block an already allocated lambda in other nodes
def blockLambda(wavelength, node):
	ln = lambda_node[wavelength]
	for i in range(len(ln)):
		if i != node:
			ln[i] = 0


#check if a lambda is free to be allocated on a given node
def checkLambdaNode(node, wavelength):
	if lambda_node[wavelength][node] == 1:
		return True
	else:
		return False

#check if node has at least one activated VPON
def checkNodeVPON(node):
	if nodes_lambda[node]:
		return True
	else:
		return False

#get the first available VPON in a node
def getFirstFreeVPON(node):
	if checkNodeVPON(node):
		for i in nodes_lambda[node]:
			if getLambdaCapacity(i) >= RRHband:
				return i
	else:#no VPON here
		return None

#get the lambda with most allocated RRHs
def getMaxLoadVPON(node):
	vp = max(nodes_vpons_capacity[node], key=nodes_vpons_capacity[node].get)

#get the lambda with least allocated RRHs
def getMinLoadVPON(node):
	return min(nodes_vpons_capacity[node], key=nodes_vpons_capacity[node].get)

#update the capacity of the vpons allocated in each node:
def updateNodeVPONsCapacity():
	for i in nodes_vpons_capacity:
		for j in nodes_vpons_capacity[i]:
			nodes_vpons_capacity[i][j] = wavelength_capacity[j]

#create the ilp class
class ILP(object):
	def __init__(self, rrh, rrhs, nodes, lambdas, relaxed):
		self.rrh = rrh
		self.fog = []
		for i in rrh:
			self.fog.append(i.rrhs_matrix)
		self.rrhs = rrhs
		self.nodes = nodes
		self.lambdas = lambdas
		self.relaxed = relaxed
		#print("THE FOG MATIX IS {}".format(self.fog))
		#self.switchBandwidth = switchBandwidth
		#self.RRHband = RRHband
		#self.wavelength_capacity = wavelength_capacity
		#self.lc_cost = lc_cost
		#self.B = B
		#self.du_processing = du_processing
		#self.nodeCost = nodeCost
		#self.du_cost = du_cost
		#self.switch_cost = switch_cost

	#run the formulation
	def run(self):
		#print("Run Being Called")
		self.setModel()
		self.setConstraints()
		self.setObjective()
		sol = self.solveILP()
		return sol

	#creates the model and the decision variables
	def setModel(self):
		self.mdl = Model("RRHs Scheduling")
		#indexes for the decision variables x[i,j,w]
		self.idx_ijw = [(i,j,w) for i in self.rrhs for j in self.nodes for w in self.lambdas]
		self.idx_ij = [(i,j) for i in self.rrhs for j in self.nodes]
		self.idx_wj = [(w, j) for w in self.lambdas for j in self.nodes]
		self.idx_j = [(j) for j in self.nodes]
		 
		 #relax the variables if the model is relaxed
		if self.relaxed == True:
			#Decision variables
			#x[rrhs][lambdas][nodes];
			self.x = self.mdl.continuous_var_dict(self.idx_ijw,  name = 'RRH/Node/Lambda', key_format = "")
			#u[rrhs][lambdas][nodes];
			self.u = self.mdl.continuous_var_dict(self.idx_ijw, name = 'RRH/Node/DU')
			#y[rrhs][nodes];
			self.y = self.mdl.continuous_var_dict(self.idx_ij, name = 'RRH/Node')
			#k[rrhs][nodes];
			self.k = self.mdl.continuous_var_dict(self.idx_ij, name = 'Redirection of RRH in Node')
			#rd[lambdas][nodes];
			self.rd = self.mdl.continuous_var_dict(self.idx_wj, name = 'DU in Node used for redirection')
			#s[lambdas][nodes];
			self.s = self.mdl.continuous_var_dict(self.idx_wj, name = 'DU activated in node')
			#e[nodes];
			self.e = self.mdl.continuous_var_dict(self.idx_j, name = "Switch/Node")
			#g[rrhs][lambdas][nodes];
			self.g = self.mdl.continuous_var_dict(self.idx_ijw, name = 'Redirection of RRH in Node in DU')
			#xn[nodes];
			self.xn = self.mdl.continuous_var_dict(self.idx_j, name = 'Node activated')
			#z[lambdas][nodes];
			self.z = self.mdl.continuous_var_dict(self.idx_wj, name = 'Lambda in Node')
		else:
			self.x = self.mdl.binary_var_dict(self.idx_ijw, name = 'RRH/Node/Lambda', key_format = "")
			#u[rrhs][lambdas][nodes];
			self.u = self.mdl.binary_var_dict(self.idx_ijw, name = 'RRH/Node/DU')
			#y[rrhs][nodes];
			self.y = self.mdl.binary_var_dict(self.idx_ij, name = 'RRH/Node')
			#k[rrhs][nodes];
			self.k = self.mdl.binary_var_dict(self.idx_ij, name = 'Redirection of RRH in Node')
			#rd[lambdas][nodes];
			self.rd = self.mdl.binary_var_dict(self.idx_wj, name = 'DU in Node used for redirection')
			#s[lambdas][nodes];
			self.s = self.mdl.binary_var_dict(self.idx_wj, name = 'DU activated in node')
			#e[nodes];
			self.e = self.mdl.binary_var_dict(self.idx_j, name = "Switch/Node")
			#g[rrhs][lambdas][nodes];
			self.g = self.mdl.binary_var_dict(self.idx_ijw, name = 'Redirection of RRH in Node in DU')
			#xn[nodes];
			self.xn = self.mdl.binary_var_dict(self.idx_j, name = 'Node activated')
			#z[lambdas][nodes];
			self.z = self.mdl.binary_var_dict(self.idx_wj, name = 'Lambda in Node')


	#create constraints
	def setConstraints(self):
		self.mdl.add_constraints(self.mdl.sum(self.x[i,j,w] for j in self.nodes for w in self.lambdas) == 1 for i in self.rrhs)#1
		self.mdl.add_constraints(self.mdl.sum(self.x[i,j,w]) >= 0.01 for i in self.rrhs for j in self.nodes for w in self.lambdas)#1.5
		self.mdl.add_constraints(self.mdl.sum(self.u[i,j,w] for j in self.nodes for w in self.lambdas) == 1 for i in self.rrhs)#2
		self.mdl.add_constraints(self.mdl.sum(self.u[i,j,w]) >= 0.01 for i in self.rrhs for j in self.nodes for w in self.lambdas)#2.5
		
		#self.mdl.add_constraints(self.mdl.sum(self.x[i,j,w] * RRHband for i in self.rrhs for j in self.nodes) <= wavelength_capacity[w] for w in self.lambdas) #TIREI PARA PODER RODAR A RELAXAÇÃO - ESSA RESTRIÇÃO TEM QUE SER TRATADA PELO ALGORITMO
		#self.mdl.add_constraints(self.mdl.sum(self.u[i,j,w] for i in self.rrhs) <= du_processing[j][w] for j in self.nodes for w in self.lambdas) #TIREI PARA PODER RODAR A RELAXAÇÃO - ESSA RESTRIÇÃO TEM QUE SER TRATADA PELO ALGORITMO
		
		#self.mdl.add_constraints(self.mdl.sum(self.k[i,j] * RRHband for i in self.rrhs) <= switchBandwidth[j] for j in self.nodes) #TIREI PARA PODER RODAR A RELAXAÇÃO - ESSA RESTRIÇÃO TEM QUE SER TRATADA PELO ALGORITMO
		self.mdl.add_constraints(B*self.xn[j] >= self.mdl.sum(self.x[i,j,w] for i in self.rrhs for w in self.lambdas) for j in self.nodes)
		self.mdl.add_constraints(self.xn[j] <= self.mdl.sum(self.x[i,j,w] for i in self.rrhs for w in self.lambdas) for j in self.nodes)
		
		self.mdl.add_constraints(B*self.z[w,j] >= self.mdl.sum(self.x[i,j,w] for i in self.rrhs) for w in self.lambdas for j in self.nodes)
		self.mdl.add_constraints(self.z[w,j] <= self.mdl.sum(self.x[i,j,w] for i in self.rrhs) for w in self.lambdas for j in self.nodes)
		
		self.mdl.add_constraints(B*self.s[w,j] >= self.mdl.sum(self.u[i,j,w] for i in self.rrhs) for w in self.lambdas for j in self.nodes)
		self.mdl.add_constraints(self.s[w,j] <= self.mdl.sum(self.u[i,j,w] for i in self.rrhs) for w in self.lambdas for j in self.nodes)
		
		#self.mdl.add_constraints(self.g[i,j,w] <= self.x[i,j,w] + self.u[i,j,w] for i in self.rrhs for j in self.nodes for w in self.lambdas)
		#self.mdl.add_constraints(self.g[i,j,w] >= self.x[i,j,w] - self.u[i,j,w] for i in self.rrhs for j in self.nodes for w in self.lambdas)
		#self.mdl.add_constraints(self.g[i,j,w] >= self.u[i,j,w] - self.x[i,j,w] for i in self.rrhs for j in self.nodes for w in self.lambdas)
		#self.mdl.add_constraints(self.g[i,j,w] <= 2 - self.x[i,j,w] - self.u[i,j,w] for i in self.rrhs for j in self.nodes for w in self.lambdas)
		
		self.mdl.add_constraints(B*self.k[i,j] >= self.mdl.sum(self.g[i,j,w] for w in self.lambdas) for i in self.rrhs for j in self.nodes)
		self.mdl.add_constraints(self.k[i,j] <= self.mdl.sum(self.g[i,j,w] for w in self.lambdas) for i in self.rrhs for j in self.nodes)
		
		self.mdl.add_constraints(B*self.rd[w,j] >= self.mdl.sum(self.g[i,j,w] for i in self.rrhs) for w in self.lambdas for j in self.nodes)
		self.mdl.add_constraints(self.rd[w,j] <= self.mdl.sum(self.g[i,j,w] for i in self.rrhs) for w in self.lambdas for j in self.nodes)
		
		self.mdl.add_constraints(B*self.e[j] >= self.mdl.sum(self.k[i,j] for i in self.rrhs) for j in self.nodes)
		self.mdl.add_constraints(self.e[j] <= self.mdl.sum(self.k[i,j] for i in self.rrhs)  for j in self.nodes)
		
		self.mdl.add_constraints(self.mdl.sum(self.z[w,j] for j in self.nodes) <= 1 for w in self.lambdas)
		#self.mdl.add_constraints(self.mdl.sum(self.z[w,j] for j in self.nodes) == 1 for w in self.lambdas)
		self.mdl.add_constraints(self.mdl.sum(self.y[i,j] for j in self.nodes) == 1 for i in self.rrhs)
		
		self.mdl.add_constraints(B*self.y[i,j] >= self.mdl.sum(self.x[i,j,w] for w in self.lambdas) for i in self.rrhs for j in self.nodes)
		self.mdl.add_constraints(self.y[i,j] <= self.mdl.sum(self.x[i,j,w] for w in self.lambdas) for i in self.rrhs  for j in self.nodes)
		
		self.mdl.add_constraints(B*self.y[i,j] >= self.mdl.sum(self.u[i,j,w] for w in self.lambdas) for i in self.rrhs for j in self.nodes)		
		self.mdl.add_constraints(self.y[i,j] <= self.mdl.sum(self.u[i,j,w] for w in self.lambdas) for i in self.rrhs  for j in self.nodes)
		self.mdl.add_constraints(self.mdl.sum(self.u[i,j,w] for i in self.rrhs) >= 0 for j in self.nodes for w in self.lambdas)

		#self.mdl.add_constraints(self.y[i,j] >= self.x[i,j,w] + self.fog[i][j] - 1 for i in self.rrhs for j in self.nodes for w in self.lambdas)
		#self.mdl.add_constraints(self.y[i,j] <= self.x[i,j,w] for i in self.rrhs for j in self.nodes for w in self.lambdas)
		#this constraints guarantees that each rrh can be allocated to either the cloud or a specific fog node
		#self.mdl.add_constraints(self.y[i,j] <= self.fog[i][j] for i in self.rrhs for j in self.nodes) #TIREI PARA PODER RODAR A RELAXAÇÃO - ESSA RESTRIÇÃO TEM QUE SER TRATADA PELO ALGORITMO
		#self.mdl.add_constraints(self.z[w,j] <= lambda_node[w][j] for w in self.lambdas for j in self.nodes) #TIREI PARA PODER RODAR A RELAXAÇÃO - ESSA RESTRIÇÃO TEM QUE SER TRATADA PELO ALGORITMO

	#set the objective function
	def setObjective(self):
		#self.mdl.minimize(self.mdl.sum(self.xn[j] * nodeCost[j] for j in self.nodes) + 
		#self.mdl.sum(self.z[w,j] * lc_cost[w] for w in self.lambdas for j in self.nodes))

		self.mdl.minimize(self.mdl.sum(self.xn[j] * nodeCost[j] for j in self.nodes) +
		self.mdl.sum(self.z[w,j] * lc_cost[w] for w in self.lambdas for j in self.nodes) + 
		(self.mdl.sum(self.k[i,j] for i in self.rrhs for j in self.nodes) + 
		self.mdl.sum(self.g[i,j,w] * switch_cost[j] for i in self.rrhs for w in self.lambdas for j in self.nodes)) + 
		(self.mdl.sum(self.s[w,j] * du_cost[j][w] for w in self.lambdas for j in self.nodes) + 
		self.mdl.sum(self.rd[w,j] * du_cost[j][w] for w in self.lambdas for j in self.nodes)) + 
		self.mdl.sum(self.e[j] * switch_cost[j] for j in self.nodes))

		#self.mdl.minimize(self.mdl.sum(self.xn[j] * nodeCost[j] for j in self.nodes) +
		#self.mdl.sum(self.x[i,j,w] * lc_cost[w] for i in self.rrhs for w in self.lambdas for j in self.nodes) +
		#self.mdl.sum(self.x[i,j,w] * nodeCost[j] for i in self.rrhs for w in self.lambdas for j in self.nodes) + 
		#self.mdl.sum(self.z[w,j] * lc_cost[w] for w in self.lambdas for j in self.nodes) + 
		#(self.mdl.sum(self.k[i,j] for i in self.rrhs for j in self.nodes) + 
		#self.mdl.sum(self.g[i,j,w] * switch_cost[j] for i in self.rrhs for w in self.lambdas for j in self.nodes)) + 
		#(self.mdl.sum(self.s[w,j] * du_cost[j][w] for w in self.lambdas for j in self.nodes) + 
		#self.mdl.sum(self.rd[w,j] * du_cost[j][w] for w in self.lambdas for j in self.nodes)) + 
		#self.mdl.sum(self.e[j] * switch_cost[j] for j in self.nodes))

	#solves the model
	def solveILP(self):
		#print("SOLVING")
		self.sol = self.mdl.solve()
		return self.sol

	#print variables values
	def print_var_values(self):
		if self.relaxed == True:
			for i in self.x:
				if self.x[i].solution_value > 0:
					print("{} is {}".format(self.x[i], self.x[i].solution_value))
			for i in self.u:
				if self.u[i].solution_value > 0:
					print("{} is {}".format(self.u[i], self.u[i].solution_value))

			for i in self.k:
				if self.k[i].solution_value > 0:
					print("{} is {}".format(self.k[i], self.k[i].solution_value))

			for i in self.rd:
				if self.rd[i].solution_value > 0:
					print("{} is {}".format(self.rd[i], self.rd[i].solution_value))

			for i in self.s:
				if self.s[i].solution_value > 0:
					print("{} is {}".format(self.s[i], self.s[i].solution_value))

			for i in self.e:
				if self.e[i].solution_value > 0:
					print("{} is {}".format(self.e[i], self.e[i].solution_value))

			for i in self.y:
				if self.y[i].solution_value > 0:
					print("{} is {}".format(self.y[i], self.y[i].solution_value))

			for i in self.g:
				if self.g[i].solution_value > 0:
					print("{} is {}".format(self.g[i], self.g[i].solution_value))

			for i in self.xn:
				if self.xn[i].solution_value > 0:
					print("{} is {}".format(self.xn[i], self.xn[i].solution_value))

			for i in self.z:
				if self.z[i].solution_value > 0:
					print("{} is {}".format(self.z[i], self.z[i].solution_value))
		else:
			for i in self.x:
				if self.x[i].solution_value >= 1:
					print("{} is {}".format(self.x[i], self.x[i].solution_value))
			for i in self.u:
				if self.u[i].solution_value >= 1:
					print("{} is {}".format(self.u[i], self.u[i].solution_value))

			for i in self.k:
				if self.k[i].solution_value >= 1:
					print("{} is {}".format(self.k[i], self.k[i].solution_value))

			for i in self.rd:
				if self.rd[i].solution_value >= 1:
					print("{} is {}".format(self.rd[i], self.rd[i].solution_value))

			for i in self.s:
				if self.s[i].solution_value >= 1:
					print("{} is {}".format(self.s[i], self.s[i].solution_value))

			for i in self.e:
				if self.e[i].solution_value >= 1:
					print("{} is {}".format(self.e[i], self.e[i].solution_value))

			for i in self.y:
				if self.y[i].solution_value >= 1:
					print("{} is {}".format(self.y[i], self.y[i].solution_value))

			for i in self.g:
				if self.g[i].solution_value >= 1:
					print("{} is {}".format(self.g[i], self.g[i].solution_value))

			for i in self.xn:
				if self.xn[i].solution_value >= 1:
					print("{} is {}".format(self.xn[i], self.xn[i].solution_value))

			for i in self.z:
				if self.z[i].solution_value >= 1:
					print("{} is {}".format(self.z[i], self.z[i].solution_value))

	#return solution variables method for the relaxation case
	def relaxReturnVariables(self, dec):
		self.var_x = []
		self.var_u = []
		self.var_k = []
		self.var_rd = []
		self.var_s = []
		self.var_e = []
		self.var_y = []
		self.var_g = []
		self.var_xn = []
		self.var_z = []
		#if self.relaxed == True:
		for i in dec.x:
			if dec.x[i].solution_value > 0:
				self.var_x.append(i)

		for i in dec.u:
			if dec.u[i].solution_value > 0:
				self.var_u.append(i)

		for i in dec.k:
			if dec.k[i].solution_value > 0:
				self.var_k.append(i)

		for i in dec.rd:
			if dec.rd[i].solution_value > 0:
				self.var_rd.append(i)

		for i in dec.s:
			if dec.s[i].solution_value > 0:
				self.var_s.append(i)

		for i in dec.e:
			if dec.e[i].solution_value > 0:
				self.var_e.append(i)

		for i in dec.y:
			if dec.y[i].solution_value > 0:
				self.var_y.append(i)

		for i in dec.g:
			if dec.g[i].solution_value > 0:
				self.var_g.append(i)

		for i in dec.xn:
			if dec.xn[i].solution_value > 0:
				self.var_xn.append(i)

		for i in dec.z:
			if dec.z[i].solution_value > 0:
				self.var_z.append(i)

		solution = DecisionVariables(self.var_x, self.var_u, self.var_k, self.var_rd, 
			self.var_s, self.var_e, self.var_y, self.var_g, self.var_xn, self.var_z)
		return solution


	#return the decision variables - using this for the relaxation metho - as relaxation never return a variable with 0, this class takes the values as they were returned
	def return_decision_variables(self):
		self.var_x = self.x
		self.var_u = self.u
		self.var_k = self.k
		self.var_rd = self.rd
		self.var_s = self.s
		self.var_e = self.e
		self.var_y = self.y
		self.var_g = self.g
		self.var_xn = self.xn
		self.var_z = self.z

		dec_variables = DecisionVariables(self.var_x, self.var_u, self.var_k, self.var_rd, self.var_s, 
			self.var_e, self.var_y, self.var_g, self.var_xn, self.var_z)
		return dec_variables

	#return the variables values
	def return_solution_values(self):
		self.var_x = []
		self.var_u = []
		self.var_k = []
		self.var_rd = []
		self.var_s = []
		self.var_e = []
		self.var_y = []
		self.var_g = []
		self.var_xn = []
		self.var_z = []
		if self.relaxed == True:
			for i in self.x:
				if self.x[i].solution_value > 0:
					self.var_x.append(i)

			for i in self.u:
				if self.u[i].solution_value > 0:
					self.var_u.append(i)

			for i in self.k:
				if self.k[i].solution_value > 0:
					self.var_k.append(i)

			for i in self.rd:
				if self.rd[i].solution_value > 0:
					self.var_rd.append(i)

			for i in self.s:
				if self.s[i].solution_value > 0:
					self.var_s.append(i)

			for i in self.e:
				if self.e[i].solution_value > 0:
					self.var_e.append(i)

			for i in self.y:
				if self.y[i].solution_value > 0:
					self.var_y.append(i)

			for i in self.g:
				if self.g[i].solution_value > 0:
					self.var_g.append(i)

			for i in self.xn:
				if self.xn[i].solution_value > 0:
					self.var_xn.append(i)

			for i in self.z:
				if self.z[i].solution_value > 0:
					self.var_z.append(i)
		else:
			for i in self.x:
				if self.x[i].solution_value >= 1:
					self.var_x.append(i)

			for i in self.u:
				if self.u[i].solution_value >= 1:
					self.var_u.append(i)

			for i in self.k:
				if self.k[i].solution_value >= 1:
					self.var_k.append(i)

			for i in self.rd:
				if self.rd[i].solution_value >= 1:
					self.var_rd.append(i)

			for i in self.s:
				if self.s[i].solution_value >= 1:
					self.var_s.append(i)

			for i in self.e:
				if self.e[i].solution_value >= 1:
					self.var_e.append(i)

			for i in self.y:
				if self.y[i].solution_value >= 1:
					self.var_y.append(i)

			for i in self.g:
				if self.g[i].solution_value >= 1:
					self.var_g.append(i)

			for i in self.xn:
				if self.xn[i].solution_value >= 1:
					self.var_xn.append(i)

			for i in self.z:
				if self.z[i].solution_value >= 1:
					self.var_z.append(i)

		solution = Solution(self.var_x, self.var_u, self.var_k, self.var_rd, 
			self.var_s, self.var_e, self.var_y, self.var_g, self.var_xn, self.var_z)

		return solution




	#return the variables values
	def oldreturn_solution_values(self):
		self.var_x = {}
		self.var_u = {}
		self.var_k = {}
		self.var_rd = {}
		self.var_s = {}
		self.var_e = {}
		self.var_y = {}
		self.var_g = {}
		self.var_xn = {}
		self.var_z = {}
		for i in self.x:
			if self.x[i].solution_value >= 1:
				self.var_x[i] = self.x[i].solution_value

		for i in self.u:
			if self.u[i].solution_value >= 1:
				self.var_u[i] = self.u[i].solution_value

		for i in self.k:
			if self.k[i].solution_value >= 1:
				self.var_k[i] = self.k[i].solution_value

		for i in self.rd:
			if self.rd[i].solution_value >= 1:
				self.var_rd[i] = self.rd[i].solution_value

		for i in self.s:
			if self.s[i].solution_value >= 1:
				self.var_s[i] = self.s[i].solution_value

		for i in self.e:
			if self.e[i].solution_value >= 1:
				self.var_e[i] = self.e[i].solution_value

		for i in self.y:
			if self.y[i].solution_value >= 1:
				self.var_y[i] = self.y[i].solution_value

		for i in self.g:
			if self.g[i].solution_value >= 1:
				self.var_g[i] = self.g[i].solution_value

		for i in self.xn:
			if self.xn[i].solution_value >= 1:
				self.var_xn[i] = self.xn[i].solution_value

		for i in self.z:
			if self.z[i].solution_value >= 1:
				self.var_z[i] = self.z[i].solution_value

		solution = Solution(self.var_x, self.var_u, self.var_k, self.var_rd, 
			self.var_s, self.var_e, self.var_y, self.var_g, self.var_xn, self.var_z)

		return solution

	#------------------------------------------------------Xiwj based allocation post processing algorithms-----------------------------------------------------------------
	#In the post processing algorithms below, the allocation of variables is done based on the Xiwj variables
	#So, we try to allocate resources considering the allocation returned for each RRH, in other words, the results of Xiwj will lead the allocation of resources

	


	#this is a naive post processing algorithm - the reasons for that are shown below
	#this class updates the network state based on the result of the ILP relaxation - Pelo que estou vendo, vou ter que rodar o update para cada RRH, e não de uma vez como fazia
	#this is the post processing algorithm that allcoates all RRHs returned on the solution at the same time
	#this algorithm takes the lambda and the DU returned from the solution and tries to allocate them, regardless if the DU and the lambda are the same
	#it will only try to allocate the same lambda and DU for a RRH when it happens for them to be different and the switch has no capacity
	#so, this method does not guarantee reduction on the switch delay
	#it also allocate the lambda returned from the solution for every RRH in a node, regardless if there is already a VPON established in that node
	#so, it will probably increase the number of VPONs in a same processing node, which will probably increase the blocking probability
	def relaxUpdate(self, solution):
		#first, check if the nodes from the relaxation solution has capacity before allocating the RRHs on them
		#update the node of the RRH
		#tries to allocate the returned node - if it is the cloud and has not free capacity, allocates the rrh to the fog
		for i in solution.var_x:
			if i[1] == 0 and checkNodeCapacity(i[1]):
				self.rrh[i[0]].var_x = i#talvez eu tire essa linha depois
				self.rrh[i[0]].node = i[1]
			else:
				if checkNodeCapacity(self.rrh[i[0]].fog):
					self.rrh[i[0]].node = self.rrh[i[0]].fog
				else:
					#print("-----------blocking--------")
					self.rrh[i[0]].blocked = True#ele só entra aqui se nem a cloud nem a fog tem capacidade, aí eu tenho que bloqueá-lo
			#allocate the lambda
			if checkLambdaNode(self.rrh[i[0]].node,i[2]) and checkLambdaCapacity(i[2]):
				#move wavelength capacity update here
				#print(wavelength_capacity)
				self.rrh[i[0]].wavelength = i[2]
				wavelength_capacity[self.rrh[i[0]].wavelength] -= RRHband
				if lambda_state[self.rrh[i[0]].wavelength] == 0:
					lambda_state[self.rrh[i[0]].wavelength] = 1
					lc_cost[self.rrh[i[0]].wavelength] = 0
				blockLambda(self.rrh[i[0]].wavelength, self.rrh[i[0]].node)
				#print(lambda_node[self.rrh[i[0]].wavelength])
			else:#if the chosen lambda is not available, tries to get a previously lambda allocated on the node
				#print("NOOOOOO")
				for j in range(len(lambda_node)):
					#another lambda is allocated on the node
					if lambda_node[j][self.rrh[i[0]].node] == 1 and lambda_node[j][self.rrh[i[0]].node] != i[2]:
						#check if it has capacity
						if checkLambdaCapacity(j):
							#it has free capacity
							self.rrh[i[0]].wavelength = j
							wavelength_capacity[self.rrh[i[0]].wavelength] -= RRHband
							if lambda_state[self.rrh[i[0]].wavelength] == 0:
								lambda_state[self.rrh[i[0]].wavelength] = 1
							lc_cost[self.rrh[i[0]].wavelength] = 0
							#print("going to break")
							break


				#for j in range(len(lambda_node[self.rrh[i[0]].node])):
				#	print(j)
				#	if lambda_node[self.rrh[i[0]].node][j] == 0 and lambda_node[self.rrh[i[0]].node][j] != i[2]:
				#		self.rrh[i[0]].wavelength = j
				#		wavelength_capacity[self.rrh[i[0]].wavelength] -= RRHband
				#		if lambda_state[self.rrh[i[0]].wavelength] == 0:
				#			lambda_state[self.rrh[i[0]].wavelength] = 1
				#		lc_cost[self.rrh[i[0]].wavelength] = 0
				#		print("going to break")
				#		break
				#if no lambda was found, take another one that is available
				if self.rrh[i[0]].wavelength == None:
					#print("anottttheeer")
					for j in range(len(lambda_state)):
						if lambda_state[j] == 0: #this lambda is available
							self.rrh[i[0]].wavelength = j
							wavelength_capacity[self.rrh[i[0]].wavelength] -= RRHband
							if lambda_state[self.rrh[i[0]].wavelength] == 0:
								lambda_state[self.rrh[i[0]].wavelength] = 1
							lc_cost[self.rrh[i[0]].wavelength] = 0
							blockLambda(self.rrh[i[0]].wavelength, self.rrh[i[0]].node)
							#print("took {}".format(j))
							#print("RRH is on VPON {}".format(self.rrh[i[0]].wavelength))
							#print(lambda_node)
							break
				#if no lambda was allocated at all, blocks the request
				if self.rrh[i[0]].wavelength == None:
					#print("bloaueeeeeou lambda")
					self.rrh[i[0]].blocked = True #blocks the request
			#turn the VPON on if it is not
			#if self.rrh[i[0]].blocked == None:
			#	node_id = self.rrh[i[0]].node
			#	if lambda_state[self.rrh[i[0]].wavelength] == 0:
			#		lambda_state[self.rrh[i[0]].wavelength] = 1
			#		lc_cost[self.rrh[i[0]].wavelength] = 0
			#		ln = lambda_node[self.rrh[i[0]].wavelength]
			#		for j in range(len(ln)):
			#			if j == node_id:
			#				ln[j] = 1
			#			else:
			#				ln[j] = 0
					

		#allocates the DU for the RRH
		for i in solution.var_u:
			#firsts check if the RRH was not blocked during node allocation
			if self.rrh[i[0]].blocked == None:
				#print("not blocked")
				#first, check if the returned DU has cpacity
				#print(checkCapacityDU(self.rrh[i[0]].node,i[2]))
				#print(du_processing[self.rrh[i[0]].node], self.rrh[i[0]].node)
				if checkCapacityDU(self.rrh[i[0]].node,i[2]):
					#print("TEEEM")
					#if du is different from the lambda, check if the switch has capacity
					if i[2] != self.rrh[i[0]].wavelength:
						#print("IS DIFFERENT")
						#print(switchBandwidth[self.rrh[i[0]].node])
						if switchBandwidth[self.rrh[i[0]].node] >= RRHband:
							self.rrh[i[0]].var_u = i
							self.rrh[i[0]].du = i[2]
						else:#if the switch has no capacity, what to do? try the DU equal to the wavelength
							if checkCapacityDU(self.rrh[i[0]].node, self.rrh[i[0]].wavelength): #the DU equal to the lambda has capacity, allocate it
								self.rrh[i[0]].du = self.rrh[i[0]].wavelength
							else:
								print("NOOOOOOOOO {}".format(self.rrh[i[0]]))
								print(self.rrh[i[0]].du)
								pass
					else:
						#print("IS EQUAL")
						self.rrh[i[0]].var_u = i
						self.rrh[i[0]].du = i[2]
				#if the DU does not have free capacity, take another one that has free capacity -
				# Pra eu pegar um diferente, eu tenho que ver se ele vai usar o switch - se for usar, o switch tem que ter capacidade, senão é bloqueado
				#nesse mesmo contexto, eu tenho que mover toda a atualização do estado da rede para depois que aloco o DU, pq, só vou atualizar a rede se o RRH não foi bloqueado
				else:
					#print("heeeeere")
					for j in range(len(du_processing[self.rrh[i[0]].node])):
						#print("heeere2222")
						if checkCapacityDU(self.rrh[i[0]].node, j):
							#print("hereeeeee33333333")
							if j != self.rrh[i[0]].wavelength:
								#print("IS DIFFERENT TOO")
								#print(switchBandwidth[self.rrh[i[0]].node])
								if switchBandwidth[self.rrh[i[0]].node] >= RRHband:
									self.rrh[i[0]].du = j
									break
								else:#if the switch has no capacity, what to do? define that
									if checkCapacityDU(self.rrh[i[0]].node, self.rrh[i[0]].wavelength): #the DU equal to the lambda has capacity, allocate it
										self.rrh[i[0]].du = self.rrh[i[0]].wavelength
									else:
										print("NOOOaaaaaaaaOOOOOO {}".format(self.rrh[i[0]]))
										print(self.rrh[i[0]].du)
										pass
							else:
								#print("second DU option is equal to wavelength of the RRH")
								self.rrh[i[0]].du = j
				#print(self.rrh[i[0]].du)
				#if no DU with capacity was found, blocks the requisition
				if self.rrh[i[0]].du == None:
					self.rrh[i[0]].blocked = True #blocks
					print("RRH {} blocked by DU".format(self.rrh[i[0]]))
				#now, if the rrhs was not blocked, update the state of the DUs at the processing nodes
				#now, if the RRH was not blocked, update the network state
				if self.rrh[i[0]].blocked == None:
					#amount of rrhs on the node
					rrhs_on_nodes[self.rrh[i[0]].node] += 1
					#turn the node on if it is not
					if nodeState[self.rrh[i[0]].node] == 0:
						#not activated, updates costs
						nodeCost[self.rrh[i[0]].node] = 0
						nodeState[self.rrh[i[0]].node] = 1
					#turn the VPON on if it is not
					#node_id = self.rrh[i[0]].node
					#if lambda_state[self.rrh[i[0]].wavelength] == 0:
					#	lambda_state[self.rrh[i[0]].wavelength] = 1
					#	lc_cost[self.rrh[i[0]].wavelength] = 0
					#	ln = lambda_node[self.rrh[i[0]].wavelength]
					#	for j in range(len(ln)):
					#		if j == node_id:
					#			ln[j] = 1
					#		else:
					#			ln[j] = 0
					#wavelength_capacity[self.rrh[i[0]].wavelength] -= RRHband
					#wavelength_capacity[self.rrh[i[0]].wavelength] -= RRHband
				#if self.rrh[i[0]].blocked == None:
					node_id = self.rrh[i[0]].node
					du_id = self.rrh[i[0]].du
					#update the DU capacitu
					du = du_processing[node_id]
					du[du_id] -= 1
					print(du_processing[node_id])
					if du_state[node_id][du_id] == 0:
						#du was deactivated - activates it
						du_state[node_id][du_id] = 1
						du_cost[node_id][du_id] = 0.0
					#now, verifies if the allocated DU is the same of the lambda, if not, activates the backplane ethernet switch
					if self.rrh[i[0]].du != self.rrh[i[0]].wavelength:
						if switch_state[self.rrh[i[0]].node] == 0:
							switch_state[self.rrh[i[0]].node] = 1
							switch_cost[self.rrh[i[0]].node] = 0.0
							switchBandwidth[self.rrh[i[0]].node] -= RRHband
						else:
							switchBandwidth[self.rrh[i[0]].node] -= RRHband
		#after all allocation is done, check if any resource has no more free capacity
		#if some resource has not free capacity, put its cost to infinity to avoid it to be selected
		#check nodes and DUs
		for i in self.nodes:
			node_capacity = checkNodeCapacity(i)
			if not node_capacity :
				nodeCost[i] = 999999999
			#now, check if its DUs has capacity
			for j in range(len(du_processing[i])):
				du_capacity = checkCapacityDU(i, j)
				if not du_capacity:
					#du_processing[i][j] = 999999999
					du_cost[i][j] = 999999999
		#check the lambdas
		for i in self.lambdas:
			lbda_capacity = checkLambdaCapacity(i) 
			if not lbda_capacity:
				lc_cost[i] = 999999999
		for i in self.rrh:
			if i.du == None:
				print("DU VAZIO")

	#this method tries to minimize lambdas on the nodes, so, regardless of the lambdas returned on the Xiwj variables, if there is a activate VPON in a node, it is allocated to the RRH i
	#this will probably increase the switch delay, but will reduce the amount of lambdas per node and so the blocking probability
	def minLambdaUpdate(self, solution):
		#first, check if the nodes from the relaxation solution has capacity before allocating the RRHs on them
		#update the node of the RRH
		#tries to allocate the returned node - if it is the cloud and has not free capacity, allocates the rrh to the fog
		for i in solution.var_x:
			if i[1] == 0 and checkNodeCapacity(i[1]):
				self.rrh[i[0]].var_x = i#talvez eu tire essa linha depois
				self.rrh[i[0]].node = i[1]
			else:
				if checkNodeCapacity(self.rrh[i[0]].fog):
					self.rrh[i[0]].node = self.rrh[i[0]].fog
				else:
					#print("-----------blocking--------")
					self.rrh[i[0]].blocked = True#ele só entra aqui se nem a cloud nem a fog tem capacidade, aí eu tenho que bloqueá-lo
			#allocate the lambda
			#verifies if the node has an activate VPON
			if checkNodeVPON(self.rrh[i[0]].node):#has active VPONs
				#now, gets the first free VPON
				vpon = getFirstFreeVPON(self.rrh[i[0]].node)
				#check if there is capacity on this VPON
				if vpon:#allocate the RRH on this VPON
					self.rrh[i[0]].wavelength = vpon
					nodes_vpons_capacity[self.rrh[i[0]].node][vpon] = wavelength_capacity[vpon]
			else:#use the lambda returned on the solution
			#check if the lambda returned on the solution can be allocated on the allocated node
				if checkLambdaNode(rrh[i[0]].node,i[2]) and checkLambdaCapacity(i[2]):
					self.rrh[i[0]].wavelength = i[2]
					nodes_vpons_capacity[self.rrh[i[0]].node][i[2]] = wavelength_capacity[i[2]]
				#else:#if the chosen lambda is not available, tries to get a previously lambda allocated on the node
				#	for j in range(len(lambda_node[self.rrh[i[0]].node])):
				#		if lambda_node[self.rrh[i[0]].node][j] == 0 and lambda_node[self.rrh[i[0]].node][j] != i[2]:
				#			self.rrh[i[0]].wavelength = j
				#			break
				#if no lambda was found, take another one that is available
				if self.rrh[i[0]].wavelength == None:
					for j in range(len(lambda_state)):
						if lambda_state[j] == 0: #this lambda is available
							self.rrh[i[0]].wavelength = j
							nodes_vpons_capacity[self.rrh[i[0]].node][j] = wavelength_capacity[j]
							break
				#if no lambda was allocated at all, blocks the request
				if self.rrh[i[0]].wavelength == None:
					#print("bloaueeeeeou lambda")
					self.rrh[i[0]].blocked = True #blocks the request
		#allocates the DU for the RRH
		#First, it tries to allocate a DU that has the same index as the wavelength allocated to the RRH - I CLOUD TRY DIFFERENT POLICIES HERE???
		for i in solution.var_u:
			#firsts check if the RRH was not blocked during node allocation
			if self.rrh[i[0]].blocked == None:
				#check if the DU with same index as wavelength is free
				if checkCapacityDU(self.rrh[i[0]].node, self.rrh[i[0]].wavelength):
					self.rrh[i[0]].du = i[2]
				else:#if the DU with same index as wavelength has no capacity, try the returned from the solution
					if checkCapacityDU(self.rrh[i[0]].node,i[2]):
						#print("TEEEM")
						#if du is different from the lambda, check if the switch has capacity
						if i[2] != self.rrh[i[0]].wavelength:
							print("IS DIFFERENT")
							print(switchBandwidth[self.rrh[i[0]].node])
							if switchBandwidth[self.rrh[i[0]].node] >= RRHband:
								self.rrh[i[0]].var_u = i
								self.rrh[i[0]].du = i[2]
							else:#if the switch has no capacity, what to do? try the DU equal to the wavelength
								if checkCapacityDU(self.rrh[i[0]].node, self.rrh[i[0]].wavelength): #the DU equal to the lambda has capacity, allocate it
									self.rrh[i[0]].du = self.rrh[i[0]].wavelength
								else:
									pass
					#if the DU returned on the solution does not have free capacity, take another one that has free capacity -
					# Pra eu pegar um diferente, eu tenho que ver se ele vai usar o switch - se for usar, o switch tem que ter capacidade, senão é bloqueado
					#nesse mesmo contexto, eu tenho que mover toda a atualização do estado da rede para depois que aloco o DU, pq, só vou atualizar a rede se o RRH não foi bloqueado
					else:
						#print("heeeeere")
						for j in range(len(du_processing[self.rrh[i[0]].node])):
							#print("heeere2222")
							if checkCapacityDU(self.rrh[i[0]].node, j):
								#print("hereeeeee33333333")
								if j != self.rrh[i[0]].wavelength:
									print("IS DIFFERENT TOO")
									print(switchBandwidth[self.rrh[i[0]].node])
									if switchBandwidth[self.rrh[i[0]].node] >= RRHband:
										self.rrh[i[0]].du = j
										break
									else:#if the switch has no capacity, what to do? define that
										if checkCapacityDU(self.rrh[i[0]].node, self.rrh[i[0]].wavelength): #the DU equal to the lambda has capacity, allocate it
											self.rrh[i[0]].du = self.rrh[i[0]].wavelength
										else:
											pass
								else:
									#print("second DU option is equal to wavelength of the RRH")
									self.rrh[i[0]].du = j
				#if no DU with capacity was found, blocks the requisition
				if self.rrh[i[0]].du == None:
					self.rrh[i[0]].blocked = True #blocks
				#now, if the RRH was not blocked, update the network state
				if self.rrh[i[0]].blocked == None:
					#amount of rrhs on the node
					rrhs_on_nodes[self.rrh[i[0]].node] += 1
					#turn the node on if it is not
					if nodeState[self.rrh[i[0]].node] == 0:
						#not activated, updates costs
						nodeCost[self.rrh[i[0]].node] = 0
						nodeState[self.rrh[i[0]].node] = 1
					#turn the VPON on if it is not
					node_id = self.rrh[i[0]].node
					if lambda_state[self.rrh[i[0]].wavelength] == 0:
						lambda_state[self.rrh[i[0]].wavelength] = 1
						lc_cost[self.rrh[i[0]].wavelength] = 0
						ln = lambda_node[self.rrh[i[0]].wavelength]
						for j in range(len(ln)):
							if j == node_id:
								ln[j] = 1
							else:
								ln[j] = 0
					wavelength_capacity[self.rrh[i[0]].wavelength] -= RRHband
					#wavelength_capacity[self.rrh[i[0]].wavelength] -= RRHband
				#if self.rrh[i[0]].blocked == None:
					node_id = self.rrh[i[0]].node
					du_id = self.rrh[i[0]].du
					#update the DU capacitu
					du = du_processing[node_id]
					du[du_id] -= 1
					if du_state[node_id][du_id] == 0:
						#du was deactivated - activates it
						du_state[node_id][du_id] = 1
						du_cost[node_id][du_id] = 0.0
					#now, verifies if the allocated DU is the same of the lambda, if not, activates the backplane ethernet switch
					if self.rrh[i[0]].du != self.rrh[i[0]].wavelength:
						if switch_state[self.rrh[i[0]].node] == 0:
							switch_state[self.rrh[i[0]].node] = 1
							switch_cost[self.rrh[i[0]].node] = 0.0
							switchBandwidth[self.rrh[i[0]].node] -= RRHband
						else:
							switchBandwidth[self.rrh[i[0]].node] -= RRHband
		#after all allocation is done, check if any resource has no more free capacity
		#if some resource has not free capacity, put its cost to infinity to avoid it to be selected
		#check nodes and DUs
		updateNodeVPONsCapacity()
		for i in self.nodes:
			node_capacity = checkNodeCapacity(i)
			if not node_capacity :
				nodeCost[i] = 999999999
			#now, check if its DUs has capacity
			for j in range(len(du_processing[i])):
				du_capacity = checkCapacityDU(i, j)
				if not du_capacity:
					#du_processing[i][j] = 999999999
					du_cost[i][j] = 999999999
		#check the lambdas
		for i in self.lambdas:
			lbda_capacity = checkLambdaCapacity(i) 
			if not lbda_capacity:
				lc_cost[i] = 999999999




	#--------------------------------------------End of Xiwj based post processing algorithms


	#this class updates the network state based on the result of the ILP solution
	#it takes the node activated and updates its costs, the lambda allocated and the DUs capacity, either activate or not the switch
	#and also updates the cost and capacity of the lambda used
	#just remembering, when a lambda is allocated to its node, if this node is not being processed by the ilp, all lambdas allcoated
	#to it receives capacity 0 to guarantee that they will not be used
	#when both a node and one of its DUs are allocated, they costs are updated to 0 to guarantee that they are already activated 
	#when they are passed to be either or not selected to a new RRH, thus guaranteeing that they are already turned on and no additional
	#"turning on" cost will be computed
	#Finally, the updated made by this method only acts upon the activated node (and its DUs) and the allocated lambda
	def updateValues(self, solution):
		self.updateRRH(solution)
		#search the node(s) returned from the solution
		for key in solution.var_x:
			node_id = key[1]
			rrhs_on_nodes[node_id] += 1
			#node = pns[node_id]
			if nodeState[node_id] == 0:
				#not activated, updates costs
				nodeCost[node_id] = 0
				nodeState[node_id] = 1
			lambda_id = key[2]
			if lambda_state[lambda_id] == 0:
				lambda_state[lambda_id] = 1
				lc_cost[lambda_id] = 0
				ln = lambda_node[lambda_id]
				for i in range(len(ln)):
					if i == node_id:
						ln[i] = 1
					else:
						ln[i] = 0
			wavelength_capacity[lambda_id] -= RRHband	
			#updates the DUs capacity
		for d in solution.var_u:
			node_id = d[1]
			du_id = d[2]
			#update the DU capacitu
			du = du_processing[node_id]
			du[du_id] -= 1
			if du_state[node_id][du_id] == 0:
				#du was deactivated - activates it
				du_state[node_id][du_id] = 1
				du_cost[node_id][du_id] = 0.0
			#updated the lambdas capacities
		#for w in solution.var_z:
		#	node_id = w[1]
		#	lambda_id = w[0]
		#	if lambda_state[lambda_id] == 0:
		#		lambda_state[lambda_id] = 1
		#		lc_cost[lambda_id] = 0
		#		ln = lambda_node[lambda_id]
		#		for i in range(len(ln)):
		#			if i == node_id:
		#				ln[i] = 1
		#			else:
		#				ln[i] = 0
		#	wavelength_capacity[lambda_id] -= RRHband
		if solution.var_e:
			for e in solution.var_e:
				for i in range(len(switch_cost)):
					if e == i:
						if switch_state[i] == 0:
							switch_state[i] = 1
							switch_cost[i] = 0.0
		if solution.var_k:
			for k in solution.var_k:
				for i in range(len(switchBandwidth)):
					if k[1] == i:
						switchBandwidth[i] -= RRHband

	#put the solution values into the RRH
	def updateRRH(self,solution):
			for i in range(len(self.rrh)):
				self.rrh[i].var_x = solution.var_x[i]
				self.rrh[i].var_u = solution.var_u[i]

	#deallocates the RRH
	#This method takes the RRH to be deallocated and free the resources from the
	#data structures of the node, lambda, du and switches
	def deallocateRRH(self, rrh):
		#print("Deallocating {}".format(rrh.id))
		#take the decision variables on the rrh and release the resources
		#take the node, lambda and DU
		#node_id = rrh.var_x[1]
		node_id = rrh.node
		rrhs_on_nodes[node_id] -= 1
		#lambda_id = rrh.var_x[2]
		lambda_id = rrh.wavelength
		#print("Freeing DU {}".format(rrh.var_u[2]))
		#du = rrh.var_u[2]
		du = rrh.du
		#find the wavelength
		wavelength_capacity[lambda_id] += RRHband
		#updates the DU capacity
		node = du_processing[node_id]
		#print("Deallocatin DU {}".format(du))
		node[du] += 1
		#verify if the du needs to be turned off
		if node_id == 0:
			if node[du] == cloud_du_capacity and du_state[node_id][du] == 1:
				du_state[node_id][du] = 0
				du_cost[node_id][du] = 100.0
		else:
			if node[du] == fog_du_capacity and du_state[node_id][du] == 1:
				du_state[node_id][du] = 0
				du_cost[node_id][du] = 50.0
		#update the switch capacity if this RRH was redirectioned
		#verifies if the lambda and DU used are different, if so, update the switch capacity
		if lambda_id != du:
			#lambda and Du are different
			switchBandwidth[node_id] += RRHband
		#now, updates the state and costs of the resources, if they were completely released
		if wavelength_capacity[lambda_id] == 10000.0 and lambda_state[lambda_id] == 1:
			lambda_state[lambda_id] = 0
			lc_cost[lambda_id] = 20.0
			for i in range(len(lambda_node[lambda_id])):
				lambda_node[lambda_id][i] = 1
		if switchBandwidth[node_id] == 10000.0 and switch_state[node_id] == 1:
			switch_state[node_id] = 0
			switch_cost[node_id] = 15.0
		#check if the node has RRHs being processed
		if rrhs_on_nodes[node_id] == 0 and nodeState[node_id] == 1:
			nodeState[node_id] = 0
			if node_id == 0:
				nodeCost[node_id] = 600.0
			else:
				nodeCost[node_id] = 500.0
		#print("RRH {} was deallocated".format(rrh.id))

	#reset the values of the entry parameters
	def resetValues(self):
		global rrhs_on_nodes, lambda_node, du_processing, du_state, nodeState, nodeCost, du_cost, lc_cost, switchBandwidth, switch_cost 
		global wavelength_capacity, lambda_state, switch_state
		#to keep the amount of RRHs being processed on each node
		rrhs_on_nodes = [0,0,0]
		#to assure that each lamba allocatedto a node can only be used on that node on the incremental execution of the ILP
		lambda_node = [
		[1,1,1],
		[1,1,1],
		[1,1,1],
		[1,1,1],

		]

		#to test if the rrh can be allcoated to the node
		fog = [
		[1,1,0,0,0,0,1,0,0,0],
		[1,1,0,0,0,0,0,0,0,0],
		[1,1,0,0,0,0,0,0,0,0],
		]
		du_processing = [
		[8.0, 8.0, 8.0, 8.0],
		[4.0, 4.0, 4.0, 4.0 ],
		[4.0, 4.0, 4.0, 4.0 ],




		]

		#used to calculate the processing usage of the node
		dus_total_capacity = [
		[8.0, 8.0, 8.0, 8.0],
		[4.0, 4.0, 4.0, 4.0 ],
		[4.0, 4.0, 4.0, 4.0 ],


		]

		du_state = [
		[0, 0, 0, 0],
		[0, 0, 0, 0],
		[0, 0, 0, 0],


		]

		nodeState = [0,0,0]

		nodeCost = [
		0.0,
		300.0,
		300.0,


		]

		du_cost = [
		[100.0, 100.0, 100.0, 100.0],
		[50.0, 50.0, 50.0, 50.0],
		[50.0, 50.0, 50.0, 50.0],


		]

		lc_cost = [
		20.0,
		20.0,
		20.0,
		20.0,


		]

		switch_cost = [15.0, 15.0, 15.0]
		switchBandwidth = [10000.0,10000.0,10000.0]
		wavelength_capacity = [10000.0, 10000.0, 10000.0, 10000.0]
		RRHband = 614.4;
		#lc_cost = 20
		B = 1000000
		cloud_du_capacity = 9.0
		fog_du_capacity = 1.0
		lambda_state = [0,0,0,0]
		switch_state = [0,0,0]
		#number of rrhs
		rrhs = range(0,1)
		#number of nodes
		nodes = range(0, 3)
		#number of lambdas
		lambdas = range(0, 4)



#encapsulates decision variables
class DecisionVariables(object):
	def __init__(self, var_x, var_u, var_k, var_rd, var_s, var_e, var_y, var_g, var_xn, var_z):
		self.var_x = var_x
		self.var_u = var_u
		self.var_k = var_k
		self.var_rd = var_rd
		self.var_s = var_s
		self.var_e = var_e
		self.var_y = var_y
		self.var_g = var_g
		self.var_xn = var_xn
		self.var_z = var_z

#encapsulates the solution values
class Solution(object):
	def __init__(self, var_x, var_u, var_k, var_rd, var_s, var_e, var_y, var_g, var_xn, var_z):
		self.var_x = var_x
		self.var_u = var_u
		self.var_k = var_k
		self.var_rd = var_rd
		self.var_s = var_s
		self.var_e = var_e
		self.var_y = var_y
		self.var_g = var_g
		self.var_xn = var_xn
		self.var_z = var_z

class ProcessingNode(object):
	def __init__(self, aId, du_amount, cloud_du_capacity, fog_du_capacity):
		self.id = aId
		self.dus = []
		self.state = 0
		self.lambdas = []
		self.lambdas_capacity = []
		self.du_state = []
		self.du_cost = []
		self.switch_state = 0
		self.switch_cost = 15.0
		self.switchBandwidth = 10000.0
		for i in range(du_amount):
			self.lambdas.append(0)
			self.du_state.append(0)
		if(self.id == 0):
			self.type = "Cloud"
			self.cost = 600.0
			for i in range(du_amount):
				self.dus.append(cloud_du_capacity)
				self.du_cost.append(100.0)
		else:
			self.type = "Fog"
			self.cost = 500.0
			for i in range(du_amount):
				self.dus.append(fog_du_capacity)
				self.du_cost.append(50.0)

	def decreaseDUCapacity(self, index):
		self.dus[index] -= 1

	def increaseDUCapacity(self, index):
		self.dus[index] += 1

	def allocateNode(self):
		self.cost = 0.0
		self.state = 1

	def deallocateNode(self):
		self.cost = 600.0
		self.state = 0

	#print node states
	def printNode(self):
		print("Node Type: {} Id: {}: State: {} Cost: {}".format(self.type, self.id, self.state, self.cost))
		print("Wavelengths:")
		for w in lambdas:
			if self.lambdas[w] == 1:
				print("Lambda: {} Capacity: {} Cost: {}".format(self.lambdas[w], wavelength_capacity[w], lc_cost[w]))
		print("DUs: ")
		for d in lambdas:
			print("DU: {} Active: {} Cost: {} Capacity: {}".format(d, du_state[self.id][d], du_cost[self.id][d], du_processing[self.id][d]))
		print("Switch: Active: {} Cost: {} Capacity: {}".format(self.switch_state, self.switch_cost, self.switchBandwidth))

#this class represents a RRH containing its possible processing nodes
class RRH(object):
	def __init__(self, aId, rrhs_matrix, env, service_time, cp):
		#self.id = aId
		#self.rrhs_matrix = rrhs_matrix
		#self.var_x = None
		#self.var_u = None
		#self.fog = None
		#self.node = None
		#self.wavelength = None
		#self.du = None
		#self.blocked = None
		self.id = aId
		self.rrhs_matrix = rrhs_matrix
		self.var_x = None
		self.var_u = None
		self.env = env
		self.service_time = service_time
		self.cp = cp
		self.generationTime = 0.0
		self.waitingTime = 0.0
		self.fog = None
		self.node = None
		self.wavelength = None
		self.du = None
		self.blocked = False

	#updates the generation time
	def updateGenTime(self, gen_time):
		self.generationTime = gen_time

	#updates the waiting time
	def updateWaitTime(self, wait_time):
		self.waitingTime = wait_time - self.generationTime

	def run(self):
		t = np.uniform((next_time -self.env.now)/4, next_time -self.env.now)
		#t = np.expovariate(1/1000)
		#print("Interval time is {}".format(next_time -self.env.now))
		#print("Service is {}".format(t))
		yield self.env.timeout(t)
		self.cp.departs.put(self)

#this class represents the input object to be passed to the ILP
class ilpInput(object):
	def __init__(self, du_processing, du_cost, switchBandwidth, fog):
		self.du_processing = du_processing
		self.du_cost = du_cost
		self.switchBandwidth = switchBandwidth
		self.fog = fog
	def prepareData(self, rrh):
		self.fog.append(rrh.rrhs_matrix)
		#take the nodes indicated by the rrh's connected nodes
		for i in range(len(rrh.rrhs_matrix)):
			if rrh.rrhs_matrix[i] == 1:
			#retrieve the node and mount the data structures
				node = pns[i]
				self.du_processing.append(node.dus)
				self.du_cost.append(node.du_cost)
				self.switchBandwidth.append(node.switchBandwidth)
		newInput = ilpInput(self.du_processing, self.du_cost, self.switchBandwidth, self.fog)
		return newInput

#Utility class
class Util(object):
	#print all active nodes
	def printActiveNodes(self):
		for i in pns:
			if i.state == 1:
				i.printNode()

	#create a list of RRHs with its own connected processing nodes
	def createRRHs(self, amount):
		rrhs = []
		for i in range(amount):
			rrhs_matrix = [1,0]
			if i < 10:
				rrhs_matrix[1] = 1
				r = RRH(i, rrhs_matrix)
				rrhs.append(r)
			if i >= 10 and i < 20:
				rrhs_matrix[1] = 1
				r = RRH(i, rrhs_matrix)
				rrhs.append(r)
			if i >= 20 and i < 30:
				rrhs_matrix[1] = 1
				r = RRH(i, rrhs_matrix)
				rrhs.append(r)
			if i >= 30 and i < 40:
				rrhs_matrix[1] = 1
				r = RRH(i, rrhs_matrix)
				rrhs.append(r)
			if i >= 40 and i < 50:
				rrhs_matrix[1] = 1
				r = RRH(i, rrhs_matrix)
				rrhs.append(r)
			if i >= 50 and i < 60:
				rrhs_matrix[1] = 1
				r = RRH(i, rrhs_matrix)
				rrhs.append(r)
			if i >= 60 and i < 70:
				rrhs_matrix[1] = 1
				r = RRH(i, rrhs_matrix)
				rrhs.append(r)
			if i >= 70 and i < 80:
				rrhs_matrix[1] = 1
				r = RRH(i, rrhs_matrix)
				rrhs.append(r)
			if i >= 80 and i < 90:
				rrhs_matrix[1] = 1
				r = RRH(i, rrhs_matrix)
				rrhs.append(r)
			if i >= 90 and i < 100:	
				rrhs_matrix[1] = 1
				r = RRH(i, rrhs_matrix)
				rrhs.append(r)
		return rrhs

	#update which is the fog node of each RRH
	def fogNodeRRH(self, rrhs):
		for r in rrhs:
			for i in range(len(r.rrhs_matrix)):
				if i != 0 and r.rrhs_matrix[i] == 1:
					r.fog = i


	#create a list of RRHs with its own connected processing nodes
	def newCreateRRHs(self, amount, env, service_time, cp):
		rrhs = []
		for i in range(amount):
			r = RRH(i, [1,0,0], env, service_time, cp)
			rrhs.append(r)
		self.setMatrix(rrhs)
		self.fogNodeRRH(rrhs)
		return rrhs

	#set the rrhs_matrix for each rrh created
	def setMatrix(self, rrhs):
		count = 1
		for r in rrhs:
			if count <= len(r.rrhs_matrix)-1:
				r.rrhs_matrix[count] = 1
				count += 1
			else:
				count = 1
				r.rrhs_matrix[count] = 1
				count += 1

	#compute the power consumption at the moment
	def getPowerConsumption(self):
		netCost = 0.0
		#compute all activated nodes
		for i in range(len(nodeState)):
			if nodeState[i] == 1:
				if i == 0:
					netCost += 600.0
				else:
					netCost += 500.0
			#compute activated DUs
			for j in range(len(du_state[i])):
				if du_state[i][j] == 1:
					if i == 0:
						netCost += 100.0
					else:
						netCost += 50.0
		#compute lambda and switch costs
		for w in lambda_state:
			if w == 1:
				netCost += 20.0
		for s in switch_state:
			if s == 1:
				netCost += 15.0
		return netCost	


#Test
util = Util()

#to keep the amount of RRHs being processed on each node
#rrhs_on_nodes = [0,0,0]

#to keep the amount of RRHs being processed on each node
rrhs_on_nodes = [0,0,0]
#to assure that each lamba allocatedto a node can only be used on that node on the incremental execution of the ILP
lambda_node = [
[1,1,1],
[1,1,1],
[1,1,1],
[1,1,1],

]

#to test if the rrh can be allcoated to the node
fog = [
[1,1,0,0,0,0,1,0,0,0],
[1,1,0,0,0,0,0,0,0,0],
[1,1,0,0,0,0,0,0,0,0],
]

du_processing = [
[8.0, 8.0, 8.0, 8.0],
[4.0, 4.0, 4.0, 4.0 ],
[4.0, 4.0, 4.0, 4.0 ],
]

#du_processing = [[1.0, 1.0, 1.0, 0.0],[1.0, 0.0, 0.0, 0.0 ],[1.0, 0.0, 0.0, 0.0 ]]
#used to calculate the processing usage of the node
dus_total_capacity = [
[8.0, 8.0, 8.0, 8.0],
[4.0, 4.0, 4.0, 4.0 ],
[4.0, 4.0, 4.0, 4.0 ],


]

du_state = [
[0, 0, 0, 0],
[0, 0, 0, 0],
[0, 0, 0, 0],


]

nodeState = [0,0,0]

nodeCost = [
0.0,
300.0,
300.0,


]

du_cost = [
[100.0, 100.0, 100.0, 100.0],
[50.0, 50.0, 50.0, 50.0],
[50.0, 50.0, 50.0, 50.0],


]

lc_cost = [
20.0,
20.0,
20.0,
20.0,


]



switch_cost = [15.0, 15.0, 15.0]
switchBandwidth = [10000.0,10000.0,10000.0]
wavelength_capacity = [10000.0, 10000.0, 10000.0, 10000.0]
RRHband = 614.4;
#lc_cost = 20
B = 1000000
cloud_du_capacity = 9.0
fog_du_capacity = 1.0
lambda_state = [0,0,0,0]
switch_state = [0,0,0]
#number of rrhs
rrhs = range(0,1)
#number of nodes
nodes = range(0, 3)
#number of lambdas
lambdas = range(0, 4)

nodes_lambda = {}

for i in nodes:
	nodes_lambda[i] = []

nodes_vpons_capacity = {}
for i in nodes:
	nodes_vpons_capacity[i] = {}



'''
u = Util()
antenas = u.newCreateRRHs(4)
for i in antenas:
	print(i.rrhs_matrix)
	print(i.fog)


#for i in range(len(antenas)):
#	print(antenas[i].rrhs_matrix)
#np.shuffle(antenas)
#ilp = ILP(antenas, range(len(antenas)), nodes, lambdas, False)
#s = ilp.run()
#sol = ilp.return_solution_values()
#ilp.print_var_values()
#ilp.updateValues(sol)
#print("Solving time: {}".format(s.solve_details.time))
#relaxed
np.shuffle(antenas)
ilp = ILP(antenas, range(len(antenas)), nodes, lambdas, True)
s = ilp.run()
sol = ilp.return_solution_values()
ilp.print_var_values()
#ilp.updateValues(sol)
#for i in ilp.y:
#	print("{} is {}".format(ilp.y[i],ilp.y[i].solution_value))
print("Solving time: {}".format(s.solve_details.time))
'''
'''
print(du_processing)
print(lambda_node)
#for i in sol.var_u:
#	print(i)
#print(rrhs_on_nodes)
#for i in antenas:
#	print(i.var_u)
#print(wavelength_capacity)
#print(du_processing)
cost = 0.0
cost = util.getPowerConsumption()
print("Power consumption is {}".format(cost))
'''
'''
u = Util()
antenas = u.createRRHs(11, None, None,None)
#for i in range(len(antenas)):
#	print(antenas[i].rrhs_matrix)
np.shuffle(antenas)
ilp = ILP(antenas, range(len(antenas)), nodes, lambdas)
s = ilp.run()
sol = ilp.return_solution_values()
ilp.updateValues(sol)
#print("Solving time: {}".format(s.solve_details.time))
#for i in sol.var_u:
#	print(i)
#print(rrhs_on_nodes)
#for i in antenas:
#	print(i.var_u)
#print(wavelength_capacity)
#print(du_processing)
#cost = 0.0
#cost = util.getPowerConsumption()
#print("Power consumption is {}".format(cost))
print(du_processing)
'''
"""
for i in nodes:
	pns.append(ProcessingNode(i, len(wavelength_capacity), cloud_du_capacity, fog_du_capacity))
#	pns[i].printNode()
#test
r = RRH(1,[1,1,0,0,0,0,0,0,0,0])
r2 = RRH(2,[1,1,0,0,0,0,0,0,0,0])
r3 = RRH(3,[1,1,0,0,0,0,0,0,0,0])
ilp = ILP(r, rrhs, nodes, lambdas, switchBandwidth, RRHband, wavelength_capacity, lc_cost, B, du_processing, 
	nodeCost, du_cost, switch_cost)
s = ilp.run()
solu = ilp.return_solution_values()
#print(r.var_x)
#print(r.var_u)
ilp.updateValues(solu)
#ilp.print_var_values()
#print(wavelength_capacity)
#for i in lambda_node:
#	print(i)
#print(nodeCost)
#print(wavelength_capacity)
#for i in lambda_node:
#	print(i)
#print(nodeCost)
ilp = ILP(r2, rrhs, nodes, lambdas, switchBandwidth, RRHband, wavelength_capacity, lc_cost, B, du_processing, 
	nodeCost, du_cost, switch_cost)
s = ilp.run()
solu = ilp.return_solution_values()
ilp.updateValues(solu)
ilp = ILP(r3, rrhs, nodes, lambdas, switchBandwidth, RRHband, wavelength_capacity, lc_cost, B, du_processing, 
	nodeCost, du_cost, switch_cost)
s = ilp.run()
solu = ilp.return_solution_values()
ilp.updateValues(solu)
#for i in lambda_node:
#	print(i)
#print(nodeCost)
print(wavelength_capacity)
for i in lambda_node:
	print(i)
print(nodeCost)
ilp.deallocateRRH(r)
ilp.deallocateRRH(r2)
ilp.deallocateRRH(r3)
print(wavelength_capacity)
for i in lambda_node:
	print(i)
print(nodeCost)

#print(lambda_node)
#ilp = ILP(fog, range(0,1), nodes, lambdas, switchBandwidth, RRHband, wavelength_capacity, lc_cost, B, du_processing, 
#	nodeCost, du_cost, switch_cost)
#s = ilp.run()
#solu = ilp.return_solution_values()
#ilp.updateValues(solu)
#print(nodeCost)
#ilp.print_var_values()
#ilp.mdl.print_information()
#print("The decision variables values are:")
#ilp.print_var_values()
#solu = ilp.return_solution_values()
#ilp.updateValues(solu)
#print("Optimal solution is {} ".format(s.objective_value))
#print("Decision variables are: ")
#print(solu.var_x)
#for k in solu.var_x:
#	for w in k:
#		print(w)
#print(solu.var_u)
#print(solu.var_e)
#print(len(solu.var_e))
#pns[1].printNode()
#print(wavelength_capacity)
#print(lambda_node)
#test 2
#r = RRH(1,[1,1,0,0,0,0,0,0,0,0])
#ip = ilpInput([], [], [], [])
#nip = ip.prepareData(r)
#fog2 = []
#fog2.append(r.rrhs_matrix)
#ilp = ILP(nip.fog, rrhs, nodes, lambdas, nip.switchBandwidth, RRHband, wavelength_capacity, lambda_cost, B, nip.du_processing, 
#	nodeCost, nip.du_cost, switch_cost)
#s = ilp.run()
#ilp.mdl.print_information()
#solu = ilp.return_solution_values()
#ilp.updateValues(solu)
#print("Optimal solution is {} ".format(s.objective_value))
#util.printActiveNodes()
"""
"""
p = ProcessingNode(0, 10)
p1 = ProcessingNode(1, 10)
print(p.type)
print(p.dus)
print(p1.type)
print(p1.dus)

u = Util()
r = u.createRRHs(15)
for i in r:
	print(i.rrhs_matrix)
"""