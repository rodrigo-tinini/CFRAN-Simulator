from docplex.mp.model import Model
#This ILP does the allocation of batches of RRHs to the processing nodes.
#It considers that each RRH is connected to the cloud and to only one fog node.

#create the ilp class
class ILP(object):
	def __init__(self, fog, rrhs, nodes, lambdas, switchBandwidth, RRHband, wavelength_capacity, lc_cost, B, du_processing, nodeCost, du_cost):
		self.fog = fog
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
		self.mdl.add_constraints(self.mdl.sum(self.x[i,j,w] * self.RRHband for i in self.rrhs for j in self.nodes) <= self.wavelength_capacity[w] for w in self.lambdas)
		self.mdl.add_constraints(self.mdl.sum(self.u[i,j,w] for i in self.rrhs) <= self.du_processing[j][w] for j in self.nodes for w in self.lambdas)
		self.mdl.add_constraints(self.mdl.sum(self.k[i,j] * self.RRHband for i in self.rrhs) <= self.switchBandwidth[j] for j in self.nodes)
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
		self.mdl.add_constraints(self.y[i,j] <= self.fog[i][j] for i in self.rrhs for j in self.nodes)
		

	#set the objective function
	def setObjective(self):
		self.mdl.minimize(self.mdl.sum(self.xn[j] * self.nodeCost[j] for j in self.nodes) + 
		self.mdl.sum(self.z[w,j] * self.lc_cost for w in self.lambdas for j in self.nodes) + 
		(self.mdl.sum(self.k[i,j] for i in self.rrhs for j in self.nodes) + 
		self.mdl.sum(self.g[i,j,w] * 15.0 for i in self.rrhs for w in self.lambdas for j in self.nodes)) + 
		(self.mdl.sum(self.s[w,j] * self.du_cost[j][w] for w in self.lambdas for j in self.nodes) + 
		self.mdl.sum(self.rd[w,j] * self.du_cost[j][w] for w in self.lambdas for j in self.nodes)) + 
		self.mdl.sum(self.e[j] * 50.0 for j in self.nodes))

	#solves the model
	def solveILP(self):
		self.sol = self.mdl.solve()
		return self.sol

	#print variables values
	def print_var_values(self):
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

	#return the variables values
	def return_solution_values(self):
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

#Test

#to test if the rrh can be allcoated to the node
fog = [
[1,1],
[1,1],
[1,1],
[1,1],
[1,1],
]

du_processing = [
[1.0, 2.0],
[1.0, 1.0],
]

nodeCost = [
600.0,
500.0,
]

du_cost = [
[100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0],
[50.0, 50.0, 50.0, 50.0, 50.0, 50.0, 50.0, 50.0, 50.0, 50.0],
]

#number of rrhs
rrhs = range(0,5)
#number of nodes
nodes = range(0, 2)
#number of lambdas
lambdas = range(0, 2)
switchBandwidth = [10000.0,10000.0,10000.0,10000.0,10000.0,10000.0,10000.0,10000.0,10000.0,10000.0]
wavelength_capacity = [10000.0, 10000.0]
RRHband = 614.4;
lc_cost = 20
B = 1000000

#test
ilp = ILP(fog, rrhs, nodes, lambdas, switchBandwidth, RRHband, wavelength_capacity, lc_cost, B, du_processing, 
	nodeCost, du_cost)
s = ilp.run()
ilp.mdl.print_information()
print("The decision variables values are:")
ilp.print_var_values()
solu = ilp.return_solution_values()
print("Optimal solution is {} ".format(s.objective_value))
print(solu.var_x)

