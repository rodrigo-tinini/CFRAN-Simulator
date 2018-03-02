import simpy
import functools
import random as np
import time
from enum import Enum
from scipy.stats import norm

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
print(loads)
stamps = len(loads)
traffics = []

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
		while True:
			yield self.env.timeout(self.dist(self))
			self.req_count += 1
			total_period_requests +=1
			r = Request(self.env, self.req_count, self.service, self.cp)
			print("Generated {} at {}".format(r.id, self.env.now))
			self.cp.requests.put(r)

	#changing of load
	def change_load(self):
		while True:
			global traffics
			#global loads
			global arrival_rate
			global total_period_requests
			self.action = self.action = self.env.process(self.run())
			yield self.env.timeout(change_time)
			traffics.append(total_period_requests)
			arrival_rate = change_time/loads.pop()
			#print("Arrival rate now is {} at {} and was generated {}".format(arrival_rate, self.env.now/3600, total_period_requests))
			total_period_requests = 0

#user request
class Request(object):
	def __init__(self, env, aId, service, cp):
		self.env = env
		self.id = aId
		self.service_time = service
		self.cp = cp
		#self.action = self.env.process(self.run())

	#executes this request and send it to deallocation after its service time
	def run(self):
		yield self.env.timeout(self.service_time(self))
		#print("Request {} departing".format(self.id))
		self.cp.departs.put(self)

#control plane that controls the allocations and deallocations
class Control_Plane(object):
	def __init__(self, env):
		self.env = env
		self.requests = simpy.Store(self.env)
		self.departs = simpy.Store(self.env)
		self.action = self.env.process(self.run())
		self.deallocation = self.env.process(self.depart_request())

	#take requests and tries to allocate
	def run(self):
		while True:
			r = yield self.requests.get()
			print("Allocating request {}".format(r.id))
			self.env.process(r.run())

	#starts the deallocation of a request
	def depart_request(self):
		while True:
			r = yield self.departs.get()
			print("Deallocating request {}".format(r.id))


env = simpy.Environment()
cp = Control_Plane(env)
t = Traffic_Generator(env, distribution, service_time, cp)
print("\Begin at "+str(env.now))
env.run(until = 7201)
print("Total generated requests {}".format(t.req_count))
print("\End at "+str(env.now))