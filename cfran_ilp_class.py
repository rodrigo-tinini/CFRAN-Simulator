from docplex.mp.model import Model

#create the ilp class
class ILP(object):
	def __init__(self, rrhs, nodes, lambdas, switchBandwidth, RRHband, wavelength_capacity, lc_cost, B, du_processing, nodeCost, du_cost):
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
		idx_ijw = [(i,j,w) for i in self.rrhs for j in self.nodes for w in self.lambdas]
		idx_ij = [(i,j) for i in self.rrhs for j in self.nodes]
		idx_wj = [(w, j) for w in self.lambdas for j in self.nodes]
		idx_j = [(j) for j in self.nodes]
		 
		#Decision variables
		#x[rrhs][lambdas][nodes];
		self.x = self.mdl.binary_var_dict(idx_ijw, name = 'RRH/Node/Lambda')
		#u[rrhs][lambdas][nodes];
		self.u = self.mdl.binary_var_dict(idx_ijw, name = 'RRH/Node/DU')
		#y[rrhs][nodes];
		self.y = self.mdl.binary_var_dict(idx_ij, name = 'RRH/Node')
		#k[rrhs][nodes];
		self.k = self.mdl.binary_var_dict(idx_ij, name = 'Redirection of RRH in Node')
		#rd[lambdas][nodes];
		self.rd = self.mdl.binary_var_dict(idx_wj, name = 'DU in Node used for redirection')
		#s[lambdas][nodes];
		self.s = self.mdl.binary_var_dict(idx_wj, name = 'DU activated in node')
		#e[nodes];
		self.e = self.mdl.binary_var_dict(idx_j, name = "Switch/Node")
		#g[rrhs][lambdas][nodes];
		self.g = self.mdl.binary_var_dict(idx_ijw, name = 'Redirection of RRH in Node in DU')
		#xn[nodes];
		self.xn = self.mdl.binary_var_dict(idx_j, name = 'Node activated')
		#z[lambdas][nodes];
		self.z = self.mdl.binary_var_dict(idx_wj, name = 'Lambda in Node')

	#create constraints
	def setConstraints(self):
		self.mdl.add_constraints(self.mdl.sum(self.x[i,j,w] for j in self.nodes for w in self.lambdas) == 1 for i in self.rrhs)#1
		self.mdl.add_constraints(self.mdl.sum(self.u[i,j,w] for j in self.nodes for w in self.lambdas) == 1 for i in self.rrhs)#2
		self.mdl.add_constraints(self.mdl.sum(self.x[i,j,w] * self.RRHband for i in self.rrhs for j in self.nodes) <= self.wavelength_capacity for w in self.lambdas)
		self.mdl.add_constraints(self.mdl.sum(self.u[i,j,w] for i in self.rrhs) <= self.du_processing[j][w] for j in self.nodes for w in self.lambdas)
		self.mdl.add_constraints(self.mdl.sum(self.k[i,j] * self.RRHband for i in self.rrhs) <= self.switchBandwidth for j in self.nodes)
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

	#set the objective function
	def setObjective(self):
		self.mdl.minimize(self.mdl.sum(self.xn[j] * self.nodeCost[j] for j in self.nodes) + self.mdl.sum(self.z[w,j] * self.lc_cost for w in self.lambdas for j in self.nodes) + (self.mdl.sum(self.k[i,j] for i in self.rrhs for j in self.nodes) + self.mdl.sum(self.g[i,w,j] * 15.0 for i in self.rrhs for w in self.lambdas for j in self.nodes)) + (self.mdl.sum(self.s[w,j] * self.du_cost[j][w] for w in self.lambdas for j in self.nodes) + self.mdl.sum(self.rd[w,j] * self.du_cost[j][w] for w in self.lambdas for j in self.nodes)) + self.mdl.sum(self.e[j] * 50.0 for j in self.nodes))

	#solves the model
	def solveILP(self):
		self.sol = self.mdl.solve()
		return self.sol

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
]

nodeCost = [
600.0,
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

#number of rrhs
rrhs = range(0,10)
#number of nodes
nodes = range(0, 10)
#number of lambdas
lambdas = range(0, 10)
switchBandwidth = 10000.0
RRHband = 614.4;
wavelength_capacity = 10000.0;
lc_cost = 20
B = 1000000

#test
ilp = ILP(rrhs, nodes, lambdas, switchBandwidth, RRHband, wavelength_capacity, lc_cost, B, du_processing, nodeCost, du_cost)
s = ilp.run()
print(ilp.mdl.print_information())
print(s.objective_value)