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

nodeCost = [
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

#constraints - modify for my constraints
#mdl.add_constraints(mdl.sum(self.assign_user_to_server_vars[u, s] * u.running for u in all_users) <= max_proc_per_server for s in all_servers)
mdl.add_constraints(mdl.sum(x[i,j,w] for j in nodes for w in lambdas) == 1 for i in rrhs)#1
mdl.add_constraints(mdl.sum(u[i,j,w] for j in nodes for w in lambdas) == 1 for i in rrhs)#2
mdl.add_constraints(mdl.sum(x[i,j,w] * RRHband for i in rrhs for j in nodes) <= wavelength_capacity for w in lambdas)
mdl.add_constraints(mdl.sum(u[i,j,w] for i in rrhs) <= du_processing[j][w] for j in nodes for w in lambdas)
mdl.add_constraints(mdl.sum(k[i,j] * RRHband for i in rrhs) <= switchBandwidth for j in nodes)
mdl.add_constraints(B*xn[j] >= mdl.sum(x[i,j,w] for i in rrhs for w in lambdas) for j in nodes)
mdl.add_constraints(xn[j] <= mdl.sum(x[i,j,w] for i in rrhs for w in lambdas) for j in nodes)
mdl.add_constraints(B*z[w,j] >= mdl.sum(x[i,j,w] for i in rrhs) for w in lambdas for j in nodes)
mdl.add_constraints(z[w,j] <= mdl.sum(x[i,j,w] for i in rrhs) for w in lambdas for j in nodes)
mdl.add_constraints(B*s[w,j] >= mdl.sum(u[i,j,w] for i in rrhs) for w in lambdas for j in nodes)
mdl.add_constraints(s[w,j] <= mdl.sum(u[i,j,w] for i in rrhs) for w in lambdas for j in nodes)
mdl.add_constraints(g[i,j,w] <= x[i,j,w] + u[i,j,w] for i in rrhs for j in nodes for w in lambdas)
mdl.add_constraints(g[i,j,w] >= x[i,j,w] - u[i,j,w] for i in rrhs for j in nodes for w in lambdas)
mdl.add_constraints(g[i,j,w] >= u[i,j,w] - x[i,j,w] for i in rrhs for j in nodes for w in lambdas)
mdl.add_constraints(g[i,j,w] <= 2 - x[i,j,w] - u[i,j,w] for i in rrhs for j in nodes for w in lambdas)
mdl.add_constraints(B*k[i,j] >= mdl.sum(g[i,j,w] for w in lambdas) for i in rrhs for j in nodes)
mdl.add_constraints(k[i,j] <= mdl.sum(g[i,j,w] for w in lambdas) for i in rrhs for j in nodes)
mdl.add_constraints(B*rd[w,j] >= mdl.sum(g[i,j,w] for i in rrhs) for w in lambdas for j in nodes)
mdl.add_constraints(rd[w,j] <= mdl.sum(g[i,j,w] for i in rrhs) for w in lambdas for j in nodes)
mdl.add_constraints(B*e[j] >= mdl.sum(k[i,j] for i in rrhs) for j in nodes)
mdl.add_constraints(e[j] <= mdl.sum(k[i,j] for i in rrhs)  for j in nodes)
mdl.add_constraints(mdl.sum(z[w,j] for j in nodes) <= 1 for w in lambdas)
mdl.add_constraints(mdl.sum(y[i,j] for j in nodes) == 1 for i in rrhs)
mdl.add_constraints(B*y[i,j] >= mdl.sum(x[i,j,w] for w in lambdas) for i in rrhs for j in nodes)
mdl.add_constraints(y[i,j] <= mdl.sum(x[i,j,w] for w in lambdas) for i in rrhs  for j in nodes)
mdl.add_constraints(B*y[i,j] >= mdl.sum(u[i,j,w] for w in lambdas) for i in rrhs for j in nodes)
mdl.add_constraints(y[i,j] <= mdl.sum(u[i,j,w] for w in lambdas) for i in rrhs  for j in nodes)
mdl.add_constraints(mdl.sum(u[i,j,w] for i in rrhs) >= 0 for j in nodes for w in lambdas)
""" 
//constraints
 subject to{
 -forall(i in rrhs) sum(w in lambdas, j in nodes) x[i][w][j] == 1;//2
 -forall(i in rrhs) sum(w in lambdas, j in nodes) u[i][w][j] == 1;//3
 -forall(w in lambdas) sum(i in rrhs, j in nodes) x[i][w][j]*RRHband <= wavelength_capacity;//4 
 -forall(j in nodes, w in lambdas) sum(i in rrhs) u[i][w][j] <= du_processing[j][w];//5 - O problema está aqui, o programa só está considerando como capacidade dos DU a soma das capacidades do DUs de último índice
 -forall(j in nodes) sum(i in rrhs) k[i][j]*RRHband <= switchBandwidth;//6
 -forall(j in nodes) B*xn[j] >= sum(i in rrhs, w in lambdas) x[i][w][j];//7
 -forall(j in nodes) xn[j] <= sum(i in rrhs, w in lambdas) x[i][w][j];//8
 -forall(j in nodes, w in lambdas) B*z[w][j] >= sum(i in rrhs) x[i][w][j];//9
 -forall(j in nodes, w in lambdas) z[w][j] <= sum(i in rrhs) x[i][w][j];//10
 //11 e 12 talvez já são implementadas pela 9 e 10 para ativar o line card do lambda
-forall(j in nodes, w in lambdas) B*s[w][j] >= sum(i in rrhs) u[i][w][j];//13
-forall(j in nodes, w in lambdas) s[w][j] <= sum(i in rrhs) u[i][w][j];//14
-forall(i in rrhs, w in lambdas, j in nodes) g[i][w][j] <= x[i][w][j] + u[i][w][j];//15
-forall(i in rrhs, w in lambdas, j in nodes) g[i][w][j] >= x[i][w][j] - u[i][w][j];//16
-forall(i in rrhs, w in lambdas, j in nodes) g[i][w][j] >= u[i][w][j] - x[i][w][j];//17
-forall(i in rrhs, w in lambdas, j in nodes) g[i][w][j] <= 2 - x[i][w][j] - u[i][w][j];//18
-forall(i in rrhs, j in nodes) B*k[i][j] >= sum(w in lambdas) g[i][w][j];//19
-forall(i in rrhs, j in nodes) k[i][j] <= sum(w in lambdas) g[i][w][j];//20
-forall(j in nodes, w in lambdas) B*rd[w][j] >= sum(i in rrhs) g[i][w][j];//21
-forall(j in nodes, w in lambdas) rd[w][j] <= sum(i in rrhs) g[i][w][j];//22
-forall(j in nodes) B*e[j] >= sum(i in rrhs) k[i][j];//23
-forall(j in nodes) e[j] <= sum(i in rrhs) k[i][j];//24

//restrições para garantir que o lambda é alocada só uma vez no nó
-forall(w in lambdas) sum(j in nodes) z[w][j] <= 1;//25
-forall(i in rrhs) sum(j in nodes) y[i][j] == 1;//26
forall(i in rrhs, j in nodes) B*y[i][j] >= sum(w in lambdas) x[i][w][j];//27
forall(i in rrhs, j in nodes) y[i][j] <= sum(w in lambdas) x[i][w][j];//28
forall(i in rrhs, j in nodes) B*y[i][j] >= sum(w in lambdas) u[i][w][j];//29
forall(i in rrhs, j in nodes) y[i][j] <= sum(w in lambdas) u[i][w][j];//30
forall(j in nodes, w in lambdas) sum(i in rrhs) u[i][w][j] >= 0;
"""
mdl.print_information()