import simpy
import functools
import random as np
import time
from enum import Enum
from scipy.stats import norm
import matplotlib.pyplot as plt
import cfran_batch_ilp as lp

#inter arrival rate of the users requests
arrival_rate = 3600
#distribution for arrival of packets
distribution = lambda x: np.expovariate(1/arrival_rate)
#service time of a request
service_time = lambda x: np.randint(1, 600)
#total generated requests per timestamp
total_period_requests = 0
#timestamp to change the load
change_time = 3600
#to generate the traffic load of each timestamp
loads = []
#number of timestamps of load changing
stamps = 24
for i in range(stamps):
	x = norm.pdf(i, 10, 2)
	x *= 500000
	#x= round(x,4)
	#if x != 0:
	#	loads.append(x)
	loads.append(x)
loads.reverse()
#print(loads)
stamps = len(loads)
#record the requests arrived at each stamp
traffics = []
#amount of rrhs
rrhs_amount = 2
#list of rrhs of the network
rrhs = []
#amount of processing nodes
nodes_amount = 10
#list of processing nodes
nodes = []
#capacity of each rrh
rrh_capacity = 5000
#keeps the non allocated requests
no_allocated = []
total_aloc = 0
total_nonaloc = 0
switchBandwidth = [10000.0,10000.0,10000.0,10000.0,10000.0,10000.0,10000.0,10000.0,10000.0,10000.0]
wavelength_capacity = [10000.0, 10000.0,10000.0,10000.0,10000.0,10000.0,10000.0,10000.0,10000.0,10000.0]
lc_cost = 20
B = 1000000
op = 0
maximum_load = 100

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
		while True and total_period_requests <= maximum_load:
			yield self.env.timeout(self.dist(self))
			self.req_count += 1
			total_period_requests +=1
			#takes the first turned off RRH
			for r in rrhs:
				if r.enabled == False:
					self.cp.requests.put(r)

	#changing of load
	def change_load(self):
		while True:
			global traffics
			#global loads
			global arrival_rate
			global total_period_requests
			#self.action = self.action = self.env.process(self.run())
			yield self.env.timeout(change_time)
			traffics.append(total_period_requests)
			arrival_rate = change_time/loads.pop()
			self.action = self.action = self.env.process(self.run())
			print("Arrival rate now is {} at {} and was generated {}".format(arrival_rate, self.env.now/3600, total_period_requests))
			total_period_requests = 0

#control plane that controls the allocations and deallocations
class Control_Plane(object):
	def __init__(self, env):
		self.env = env
		self.requests = simpy.Store(self.env)
		self.departs = simpy.Store(self.env)
		self.action = self.env.process(self.run())
		#self.deallocation = self.env.process(self.depart_request())
		self.audit = self.env.process(self.checkNetwork())


	#take requests and tries to allocate on a RRH
	def run(self):
		global total_aloc
		global total_nonaloc
		global no_allocated
		while True:
			r = yield self.requests.get()
			#print("Allocating request {}".format(r.id))
			#as soon as it gets the request, allocates it into a RRH
			#----------------------CALLS THE ILP-------------------------
			print("Calling ILP")
			#after calling the ILP and and getting a solution
			#starts the RRH by calling its running funciton


	#starts the deallocation of a request
	def depart_request(self):
		while True:
			r = yield self.departs.get()
			print("Deallocating request {}".format(r.id))

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

env = simpy.Environment()
cp = Control_Plane(env)
nodes = range(0	,10)
processing_nodes = []



t = Traffic_Generator(env, distribution, service_time, cp)
print("\Begin at "+str(env.now))
env.run(until = 86401)
print("Total generated requests {}".format(t.req_count))
print("Allocated {}".format(total_aloc))
print("Optimal solution got: {}".format(op))
print("Non allocated {}".format(total_nonaloc))
print("Size of Nonallocated {}".format(len(no_allocated)))
print("\End at "+str(env.now))