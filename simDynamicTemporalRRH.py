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
for i in range(stamps):
	x = norm.pdf(i, 12, 4)
	x *= 100
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
incremental_blocking = 0
batch_blocking = 0
total_inc_blocking = []
total_batch_blocking = []

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
			#print("To entrando aqui!!!!")
			#if total_period_requests <= maximum_load:
			yield self.env.timeout(self.dist(self))
			self.req_count += 1
			#takes the first turned off RRH
			if rrhs:
				r = rrhs.pop()
				#print("Took {} RRHS list is {}".format(r.id, len(rrhs)))
				self.cp.requests.put(r)
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
			if power_consumption:
				average_power_consumption.append(round(numpy.mean(power_consumption),4))
				power_consumption = []
			else:
				average_power_consumption.append(0.0)
			self.action = self.action = self.env.process(self.run())
			if batch_power_consumption:
				batch_average_consumption.append(round(numpy.mean(batch_power_consumption), 4))
				batch_power_consumption = []
			else:
				batch_average_consumption.append(0.0)
			print("Arrival rate now is {} at {} and was generated {}".format(arrival_rate, self.env.now/3600, total_period_requests))
			total_period_requests = 0

#control plane that controls the allocations and deallocations
class Control_Plane(object):
	def __init__(self, env, util):
		self.env = env
		self.requests = simpy.Store(self.env)
		self.departs = simpy.Store(self.env)
		self.action = self.env.process(self.run())
		self.deallocation = self.env.process(self.depart_request())
		#self.audit = self.env.process(self.checkNetwork())
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
		#create a list for the batch solution
		batch_list = actives
		while True:
			r = yield self.requests.get()
			#create a list containing the rrhs
			antenas = []
			antenas.append(r)
			#put the rrh on the batch list for the batch scheduling
			batch_list.append(r)
			#print("Allocating request {}".format(r.id))
			#as soon as it gets the request, allocates it into a RRH
			#----------------------CALLS THE ILP-------------------------
			self.ilp = lp.ILP(antenas, range(len(antenas)), lp.nodes, lp.lambdas)
			#print("Calling ILP")
			#calling the incremental ILP
			s = self.ilp.run()
			if s != None:
				#print("Optimal solution is: {}".format(s.objective_value))
				sol = self.ilp.return_solution_values()
				self.ilp.updateValues(sol)
				for i in antenas:
					self.env.process(i.run())
					actives.append(i)
					#print("ACTIVE IS {}".format(len(actives)))
					antenas.pop()
					count += 1
					power_consumption.append(self.util.getPowerConsumption(lp))
					print("SOLVED INC")
					print("inc {}".format(lp.du_processing))
					#print("Cost is {}".format(power_consumption))
				#print("Allocated {}".format(len(rrhs)))
				#print("rrhs on node {}".format(lp.rrhs_on_nodes))
				#print(lp.du_processing)
			else:
				#print("Can't find a solution!! {}".format(len(rrhs)))
				rrhs.append(r)
				antenas.pop()
				incremental_blocking +=1
			#calls the batch ilp
			self.ilpBatch = plp.ILP(batch_list, range(len(batch_list)), plp.nodes, plp.lambdas)
			b_s = self.ilpBatch.run()
			if b_s != None:
				print("SOLVED BATCH")
				#print("Optimal solution is: {}".format(s.objective_value))
				b_sol = self.ilpBatch.return_solution_values()
				self.ilpBatch.updateValues(b_sol)
				batch_power_consumption.append(self.util.getPowerConsumption(plp))
				self.ilpBatch.resetValues()
				print("batch {}".format(lp.du_processing))
			else:
				#print("Cant Batch allocate")
				#print(plp.lambda_node)
				batch_blocking += 1



	#starts the deallocation of a request
	def depart_request(self):
		global rrhs
		#global actives
		while True:
			r = yield self.departs.get()
			self.ilp.deallocateRRH(r)
			r.var_x = None
			r.var_u = None
			rrhs.append(r)
			np.shuffle(rrhs)
			actives.pop()
			#print("Deallocating RRH {}".format(r.id))

	#allocates the RRHs/ONU turned on into a VPON in a processing node
	def allocateRRH(self, rrh):
		ilp = lp.ILP(range(0,1), range(0,2), range(0,10),switchBandwidth, 614.4, wavelength_capacity, lc_cost, B,
		 r.createDUCapacitiesMatrix(), r.createNodeCostsMatrix(), r.createDUCostsMatrix())
		s = ilp.run()
		#print("Optimal allocation is {}".format(s.objective_value))

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
			rrhs_matrix = [1,0,0,0,0,0,0,0,0,0]
			if i < 10:
				rrhs_matrix[1] = 1
				r = RRH(i, rrhs_matrix, env, service_time, cp)
				rrhs.append(r)
			if i >= 10 and i < 20:
				rrhs_matrix[2] = 1
				r = RRH(i, rrhs_matrix, env, service_time, cp)
				rrhs.append(r)
			if i >= 20 and i < 30:
				rrhs_matrix[3] = 1
				r = RRH(i, rrhs_matrix, env, service_time, cp)
				rrhs.append(r)
			if i >= 30 and i < 40:
				rrhs_matrix[4] = 1
				r = RRH(i, rrhs_matrix, env, service_time, cp)
				rrhs.append(r)
			if i >= 40 and i < 50:
				rrhs_matrix[5] = 1
				r = RRH(i, rrhs_matrix, env, service_time, cp)
				rrhs.append(r)
			if i >= 50 and i < 60:
				rrhs_matrix[6] = 1
				r = RRH(i, rrhs_matrix, env, service_time, cp)
				rrhs.append(r)
			if i >= 60 and i < 70:
				rrhs_matrix[7] = 1
				r = RRH(i, rrhs_matrix, env, service_time, cp)
				rrhs.append(r)
			if i >= 70 and i < 80:
				rrhs_matrix[8] = 1
				r = RRH(i, rrhs_matrix, env, service_time, cp)
				rrhs.append(r)
			if i >= 80 and i < 90:
				rrhs_matrix[9] = 1
				r = RRH(i, rrhs_matrix, env, service_time, cp)
				rrhs.append(r)
			if i >= 90 and i < 100:	
				rrhs_matrix[9] = 1
				r = RRH(i, rrhs_matrix, env, service_time, cp)
				rrhs.append(r)
		return rrhs

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


