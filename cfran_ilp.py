from docplex.mp.model import Model

#instantiate the model
mdl = Model()

#Input variables

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

nodeCost = 
[
600.0,
600.0,
600.0,
600.0,
600.0,
600.0,
600.0,
600.0,
600.0,
600.0,
]

du_cost = [
[100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0],
[100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0],
[100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0],
[100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0],
[100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0],
[100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0],
[100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0],
[100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0],
[100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0],
[100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0],
]

#indexes for the decision variables x[i,j,w]
idx_ijw = [(i,j,w) for i in rrhs for j in nodes for w in lambdas]
idx_ij = [(i,j) for i in rrhs for j in nodes]
idx_wj = [(w, j) for w in lambdas for j in nodes]
idx_j = [(j) for j in nodes]
 
#Decision variables
#x[rrhs][lambdas][nodes];
x = mdl.binary_var_dict(idx_ijw)
#u[rrhs][lambdas][nodes];
u = mdl.binary_var_dict(idx_ijw)
#y[rrhs][nodes];
y = mdl.binary_var_dict(idx_ij)
#k[rrhs][nodes];
k = mdl.binary_var_dict(idx_ij)
#rd[lambdas][nodes];
rd = mdl.binary_var_dict(idx_wj)
#s[lambdas][nodes];
s = mdl.binary_var_dict(idx_wj)
#e[nodes];
e = mdl.binary_var_dict(idx_j)
#g[rrhs][lambdas][nodes];
g = mdl.binary_var_dict(idx_ijw)
#xn[nodes];
xn = mdl.binary_var_dict(idx_j)
#z[lambdas][nodes];
z = mdl.binary_var_dict(idx_wj)
