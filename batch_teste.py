from docplex.mp.model import Model
import simpy
import functools
import random as np
import time
from enum import Enum
from scipy.stats import norm
import matplotlib.pyplot as plt
#This ILP does the allocation of batches of RRHs to the processing nodes.
#It considers that each RRH is connected to the cloud and to only one fog node.

#create the ilp class
class ILP(object):
	def __init__(self, rrh, rrhs, nodes, lambdas, switchBandwidth, RRHband, wavelength_capacity, lc_cost, B, du_processing, 
		nodeCost, du_cost, switch_cost):
		self.rrh = rrh
		self.fog = self.rrh.rrhs_matrix
		self.rrhs = rrhs
		self.nodes = nodes
		self.lambdas = lambdas
		self.switchBandwidth = switchBandwidth
		self.RRHband = RRHband
		self.wavelength_capacity = wavelength_capacity
		self.lc_cost = lc_cost
		self.B = B
		self.du_processing = du_processing
		self.nodeCost = nodeCost
		self.du_cost = du_cost
		self.switch_cost = switch_cost

	#run the formulation
	def run(self):
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
		 
		#Decision variables
		#x[rrhs][lambdas][nodes];
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
		self.mdl.add_constraints(self.mdl.sum(self.u[i,j,w] for j in self.nodes for w in self.lambdas) == 1 for i in self.rrhs)#2
		self.mdl.add_constraints(self.mdl.sum(self.x[i,j,w] * self.RRHband for i in self.rrhs for j in self.nodes) <= wavelength_capacity[w] for w in self.lambdas)
		self.mdl.add_constraints(self.mdl.sum(self.u[i,j,w] for i in self.rrhs) <= du_processing[j][w] for j in self.nodes for w in self.lambdas)
		self.mdl.add_constraints(self.mdl.sum(self.k[i,j] * self.RRHband for i in self.rrhs) <= switchBandwidth[j] for j in self.nodes)
		self.mdl.add_constraints(self.B*self.xn[j] >= self.mdl.sum(self.x[i,j,w] for i in self.rrhs for w in self.lambdas) for j in self.nodes)
		self.mdl.add_constraints(self.xn[j] <= self.mdl.sum(self.x[i,j,w] for i in self.rrhs for w in self.lambdas) for j in self.nodes)
		self.mdl.add_constraints(self.B*self.z[w,j] >= self.mdl.sum(self.x[i,j,w] for i in self.rrhs) for w in self.lambdas for j in self.nodes)
		self.mdl.add_constraints(self.z[w,j] <= self.mdl.sum(self.x[i,j,w] for i in self.rrhs) for w in self.lambdas for j in self.nodes)
		self.mdl.add_constraints(self.B*self.s[w,j] >= self.mdl.sum(self.u[i,j,w] for i in self.rrhs) for w in self.lambdas for j in self.nodes)
		self.mdl.add_constraints(self.s[w,j] <= self.mdl.sum(self.u[i,j,w] for i in self.rrhs) for w in self.lambdas for j in self.nodes)
		self.mdl.add_constraints(self.g[i,j,w] <= self.x[i,j,w] + self.u[i,j,w] for i in self.rrhs for j in self.nodes for w in self.lambdas)
		self.mdl.add_constraints(self.g[i,j,w] >= self.x[i,j,w] - self.u[i,j,w] for i in self.rrhs for j in self.nodes for w in self.lambdas)
		self.mdl.add_constraints(self.g[i,j,w] >= self.u[i,j,w] - self.x[i,j,w] for i in self.rrhs for j in self.nodes for w in self.lambdas)
		self.mdl.add_constraints(self.g[i,j,w] <= 2 - self.x[i,j,w] - self.u[i,j,w] for i in self.rrhs for j in self.nodes for w in self.lambdas)
		self.mdl.add_constraints(self.B*self.k[i,j] >= self.mdl.sum(self.g[i,j,w] for w in self.lambdas) for i in self.rrhs for j in self.nodes)
		self.mdl.add_constraints(self.k[i,j] <= self.mdl.sum(self.g[i,j,w] for w in self.lambdas) for i in self.rrhs for j in self.nodes)
		self.mdl.add_constraints(self.B*self.rd[w,j] >= self.mdl.sum(self.g[i,j,w] for i in self.rrhs) for w in self.lambdas for j in self.nodes)
		self.mdl.add_constraints(self.rd[w,j] <= self.mdl.sum(self.g[i,j,w] for i in self.rrhs) for w in self.lambdas for j in self.nodes)
		self.mdl.add_constraints(self.B*self.e[j] >= self.mdl.sum(self.k[i,j] for i in self.rrhs) for j in self.nodes)
		self.mdl.add_constraints(self.e[j] <= self.mdl.sum(self.k[i,j] for i in self.rrhs)  for j in self.nodes)
		self.mdl.add_constraints(self.mdl.sum(self.z[w,j] for j in self.nodes) <= 1 for w in self.lambdas)
		self.mdl.add_constraints(self.mdl.sum(self.y[i,j] for j in self.nodes) == 1 for i in self.rrhs)
		self.mdl.add_constraints(self.B*self.y[i,j] >= self.mdl.sum(self.x[i,j,w] for w in self.lambdas) for i in self.rrhs for j in self.nodes)
		self.mdl.add_constraints(self.y[i,j] <= self.mdl.sum(self.x[i,j,w] for w in self.lambdas) for i in self.rrhs  for j in self.nodes)
		self.mdl.add_constraints(self.B*self.y[i,j] >= self.mdl.sum(self.u[i,j,w] for w in self.lambdas) for i in self.rrhs for j in self.nodes)
		self.mdl.add_constraints(self.y[i,j] <= self.mdl.sum(self.u[i,j,w] for w in self.lambdas) for i in self.rrhs  for j in self.nodes)
		self.mdl.add_constraints(self.mdl.sum(self.u[i,j,w] for i in self.rrhs) >= 0 for j in self.nodes for w in self.lambdas)

		#self.mdl.add_constraints(self.y[i,j] >= self.x[i,j,w] + self.fog[i][j] - 1 for i in self.rrhs for j in self.nodes for w in self.lambdas)
		#self.mdl.add_constraints(self.y[i,j] <= self.x[i,j,w] for i in self.rrhs for j in self.nodes for w in self.lambdas)
		#this constraints guarantees that each rrh can be allocated to either the cloud or a specific fog node
		self.mdl.add_constraints(self.y[i,j] <= fog[i][j] for i in self.rrhs for j in self.nodes)
		self.mdl.add_constraints(self.z[w,j] <= lambda_node[w][j] for w in self.lambdas for j in self.nodes)

	#set the objective function
	def setObjective(self):
		self.mdl.minimize(self.mdl.sum(self.xn[j] * nodeCost[j] for j in self.nodes) + 
		self.mdl.sum(self.z[w,j] * lc_cost[w] for w in self.lambdas for j in self.nodes) + 
		(self.mdl.sum(self.k[i,j] for i in self.rrhs for j in self.nodes) + 
		self.mdl.sum(self.g[i,j,w] * switch_cost[j] for i in self.rrhs for w in self.lambdas for j in self.nodes)) + 
		(self.mdl.sum(self.s[w,j] * du_cost[j][w] for w in self.lambdas for j in self.nodes) + 
		self.mdl.sum(self.rd[w,j] * du_cost[j][w] for w in self.lambdas for j in self.nodes)) + 
		self.mdl.sum(self.e[j] * switch_cost[j] for j in self.nodes))

	#solves the model
	def solveILP(self):
		self.sol = self.mdl.solve()
		return self.sol

	#print variables values
	def print_var_values(self):
		c=0
		for i in self.x:
			if self.x[i].solution_value >= 1:
				print("{} {} is {}".format(c, self.x[i], self.x[i].solution_value))
				c+=1

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
			node = pns[node_id]
			if node.state == 0:
				#not activated, updates costs
				nodeCost[node_id] = 0	
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
		for w in solution.var_z:
			node_id = w[1]
			lambda_id = w[0]
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
		if solution.var_e:
			for e in solution.var_e:
				print(e)
				for i in range(len(switch_cost)):
					if e == i:
						if switch_state[i] == 0:
							switch_state[i] = 1
							switch_cost[i] = 0.0
		else:
			print("is empty")
		if solution.var_k:
			for k in solution.var_k:
				for i in range(len(switchBandwidth)):
					if k[1] == i:
						switchBandwidth[i] -= RRHband

	#put the solution values into the RRH
	def updateRRH(self,solution):
			self.rrh.var_x = solution.var_x[0]
			self.rrh.var_u = solution.var_u[0]

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
	def __init__(self, aId, rrhs_matrix):
		self.id = aId
		self.rrhs_matrix = rrhs_matrix
		self.var_x = None
		self.var_u = None

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
			rrhs_matrix = [1,0,0,0,0,0,0,0,0,0]
			if i < 10:
				rrhs_matrix[1] = 1
				r = RRH(i, rrhs_matrix)
				rrhs.append(r)
			if i >= 10 and i < 20:
				rrhs_matrix[2] = 1
				r = RRH(i, rrhs_matrix)
				rrhs.append(r)
			if i >= 20 and i < 30:
				rrhs_matrix[3] = 1
				r = RRH(i, rrhs_matrix)
				rrhs.append(r)
			if i >= 30 and i < 40:
				rrhs_matrix[4] = 1
				r = RRH(i, rrhs_matrix)
				rrhs.append(r)
			if i >= 40 and i < 50:
				rrhs_matrix[5] = 1
				r = RRH(i, rrhs_matrix)
				rrhs.append(r)
			if i >= 50 and i < 60:
				rrhs_matrix[6] = 1
				r = RRH(i, rrhs_matrix)
				rrhs.append(r)
			if i >= 60 and i < 70:
				rrhs_matrix[7] = 1
				r = RRH(i, rrhs_matrix)
				rrhs.append(r)
			if i >= 70 and i < 80:
				rrhs_matrix[8] = 1
				r = RRH(i, rrhs_matrix)
				rrhs.append(r)
			if i >= 80 and i < 90:
				rrhs_matrix[9] = 1
				r = RRH(i, rrhs_matrix)
				rrhs.append(r)
			if i >= 90 and i < 100:	
				rrhs_matrix[9] = 1
				r = RRH(i, rrhs_matrix)
				rrhs.append(r)
		return rrhs



