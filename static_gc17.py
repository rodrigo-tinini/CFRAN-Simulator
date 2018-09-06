import time
import importlib
import gc17ILP as gc

def genLogs(s):
	#power consumption
	for policy in lambda_policies:
		with open('/home/tinini/Área de Trabalho/Simulador/CFRAN-Simulator/ilp_static/logs/power/{}_power_consumption_{}.txt'.format(s,policy),'a') as filehandle:  
		    #filehandle.write("{}\n\n".format(i))
		    filehandle.writelines("%s\n" % p for p in power_consumption["{}".format(policy)])
		    filehandle.write("\n")
		    #filehandle.write("\n")
		with open('/home/tinini/Área de Trabalho/Simulador/CFRAN-Simulator/ilp_static/logs/exec_time/{}_execution_time_{}.txt'.format(s,policy),'a') as filehandle:  
		    #filehandle.write("{}\n\n".format(i))
		    filehandle.writelines("%s\n" % p for p in execution_time["{}".format(policy)])
		    filehandle.write("\n")
		    #filehandle.write("\n")
		with open('/home/tinini/Área de Trabalho/Simulador/CFRAN-Simulator/ilp_static/logs/delay/{}_minimum_average_delay_{}.txt'.format(s,policy),'a') as filehandle:  
		    #filehandle.write("{}\n\n".format(i))
		    filehandle.writelines("%s\n" % p for p in average_delay["{}".format(policy)])
		    filehandle.write("\n")
		    #filehandle.write("\n")
'''
#old gen logs, for simple executions of the ILP considering only one policy to log
def genLogs():
	#power consumption
	with open('/home/tinini/Área de Trabalho/Simulador/CFRAN-Simulator/ilp_static/logs/power/power_consumption_{}.txt'.format(amount),'a') as filehandle:  
	    filehandle.write("{}\n\n".format(i))
	    filehandle.writelines("%s\n" % p for p in power_consumption["{}".format(policy)])
	    filehandle.write("\n")
	    #filehandle.write("\n")
	with open('/home/tinini/Área de Trabalho/Simulador/CFRAN-Simulator/ilp_static/logs/exec_time/execution_time_{}.txt'.format(amount),'a') as filehandle:  
	    filehandle.write("{}\n\n".format(i))
	    filehandle.writelines("%s\n" % p for p in execution_time["{}".format(policy)])
	    filehandle.write("\n")
	    #filehandle.write("\n")
	with open('/home/tinini/Área de Trabalho/Simulador/CFRAN-Simulator/ilp_static/logs/delay/minimum_average_delay_{}.txt'.format(amount),'a') as filehandle:  
	    filehandle.write("{}\n\n".format(i))
	    filehandle.writelines("%s\n" % p for p in average_delay["{}".format(policy)])
	    filehandle.write("\n")
	    #filehandle.write("\n")
'''
#wavelength assignment policies (GC17 + ISCC)
lambda_policies = ['vpon', 'rrha', 'ca']

#logging variables
#power_consumption = []
#execution_time = []
#average_delay = []

#logging variables for each of the wavelength assignment schemes from GC17 and ISCC
power_consumption = {}
execution_time = {}
average_delay = {}

for i in lambda_policies:
	power_consumption['{}'.format(i)] = []
	execution_time['{}'.format(i)] = []
	average_delay['{}'.format(i)] = []

def reloadDicts():
	global power_consumption, execution_time, average_delay
	for i in lambda_policies:
		power_consumption['{}'.format(i)] = []
		execution_time['{}'.format(i)] = []
		average_delay['{}'.format(i)] = []

#util function
util = gc.Util()

#old execution considering automatic increase of number of RRHs
'''
amount = 5
for i in range(40):
	print("AMOUNT IS {}".format(amount))
	importlib.reload(gc)
	antenas = []
	antenas = util.staticCreateRRHs(amount)
	util.setExperiment(antenas, gc.fog_amount)
	#for i in antenas:
	#	print(i.rrhs_matrix)
	ilp = gc.ILP(antenas, range(len(antenas)), gc.nodes, gc.lambdas)
	s = ilp.run()
	sol = ilp.return_solution_values()
	ilp.updateValues(sol)
	power_consumption.append(util.getPowerConsumption())
	execution_time.append(s.solve_details.time)
	average_delay.append(util.overallDelay(sol))
	amount += 5
genLogs()
'''

