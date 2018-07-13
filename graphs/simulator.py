import simpy
import functools
import random as np
import time
from enum import Enum
import numpy
from scipy.stats import norm
import matplotlib.pyplot as plt
import copy
import sys
import graph as g
import networkx as nx
#cpri line rate
cpri_line = 614.4
#count the total of requested RRHs
total_requested = []
#count allocated requests
sucs_reqs = 0
total_allocated = []
network_threshold = 0.8
traffic_quocient = 50
rrhs_quantity = 35
served_requests = 0
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
	x = norm.pdf(i, 12, 3)
	x *= traffic_quocient
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
			#if rrhs:
			#if total_period_requests <= maximum_load:
			yield self.env.timeout(self.dist(self))
			#total_period_requests +=1
			self.req_count += 1
			#takes the first turned off RRH
			if g.rrhs:
				r = g.rrhs.pop()
				self.cp.requests.put(r)
				print("Took {}".format(r.id))
				#r.updateGenTime(self.env.now)
				#r.enabled = True
				total_period_requests +=1
				#np.shuffle(rrhs)
			else:
				#print("Empty at {}".format(self.env.now))
				pass


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
			global inc_batch_power_consumption
			global incremental_blocking
			global batch_blocking
			global served_requests
			global sucs_reqs
			#self.action = self.action = self.env.process(self.run())
			yield self.env.timeout(change_time)
			actual_stamp = self.env.now
			#print("next time {}".format(next_time))
			next_time = actual_stamp + change_time
			traffics.append(total_period_requests)
			arrival_rate = loads.pop()/change_time
			self.action = self.env.process(self.run())
			print("Arrival rate now is {} at {} and was generated {}".format(arrival_rate, self.env.now/3600, total_period_requests))
			total_requested.append(total_period_requests)
			#print(avg_act_cloud)
			#print(avg_act_fog)
			#print("Was served {}".format(served_requests))
			#served_requests = 0
			#print("Total Node Migrations: {}".format(avg_external_migrations))
			#print("Total In Node Migrations: {}".format(avg_internal_migrations))
			total_period_requests = 0
			sucs_reqs = 0

#control plane that controls the allocations and deallocations
class Control_Plane(object):
	def __init__(self, env, type, graph):
		self.env = env
		self.requests = simpy.Store(self.env)
		self.departs = simpy.Store(self.env)
		self.action = self.env.process(self.run())
		self.deallocation = self.env.process(self.depart_request())
		self.type = type
		self.graph = graph
		
	#create rrhs
	def createRRHs(self, amount, env):
		for i in range(amount):
   			g.rrhs.append(RRH(cpri_line, i, self,self.env))
			
	#take requests and tries to allocate on a RRH
	def run(self):
		global total_aloc
		global total_nonaloc
		global no_allocated
		global count
		global actives
		global incremental_blocking
		#global batch_blocking
		global inc_block
		global batch_block
		global count_rrhs
		while True:
			r = yield self.requests.get()
			print("Got {}".format(r.id))
			g.actives_rrhs.append(r)
			g.startNode(gp, r.id)
			self.env.process(r.run())
			g.assignVPON(self.graph)


	#starts the deallocation of a request
	def depart_request(self):
		while True:
			r = yield self.departs.get()
			print("Departing {}".format(r.id))
			g.actives_rrhs.remove(r)
			g.rrhs.append(r)
			g.endNode(self.graph, r.id)
			np.shuffle(g.rrhs)

	#to capture the state of the network at a given rate - will be used to take the metrics at a given (constant) moment
	def checkNetwork(self):
		while True:
			yield self.env.timeout(1800)
			print("Taking network status at {}".format(self.env.now))
			print("Total generated requests is {}".format(total_period_requests))

#rrh
class RRH(object):
	def __init__(self, cpri_line, rrhId, cp, env):
		self.cpri_line = cpri_line
		self.id = "RRH{}".format(rrhId)
		self.cp = cp
		self.env = env

	def run(self):
		t = np.uniform((next_time -self.env.now)/4, next_time -self.env.now)
		yield self.env.timeout(t)
		self.cp.departs.put(self)



	#reset the parameters
	def resetParams(self):
		global count, change_time, next_time, actual_stamp, arrival_rate, service_time, total_period_requests, loads, actives, stamps, hours_range, arrival_rate, distribution,traffics
		global power_consumption,average_power_consumption,	batch_power_consumption,batch_average_consumption,incremental_blocking,batch_blocking
		global redirected,activated_nodes,average_act_nodes,b_activated_nodes,b_average_act_nodes
		global activated_lambdas,average_act_lambdas,b_activated_lambdas,b_average_act_lambdas,	activated_dus,average_act_dus,b_activated_dus
		global b_average_act_dus,activated_switchs,	average_act_switch,	b_activated_switchs,b_average_act_switch,redirected_rrhs,average_redir_rrhs
		global b_redirected_rrhs,b_average_redir_rrhs,time_inc,	avg_time_inc,time_b,avg_time_b,count_cloud,	count_fog,b_count_cloud,b_count_fog
		global max_count_cloud,	average_count_fog,b_max_count_cloud,b_average_count_fog,batch_rrhs_wait_time,avg_batch_rrhs_wait_time
		global inc_batch_count_cloud, inc_batch_max_count_cloud, inc_batch_count_fog, inc_batch_average_count_fog, time_inc_batch, avg_time_inc_batch
		global inc_batch_redirected_rrhs, inc_batch_average_redir_rrhs, inc_batch_power_consumption, inc_batch_average_consumption, inc_batch_activated_nodes
		global inc_batch_average_act_nodes, inc_batch_activated_lambdas, inc_batch_average_act_lambdas,	inc_batch_activated_dus, inc_batch_average_act_dus
		global inc_batch_activated_switchs, inc_batch_average_act_switch
		global inc_blocking, total_inc_blocking, batch_blocking, total_batch_blocking, inc_batch_blocking, total_inc_batch_blocking
		global external_migrations, internal_migrations, avg_external_migrations, avg_internal_migrations, served_requests
		global lambda_usage, avg_lambda_usage,proc_usage, avg_proc_usage
		global act_cloud, act_fog, avg_act_cloud, avg_act_fog, daily_migrations
		global count_ext_migrations, total_service_availability, avg_service_availability, avg_total_allocated, total_requested

		total_requested = []
		served_requests = 0
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
			x = norm.pdf(i, 12, 3)
			x *= traffic_quocient
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

#starts simulation
#simulation environment
env = simpy.Environment()
#create the graph
gp = g.createGraph()
#create the control plane
cp = Control_Plane(env, "Graph", gp)
#traffic generator
tg = Traffic_Generator(env,distribution, None, cp)
#create the rrhs
cp.createRRHs(10,env)
#create fog nodes
g.addFogNodes(gp, 2)
#add RRHs to the graph
#10 rrhs per fog node
g.addRRHs(gp, 0, 5, "0")
g.addRRHs(gp, 5, 10, "1")
#starts the simulation
env.run(until = 86401)
#for i in range(len(g.actives_rrhs)):
#	print(gp["s"]["RRH{}".format(i)]["capacity"])
#	print(nx.edges(gp, "RRH{}".format(i)))
#print(nx.edges(gp))
#print(gp["fog0"]["d"]["capacity"])
#neighbors = g.nx.all_neighbors(gp, "s")
#for i in neighbors:
#	print(i)
#print("Cost is {}".format(g.assignVPON(gp)))