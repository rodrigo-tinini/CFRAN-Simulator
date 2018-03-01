import simpy
import functools
import random as np
import time
from enum import Enum
from scipy.stats import norm

#distribution for arrival of packets
distribution = lambda x: np.expovariate(1/0.05)
traffic_time_change = 0.5
actual_traffic = 0.0

#control plane class that controls the network operation
class ControlPlane(object):
	def __init__(self, env):
		self.env = env
		self.requests = simpy.Store(self.env)
		self.fluctuation = self.env.process(self.traffic_variation())
		self.pop_requests = self.env.process(self.run())

	#main method that waits for a request to arrive to schedule it
	def run(self):
		while True:
			r = yield self.requests.get()
			#print("Took request "+str(r.id))

	#method that changes the traffic of the network
	def traffic_variation(self):
		while True:
			global actual_traffic
			yield self.env.timeout(traffic_time_change)
			actual_traffic = round(norm.pdf(self.env.now, 12, 2), 4)*500
			print("Actual traffic "+str(actual_traffic)+" at "+str(self.env.now))

#traffic generator
class TrafficGenerator(object):
	def __init__(self, env, control_plane, distro):
		self.env = env
		self.cp = control_plane
		self.dist = distro
		self.count = 0
		self.action = self.env.process(self.run())

	#run method that generates traffic according to a interarrival rate
	def run(self):
		while True:
			yield self.env.timeout(self.dist(self))
			r = Request(self.env, self.count)
			self.count+=1
			self.cp.requests.put(r)
			self.env.process(r.run())

#request class
class Request(object):
	def __init__(self, env, aId):
		self.env = env
		self.id = aId

	#class that run the request after it is scheduled
	def run(self):
		yield self.env.timeout(np.randint(1,10))
		#print("Request "+str(self.id)+" departing network")

env = simpy.Environment()
cp = ControlPlane(env)
t = TrafficGenerator(env, cp, distribution)
print("\Begin at "+str(env.now))
env.run(until = 24)
print("\End at "+str(env.now))