#################################################---3RRHs per aggregation groups
############################################### 5 Aggregation groups 
#initial amount of rrhs
amount = 15
#VPONs executions
#main loop
#5 aggregation groups
reloadDicts()
print("AMOUNT IS {}".format(amount))
importlib.reload(gc)
antenas = []
antenas = util.staticCreateRRHs(amount)
util.setExperiment(antenas, gc.fog_amount)
#for i in antenas:
#	print(i.rrhs_matrix)
ilp = gc.ILP(antenas, range(len(antenas)), gc.nodes, gc.lambdas)
s = ilp.run()
sol = ilp.return_solution_values()
ilp.updateValues(sol)
power_consumption['vpon'].append(util.getPowerConsumption())
execution_time['vpon'].append(s.solve_details.time)
average_delay['vpon'].append(util.overallDelay(sol))
genLogs("3X5")

amount = 15
#RRHA executions - NEED TO ADD THE CONSTRAINT TO AVOID VPON ON THE MODEL
#main loop
#5 aggregation groups
reloadDicts()
print("AMOUNT IS {}".format(amount))
importlib.reload(gc)
antenas = []
antenas = util.staticCreateRRHs(amount)
util.setExperiment(antenas, gc.fog_amount)
#for i in antenas:
#	print(i.rrhs_matrix)
ilp = gc.ILP(antenas, range(len(antenas)), gc.nodes, gc.lambdas)
ilp.mdl.add_constraints(ilp.mdl.sum(ilp.x[i,j,w] for i in ilp.rrhs ) <= 1 for j in ilp.nodes for w in ilp.lambdas)
s = ilp.run()
sol = ilp.return_solution_values()
ilp.updateValues(sol)
power_consumption['rrha'].append(util.getPowerConsumption())
execution_time['rrha'].append(s.solve_details.time)
average_delay['rrha'].append(util.overallDelay(sol))
genLogs("3X5")

amount = 5
#CA executions - NEED TO ADDTHE COINSTRAINT TO AVOID VPON ON THE MODEL AND CHANGE THE RRH BAND TO THE BAND OF THE ENTIRE AGGREGATION GROUP
#main loop
#5 aggregation groups
reloadDicts()
print("AMOUNT IS {}".format(amount))
importlib.reload(gc)
gc.RRHband = 3 * gc.RRHband
gc.cpri_rate = 3* gc.cpri_rate
antenas = []
antenas = util.staticCreateRRHs(amount)
util.setExperiment(antenas, gc.fog_amount)
#for i in antenas:
#	print(i.rrhs_matrix)
ilp = gc.ILP(antenas, range(len(antenas)), gc.nodes, gc.lambdas)
ilp.mdl.add_constraints(ilp.mdl.sum(ilp.x[i,j,w] for i in ilp.rrhs ) <= 1 for j in ilp.nodes for w in ilp.lambdas)
s = ilp.run()
sol = ilp.return_solution_values()
ilp.updateValues(sol)
power_consumption['ca'].append(util.getPowerConsumption())
execution_time['ca'].append(s.solve_details.time)
average_delay['ca'].append(util.overallDelay(sol))
genLogs("3X5")

############################################### 10 Aggregation groups 
#initial amount of rrhs
amount = 30
#VPONs executions
#main loop
#10 aggregation groups
reloadDicts()
print("AMOUNT IS {}".format(amount))
importlib.reload(gc)
antenas = []
antenas = util.staticCreateRRHs(amount)
util.setExperiment(antenas, gc.fog_amount)
#for i in antenas:
#	print(i.rrhs_matrix)
ilp = gc.ILP(antenas, range(len(antenas)), gc.nodes, gc.lambdas)
s = ilp.run()
sol = ilp.return_solution_values()
ilp.updateValues(sol)
power_consumption['vpon'].append(util.getPowerConsumption())
execution_time['vpon'].append(s.solve_details.time)
average_delay['vpon'].append(util.overallDelay(sol))
genLogs("3X10")

amount = 30
#RRHA executions - NEED TO ADD THE CONSTRAINT TO AVOID VPON ON THE MODEL
#main loop
#10 aggregation groups
reloadDicts()
print("AMOUNT IS {}".format(amount))
importlib.reload(gc)
antenas = []
antenas = util.staticCreateRRHs(amount)
util.setExperiment(antenas, gc.fog_amount)
#for i in antenas:
#	print(i.rrhs_matrix)
ilp = gc.ILP(antenas, range(len(antenas)), gc.nodes, gc.lambdas)
ilp.mdl.add_constraints(ilp.mdl.sum(ilp.x[i,j,w] for i in ilp.rrhs ) <= 1 for j in ilp.nodes for w in ilp.lambdas)
s = ilp.run()
sol = ilp.return_solution_values()
ilp.updateValues(sol)
power_consumption['rrha'].append(util.getPowerConsumption())
execution_time['rrha'].append(s.solve_details.time)
average_delay['rrha'].append(util.overallDelay(sol))
genLogs("3X10")