#Test
util = Util()

#to assure that each lamba allocatedto a node can only be used on that node on the incremental execution of the ILP
#FAZER O MÉTODO UPDATE ATUALIZAR ESSA MATRIZ TB
lambda_node = [
[1,1,1,1,1,1,1,1,1,1],
[1,1,1,1,1,1,1,1,1,1],
[1,1,1,1,1,1,1,1,1,1],
[1,1,1,1,1,1,1,1,1,1],
[1,1,1,1,1,1,1,1,1,1],
[1,1,1,1,1,1,1,1,1,1],
[1,1,1,1,1,1,1,1,1,1],
[1,1,1,1,1,1,1,1,1,1],
[1,1,1,1,1,1,1,1,1,1],
[1,1,1,1,1,1,1,1,1,1],
]

#to test if the rrh can be allcoated to the node
fog = [
[1,1,0,0,0,0,1,0,0,0],
[1,1,0,0,0,0,0,0,0,0],
[1,1,0,0,0,0,0,0,0,0],
]
du_processing = [
[9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0],
[1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
[1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
[1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
[1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
[1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
[1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
[1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
[1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
[1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
[1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0],

]

du_state = [
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
]

nodeCost = [
600000000000000.0,
500.0,
500.0,
500.0,
500.0,
500.0,
500.0,
500.0,
500.0,
500.0,
]
du_cost = [
[100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0],
[50.0, 50.0, 50.0, 50.0, 50.0, 50.0, 50.0, 50.0, 50.0, 50.0],
[50.0, 50.0, 50.0, 50.0, 50.0, 50.0, 50.0, 50.0, 50.0, 50.0],
[50.0, 50.0, 50.0, 50.0, 50.0, 50.0, 50.0, 50.0, 50.0, 50.0],
[50.0, 50.0, 50.0, 50.0, 50.0, 50.0, 50.0, 50.0, 50.0, 50.0],
[50.0, 50.0, 50.0, 50.0, 50.0, 50.0, 50.0, 50.0, 50.0, 50.0],
[50.0, 50.0, 50.0, 50.0, 50.0, 50.0, 50.0, 50.0, 50.0, 50.0],
[50.0, 50.0, 50.0, 50.0, 50.0, 50.0, 50.0, 50.0, 50.0, 50.0],
[50.0, 50.0, 50.0, 50.0, 50.0, 50.0, 50.0, 50.0, 50.0, 50.0],
[50.0, 50.0, 50.0, 50.0, 50.0, 50.0, 50.0, 50.0, 50.0, 50.0],
]
lc_cost = [
20.0,
20.0,
20.0,
20.0,
20.0,
20.0,
20.0,
20.0,
20.0,
20.0,
]

lambda_state = [0,0,0,0,0,0,0,0,0,0]
switch_state = [0,0,0,0,0,0,0,0,0,0]
#number of rrhs
rrhs = range(0,2)
#number of nodes
nodes = range(0, 10)
#number of lambdas
lambdas = range(0, 10)
switch_cost = [15.0, 15.0, 15.0, 15.0, 15.0, 15.0, 15.0, 15.0, 15.0, 15.0,]
switchBandwidth = [10000.0,10000.0,10000.0,10000.0,10000.0,10000.0,10000.0,10000.0,10000.0,10000.0]
wavelength_capacity = [10000.0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
RRHband = 614.4;
#lc_cost = 20
B = 1000000
cloud_du_capacity = 9.0
fog_du_capacity = 1.0
pns = []
for i in nodes:
	pns.append(ProcessingNode(i, len(wavelength_capacity), cloud_du_capacity, fog_du_capacity))
#	pns[i].printNode()
#test
r = RRH(1,[1,1,0,0,0,0,0,0,0,0])
ilp = ILP(r, rrhs, nodes, lambdas, switchBandwidth, RRHband, wavelength_capacity, lc_cost, B, du_processing, 
	nodeCost, du_cost, switch_cost)
s = ilp.run()
solu = ilp.return_solution_values()
print(r.var_x)
print(r.var_u)
ilp.updateValues(solu)
ilp.print_var_values()
print(switch_cost)
print(switch_state)
print(switchBandwidth)
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