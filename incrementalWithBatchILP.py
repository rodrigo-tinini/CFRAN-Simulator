import simpy
import functools
import random as np
import time
from enum import Enum
import numpy
from scipy.stats import norm
import matplotlib.pyplot as plt
import batch_teste as lp
import pureBatchILP as plp
import copy


inc_block = 0
batch_block = 0
count = 0
#timestamp to change the load
change_time = 3600
#the next time
next_time = 3600
#the actual hout time stamp
actual_stamp = 0.0
#inter arrival rate of the users requests
arrival_rate = 3600
#service time of a request
service_time = lambda x: np.uniform(0,100)
#total generated requests per timestamp
total_period_requests = 0
#to generate the traffic load of each timestamp
loads = []
actives = []
#number of timestamps of load changing
stamps = 24
hours_range = range(1, stamps+1)
for i in range(stamps):
	x = norm.pdf(i, 12, 2)
	x *= 50
	#x= round(x,4)
	#if x != 0:
	#	loads.append(x)
	loads.append(x)
#distribution for arrival of packets
#first arrival rate of the simulation - to initiate the simulation
arrival_rate = loads[0]/change_time
distribution = lambda x: np.expovariate(arrival_rate)
loads.reverse()
#print(loads)
stamps = len(loads)
#record the requests arrived at each stamp
traffics = []
#amount of rrhs
rrhs_amount = 100
#list of rrhs of the network
rrhs = []
#amount of processing nodes
nodes_amount = 10
#list of processing nodes
nodes = []
rrh_nodes = range(0,10)
#capacity of each rrh
rrh_capacity = 5000
#keeps the non allocated requests
no_allocated = []
total_aloc = 0
total_nonaloc = 0
lambdas = range(0,10)
switchBandwidth = [10000.0,10000.0,10000.0,10000.0,10000.0,10000.0,10000.0,10000.0,10000.0,10000.0]
wavelength_capacity = [10000.0, 10000.0,10000.0,10000.0,10000.0,10000.0,10000.0,10000.0,10000.0,10000.0]
lc_cost = 20
B = 1000000
op = 0
maximum_load = 100
#to keep the consumption of each allcoated RRH
power_consumption = []
#average of power consumption of each hour of the dary
average_power_consumption = []
#to keep the power consumption of the batch allocation
batch_power_consumption = []
#to jeep the average consumption of each hour of the day for the batch case
batch_average_consumption = []
#counting the blocked RRHs
inc_batch_blocking = 0
incremental_blocking = 0
batch_blocking = 0
total_inc_blocking = []
total_batch_blocking = []
#to count the redirected rrhs
redirected = []
#to count the activated nodes
activated_nodes = []
average_act_nodes = []
b_activated_nodes = []
b_average_act_nodes = []
#to count the activated lambdas
activated_lambdas = []
average_act_lambdas = []
b_activated_lambdas = []
b_average_act_lambdas = []
#to count the activated DUs
activated_dus = []
average_act_dus = []
b_activated_dus = []
b_average_act_dus = []
#to count the activated switches
activated_switchs = []
average_act_switch = []
b_activated_switchs = []
b_average_act_switch = []
#to count the redirected RRHs
redirected_rrhs = []
average_redir_rrhs = []
b_redirected_rrhs = []
b_average_redir_rrhs = []
#count the amount of time the solution took
time_inc = []
avg_time_inc = []
time_b = []
avg_time_b = []
#count the occurrences of cloud and fog nodes
count_cloud = []
count_fog = []
b_count_cloud = []
b_count_fog = []
max_count_cloud = []
average_count_fog = []
b_max_count_cloud = []
b_average_count_fog = []

#variables for the inc_batch scheduling
inc_batch_count_cloud = []
inc_batch_max_count_cloud = [] 
inc_batch_count_fog = []
inc_batch_average_count_fog = []
time_inc_batch = []
avg_time_inc_batch = []
inc_batch_redirected_rrhs = []
inc_batch_average_redir_rrhs = []
inc_batch_power_consumption = []
inc_batch_average_consumption = []
inc_batch_activated_nodes = []
inc_batch_average_act_nodes = []
inc_batch_activated_lambdas = []
inc_batch_average_act_lambdas = []
inc_batch_activated_dus = []
inc_batch_average_act_dus = []
inc_batch_activated_switchs = []
inc_batch_average_act_switch = []
#------------------------------

inc_batch_power_consumption =[]
inc_batch_redirected_rrhs = []
inc_batch_activated_nodes= [] 
inc_batch_activated_lambdas =[]
inc_batch_activated_dus = []
inc_batch_activated_switchs = []

inc_avg_batch_power_consumption =[]
inc_avg_batch_redirected_rrhs = []
inc_avg_batch_activated_nodes= [] 
inc_avg_batch_activated_lambdas =[]
inc_avg_batch_activated_dus = []
inc_avg_batch_activated_switchs = []


incremental_power_consumption = []