amount = 10
#CA executions - NEED TO ADDTHE COINSTRAINT TO AVOID VPON ON THE MODEL AND CHANGE THE RRH BAND TO THE BAND OF THE ENTIRE AGGREGATION GROUP
#main loop
#10 aggregation groups
reloadDicts()
print("AMOUNT IS {}".format(amount))
importlib.reload(gc)
gc.RRHband = 3* gc.RRHband
gc.cpri_rate = 3* gc.cpri_rate
antenas = []
antenas = util.staticCreateRRHs(amount)
util.setExperiment(antenas, gc.fog_amount)
#for i in antenas:
#	print(i.rrhs_matrix)
ilp = gc.ILP(antenas, range(len(antenas)), gc.nodes, gc.lambdas)
ilp.mdl.add_constraints(ilp.mdl.sum(ilp.x[i,j,w] for i in ilp.rrhs ) <= 1 for j in ilp.nodes for w in ilp.lambdas)
s = ilp.run()
sol = ilp.return_solution_values()
ilp.updateValues(sol)
power_consumption['ca'].append(util.getPowerConsumption())
execution_time['ca'].append(s.solve_details.time)
average_delay['ca'].append(util.overallDelay(sol))
genLogs("3X10")

############################################### 15 Aggregation groups 
#initial amount of rrhs
amount = 45
#VPONs executions
#main loop
#15 aggregation groups
reloadDicts()
print("AMOUNT IS {}".format(amount))
importlib.reload(gc)
antenas = []
antenas = util.staticCreateRRHs(amount)
util.setExperiment(antenas, gc.fog_amount)
#for i in antenas:
#	print(i.rrhs_matrix)
ilp = gc.ILP(antenas, range(len(antenas)), gc.nodes, gc.lambdas)
s = ilp.run()
sol = ilp.return_solution_values()
ilp.updateValues(sol)
power_consumption['vpon'].append(util.getPowerConsumption())
execution_time['vpon'].append(s.solve_details.time)
average_delay['vpon'].append(util.overallDelay(sol))
genLogs("3X15")

amount = 45
#RRHA executions - NEED TO ADD THE CONSTRAINT TO AVOID VPON ON THE MODEL
#main loop
#15 aggregation groups
reloadDicts()
print("AMOUNT IS {}".format(amount))
importlib.reload(gc)
antenas = []
antenas = util.staticCreateRRHs(amount)
util.setExperiment(antenas, gc.fog_amount)
#for i in antenas:
#	print(i.rrhs_matrix)
ilp = gc.ILP(antenas, range(len(antenas)), gc.nodes, gc.lambdas)
ilp.mdl.add_constraints(ilp.mdl.sum(ilp.x[i,j,w] for i in ilp.rrhs ) <= 1 for j in ilp.nodes for w in ilp.lambdas)
s = ilp.run()
sol = ilp.return_solution_values()
ilp.updateValues(sol)
power_consumption['rrha'].append(util.getPowerConsumption())
execution_time['rrha'].append(s.solve_details.time)
average_delay['rrha'].append(util.overallDelay(sol))
genLogs("3X15")

amount = 15
#CA executions - NEED TO ADDTHE COINSTRAINT TO AVOID VPON ON THE MODEL AND CHANGE THE RRH BAND TO THE BAND OF THE ENTIRE AGGREGATION GROUP
#main loop
#15 aggregation groups
reloadDicts()
print("AMOUNT IS {}".format(amount))
importlib.reload(gc)
gc.RRHband = 3* gc.RRHband
gc.cpri_rate = 3* gc.cpri_rate
antenas = []
antenas = util.staticCreateRRHs(amount)
util.setExperiment(antenas, gc.fog_amount)
#for i in antenas:
#	print(i.rrhs_matrix)
ilp = gc.ILP(antenas, range(len(antenas)), gc.nodes, gc.lambdas)
ilp.mdl.add_constraints(ilp.mdl.sum(ilp.x[i,j,w] for i in ilp.rrhs ) <= 1 for j in ilp.nodes for w in ilp.lambdas)
s = ilp.run()
sol = ilp.return_solution_values()
ilp.updateValues(sol)
power_consumption['ca'].append(util.getPowerConsumption())
execution_time['ca'].append(s.solve_details.time)
average_delay['ca'].append(util.overallDelay(sol))
genLogs("3X15")

