#DOCPLEX of the GC'17 ILP
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

#log variables
power_consumption = []
execution_time = []
average_delay = []

#transmission delay to nodes
#considering a propagation time of 2*10^8 m/s and a core of mm 50µm
cloud_delay = 0.0000980654
fog_delay = 0.0001961308

#number of fogs
fog_amount = 5

#to keep the amount of RRHs being processed on each node
rrhs_on_nodes = [0,0,0,0,0,0]

cpri_rate = 614.4

node_capacity = [92160, 18432, 18432, 18432, 18432, 18432]

#du cost of each node
cost_du = [100.0, 50.0, 50.0, 50.0, 50.0, 50.0]

#to assure that each lamba allocatedto a node can only be used on that node on the incremental execution of the ILP
lambda_node = [
[1,1,1,1,1,1],
[1,1,1,1,1,1],
[1,1,1,1,1,1],
[1,1,1,1,1,1],
[1,1,1,1,1,1],
[1,1,1,1,1,1],
[1,1,1,1,1,1],
[1,1,1,1,1,1],
[1,1,1,1,1,1],
[1,1,1,1,1,1],
[1,1,1,1,1,1],
[1,1,1,1,1,1],
[1,1,1,1,1,1],
[1,1,1,1,1,1],
[1,1,1,1,1,1],
[1,1,1,1,1,1],
[1,1,1,1,1,1],
[1,1,1,1,1,1],
[1,1,1,1,1,1],
[1,1,1,1,1,1],
]

#to test if the rrh can be allcoated to the node
fog = [
[1,1,0,0,0,0,1,0,0,0],
[1,1,0,0,0,0,0,0,0,0],
[1,1,0,0,0,0,0,0,0,0],
]

du_processing = [
[16.0, 16.0, 16.0, 16.0, 16.0],
[4, 4, 4, 4, 4],
[4, 4, 4, 4, 4],
[4, 4, 4, 4, 4],
[4, 4, 4, 4, 4],
[4, 4, 4, 4, 4],
]

du_state = [
[0, 0, 0, 0, 0],
[0, 0, 0, 0, 0],
[0, 0, 0, 0, 0],
[0, 0, 0, 0, 0],
[0, 0, 0, 0, 0],
[0, 0, 0, 0, 0],
]

nodeState = [0,0,0,0,0,0]

#nodeCost = [
#600.0,
#300.0,
#300.0,
#300.0,
#300.0,
#300.0,
#]
nodeCost = [
0.0,
300.0,
300.0,
300.0,
300.0,
300.0,
]