util = Util()
env = simpy.Environment()
cp = Control_Plane(env, util)
rrhs = util.createRRHs(50, env, service_time, cp)
np.shuffle(rrhs)
t = Traffic_Generator(env, distribution, service_time, cp)
print("\Begin at "+str(env.now))
env.run(until = 32401)
print("Total generated requests {}".format(t.req_count))
#print("Allocated {}".format(total_aloc))
#print("Optimal solution got: {}".format(op))
#print("Non allocated {}".format(total_nonaloc))
#print("Size of Nonallocated {}".format(len(no_allocated)))
print("\End at "+str(env.now))
print(len(actives))
print(lp.du_processing)
print(lp.wavelength_capacity)
print(lp.rrhs_on_nodes)
print("Daily power consumption (Incremental) were: {}".format(average_power_consumption))
print("Daily power consumption (Batch) were: {}".format(batch_average_consumption))
plt.plot(average_power_consumption, label = "incremental ilp")
plt.plot(batch_average_consumption, label = "batch ilp")
plt.xlabel("Time of the day")
plt.ylabel("Average Power Consumption")
plt.show()
plt.plot(total_inc_blocking, label = "incremental blocking")
plt.plot(total_batch_blocking, label = "batch blocking")
plt.xlabel("Time of the day")
plt.ylabel("Blocked Requests")
plt.show()
print("Batch failed {}".format(batch_count))