#################################################---4 RRHs per aggregation groups
############################################### 5 Aggregation groups 
#initial amount of rrhs
amount = 20
#VPONs executions
#main loop
#5 aggregation groups
reloadDicts()
print("AMOUNT IS {}".format(amount))
importlib.reload(gc)
antenas = []
antenas = util.staticCreateRRHs(amount)
util.setExperiment(antenas, gc.fog_amount)
#for i in antenas:
#	print(i.rrhs_matrix)
ilp = gc.ILP(antenas, range(len(antenas)), gc.nodes, gc.lambdas)
s = ilp.run()
sol = ilp.return_solution_values()
ilp.updateValues(sol)
power_consumption['vpon'].append(util.getPowerConsumption())
execution_time['vpon'].append(s.solve_details.time)
average_delay['vpon'].append(util.overallDelay(sol))
genLogs("4X5")

amount = 20
#RRHA executions - NEED TO ADD THE CONSTRAINT TO AVOID VPON ON THE MODEL
#main loop
#5 aggregation groups
reloadDicts()
print("AMOUNT IS {}".format(amount))
importlib.reload(gc)
antenas = []
antenas = util.staticCreateRRHs(amount)
util.setExperiment(antenas, gc.fog_amount)
#for i in antenas:
#	print(i.rrhs_matrix)
ilp = gc.ILP(antenas, range(len(antenas)), gc.nodes, gc.lambdas)
ilp.mdl.add_constraints(ilp.mdl.sum(ilp.x[i,j,w] for i in ilp.rrhs ) <= 1 for j in ilp.nodes for w in ilp.lambdas)
s = ilp.run()
sol = ilp.return_solution_values()
ilp.updateValues(sol)
power_consumption['rrha'].append(util.getPowerConsumption())
execution_time['rrha'].append(s.solve_details.time)
average_delay['rrha'].append(util.overallDelay(sol))
genLogs("4X5")

amount = 5
#CA executions - NEED TO ADDTHE COINSTRAINT TO AVOID VPON ON THE MODEL AND CHANGE THE RRH BAND TO THE BAND OF THE ENTIRE AGGREGATION GROUP
#main loop
#5 aggregation groups
reloadDicts()
print("AMOUNT IS {}".format(amount))
importlib.reload(gc)
gc.RRHband = 4 * gc.RRHband
gc.cpri_rate = 4* gc.cpri_rate
antenas = []
antenas = util.staticCreateRRHs(amount)
util.setExperiment(antenas, gc.fog_amount)
#for i in antenas:
#	print(i.rrhs_matrix)
ilp = gc.ILP(antenas, range(len(antenas)), gc.nodes, gc.lambdas)
ilp.mdl.add_constraints(ilp.mdl.sum(ilp.x[i,j,w] for i in ilp.rrhs ) <= 1 for j in ilp.nodes for w in ilp.lambdas)
s = ilp.run()
sol = ilp.return_solution_values()
ilp.updateValues(sol)
power_consumption['ca'].append(util.getPowerConsumption())
execution_time['ca'].append(s.solve_details.time)
average_delay['ca'].append(util.overallDelay(sol))
genLogs("4X5")

############################################### 10 Aggregation groups 
#initial amount of rrhs
amount = 40
#VPONs executions
#main loop
#10 aggregation groups
reloadDicts()
print("AMOUNT IS {}".format(amount))
importlib.reload(gc)
antenas = []
antenas = util.staticCreateRRHs(amount)
util.setExperiment(antenas, gc.fog_amount)
#for i in antenas:
#	print(i.rrhs_matrix)
ilp = gc.ILP(antenas, range(len(antenas)), gc.nodes, gc.lambdas)
s = ilp.run()
sol = ilp.return_solution_values()
ilp.updateValues(sol)
power_consumption['vpon'].append(util.getPowerConsumption())
execution_time['vpon'].append(s.solve_details.time)
average_delay['vpon'].append(util.overallDelay(sol))
genLogs("4X10")

amount = 40
#RRHA executions - NEED TO ADD THE CONSTRAINT TO AVOID VPON ON THE MODEL
#main loop
#10 aggregation groups
reloadDicts()
print("AMOUNT IS {}".format(amount))
importlib.reload(gc)
antenas = []
antenas = util.staticCreateRRHs(amount)
util.setExperiment(antenas, gc.fog_amount)
#for i in antenas:
#	print(i.rrhs_matrix)
ilp = gc.ILP(antenas, range(len(antenas)), gc.nodes, gc.lambdas)
ilp.mdl.add_constraints(ilp.mdl.sum(ilp.x[i,j,w] for i in ilp.rrhs ) <= 1 for j in ilp.nodes for w in ilp.lambdas)
s = ilp.run()
sol = ilp.return_solution_values()
ilp.updateValues(sol)
power_consumption['rrha'].append(util.getPowerConsumption())
execution_time['rrha'].append(s.solve_details.time)
average_delay['rrha'].append(util.overallDelay(sol))
genLogs("4X10")