du_cost = [
[100.0, 100.0, 100.0, 100.0, 100.0],
[50.0, 50.0, 50.0, 50.0, 50.0],
[50.0, 50.0, 50.0, 50.0, 50.0],
[50.0, 50.0, 50.0, 50.0, 50.0],
[50.0, 50.0, 50.0, 50.0, 50.0],
[50.0, 50.0, 50.0, 50.0, 50.0],
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


#switch_cost = [15.0, 15.0, 15.0, 15.0, 15.0]
#switchBandwidth = [10000.0,10000.0,10000.0,10000.0,10000.0]
wavelength_capacity = [10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0, 10000.0]
RRHband = 614.4;
#lc_cost = 20
B = 1000000
cloud_du_capacity = 9.0
fog_du_capacity = 1.0
lambda_state = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
#switch_state = [0,0,0,0,0]
#number of rrhs
rrhs = range(0,1)
#number of nodes
nodes = range(0, 6)
#number of lambdas
lambdas = range(0, 20)

#create the ilp class
class ILP(object):
	def __init__(self, rrh, rrhs, nodes, lambdas):
		self.rrh = rrh
		self.fog = []
		for i in rrh:
			self.fog.append(i.rrhs_matrix)
		self.rrhs = rrhs
		self.nodes = nodes
		self.lambdas = lambdas

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
		#x[rrhs][lambdas][nodes]; RRH i is processedat j with lambdaw
		self.x = self.mdl.binary_var_dict(self.idx_ijw, name = 'RRH in Node with Lambda', key_format = "")
		#y[rrhs][nodes];
		self.y = self.mdl.binary_var_dict(self.idx_ij, name = 'RRH in Node')
		#xn[nodes]; Node n is activated
		self.xn = self.mdl.binary_var_dict(self.idx_j, name = 'Node activated')
		#z[lambdas][nodes];Lambda w is allocated to node j
		self.z = self.mdl.binary_var_dict(self.idx_wj, name = 'Lambda in Node')

	#create constraints
	def setConstraints(self):
		self.mdl.add_constraints(self.mdl.sum(self.x[i,j,w] for j in self.nodes for w in self.lambdas) == 1 for i in self.rrhs)#1
		#next constraint used for the pure globecom experiments in order to explorer the cpri line rates aggregation into dedicated wavelengths (not vpon, for vpon, remove this line)
		self.mdl.add_constraints(self.mdl.sum(self.x[i,j,w] for i in self.rrhs ) <= 1 for j in self.nodes for w in self.lambdas)#1

		self.mdl.add_constraints(self.mdl.sum(self.x[i,j,w] * RRHband for i in self.rrhs for j in self.nodes) <= wavelength_capacity[w] for w in self.lambdas)

		self.mdl.add_constraints(self.mdl.sum(self.x[i,j,w] * cpri_rate for i in self.rrhs for w in self.lambdas) <= node_capacity[j] for j in self.nodes)


		self.mdl.add_constraints(B*self.xn[j] >= self.mdl.sum(self.x[i,j,w] for i in self.rrhs for w in self.lambdas) for j in self.nodes)
		self.mdl.add_constraints(self.xn[j] <= self.mdl.sum(self.x[i,j,w] for i in self.rrhs for w in self.lambdas) for j in self.nodes)
		self.mdl.add_constraints(B*self.z[w,j] >= self.mdl.sum(self.x[i,j,w] for i in self.rrhs) for w in self.lambdas for j in self.nodes)
		self.mdl.add_constraints(self.z[w,j] <= self.mdl.sum(self.x[i,j,w] for i in self.rrhs) for w in self.lambdas for j in self.nodes)
		self.mdl.add_constraints(self.mdl.sum(self.z[w,j] for j in self.nodes) <= 1 for w in self.lambdas)
		self.mdl.add_constraints(self.mdl.sum(self.y[i,j] for j in self.nodes) == 1 for i in self.rrhs)
		self.mdl.add_constraints(B*self.y[i,j] >= self.mdl.sum(self.x[i,j,w] for w in self.lambdas) for i in self.rrhs for j in self.nodes)
		self.mdl.add_constraints(self.y[i,j] <= self.mdl.sum(self.x[i,j,w] for w in self.lambdas) for i in self.rrhs  for j in self.nodes)

		#self.mdl.add_constraints(self.y[i,j] >= self.x[i,j,w] + self.fog[i][j] - 1 for i in self.rrhs for j in self.nodes for w in self.lambdas)
		#self.mdl.add_constraints(self.y[i,j] <= self.x[i,j,w] for i in self.rrhs for j in self.nodes for w in self.lambdas)
		#this constraints guarantees that each rrh can be allocated to either the cloud or a specific fog node
		self.mdl.add_constraints(self.y[i,j] <= self.fog[i][j] for i in self.rrhs for j in self.nodes)
		self.mdl.add_constraints(self.z[w,j] <= lambda_node[w][j] for w in self.lambdas for j in self.nodes)

	#set the objective function
	def setObjective(self):
		#self.mdl.minimize(self.mdl.sum(self.xn[j] * nodeCost[j] for j in self.nodes))
		self.mdl.minimize(self.mdl.sum(self.xn[j] * nodeCost[j] for j in self.nodes) + 
		self.mdl.sum(self.z[w,j] * (lc_cost[w] + cost_du[j]) for w in self.lambdas for j in self.nodes) )

	#solves the model
	def solveILP(self):
		self.sol = self.mdl.solve()
		return self.sol

	#print variables values
	def print_var_values(self):
		for i in self.x:
			if self.x[i].solution_value >= 1:
				print("{} is {}".format(self.x[i], self.x[i].solution_value))
		for i in self.xn:
			if self.xn[i].solution_value >= 1:
				print("{} is {}".format(self.xn[i], self.xn[i].solution_value))

		for i in self.z:
			if self.z[i].solution_value >= 1:
				print("{} is {}".format(self.z[i], self.z[i].solution_value))


#return the variables values
	def return_solution_values(self):
		self.var_x = []
		self.var_xn = []
		self.var_z = []
		for i in self.x:
			if self.x[i].solution_value >= 1:
				self.var_x.append(i)
		for i in self.xn:
			if self.xn[i].solution_value >= 1:
				self.var_xn.append(i)
		for i in self.z:
			if self.z[i].solution_value >= 1:
				self.var_z.append(i)

		solution = Solution(self.var_x, self.var_xn, self.var_z)

		return solution



	#this method updates the network state based on the result of the ILP solution
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
			node_capacity[node_id] -= cpri_rate
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
		

	#put the solution values into the RRH
	def updateRRH(self,solution):
			for i in range(len(self.rrh)):
				self.rrh[i].var_x = solution.var_x[i]

	#deallocates the RRH
	#This method takes the RRH to be deallocated and free the resources from the
	#data structures of the node, lambda, du and switches
	def deallocateRRH(self, rrh):
		#take the decision variables on the rrh and release the resources
		#take the node, lambda and DU
		node_id = rrh.var_x[1]
		rrhs_on_nodes[node_id] -= 1
		node_capacity[node_id] += cpri_rate
		lambda_id = rrh.var_x[2]
		du = rrh.var_u[2]
		#find the wavelength
		wavelength_capacity[lambda_id] += RRHband
		#now, updates the state and costs of the resources, if they were completely released
		if wavelength_capacity[lambda_id] == 10000.0 and lambda_state[lambda_id] == 1:
			lambda_state[lambda_id] = 0
			lc_cost[lambda_id] = 20.0
			for i in range(len(lambda_node[lambda_id])):
				lambda_node[lambda_id][i] = 1
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
		
		cpri_rate = 614.4

		#du cost of each node
		cost_du = [100.0, 50.0, 50.0]

		node_capacity = [15360, 6144, 6144]

		#to keep the amount of RRHs being processed on each node
		rrhs_on_nodes = [0,0,0]

		#to assure that each lamba allocatedto a node can only be used on that node on the incremental execution of the ILP
		lambda_node = [
		[1,1,1],
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
		[5.0, 5.0, 5.0, 5.0, 5.0],
		[2.0, 2.0, 2.0, 2.0, 2.0],
		[2.0, 2.0, 2.0, 2.0, 2.0],



		]

		du_state = [
		[0, 0, 0, 0, 0],
		[0, 0, 0, 0, 0],
		[0, 0, 0, 0, 0],


		]

		nodeState = [0,0,0]

		nodeCost = [
		600.0,
		500.0,
		500.0,

		]

		du_cost = [
		[100.0, 100.0, 100.0, 100.0, 100.0],
		[50.0, 50.0, 50.0, 50.0, 50.0],
		[50.0, 50.0, 50.0, 50.0, 50.0],


		]
		lc_cost = [
		20.0,
		20.0,
		20.0,
		20.0,
		20.0,

		]

		switch_cost = [15.0, 15.0, 15.0]
		switchBandwidth = [10000.0,10000.0,10000.0]
		wavelength_capacity = [10000.0, 10000.0, 10000.0, 10000.0, 10000.0]
		RRHband = 614.4;
		#lc_cost = 20
		B = 1000000
		cloud_du_capacity = 9.0
		fog_du_capacity = 1.0
		lambda_state = [0,0,0,0,0]
		switch_state = [0,0,0]
		#number of rrhs
		rrhs = range(0,1)
		#number of nodes
		nodes = range(0, 3)
		#number of lambdas
		lambdas = range(0, 5)

#encapsulates the solution values
class Solution(object):
	def __init__(self, var_x, var_xn, var_z):
		self.var_x = var_x
		self.var_xn = var_xn
		self.var_z = var_z

#this class represents a RRH containing its possible processing nodes
class RRH(object):
	def __init__(self, aId, rrhs_matrix):
		self.id = aId
		self.rrhs_matrix = rrhs_matrix
		self.var_x = None

#Utility class
class Util(object):

	#gets the overall delay of the network
    def overallDelay(self, solution):
        #search for each rrh on the solution variable and
        #compute the delay according to the type of the node
        for key in solution.var_x:
            node_id = key[1]
            print(node_id)

	#compute the power consumption at the moment
	def getPowerConsumption(self):
		netCost = 0.0
		#compute all activated nodes
		for i in range(len(nodeState)):
			if nodeState[i] == 1:
				if i == 0:
					netCost += 600.0
				else:
					netCost += 300.0
		#compute lambda and switch costs
		for w in lambda_state:
			if w == 1:
				netCost += 20.0
		return netCost

	#------------------------------------------------------------------------------------------#
	#--------------------------Methods for the dynamic case-------------------------------------#
	#create a list of RRHs with its own connected processing nodes - for the dynamic case
	def newCreateRRHs(self, amount):
		rrhs = []
		for i in range(amount):
			r = RRH(i, [1,0,0,0,0])
			rrhs.append(r)
		self.setMatrix(rrhs)
		return rrhs

	#set the rrhs_matrix for each rrh created - for the dynamic case
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

	#------------------------------------------------------------------------------------------#
	#--------------------------Methods for the static case-------------------------------------#

	#set matrix 
	def staticSetMatrix(self, rrhs, bottom, top, fog):
		for i in range(bottom, top):
			rrhs[i].rrhs_matrix[fog] = 1

	#another create rrhs method to be used on the static case
	#it creates the rrhs-fog matrix according to the amount of processing nodes declared
	def staticCreateRRHs(self, rrhs_amount):	
		#create the rrhs
		rrhs = []
		for i in range(rrhs_amount):
			r = RRH(i, [1,0,0,0,0,0])
			rrhs.append(r)
		return rrhs

	#this method distributes RRHs uniformly to the fog nodes (example, 5 antenas, 5 fog nodes, 1 antena connected per fog, 10 antenas, 5 fog, 2 antenas per fog and so on)
	def setExperiment(self, antenas, fogs):
		divided = int(len(antenas)/fogs)
		self.staticSetMatrix(antenas, 0, divided, 1)
		self.staticSetMatrix(antenas,  divided, divided*2, 2)
		self.staticSetMatrix(antenas,  divided*2, divided*3, 3)
		self.staticSetMatrix(antenas,  divided*3, divided*4, 4)
		self.staticSetMatrix(antenas,  divided*4, divided*5, 5)

#Test
'''
util = Util()
#runs experiments
exec_number = 10
for i in range(exec_number):
	#increment
	amount = 45
	antenas = []
	for i in range(amount):
		antenas = util.newCreateRRHs(amount)
	ilp = ILP(antenas, range(len(antenas)), nodes, lambdas)
	s = ilp.run()
	print(s.objective_value)
	print(s.solve_details.time)
'''
util = Util()
amount = 20
antenas = []
antenas = util.staticCreateRRHs(amount)
util.setExperiment(antenas, fog_amount)
#for i in antenas:
#	print(i.rrhs_matrix)
#util.staticSetMatrix(antenas, 0, 32, 1)
#util.staticSetMatrix(antenas, 32, 64, 2)
#util.staticSetMatrix(antenas, 64, 100, 3)
#util.staticSetMatrix(antenas, 96, 128, 4)
#util.staticSetMatrix(antenas, 128, 160, 5)
ilp = ILP(antenas, range(len(antenas)), nodes, lambdas)
s = ilp.run()
print(s.objective_value)
sol = ilp.return_solution_values()
ilp.updateValues(sol)
print(util.getPowerConsumption())
#print(s.solve_details.time)
