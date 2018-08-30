import time
import importlib
import gc17ILP as gc

def genLogs():
	#power consumption
	with open('/home/tinini/Área de Trabalho/Simulador/CFRAN-Simulator/ilp_static/logs/power_consumption{}.txt'.format(amount-5),'a') as filehandle:  
	    filehandle.write("{}\n\n".format(i))
	    filehandle.writelines("%s\n" % p for p in power_consumption)
	    filehandle.write("\n")
	    #filehandle.write("\n")
	with open('/home/tinini/Área de Trabalho/Simulador/CFRAN-Simulator/ilp_static/logs/execution_time{}.txt'.format(amount-5),'a') as filehandle:  
	    filehandle.write("{}\n\n".format(i))
	    filehandle.writelines("%s\n" % p for p in execution_time)
	    filehandle.write("\n")
	    #filehandle.write("\n")
	with open('/home/tinini/Área de Trabalho/Simulador/CFRAN-Simulator/ilp_static/logs/minimum_average_delay{}.txt'.format(amount-5),'a') as filehandle:  
	    filehandle.write("{}\n\n".format(i))
	    filehandle.writelines("%s\n" % p for p in average_delay)
	    filehandle.write("\n")
	    #filehandle.write("\n")

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

#util function
util = gc.Util()

#################################################---3RRHs per aggregation groups
#initial amount of rrhs
amount = 3
#VPONs executions
#main loop
#5 aggregation groups
for i in range(5):
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
	amount += 5
genLogs()

amount = 3
#RRHA executions - NEED TO ADD THE CONSTRAINT TO AVOID VPON ON THE MODEL
#main loop
#10 aggregation groups
for i in range(10):
	print("AMOUNT IS {}".format(amount))
	importlib.reload(gc)
	antenas = []
	antenas = util.staticCreateRRHs(amount)
	util.setExperiment(antenas, gc.fog_amount)
	#for i in antenas:
	#	print(i.rrhs_matrix)
	ilp = gc.ILP(antenas, range(len(antenas)), gc.nodes, gc.lambdas)
	ilp.addNewConstraint(self.mdl.sum(self.x[i,j,w] for i in self.rrhs ) <= 1 for j in self.nodes for w in self.lambdas)
	s = ilp.run()
	sol = ilp.return_solution_values()
	ilp.updateValues(sol)
	power_consumption['rrha'].append(util.getPowerConsumption())
	execution_time['rrha'].append(s.solve_details.time)
	average_delay['rrha'].append(util.overallDelay(sol))
	amount += 5
genLogs()

amount = 3
#CA executions - NEED TO ADDTHE COINSTRAINT TO AVOID VPON ON THE MODEL AND CHANGE THE RRH BAND TO THE BAND OF THE ENTIRE AGGREGATION GROUP
#main loop
#15 aggregation groups
for i in range(15):
	print("AMOUNT IS {}".format(amount))
	importlib.reload(gc)
	gc.RRHBand = amount * RRHBand
	antenas = []
	antenas = util.staticCreateRRHs(amount)
	util.setExperiment(antenas, gc.fog_amount)
	#for i in antenas:
	#	print(i.rrhs_matrix)
	ilp = gc.ILP(antenas, range(len(antenas)), gc.nodes, gc.lambdas)
	ilp.addNewConstraint(self.mdl.sum(self.x[i,j,w] for i in self.rrhs ) <= 1 for j in self.nodes for w in self.lambdas)
	s = ilp.run()
	sol = ilp.return_solution_values()
	ilp.updateValues(sol)
	power_consumption['ca'].append(util.getPowerConsumption())
	execution_time['ca'].append(s.solve_details.time)
	average_delay['ca'].append(util.overallDelay(sol))
	amount += 5
genLogs()