incremental_time = []
batch_time = []

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
lambda_cost = [
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
#rrhs = util.createRRHs(100, env, cp, service_time)
batch_count = 0

#batch_rrhs_wait_time
batch_rrhs_wait_time = []
avg_batch_rrhs_wait_time = []

#rrhs inc Batch threshold
load_threshold = 10
count_rrhs = 0


#traffic generator - generates requests considering the distribution
class Traffic_Generator(object):
	def __init__(self, env, distribution, service, cp):
		self.env = env
		self.dist = distribution
		self.service = service
		self.cp = cp
		self.req_count = 0
		self.action = self.env.process(self.run())
		self.load_variation = self.env.process(self.change_load())

	#generation of requests
	def run(self):
		global total_period_requests
		global rrhs
		#global actives
		while True:
			#if total_period_requests <= maximum_load:
			yield self.env.timeout(self.dist(self))
			self.req_count += 1
			#takes the first turned off RRH
			if rrhs:
				r = rrhs.pop()
				#print("Took {} RRHS list is {}".format(r.id, len(rrhs)))
				self.cp.requests.put(r)
				r.updateGenTime(self.env.now)
				r.enabled = True
				total_period_requests +=1
				#np.shuffle(rrhs)
			else:
				pass
				#print("All RRHs are active!")
			#else:
			#	print("No RRHs!")
			#yield self.env.timeout(0.05)

	#changing of load
	def change_load(self):
		while True:
			global traffics
			#global loads
			global arrival_rate
			global total_period_requests
			global next_time
			global power_consumption
			global incremental_power_consumption
			global batch_power_consumption
			global incremental_blocking
			global batch_blocking
			#self.action = self.action = self.env.process(self.run())
			yield self.env.timeout(change_time)
			actual_stamp = self.env.now
			#print("next time {}".format(next_time))
			next_time = actual_stamp + change_time
			traffics.append(total_period_requests)
			arrival_rate = loads.pop()/change_time
			#print("RRHS on {}".format(len(actives)))
			#print("RRHs off {}".format(len(rrhs)))
			total_inc_blocking.append(incremental_blocking)
			total_batch_blocking.append(batch_blocking)
			incremental_blocking = 0
			batch_blocking = 0
			#count averages for the batch case
			if self.cp.type == "inc":
				self.countIncAverages()
				print("Incremental HOUR is {}".format(incremental_power_consumption))
			#count averages for the batch case
			elif self.cp.type == "batch":
				self.countBatchAverages()
			elif self.cp.type == "inc_batch":
				self.countIncBatchAverages()
			elif self.cp.type == "load_inc_batch":
				self.countIncBatchAverages()
			self.action = self.env.process(self.run())
			print("Arrival rate now is {} at {} and was generated {}".format(arrival_rate, self.env.now/3600, total_period_requests))
			total_period_requests = 0

	#count averages consumptions and active resources for any case
	def countAverageResources(self):
		pass


	#count average consumptions and activeresources for incremental with batch case
	def countIncBatchAverages(self):
		global inc_batch_count_cloud
		global inc_batch_max_count_cloud
		global inc_batch_count_fog
		global inc_batch_average_count_fog
		global time_inc_batch
		global avg_time_inc_batch
		global inc_batch_redirected_rrhs
		global inc_batch_average_redir_rrhs
		global inc_batch_power_consumption
		global inc_batch_average_consumption
		global inc_batch_activated_nodes
		global inc_batch_average_act_nodes
		global inc_batch_activated_lambdas
		global inc_batch_average_act_lambdas
		global inc_batch_activated_dus
		global inc_batch_average_act_dus
		global inc_batch_activated_switchs
		global inc_batch_average_act_switch

		if inc_batch_count_cloud:
			inc_batch_max_count_cloud.append(sum((inc_batch_count_cloud)))
			inc_batch_count_cloud = []
		else:
			inc_batch_max_count_cloud.append(0.0)
		#activation of fog nodes
		if inc_batch_count_fog:
			inc_batch_average_count_fog.append(sum((inc_batch_count_fog)))
			inc_batch_count_fog = []
		else:
			inc_batch_average_count_fog.append(0.0)
		#calculates the average time spent for the solution on this hour
		if time_inc_batch:
			avg_time_inc_batch.append((numpy.mean(time_inc_batch)))
			time_inc_batch = []
		else:
			avg_time_inc_batch.append(0.0)
		#calculates the averages of power consumption and active resources
		#calculates the number of redirected RRHs
		if inc_batch_redirected_rrhs:
			inc_batch_average_redir_rrhs.append(sum((inc_batch_redirected_rrhs)))
			inc_batch_redirected_rrhs = []
		else:
			inc_batch_average_redir_rrhs.append(0)
		#power consumption for the incremental case
		if inc_batch_power_consumption:
			inc_batch_average_consumption.append(round(numpy.mean(inc_batch_power_consumption),4))
			inc_batch_power_consumption = []
		else:
			inc_batch_average_consumption.append(0.0)
		#activated nodes for the incremental case
		if inc_batch_activated_nodes:
			inc_batch_average_act_nodes.append(numpy.mean(inc_batch_activated_nodes))
			inc_batch_activated_nodes = []
		else:
			inc_batch_average_act_nodes.append(0)
		#activated lambdas for the incremental case
		if inc_batch_activated_lambdas:
			inc_batch_average_act_lambdas.append(numpy.mean(inc_batch_activated_lambdas))
			inc_batch_activated_lambdas = []
		else:
			inc_batch_average_act_lambdas.append(0)
		#activated DUs for the incremental case
		if inc_batch_activated_dus:
			inc_batch_average_act_dus.append(numpy.mean(inc_batch_activated_dus))
			inc_batch_activated_dus = []
		else:
			inc_batch_average_act_dus.append(0)
		#activated switches for the incremental case
		if inc_batch_activated_switchs:
			inc_batch_average_act_switch.append(numpy.mean(inc_batch_activated_switchs))
			inc_batch_activated_switchs = []
		else:
			inc_batch_average_act_switch.append(0)

	#count average consumptions and activeresources for incremental with batch case
	def countLoadIncBatchAverages(self):
		pass


	#count average consumptions and active resources for the incremental case
	def countIncAverages(self):
		global incremental_power_consumption
		global activated_nodes
		global activated_dus
		global activated_lambdas
		global activated_switchs
		global redirected_rrhs
		global time_inc
		global count_cloud
		global count_fog
		if count_cloud:
			max_count_cloud.append(sum((count_cloud)))
			count_cloud = []
		else:
			max_count_cloud.append(0.0)
		#activation of fog nodes
		if count_fog:
			average_count_fog.append(sum((count_fog)))
			count_fog = []
		else:
			average_count_fog.append(0.0)
		#calculates the average time spent for the solution on this hour
		if time_inc:
			avg_time_inc.append((numpy.mean(time_inc)))
			time_inc = []
		else:
			avg_time_inc.append(0.0)
		#calculates the averages of power consumption and active resources
		#calculates the number of redirected RRHs
		if redirected_rrhs:
			average_redir_rrhs.append(sum((redirected_rrhs)))
			redirected_rrhs = []
		else:
			average_redir_rrhs.append(0)
		#power consumption for the incremental case
		if incremental_power_consumption:
			print(incremental_power_consumption)
			average_power_consumption.append(round(numpy.mean(incremental_power_consumption),4))
			incremental_power_consumption = []
		else:
			average_power_consumption.append(0.0)
		#activated nodes for the incremental case
		if activated_nodes:
			average_act_nodes.append(numpy.mean(activated_nodes))
			activated_nodes = []
		else:
			average_act_nodes.append(0)
		#activated lambdas for the incremental case
		if activated_lambdas:
			average_act_lambdas.append(numpy.mean(activated_lambdas))
			activated_lambdas = []
		else:
			average_act_lambdas.append(0)
		#activated DUs for the incremental case
		if activated_dus:
			average_act_dus.append(numpy.mean(activated_dus))
			activated_dus = []
		else:
			average_act_dus.append(0)
		#activated switches for the incremental case
		if activated_switchs:
			average_act_switch.append(numpy.mean(activated_switchs))
			activated_switchs = []
		else:
			average_act_switch.append(0)


	#count average consumptions and active resources for the incremental case
	def countBatchAverages(self):
		global batch_power_consumption
		global b_activated_nodes
		global b_activated_dus
		global b_activated_lambdas
		global b_activated_switchs
		global b_redirected_rrhs
		global time_b
		global b_count_cloud
		global b_count_fog
		global batch_rrhs_wait_time	
		if batch_rrhs_wait_time:
			avg_batch_rrhs_wait_time.append(numpy.mean(batch_rrhs_wait_time))
			batch_rrhs_wait_time = []
		else:
			avg_batch_rrhs_wait_time.append(0.0)
		if b_count_cloud:
			b_max_count_cloud.append(sum((b_count_cloud)))
			b_count_cloud = []
		else:
			b_max_count_cloud.append(0.0)
		if b_count_fog:
			b_average_count_fog.append(sum((b_count_fog)))
			b_count_fog = []
		else:
			b_average_count_fog.append(0.0)
		#calculates the average time spent for the solution on this hour
		if time_b:
			avg_time_b.append((numpy.mean(time_b)))
			time_b = []
		else:
			avg_time_b.append(0.0)
		#calculates the averages of power consumption and active resources
		#calculates the number of redirected RRHs
		if b_redirected_rrhs:
			b_average_redir_rrhs.append(sum((b_redirected_rrhs)))
			b_redirected_rrhs = []
		else:
			b_average_redir_rrhs.append(0)
		#power consumption for the incremental case
		#power consumption for the batch case
		if batch_power_consumption:
			batch_average_consumption.append(round(numpy.mean(batch_power_consumption), 4))
			batch_power_consumption = []
		else:
			batch_average_consumption.append(0.0)
		#activated nodes for the incremental case
		if b_activated_nodes:
			b_average_act_nodes.append(numpy.mean(b_activated_nodes))
			b_activated_nodes = []
		else:
			b_average_act_nodes.append(0)
		#activated lambdas for the incremental case
		if b_activated_lambdas:
			b_average_act_lambdas.append(numpy.mean(b_activated_lambdas))
			b_activated_lambdas = []
		else:
			b_average_act_lambdas.append(0)
		#activated DUs for the incremental case
		if b_activated_dus:
			b_average_act_dus.append(numpy.mean(b_activated_dus))
			b_activated_dus = []
		else:
			b_average_act_dus.append(0)
		#activated switches for the incremental case
		if b_activated_switchs:
			b_average_act_switch.append(numpy.mean(b_activated_switchs))
			b_activated_switchs = []
		else:
			b_average_act_switch.append(0)



#control plane that controls the allocations and deallocations
class Control_Plane(object):
	def __init__(self, env, util, type):
		self.env = env
		self.requests = simpy.Store(self.env)
		self.departs = simpy.Store(self.env)
		self.action = self.env.process(self.run())
		self.deallocation = self.env.process(self.depart_request())
		#self.audit = self.env.process(self.checkNetwork())
		self.type = type
		self.ilp = None
		self.util = util
		self.ilpBatch = None

	#take requests and tries to allocate on a RRH
	def run(self):
		global total_aloc
		global total_nonaloc
		global no_allocated
		global count
		global actives
		global incremental_blocking
		global batch_blocking
		global inc_block
		global batch_block
		global count_rrhs
		while True:
			#print(count_rrhs)
			r = yield self.requests.get()
			antenas = []
			antenas.append(r)
			if self.type == "inc":
				self.incSched(r, antenas, plp, incremental_power_consumption, redirected_rrhs, activated_nodes, activated_lambdas, activated_dus, activated_switchs)
			elif self.type == "batch":
				self.batchSched(r, plp, batch_power_consumption,b_redirected_rrhs,b_activated_nodes, b_activated_lambdas, b_activated_dus, b_activated_switchs)
			elif self.type == "inc_batch":
				self.incrementalBatchSched(r,antenas, plp)
			elif self.type == "load_inc_batch":
				self.loadIncBatchSched(r, antenas, plp)

	#incremental scheduling
	def incSched(self, r, antenas, ilp_module, incremental_power_consumption, redirected_rrhs, 
		activated_nodes, activated_lambdas, activated_dus, activated_switchs):
		count_nodes = 0
		count_lambdas = 0
		count_dus = 0
		count_switches = 0
		#print("Calling Incremental")
		block = 0
		self.ilp = plp.ILP(antenas, range(len(antenas)), ilp_module.nodes, ilp_module.lambdas)
		solution = self.ilp.run()
		if solution == None:
			rrhs.append(r)
			np.shuffle(rrhs)
			antenas = []
			print("Incremental Blocking")
			block += 1
			incremental_power_consumption.append(self.util.getPowerConsumption(ilp_module))
		else:
			solution_values = self.ilp.return_solution_values()
			self.ilp.updateValues(solution_values)
			time_inc.append(solution.solve_details.time)
			r.updateWaitTime(self.env.now)
			for i in antenas:
				self.env.process(i.run())
				actives.append(i)
				#print("ACTIVE IS {}".format(len(actives)))
				antenas.remove(i)
				incremental_power_consumption.append(self.util.getPowerConsumption(ilp_module))
			#count the activeresources
			if redirected_rrhs:
				redirected_rrhs.append(sum((redirected_rrhs[-1], len(solution_values.var_k))))
			else:
				redirected_rrhs.append(len(solution_values.var_k))
			for i in ilp_module.nodeState:
				if i == 1:
					count_nodes += 1
			activated_nodes.append(count_nodes)
			for i in ilp_module.lambda_state:
				if i == 1:
					count_lambdas += 1
			activated_lambdas.append(count_lambdas)
			for i in ilp_module.du_state:
				for j in i:
					if j == 1:
						count_dus += 1
			activated_dus.append(count_dus)
			for i in ilp_module.switch_state:
				if i == 1:
					count_switches += 1
			activated_switchs.append(count_switches)
			return solution

	#batch scheduling
	def batchSched(self, r, ilp_module, batch_power_consumption,b_redirected_rrhs,
		b_activated_nodes, b_activated_lambdas, b_activated_dus, b_activated_switchs):
		count_nodes = 0
		count_lambdas = 0
		count_dus = 0
		count_switches = 0
		block = 0
		#print("Calling Batch")
		batch_list = copy.copy(actives)
		batch_list.append(r)
		actives.append(r)
		self.ilp = plp.ILP(actives, range(len(actives)), ilp_module.nodes, ilp_module.lambdas)
		self.ilp.resetValues()
		solution = self.ilp.run()
		if solution == None:
			rrhs.append(r)
			actives.remove(r)
			np.shuffle(rrhs)
			print("Batch Blocking")
			print("Cant Schedule {} RRHs".format(len(actives)))
			batch_power_consumption.append(self.util.getPowerConsumption(ilp_module))
			block += 1
		else:
			solution_values = self.ilp.return_solution_values()
			self.ilp.updateValues(solution_values)
			batch_time.append(solution.solve_details.time)
			r.updateWaitTime(self.env.now+solution.solve_details.time)
			#print("Gen is {} ".format(r.generationTime))
			#print("NOW {} ".format(r.waitingTime))
			self.env.process(r.run())
			batch_power_consumption.append(self.util.getPowerConsumption(ilp_module))
			batch_rrhs_wait_time.append(self.averageWaitingTime(actives))
			if b_redirected_rrhs:
				b_redirected_rrhs.append(sum((b_redirected_rrhs[-1], len(solution_values.var_k))))
			else:
				b_redirected_rrhs.append(len(solution_values.var_k))
			#counts the current activated nodes, lambdas, DUs and switches
			for i in ilp_module.nodeState:
				if i == 1:
					count_nodes += 1
			b_activated_nodes.append(count_nodes)
			for i in ilp_module.lambda_state:
				if i == 1:
					count_lambdas += 1
			b_activated_lambdas.append(count_lambdas)
			for i in ilp_module.du_state:
				for j in i:
					if j == 1:
						count_dus += 1
			b_activated_dus.append(count_dus)
			for i in ilp_module.switch_state:
				if i == 1:
					count_switches += 1
			b_activated_switchs.append(count_switches)
			return solution

	#calculates the average waiting time of RRHs to be scheduled
	def averageWaitingTime(self, antenas):
		avg = []
		for r in antenas:
			avg.append(r.waitingTime)
		if sum(avg) > 0:
			return numpy.mean(avg)
		else:
			return 0


	#jointly incremental and batch scheduling
	#this method calls the batch scheduling every time that a certain amount of RRHs arrived on the network
	#after the batch is called, this threshold of RRHs is set to zero, so the process begins and the batch is called
	#every after "x" RRHs
	def incrementalBatchSched(self, r, antenas, ilp_module):
		global count_rrhs
		#verifies if is it time to call the batch scheduling
		if count_rrhs == load_threshold:
			print("Entering batch")
			#calls the batch scheduling
			s = self.batchSched(r, ilp_module,inc_batch_power_consumption,inc_batch_redirected_rrhs,inc_batch_activated_nodes, 
				inc_batch_activated_lambdas,inc_batch_activated_dus,inc_batch_activated_switchs)
			count_rrhs = 0
		else:
			print("entrou inc")
			#print(count_rrhs)
			s = self.incSched(r, antenas, ilp_module,inc_batch_power_consumption,inc_batch_redirected_rrhs,inc_batch_activated_nodes, 
				inc_batch_activated_lambdas,inc_batch_activated_dus,inc_batch_activated_switchs)
			count_rrhs += 1

	#this method performs the incremental scheduling until a certain load of RRHs is activated on the network
	#and above that load, only the batch scheduling is performed
	#the incremental scheduling is only performed again when the load is under certain threshold
	def loadIncBatchSched(self, r, antenas, ilp_module):
		#verifies if is it time to call the batch scheduling
		if len(actives) >= load_threshold:
			#calls the batch scheduling
			s = self.batchSched(r, ilp_module,inc_batch_power_consumption,inc_batch_redirected_rrhs,inc_batch_activated_nodes, 
				inc_batch_activated_lambdas,inc_batch_activated_dus,inc_batch_activated_switchs)
		else:
			s = self.incSched(r, antenas, ilp_module,inc_batch_power_consumption,inc_batch_redirected_rrhs,inc_batch_activated_nodes, 
				inc_batch_activated_lambdas,inc_batch_activated_dus,inc_batch_activated_switchs)





	#starts the deallocation of a request
	def depart_request(self):
		global rrhs
		#global actives
		while True:
			r = yield self.departs.get()
			self.ilp.deallocateRRH(r)
			#self.ilp.resetValues()
			r.var_x = None
			r.var_u = None
			r.enabled = False
			rrhs.append(r)
			np.shuffle(rrhs)
			actives.remove(r)
				

	#to capture the state of the network at a given rate - will be used to take the metrics at a given (constant) moment
	def checkNetwork(self):
		while True:
			yield self.env.timeout(1800)
			print("Taking network status at {}".format(self.env.now))
			print("Total generated requests is {}".format(total_period_requests))
"""
#RRH that allocates the user requests according to its availability
#each rrh is connected to both a cloud node and a fog node
#each rrh can connect to a single fog node - a fog node can be connected to multiple rrhs
class RRH(object):
	def __init__(self, env, aId, capacity, control_plane,cloud, fog):
		self.env = env
		self.id = aId
		self.allocated = False
		self.enabled = False
		#processing nodes connected to this rrh
		self.pns = []
		self.cp = cp
		self.action = None

		#executes this request and send it to deallocation after its service time
	def run(self):
		yield self.env.timeout(self.service_time(self))
		#print("Request {} departing".format(self.id))
		self.cp.departs.put(self)
"""

#this class represents a RRH containing its possible processing nodes
class RRH(object):
	def __init__(self, aId, rrhs_matrix, env, service_time, cp):
		self.id = aId
		self.rrhs_matrix = rrhs_matrix
		self.var_x = None
		self.var_u = None
		self.env = env
		self.service_time = service_time
		self.cp = cp
		self.generationTime = 0.0
		self.waitingTime = 0.0

	#updates the generation time
	def updateGenTime(self, gen_time):
		self.generationTime = gen_time

	#updates the waiting time
	def updateWaitTime(self, wait_time):
		self.waitingTime = wait_time - self.generationTime

	def run(self):
		yield self.env.timeout(np.uniform(0, next_time -self.env.now))
		self.cp.departs.put(self)

#Utility class
class Util(object):
	#print all active nodes
	def printActiveNodes(self):
		for i in pns:
			if i.state == 1:
				i.printNode()

	#create a list of RRHs with its own connected processing nodes
	def createRRHs(self, amount,env, service_time, cp):
		rrhs = []
		for i in range(amount):
			r = RRH(i, [1,0,0], env, service_time, cp)
			rrhs.append(r)
		self.setMatrix(rrhs)
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
	def getPowerConsumption(self, ilp):
		netCost = 0.0
		#compute all activated nodes
		for i in range(len(ilp.nodeState)):
			if ilp.nodeState[i] == 1:
				if i == 0:
					netCost += 600.0
				else:
					netCost += 500.0
			#compute activated DUs
			for j in range(len(ilp.du_state[i])):
				if ilp.du_state[i][j] == 1:
					if i == 0:
						netCost += 100.0
					else:
						netCost += 50.0
		#compute lambda and switch costs
		for w in ilp.lambda_state:
			if w == 1:
				netCost += 20.0
		for s in ilp.switch_state:
			if s == 1:
				netCost += 15.0
		return netCost

	#reset the parameters
	def resetParams(self):
		global count, change_time, next_time, actual_stamp, arrival_rate, service_time, total_period_requests, loads, actives, stamps, hours_range, arrival_rate, distribution,traffics
		global power_consumption,average_power_consumption,	batch_power_consumption,batch_average_consumption,incremental_blocking,batch_blocking
		global total_inc_blocking,total_batch_blocking,redirected,activated_nodes,average_act_nodes,b_activated_nodes,b_average_act_nodes
		global activated_lambdas,average_act_lambdas,b_activated_lambdas,b_average_act_lambdas,	activated_dus,average_act_dus,b_activated_dus
		global b_average_act_dus,activated_switchs,	average_act_switch,	b_activated_switchs,b_average_act_switch,redirected_rrhs,average_redir_rrhs
		global b_redirected_rrhs,b_average_redir_rrhs,time_inc,	avg_time_inc,time_b,avg_time_b,count_cloud,	count_fog,b_count_cloud,b_count_fog
		global max_count_cloud,	average_count_fog,b_max_count_cloud,b_average_count_fog,batch_rrhs_wait_time,avg_batch_rrhs_wait_time
		count = 0
		#timestamp to change the load
		change_time = 3600
		#the next time
		next_time = 3600
		#the actual hout time stamp
		actual_stamp = 0.0
		#inter arrival rate of the users requests
		arrival_rate = 3600
		#service time of a request
		service_time = lambda x: np.uniform(0,100)
		#total generated requests per timestamp
		total_period_requests = 0
		#to generate the traffic load of each timestamp
		loads = []
		actives = []
		#number of timestamps of load changing
		stamps = 24
		hours_range = range(1, stamps+1)
		for i in range(stamps):
			x = norm.pdf(i, 12, 2)
			x *= 50
			#x= round(x,4)
			#if x != 0:
			#	loads.append(x)
			loads.append(x)
		#distribution for arrival of packets
		#first arrival rate of the simulation - to initiate the simulation
		arrival_rate = loads[0]/change_time
		distribution = lambda x: np.expovariate(arrival_rate)
		loads.reverse()
		#print(loads)
		stamps = len(loads)
		#record the requests arrived at each stamp
		traffics = []
				#amount of rrhs
		rrhs_amount = 100
		#list of rrhs of the network
		rrhs = []
		#amount of processing nodes
		nodes_amount = 10
		#list of processing nodes
		nodes = []
		rrh_nodes = range(0,10)
		#capacity of each rrh
		rrh_capacity = 5000
		#keeps the non allocated requests
		no_allocated = []
		total_aloc = 0
		total_nonaloc = 0
		lambdas = range(0,10)
		switchBandwidth = [10000.0,10000.0,10000.0,10000.0,10000.0,10000.0,10000.0,10000.0,10000.0,10000.0]
		wavelength_capacity = [10000.0, 10000.0,10000.0,10000.0,10000.0,10000.0,10000.0,10000.0,10000.0,10000.0]
		lc_cost = 20
		B = 1000000
		op = 0
		maximum_load = 100
		#to keep the consumption of each allcoated RRH
		power_consumption = []
		#average of power consumption of each hour of the dary
		average_power_consumption = []
		#to keep the power consumption of the batch allocation
		batch_power_consumption = []
		#to jeep the average consumption of each hour of the day for the batch case
		batch_average_consumption = []
		#counting the blocked RRHs
		#incremental_blocking = 0
		#batch_blocking = 0
		#total_inc_blocking = []
		#total_batch_blocking = []
		#to count the redirected rrhs
		redirected = []
		#to count the activated nodes
		activated_nodes = []
		average_act_nodes = []
		b_activated_nodes = []
		b_average_act_nodes = []
		#to count the activated lambdas
		activated_lambdas = []
		average_act_lambdas = []
		b_activated_lambdas = []
		b_average_act_lambdas = []
		#to count the activated DUs
		activated_dus = []
		average_act_dus = []
		b_activated_dus = []
		b_average_act_dus = []
		#to count the activated switches
		activated_switchs = []
		average_act_switch = []
		b_activated_switchs = []
		b_average_act_switch = []
		#to count the redirected RRHs
		redirected_rrhs = []
		average_redir_rrhs = []
		b_redirected_rrhs = []
		b_average_redir_rrhs = []
		#count the amount of time the solution took
		time_inc = []
		avg_time_inc = []
		time_b = []
		avg_time_b = []
		#count the occurrences of cloud and fog nodes
		count_cloud = []
		count_fog = []
		b_count_cloud = []
		b_count_fog = []
		max_count_cloud = []
		average_count_fog = []
		b_max_count_cloud = []
		b_average_count_fog = []

		#variables for the inc_batch scheduling
		inc_batch_count_cloud = []
		inc_batch_max_count_cloud = [] 
		inc_batch_count_fog = []
		inc_batch_average_count_fog = []
		time_inc_batch = []
		avg_time_inc_batch = []
		inc_batch_redirected_rrhs = []
		inc_batch_average_redir_rrhs = []
		inc_batch_power_consumption = []
		inc_batch_average_consumption = []
		inc_batch_activated_nodes = []
		inc_batch_average_act_nodes = []
		inc_batch_activated_lambdas = []
		inc_batch_average_act_lambdas = []
		inc_batch_activated_dus = []
		inc_batch_average_act_dus = []
		inc_batch_activated_switchs = []
		inc_batch_average_act_switch = []
		#------------------------------

		#inc_batch_power_consumption =[]
		#inc_batch_redirected_rrhs = []
		#inc_batch_activated_nodes= [] 
		#inc_batch_activated_lambdas =[]
		#inc_batch_activated_dus = []
		#inc_batch_activated_switchs = []

		#inc_avg_batch_power_consumption =[]
		#inc_avg_batch_redirected_rrhs = []
		#inc_avg_batch_activated_nodes= [] 
		#inc_avg_batch_activated_lambdas =[]
		#inc_avg_batch_activated_dus = []
		#inc_avg_batch_activated_switchs = []


		incremental_power_consumption = []

		incremental_time = []
		batch_time = []

		batch_rrhs_wait_time = []
		avg_batch_rrhs_wait_time = []

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
		lambda_cost = [
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
		#rrhs = util.createRRHs(100, env, cp, service_time)
		batch_count = 0

	#compute which nodes are active (cloud or fog, and how many of them are active)
	def countNodes(self, ilp):
		count_cloud = 0
		count_fog = 0
		for i in range(len(ilp.nodeState)):
			if ilp.nodeState[i] == 1:
				if i == 0:
					count_cloud += 1
				else:
					count_fog += 1



"""
util = Util()
env = simpy.Environment()
cp = Control_Plane(env, util, "inc")
rrhs = util.createRRHs(10, env, service_time, cp)
np.shuffle(rrhs)
t = Traffic_Generator(env, distribution, service_time, cp)
print("\Begin at "+str(env.now))
env.run(until = 86401)
print("\End at "+str(env.now))


#---------------------------NEW RUN------------------------------------------
util.resetParams()



env = simpy.Environment()
cp = Control_Plane(env, util, "batch")
rrhs = util.createRRHs(10, env, service_time, cp)
np.shuffle(rrhs)
t = Traffic_Generator(env, distribution, service_time, cp)
print("\Begin at "+str(env.now))
env.run(until = 86401)

print("\End at "+str(env.now))



print(average_power_consumption)
print("--------")
print(batch_average_consumption)
min_power = min(min(average_power_consumption), min(batch_average_consumption))
max_power = max(max(average_power_consumption), max(batch_average_consumption))
min_dus = min(min(average_act_dus), min(b_average_act_dus))
max_dus = max(max(average_act_dus), max(b_average_act_dus))
min_switch = min(min(average_act_switch), min(b_average_act_switch))
max_switch = max(max(average_act_switch), max(b_average_act_switch))
min_redirected = min(min(average_redir_rrhs), min(b_average_redir_rrhs))
max_redirected = max(max(average_redir_rrhs), max(b_average_redir_rrhs))
min_time = min(min(avg_time_inc), min(avg_time_b))
max_time = max(max(avg_time_inc), max(avg_time_b))

#print(max_count_cloud)
#print(average_count_fog)
#print(b_max_count_cloud)
#print(b_average_count_fog)
	
#print(avg_time_inc)
#print(average_power_consumption)
print(average_power_consumption)
print(batch_average_consumption)
print("--------")
#print(b_average_act_switch)
#print(b_average_redir_rrhs)
#print(power_consumption)
#print(avg_time_b)

#generate the plots for power consumption
plt.plot(average_power_consumption, label = "Inc with Batch ILP")
plt.plot(batch_average_consumption, label = "Inc ILP")
plt.xticks(numpy.arange(min(hours_range), max(hours_range), 5))
plt.yticks(numpy.arange(min_power, max_power, 500))
plt.ylabel('Power Consumption')
plt.xlabel("Time of the day")
plt.legend()
plt.grid()
plt.savefig('/home/hextinini/Área de Trabalho/plots/power_consumption_{}.png'.format(load_threshold), bbox_inches='tight')
#plt.show()
plt.clf()

#generate the plots for activated lambdas
plt.plot(average_act_lambdas, label = "Inc with Batch ILP")
plt.plot(b_average_act_lambdas, label = "Inc ILP")
plt.xticks(numpy.arange(min(hours_range), max(hours_range), 5))
plt.yticks(numpy.arange(0, 10, 1))
plt.ylabel('Activated Lambdas')
plt.xlabel("Time of the day")
plt.legend()
plt.grid()
plt.savefig('/home/hextinini/Área de Trabalho/plots/activated_lambdas_{}.png'.format(load_threshold), bbox_inches='tight')
plt.clf()

#generate the plots for activated nodes
plt.plot(average_act_nodes, label = "Inc with Batch ILP")
plt.plot(b_average_act_nodes, label = "Inc ILP")
plt.xticks(numpy.arange(min(hours_range), max(hours_range), 5))
plt.yticks(numpy.arange(0, 10, 1))
plt.ylabel('Activated Nodes')
plt.xlabel("Time of the day")
plt.legend()
plt.grid()
plt.savefig('/home/hextinini/Área de Trabalho/plots/activated_nodes_{}.png'.format(load_threshold), bbox_inches='tight')
plt.clf()

#generate the plots for activated DUs
plt.plot(average_act_dus, label = "Inc with Batch ILP")
plt.plot(b_average_act_dus, label = "Inc ILP")
plt.xticks(numpy.arange(min(hours_range), max(hours_range), 5))
plt.yticks(numpy.arange(min_dus, max_dus+5, 5))
plt.ylabel('Activated DUs')
plt.xlabel("Time of the day")
plt.legend()
plt.grid()
plt.savefig('/home/hextinini/Área de Trabalho/plots/activated_DUs{}.png'.format(load_threshold), bbox_inches='tight')
plt.clf()

#generate the plots for activated Switches
plt.plot(average_act_switch, label = "Inc with Batch ILP")
plt.plot(b_average_act_switch, label = "Inc ILP")
plt.xticks(numpy.arange(min(hours_range), max(hours_range), 5))
plt.yticks(numpy.arange(min_switch, max_switch+1, 1))
plt.ylabel('Activated Switches')
plt.xlabel("Time of the day")
plt.legend()
plt.grid()
plt.savefig('/home/hextinini/Área de Trabalho/plots/activated_switches{}.png'.format(load_threshold), bbox_inches='tight')
plt.clf()

#generate the plots for redirected DUs
plt.plot(average_redir_rrhs, label = "Inc with Batch ILP")
plt.plot(b_average_redir_rrhs, label = "Inc ILP")
plt.xticks(numpy.arange(min(hours_range), max(hours_range), 5))
plt.yticks(numpy.arange(min_redirected, max_redirected, 10))
plt.ylabel('Redirected RRHs')
plt.xlabel("Time of the day")
plt.legend()
plt.grid()
plt.savefig('/home/hextinini/Área de Trabalho/plots/redirected_rrhs_{}.png'.format(load_threshold), bbox_inches='tight')
plt.clf()

#generate the plots for solution time
plt.plot(avg_time_inc, label = "Inc with Batch ILP")
plt.plot(avg_time_b, label = "Inc ILP")
plt.xticks(numpy.arange(min(hours_range), max(hours_range), 5))
plt.yticks(numpy.arange(min_time, max_time, 0.001))
plt.ylabel('Solution Time (seconds)')
plt.xlabel("Time of the day")
plt.legend()
plt.grid()
plt.savefig('/home/hextinini/Área de Trabalho/plots/solution_time_{}.png'.format(load_threshold), bbox_inches='tight')
plt.clf()

"""