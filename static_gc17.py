import time
import importlib
import gc17ILP as gc

def genLogs():
	#power consumption
	with open('/home/tinini/Área de Trabalho/iccSim/CFRAN-Simulator/ilp_static/logs/power_consumption{}.txt'.format(amount-5),'a') as filehandle:  
	    filehandle.write("{}\n\n".format(i))
	    filehandle.writelines("%s\n" % p for p in power_consumption)
	    filehandle.write("\n")
	    #filehandle.write("\n")
	with open('/home/tinini/Área de Trabalho/iccSim/CFRAN-Simulator/ilp_static/logs/execution_time{}.txt'.format(amount-5),'a') as filehandle:  
	    filehandle.write("{}\n\n".format(i))
	    filehandle.writelines("%s\n" % p for p in execution_time)
	    filehandle.write("\n")
	    #filehandle.write("\n")

#logging variables
power_consumption = []
execution_time = []
average_delay = []

#util function
util = gc.Util()
#initial amount of rrhs
amount = 5

#main loop
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
	amount += 5
genLogs()