amount = 10
#CA executions - NEED TO ADDTHE COINSTRAINT TO AVOID VPON ON THE MODEL AND CHANGE THE RRH BAND TO THE BAND OF THE ENTIRE AGGREGATION GROUP
#main loop
#10 aggregation groups
reloadDicts()
print("AMOUNT IS {}".format(amount))
importlib.reload(gc)
gc.RRHband = 4* gc.RRHband
gc.cpri_rate = 4* gc.cpri_rate
antenas = []
antenas = util.staticCreateRRHs(amount)
util.setExperiment(antenas, gc.fog_amount)
#for i in antenas:
#	print(i.rrhs_matrix)
ilp = gc.ILP(antenas, range(len(antenas)), gc.nodes, gc.lambdas)
ilp.mdl.add_constraints(ilp.mdl.sum(ilp.x[i,j,w] for i in ilp.rrhs ) <= 1 for j in ilp.nodes for w in ilp.lambdas)
s = ilp.run()
sol = ilp.return_solution_values()
ilp.updateValues(sol)
power_consumption['ca'].append(util.getPowerConsumption())
execution_time['ca'].append(s.solve_details.time)
average_delay['ca'].append(util.overallDelay(sol))
genLogs("4X10")

############################################### 15 Aggregation groups 
#initial amount of rrhs
amount = 60
#VPONs executions
#main loop
#15 aggregation groups
reloadDicts()
print("AMOUNT IS {}".format(amount))
importlib.reload(gc)
antenas = []
antenas = util.staticCreateRRHs(amount)
util.setExperiment(antenas, gc.fog_amount)
#for i in antenas:
#	print(i.rrhs_matrix)
ilp = gc.ILP(antenas, range(len(antenas)), gc.nodes, gc.lambdas)
s = ilp.run()
sol = ilp.return_solution_values()
ilp.updateValues(sol)
power_consumption['vpon'].append(util.getPowerConsumption())
execution_time['vpon'].append(s.solve_details.time)
average_delay['vpon'].append(util.overallDelay(sol))
genLogs("4X15")

amount = 60
#RRHA executions - NEED TO ADD THE CONSTRAINT TO AVOID VPON ON THE MODEL
#main loop
#15 aggregation groups
reloadDicts()
print("AMOUNT IS {}".format(amount))
importlib.reload(gc)
antenas = []
antenas = util.staticCreateRRHs(amount)
util.setExperiment(antenas, gc.fog_amount)
#for i in antenas:
#	print(i.rrhs_matrix)
ilp = gc.ILP(antenas, range(len(antenas)), gc.nodes, gc.lambdas)
ilp.mdl.add_constraints(ilp.mdl.sum(ilp.x[i,j,w] for i in ilp.rrhs ) <= 1 for j in ilp.nodes for w in ilp.lambdas)
s = ilp.run()
sol = ilp.return_solution_values()
ilp.updateValues(sol)
power_consumption['rrha'].append(util.getPowerConsumption())
execution_time['rrha'].append(s.solve_details.time)
average_delay['rrha'].append(util.overallDelay(sol))
genLogs("4X15")

amount = 15
#CA executions - NEED TO ADDTHE COINSTRAINT TO AVOID VPON ON THE MODEL AND CHANGE THE RRH BAND TO THE BAND OF THE ENTIRE AGGREGATION GROUP
#main loop
#15 aggregation groups
reloadDicts()
print("AMOUNT IS {}".format(amount))
importlib.reload(gc)
gc.RRHband = 4 * gc.RRHband
gc.cpri_rate = 4* gc.cpri_rate
antenas = []
antenas = util.staticCreateRRHs(amount)
util.setExperiment(antenas, gc.fog_amount)
#for i in antenas:
#	print(i.rrhs_matrix)
ilp = gc.ILP(antenas, range(len(antenas)), gc.nodes, gc.lambdas)
ilp.mdl.add_constraints(ilp.mdl.sum(ilp.x[i,j,w] for i in ilp.rrhs ) <= 1 for j in ilp.nodes for w in ilp.lambdas)
s = ilp.run()
sol = ilp.return_solution_values()
ilp.updateValues(sol)
power_consumption['ca'].append(util.getPowerConsumption())
execution_time['ca'].append(s.solve_details.time)
average_delay['ca'].append(util.overallDelay(sol))
genLogs("4X15")

