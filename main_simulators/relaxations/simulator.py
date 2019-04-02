import simpy
import functools
import random as np
import time
from enum import Enum
import numpy
from scipy.stats import norm
import matplotlib.pyplot as plt
#import batch_teste as lp
import relaxation_test as plp
import relaxation_module as rlx
import relaxedMainModule as rm
import copy
import sys
import pdb#debugging module
import importlib#to reload modules


#to count the availability of the service
total_service_availability = []
avg_service_availability = []

#count the total of requested RRHs
total_requested = []

#count allocated requests
sucs_reqs = 0
total_allocated = []
avg_total_allocated = []

external_migrations = 0
internal_migrations = 0
avg_external_migrations = []
avg_internal_migrations = []
count_ext_migrations = []

lambda_usage = []
avg_lambda_usage = []
proc_usage = []
avg_proc_usage = []

dus_total_capacity = [
		[5.0, 5.0, 5.0, 5.0, 5.0],
		[1.0, 1.0, 1.0, 1.0, 1.0],
		[1.0, 1.0, 1.0, 1.0, 1.0],
		]

dus_capacity = [8,4,4]

network_threshold = 0.8
traffic_quocient = 80
rrhs_quantity = 35
served_requests = 0
inc_block = 0
batch_block = 0
count = 0

#total migrations on the day
daily_migrations = 0
#to count the activation of cloud and fog
act_cloud = []
act_fog = []
avg_act_cloud = []
avg_act_fog = []

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
#inc_batch_blocking = 0
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

#variables for counting the blocking
inc_blocking = []
total_inc_blocking = []
batch_blocking = []
total_batch_blocking  = []
inc_batch_blocking = []
total_inc_batch_blocking = []

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
			#if rrhs:
			#if total_period_requests <= maximum_load:
			yield self.env.timeout(self.dist(self))
			#total_period_requests +=1
			self.req_count += 1
			#takes the first turned off RRH
			if rrhs:
				#print(len(rrhs))
				r = rrhs.pop()
				#print("Took {} RRHS list is {}".format(r.id, len(rrhs)))
				self.cp.requests.put(r)
				r.updateGenTime(self.env.now)
				r.enabled = True
				total_period_requests +=1
				#np.shuffle(rrhs)
			else:
				pass
				#total_period_requests +=1
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
			#print("RRHS on {}".format(len(actives)))
			#print("RRHs off {}".format(len(rrhs)))
			#total_inc_blocking.append(incremental_blocking)
			#total_batch_blocking.append(batch_blocking)
			#incremental_blocking = 0
			#batch_blocking = 0
			#count averages for the batch case
			#print("Departed{} Requested {} Accepted {}".format(served_requests,total_period_requests, sucs_reqs))
			if self.cp.type == "inc":
				self.countIncAverages()
				#print("Blocked were {}".format(total_inc_blocking))
			#count averages for the batch case
			elif self.cp.type == "batch":
				self.countBatchAverages()
			elif self.cp.type == "inc_batch":
				self.countIncBatchAverages()
			elif self.cp.type == "load_inc_batch":
				self.countIncBatchAverages()
				print("Blocked were {}".format(total_inc_batch_blocking))
			self.action = self.env.process(self.run())
			#print("Arrival rate now is {} at {} and was generated {}".format(arrival_rate, self.env.now/3600, total_period_requests))
			#print(plp.rrhs_on_nodes)
			total_requested.append(total_period_requests)
			#print(avg_act_cloud)
			#print(avg_act_fog)
			#print("Was served {}".format(served_requests))
			#served_requests = 0
			#print("Total Node Migrations: {}".format(avg_external_migrations))
			#print("Total In Node Migrations: {}".format(avg_internal_migrations))
			total_period_requests = 0
			sucs_reqs = 0

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
		global inc_batch_blocking
		global avg_external_migrations
		global avg_internal_migrations
		global external_migrations
		global internal_migrations
		global avg_lambda_usage, avg_proc_usage, lambda_usage, proc_usage
		global act_cloud, act_fog, avg_act_fog, avg_act_cloud
		global served_requests, avg_total_allocated

		#if external_migrations > 0:
		#	avg_external_migrations.append(external_migrations)
		#	external_migrations = 0
		#else:
		#	avg_external_migrations.append(0)

		if external_migrations:
			count_ext_migrations.append(external_migrations)
			avg_external_migrations.append(external_migrations/served_requests)
			external_migrations = 0
		else:
			count_ext_migrations.append(0)
			avg_external_migrations.append(0)

		if internal_migrations:
			avg_internal_migrations.append(internal_migrations)
			internal_migrations = 0
		else:
			avg_internal_migrations.append(0)

		#count the averages (sometimes sums) of metrics
		if act_cloud:
			avg_act_cloud.append(sum(act_cloud)/served_requests)
			act_cloud = []
		else:
			avg_act_cloud.append(0)

		if act_fog:
			avg_act_fog.append(sum(act_fog)/served_requests)
			act_fog = []
		else:
			avg_act_fog.append(0)

		if lambda_usage:
			avg_lambda_usage.append(numpy.mean(lambda_usage))
			lambda_usage = []
		else:
			avg_lambda_usage.append(0.0)

		if proc_usage:
			avg_proc_usage.append(numpy.mean(proc_usage))
			proc_usage = []
		else:
			avg_proc_usage.append(0.0)

		
		
		if inc_batch_blocking:
			total_inc_batch_blocking.append(sum((inc_batch_blocking)))
			inc_batch_blocking = []
		else:
			total_inc_batch_blocking.append(0)
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
			inc_batch_average_redir_rrhs.append(numpy.mean(inc_batch_redirected_rrhs))
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

		#count the probability o availability of service
		if served_requests > 0:
			avg_service_availability.append(served_requests/total_period_requests)
			avg_total_allocated.append(served_requests)
			served_requests = 0
		else:
			avg_service_availability.append(0)
			avg_total_allocated.append(0)

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
		global inc_blocking
		global avg_external_migrations
		global avg_internal_migrations
		global external_migrations
		global internal_migrations
		global avg_lambda_usage, avg_proc_usage, lambda_usage, proc_usage
		global act_cloud, act_fog, avg_act_fog, avg_act_cloud
		global served_requests, avg_total_allocated

		#if external_migrations > 0:
		#	avg_external_migrations.append(external_migrations)
		#	external_migrations = 0
		#else:
		#	avg_external_migrations.append(0)

		if external_migrations:
			count_ext_migrations.append(external_migrations)
			avg_external_migrations.append(external_migrations/served_requests)
			external_migrations = 0
		else:
			count_ext_migrations.append(0)
			avg_external_migrations.append(0)

		if internal_migrations:
			avg_internal_migrations.append(internal_migrations)
			internal_migrations = 0
		else:
			avg_internal_migrations.append(0)

		#count the averages (sometimes sums) of metrics
		if act_cloud:
			avg_act_cloud.append(sum(act_cloud)/served_requests)
			act_cloud = []
		else:
			avg_act_cloud.append(0)

		if act_fog:
			avg_act_fog.append(sum(act_fog)/served_requests)
			act_fog = []
		else:
			avg_act_fog.append(0)


		if lambda_usage:
			avg_lambda_usage.append(numpy.mean(lambda_usage))
			lambda_usage = []
		else:
			avg_lambda_usage.append(0.0)

		if proc_usage:
			avg_proc_usage.append(numpy.mean(proc_usage))
			proc_usage = []
		else:
			avg_proc_usage.append(0.0)
		
		if inc_blocking:
			total_inc_blocking.append(sum((inc_blocking)))
			inc_blocking = []
		else:
			total_inc_blocking.append(0)
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
			average_redir_rrhs.append(numpy.mean(redirected_rrhs))
			redirected_rrhs = []
		else:
			average_redir_rrhs.append(0)
		#power consumption for the incremental case
		if incremental_power_consumption:
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

		#count the probability o availability of service
		if served_requests > 0:
			avg_service_availability.append(served_requests/total_period_requests)
			avg_total_allocated.append(served_requests)
			served_requests = 0
		else:
			avg_service_availability.append(0)
			avg_total_allocated.append(0)



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
		global batch_blocking
		global avg_external_migrations
		global avg_internal_migrations
		global external_migrations
		global internal_migrations
		global avg_lambda_usage, avg_proc_usage, lambda_usage, proc_usage
		global act_cloud, act_fog, avg_act_fog, avg_act_cloud
		global served_requests, avg_total_allocated

		#if external_migrations > 0:
		#	avg_external_migrations.append(external_migrations)
		#	external_migrations = 0
		#else:
		#	avg_external_migrations.append(0)

		if external_migrations:
			count_ext_migrations.append(external_migrations)
			avg_external_migrations.append(external_migrations/served_requests)
			external_migrations = 0
		else:
			count_ext_migrations.append(0)
			avg_external_migrations.append(0)

		if internal_migrations:
			avg_internal_migrations.append(internal_migrations)
			internal_migrations = 0
		else:
			avg_internal_migrations.append(0)

		#count the averages (sometimes sums) of metrics
		if act_cloud:
			avg_act_cloud.append(sum(act_cloud)/served_requests)
			act_cloud = []
		else:
			avg_act_cloud.append(0)

		if act_fog:
			avg_act_fog.append(sum(act_fog)/served_requests)
			act_fog = []
		else:
			avg_act_fog.append(0)


		if lambda_usage:
			avg_lambda_usage.append(numpy.mean(lambda_usage))
			lambda_usage = []
		else:
			avg_lambda_usage.append(0.0)

		if proc_usage:
			avg_proc_usage.append(numpy.mean(proc_usage))
			proc_usage = []
		else:
			avg_proc_usage.append(0.0)

		if batch_blocking:
			total_batch_blocking.append(sum((batch_blocking)))
			batch_blocking = []
		else:
			total_batch_blocking.append(0)
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
			b_average_redir_rrhs.append(numpy.mean(b_redirected_rrhs))
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

		#count the probability o availability of service
		if served_requests > 0:
			avg_service_availability.append(served_requests/total_period_requests)
			avg_total_allocated.append(served_requests)
			served_requests = 0
		else:
			avg_service_availability.append(0)
			avg_total_allocated.append(0)




#control plane that controls the allocations and deallocations
class Control_Plane(object):
	def __init__(self, env, ilp_module, util, type, number_of_runs, relaxHeuristic, postProcessingHeuristic, metric, method):
		self.env = env
		self.requests = simpy.Store(self.env)
		self.departs = simpy.Store(self.env)
		self.action = self.env.process(self.run(ilp_module))
		self.deallocation = self.env.process(self.depart_request(ilp_module))
		#self.audit = self.env.process(self.checkNetwork())
		self.type = type
		self.ilp = None
		self.util = util
		self.ilpBatch = None
		self.check_load = simpy.Store(self.env)
		self.check_cloud_load = simpy.Store(self.env)
		if self.type == "load_inc_batch":
			self.load_balancing = self.env.process(self.monitorLoad(ilp_module))
			#self.cloud_balancing = self.env.process(self.cloudMonitor())
		#number of runs of the relaxed ILP model
		self.number_of_runs = number_of_runs
		#to keep the different solutions for each run of the relazed ILP model
		self.network_states = []
		self.relaxHeuristic = relaxHeuristic
		self.postProcessingHeuristic = postProcessingHeuristic
		self.metric = metric
		self.method = method



	#batch scheduling1
	def batchSched2(self, antenas, ilp_module):

		self.ilp = plp.ILP(antenas, range(len(antenas)), ilp_module.nodes, ilp_module.lambdas, True)
		#take a snapshot of the node states to account the migrations
		solution = self.ilp.run()
		if solution == None:
			print("No Solution")
			#print(plp.du_processing)
			print(solution)
		else:
			print("Solution Found")
			solution_values = self.ilp.return_decision_variables()#calling relaxation post data processing here
			#self.ilp.updateValues(solution_values)
			rlx.mostProbability(solution_values, self.ilp)#calling relaxation post data processing here
			self.ilp.relaxUpdate(solution_values)#calling relaxation post data processing here



	#calculates the mean service average time, i.e., the average total time where RRHs where processing
	def meanTotalServiceTime(self):
		pass

	#compute which nodes are active (cloud or fog, and how many of them are active)
	def countNodes(self, ilp):
		global act_cloud, act_fog
		for i in range(len(ilp.nodeState)):
			if ilp.nodeState[i] == 1:
				if i == 0:
					act_cloud.append(1)
				else:
					act_fog.append(1)

	#count external migration for only batch case - this method considers each vBBU migrated to account
	def extSingleMigrations(self, ilp_module, copy_state):
		global external_migrations
		global daily_migrations
		for i in ilp_module.nodes:
			if copy_state[i] > ilp_module.rrhs_on_nodes[i] and copy_state[0] < ilp_module.rrhs_on_nodes[0]:
				diff = copy_state[i] - ilp_module.rrhs_on_nodes[i]
				#print("MIgrated from {}: {}".format(i,diff))
				#print(copy_state[i])
				#print(ilp_module.rrhs_on_nodes[i])
				#print("----------------------")
				external_migrations += diff
				daily_migrations += diff


	#this method considers only a full load migration of a fog node to the cloud - it does not account individual vBBUs migrations
	#count external migrations
	def extMigrations(self, ilp_module, copy_nodeState):
		global external_migrations
		global daily_migrations
		if copy_nodeState != ilp_module.nodeState:
			external_migrations += 1
			daily_migrations += 1

	#monitors the network and triggers the load balancing
	def cloudMonitor(self):
		while True:
			batch_done = False
			#print("AQUIII")
			yield self.check_cloud_load.get()
			#print("Saiu alguém")
			#print("---Normal Operation---")
			#print(plp.nodeState)
			#print(len(actives))
			#print("##Normal Operation##")
			#Verify the cloud can handle the load on the DUs of the F-APs (fog nodes)
			if sum(plp.du_processing):
				#call the batch
				#print("########")
				print("Load balancing")
				#print(plp.nodeState)
				#print(len(actives))
				#print("Load is {} in {}".format(proc_loads[i], i))
				#print("########")
				count_nodes = 0
				count_lambdas = 0
				count_dus = 0
				count_switches = 0
				block = 0
				#print("Calling Batch")
				batch_list = copy.copy(actives)
				#batch_list.append(r)
				#actives.append(r)
				self.ilp = plp.ILP(actives, range(len(actives)), plp.nodes, plp.lambdas, True)
				self.ilp.resetValues()
				solution = self.ilp.run()
				if solution == None:
				#	rrhs.append(r)
				#	actives.remove(r)
				#	np.shuffle(rrhs)
					print("Batch Blocking")
					print("Cant Schedule {} RRHs".format(len(actives)))
					batch_power_consumption.append(self.util.getPowerConsumption(plp))
					batch_blocking.append(1)
				else:
					#print(solution.solve_details.time)
					solution_values = self.ilp.return_solution_values()
					self.ilp.updateValues(solution_values)
					batch_time.append(solution.solve_details.time)
					time_b.append(solution.solve_details.time)
				#	r.updateWaitTime(self.env.now+solution.solve_details.time)
					#print("Gen is {} ".format(r.generationTime))
					#print("NOW {} ".format(r.waitingTime))
				#	self.env.process(r.run())
					batch_power_consumption.append(self.util.getPowerConsumption(plp))
					batch_rrhs_wait_time.append(self.averageWaitingTime(actives))
					if solution_values.var_k:
						b_redirected_rrhs.append(len(solution_values.var_k))
					else:
						b_redirected_rrhs.append(0)
					#counts the current activated nodes, lambdas, DUs and switches
					for i in plp.nodeState:
						if i == 1:
							count_nodes += 1
					b_activated_nodes.append(count_nodes)
					for i in plp.lambda_state:
						if i == 1:
							count_lambdas += 1
					b_activated_lambdas.append(count_lambdas)
					for i in plp.du_state:
						for j in i:
							if j == 1:
								count_dus += 1
					b_activated_dus.append(count_dus)
					for i in plp.switch_state:
						if i == 1:
							count_switches += 1
					b_activated_switchs.append(count_switches)
					batch_done = True
					#count DUs and lambdas usage
					if count_lambdas > 0:
						lambda_usage.append((len(actives)*614.4)/(count_lambdas*10000.0))
					if count_dus > 0:
						proc_usage.append(len(actives)/self.getProcUsage(plp))


	#monitors the network and triggers the load balancing
	def monitorLoad(self, ilp_module):
		proc_loads = [0,0,0]
		while True:
			batch_done = False
			#print("AQUIII")
			yield self.check_load.get()
			#print("Saiu alguém")
			#print("---Normal Operation---")
			#print(plp.nodeState)
			#print(len(actives))
			#print("##Normal Operation##")
			#for i in range(len(plp.du_processing)):
			#	proc_loads[i] = (sum(plp.du_processing[i]))/ sum(plp.dus_total_capacity[i])
			#for i in range(len(proc_loads)):
			#	if proc_loads[i] >= network_threshold and proc_loads[i] < 1.0 and batch_done == False:
					#call the batch
			#print("########")
			print("Load balancing")
			#print(len(actives))
			#print(plp.lambda_node)
			#self.getProcUsage(plp)
			#print(plp.nodeState)
			#print(len(actives))
			#print("Nodes actives are: {}".format(plp.nodeState))
			#print("Lambdas actives are: {}".format(plp.lambda_node))
			#print("DUs load are: {}".format(plp.du_processing))
			#print("Load is {} in {}".format(proc_loads[i], i))
			#print("########")
			count_nodes = 0
			count_lambdas = 0
			count_dus = 0
			count_switches = 0
			block = 0
			self.runRelaxation(self.relaxHeuristic, self.postProcessingHeuristic, ilp_module, self.metric, self.method)
			'''
			#print("Calling Batch")
			batch_list = copy.copy(actives)
			#batch_list.append(r)
			#actives.append(r)
			self.ilp = plp.ILP(actives, range(len(actives)), plp.nodes, plp.lambdas, True)
			copy_state = copy.copy(plp.nodeState)
			self.ilp.resetValues()
			solution = self.ilp.run()
			if solution == None:
			#	rrhs.append(r)
			#	actives.remove(r)
			#	np.shuffle(rrhs)
				print("Batch Blocking")
				print("Cant Schedule {} RRHs".format(len(actives)))
				batch_power_consumption.append(self.util.getPowerConsumption(plp))
				inc_batch_blocking.append(1)
			else:
				#copy_state = copy.copy(plp.nodeState)
				#print(solution.solve_details.time)
				solution_values = self.ilp.return_solution_values()
				self.ilp.updateValues(solution_values)
				batch_time.append(solution.solve_details.time)
				time_b.append(solution.solve_details.time)
			#	r.updateWaitTime(self.env.now+solution.solve_details.time)
				#print("Gen is {} ".format(r.generationTime))
				#print("NOW {} ".format(r.waitingTime))
			#	self.env.process(r.run())
				#print("After Load balancing")
				#print(plp.nodeState)
				#print(len(actives))
				#print("Nodes actives are: {}".format(plp.nodeState))
				#print("Lambdas actives are: {}".format(plp.lambda_node))
				#print("DUs load are: {}".format(plp.du_processing))
				#print("Load is {} in {}".format(proc_loads[i], i))
				#print("########")
				#counts the external migrations
				self.extMigrations(plp, copy_state)
				batch_power_consumption.append(self.util.getPowerConsumption(plp))
				batch_rrhs_wait_time.append(self.averageWaitingTime(actives))
				if solution_values.var_k:
					b_redirected_rrhs.append(len(solution_values.var_k))
				else:
					b_redirected_rrhs.append(0)
				#counts the current activated nodes, lambdas, DUs and switches
				for i in plp.nodeState:
					if i == 1:
						count_nodes += 1
				b_activated_nodes.append(count_nodes)
				for i in plp.lambda_state:
					if i == 1:
						count_lambdas += 1
				b_activated_lambdas.append(count_lambdas)
				for i in plp.du_state:
					for j in i:
						if j == 1:
							count_dus += 1
				b_activated_dus.append(count_dus)
				for i in plp.switch_state:
					if i == 1:
						count_switches += 1
				b_activated_switchs.append(count_switches)
				#batch_done = True
				#count DUs and lambdas usage
				if count_lambdas > 0:
					lambda_usage.append((len(actives)*614.4)/(count_lambdas*10000.0))
				if count_dus > 0:
					proc_usage.append(len(actives)/self.getProcUsage(plp))
				'''

	#calculate the usage of each processing node
	def getProcUsage(self, plp):
		du_usage = 0
		#counts the active DUs
		for i in range(len(plp.du_state)):
			du_usage += sum(plp.du_state[i])*dus_capacity[i]
		#print("Active DUs {}".format(plp.du_state))
		#print("Processing Usage {}".format(du_usage))
		return du_usage
			
	#take requests and tries to allocate on a RRH
	def run(self, ilp_module):
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
			#print(count_rrhs)
			r = yield self.requests.get()
			antenas = []
			antenas.append(r)
			if self.type == "inc":
				self.incSched(r, antenas, ilp_module, incremental_power_consumption, redirected_rrhs, activated_nodes, activated_lambdas, activated_dus, activated_switchs, inc_blocking)
			elif self.type == "batch":
				self.batchSched(r, ilp_module, batch_power_consumption,b_redirected_rrhs,b_activated_nodes, b_activated_lambdas, b_activated_dus, b_activated_switchs, batch_blocking)
			elif self.type == "inc_batch":
				self.incrementalBatchSched(r,antenas, ilp_module)
			elif self.type == "load_inc_batch":
				self.loadIncBatchSched(r, antenas, ilp_module)

	#encapsulates the generation of auxiliary network states
	def generateNetworkStates(self):
		for i in self.number_of_runs:
				self.network_states.append(rm.NetworkState(i))
		self.relaxSolutions = rm.NetworkStateCollection(self.network_states)


	#call the relaxation solution
	def runRelaxation(self, relaxHeuristic, postProcessingHeuristic, ilp_module, metric, method, antenas = None, r = None):
		global sucs_reqs
		count_nodes = 0
		count_lambdas = 0
		count_dus = 0
		count_switches = 0
		block = 0
		#print(ilp_module == plp)
		#to compute the solution time
		solution_time = 0
		#to verify with at least one solution was found
		foundSolution = False
		#create the auxiliary network states
		#decides the paramaters of the auxiliary network states depending on the type of algorithm being called, e.g. incremental or batch
		#Verify if it is the incremental algorithm to be executed
		if self.type == "inc":
			#maintain the same state of the network, i.e do not reset the values of the original network (parameters of the plp file or another object used)
			for i in range(self.number_of_runs):
				self.network_states.append(rm.NetworkState(i, ilp_module.nodes, ilp_module.rrhs_on_nodes, ilp_module.lambda_node, ilp_module.du_processing, ilp_module.dus_total_capacity, ilp_module.du_state, ilp_module.nodeState,
					ilp_module.nodeCost, ilp_module.du_cost, ilp_module.lc_cost, ilp_module.switch_cost, ilp_module.switchBandwidth, ilp_module.wavelength_capacity, ilp_module.RRHband, ilp_module.cloud_du_capacity, 
					ilp_module.fog_du_capacity, ilp_module.lambda_state, ilp_module.switch_state))
			self.relaxSolutions = rm.NetworkStateCollection(self.network_states)
			#execute each run of the relaxation for each auxiliary network state
			for i in self.relaxSolutions.network_states:
				start = time.time()
				#create the ILP object
				self.ilp = ilp_module.ILP(antenas, range(len(antenas)), ilp_module.nodes, ilp_module.lambdas, True)
				#gets the solution
				solution = self.ilp.run()
				#verifies if a solution was found and, if so, updates this auxiliary network state
				if solution != None:
					foundSolution = True
					#get the solution values
					solution_values = self.ilp.return_decision_variables()
					#performs the post processing relaxation algorithm
					#gets the method
					print()
					postProc = getattr(rlx, self.postProcessingHeuristic)
					postProc(solution_values, ilp_module)
					#rlx.postProcessingHeuristic(solution_values, i)
					#update the network state with the relaxation heuristic passed as parameter relaxHeuristic
					#gets the method
					relaxMethod = getattr(rm, self.relaxHeuristic)
					relaxMethod(antenas, solution_values, i)
					#rm.relaxHeuristic(antenas, solution_values, i)
					#now, set some result metrics on the auxiliary network state
					#execution time
					i.setMetric(execution_time, solution.solve_details.time)
					#power consumption
					i.setMetric(power, self.util.getPowerConsumption(ilp_module))
				end = time.time()
				solution_time += end - start
			#verifies with at least one solution was found, if so, continues, else, break
			if foundSolution == True:
				sucs_reqs += 1
				#gets the best solution
				bestSolution = self.relaxSolutions.getBestNetworkState(self.metric, self.method)
				#now, updates the main network state (so far I am using the on plp file, which is the ILP module file)
				rm.relaxHeuristic(antenas, bestSolution.solution_values, ilp_module)
				#updates the execution time of this solution, which is the relaxed ILP solving time + the relaxation scheduling updating procedure
				time_inc.append(solution_time)
				r.updateWaitTime(self.env.now)
				for i in antenas:
					self.env.process(i.run())
					actives.append(i)
					antenas.remove(i)
					incremental_power_consumption.append(self.util.getPowerConsumption(ilp_module))
				#count the activeresources
				self.countNodes(ilp_module)
				#URGENTE - MEU ALGORITMO DE PÓS PROCESSAMENTO NÃO FAZ NADA COM ESSA VARIÁVEL, LOGO, ELA SEMPRE ESTARÁ VAZIA
				#ASSIM, PRECISO CRIAR UM MÉTODO PARA VERIFICAR REDIRECIONAMENTO DE DUS E CASO OUTRA VARIÁVEL FIQUE VAZIA PELO
				#ALGORITMO DE PÓS PROCESSAMENTO, CRIAR MÉTODOS PARA CONTABILIZÁ-LA TB
				if solution_values.var_k:
					redirected_rrhs.append(len(solution_values.var_k))
				else:
					redirected_rrhs.append(0)
				for i in bestSolution.nodeState:
					if i == 1:
						count_nodes += 1
				activated_nodes.append(count_nodes)
				for i in bestSolution.lambda_state:
					if i == 1:
						count_lambdas += 1
				activated_lambdas.append(count_lambdas)
				for i in bestSolution.du_state:
					for j in i:
						if j == 1:
							count_dus += 1
				activated_dus.append(count_dus)
				for i in bestSolution.switch_state:
					if i == 1:
						count_switches += 1
				activated_switchs.append(count_switches)
				#count DUs and lambdas usage
				if count_lambdas > 0:
					lambda_usage.append((len(actives)*614.4)/(count_lambdas*10000.0))
				if count_dus > 0:
					proc_usage.append(len(actives)/self.getProcUsage(bestSolution))
				print("FINISHED FOR", i.aID)
				return solution
			else:
				print("Incremental Blocking")
				#print("Nodes actives are: {}".format(plp.nodeState))
				#print("Lambdas actives are: {}".format(plp.lambda_node))
				#print("DUs load are: {}".format(plp.du_processing))
				#verifies if it is the nfv control plane
				if self.type == "load_inc_batch":
					inc_blocking.append(1)
					#s = self.batchSched(r, ilp_module,inc_batch_power_consumption,inc_batch_redirected_rrhs,inc_batch_activated_nodes, 
					#inc_batch_activated_lambdas,inc_batch_activated_dus,inc_batch_activated_switchs, inc_batch_blocking)
				else:
					rrhs.append(r)
					np.shuffle(rrhs)
					antenas = []
					#print("Incremental Blocking")
					inc_blocking.append(1)
					incremental_power_consumption.append(self.util.getPowerConsumption(ilp_module))
					return solution
		#Verify if it is the batch algorithm to be executed
		elif self.type == "batch":
			#print("INITIATE BATCH", ilp_module.rrhs_on_nodes)
			self.network_states = []
			if r != None:
				actives.append(r)
			importlib.reload(ilp_module)
			#create auxiliary network states with values reset
			for i in range(self.number_of_runs):
				nt = rm.NetworkState(i, ilp_module.nodes)
				self.network_states.append(nt)
				#print("ILP", ilp_module.rrhs_on_nodes)
				#print(nt.rrhs_on_nodes)
				#self.network_states.append(rm.NetworkState(i, ilp_module.nodes))
				#print("NEW IS",self.network_states[i].rrhs_on_nodes)
				#print(self.network_states)
			self.relaxSolutions = []
			self.relaxSolutions = rm.NetworkStateCollection(self.network_states)
			for i in self.relaxSolutions.network_states:
				print("Batch running for auxiliary network state {} with {} actives RRHs".format(i.aId, len(actives)))
				#print("Size of n state is ",len(self.relaxSolutions.network_states))
				#take a snapshot of the node states to account the migrations
				copy_state = copy.copy(ilp_module.nodeState)
				#put the snapshot of the node states into the auxiliary network state
				i.old_network_state = copy_state
				#take a snapshot of the network and its elements state
				network_copy = copy.copy(ilp_module.rrhs_on_nodes)
				cp_l =  copy.copy(ilp_module.lambda_node)
				cp_d = copy.copy(ilp_module.du_processing)
				start = time.time()
				#prepare data to execute the ILP
				#batch_list = copy.copy(actives)
				#batch_list.append(r)
				#actives.append(r)#moved out from the loop if network states because the active list were appending the same RRH i neach iteration
				#print(r.id)
				#create the ILP object
				self.ilp = ilp_module.ILP(actives, range(len(actives)), ilp_module.nodes, ilp_module.lambdas, True)
				#print("THE MATRIX IS {}".format(r.rrhs_matrix))
				#gets the solution
				solution = self.ilp.run()
				#verifies if a solution was found and, if so, updates this auxiliary network state
				if solution != None:
					foundSolution = True
					#get the solution values
					solution_values = self.ilp.return_decision_variables()
					#perform the post processing procedure
					#gets the post processing method
					postMethod = getattr(rlx, self.postProcessingHeuristic)
					postMethod(solution_values, self.ilp, i)
					#rlx.postProcessingHeuristic(solution_values, i)
					#update the network state with the relaxation heuristic passed as parameter relaxHeuristic
					#gets the metho
					#print("AFTER1", ilp_module.rrhs_on_nodes)
					relaxMethod = getattr(rm, self.relaxHeuristic)
					#The method on the line below will return a list of blocked RRHs from the relaxation method
					#if any RRH happens to be blocked (very low probability for this to happen with the batch algorithm) remove them from the "active" list and account the number of blockeds in a new list
					blocked_rrhs = None
					blocked_rrhs = relaxMethod(actives, solution_values, i)
					if blocked_rrhs:
						print("HHAAHIAHIAHIAHIAHIAHIAHIAHIAHIAHIAHIAHAIAHIAHIAHIAAH\nAHUHAUAHUAHUAHUAHUAHUAHUHAUHAUHAUHAUHA\nAHUAHUAHUAHUAHUAHUA")
						for r in blocked_rrhs:
							print("R IS {}".format(r.id))
							actives.remove(r)
							print("REMOVED {}".format(r.id))
							rrhs.append(r)
							np.shuffle(rrhs)
						i.relax_blocked = len(blocked_rrhs)
					#print("AFTER2", ilp_module.rrhs_on_nodes)
					#rm.relaxHeuristic(antenas, solution_values, i)
					i.old_network_state = network_copy
					#now, set some result metrics on the auxiliary network state
					#set the solution values
					i.setMetric("solution_values", solution_values)
					#execution time
					i.setMetric("execution_time", solution.solve_details.time)
					#power consumption
					i.setMetric("power", self.util.getPowerConsumption(i))
					#print("POWER is ",i.power)
				end = time.time()
				solution_time += end - start
			if foundSolution == True:
				#print("Iterations are finished for {} actives RRH".format(len(actives)))
				sucs_reqs += 1
				#gets the best solution
				#for i in self.relaxSolutions.network_states:
				#	print(i.power)
				bestSolution = self.relaxSolutions.getBestNetworkState(self.metric, self.method)
				#print("Best solution is {}".format(bestSolution.solution_values.var_x))
				#now, updates the main network state (so far I am using the on plp file, which is the ILP module file)
				rm.updateRealNetworkState(bestSolution, ilp_module)
				#print("RRHS ON NODES", ilp_module.rrhs_on_nodes)
				#relaxMethod(actives, bestSolution.solution_values, ilp_module)#I commented this line because we only habe to copy each attribute value from bestSolution to ilp_module
				#rm.relaxHeuristic(antenas, bestSolution.solution_values, ilp_module)#think it is not antenas on the parameters, but "actives"
				#updates the execution time of this solution, which is the relaxed ILP solving time + the relaxation scheduling updating procedure
				batch_time.append(solution_time)
				time_b.append(solution_time)
				if r != None:
					r.updateWaitTime(self.env.now+solution.solve_details.time)
				#print("Gen is {} ".format(r.generationTime))
				#print("NOW {} ".format(r.waitingTime))
				if r!= None:
					self.env.process(r.run())
				batch_power_consumption.append(self.util.getPowerConsumption(bestSolution))
				batch_rrhs_wait_time.append(self.averageWaitingTime(actives))
				#URGENTE - MEU ALGORITMO DE PÓS PROCESSAMENTO NÃO FAZ NADA COM ESSA VARIÁVEL, LOGO, ELA SEMPRE ESTARÁ VAZIA
				#ASSIM, PRECISO CRIAR UM MÉTODO PARA VERIFICAR REDIRECIONAMENTO DE DUS E CASO OUTRA VARIÁVEL FIQUE VAZIA PELO
				#ALGORITMO DE PÓS PROCESSAMENTO, CRIAR MÉTODOS PARA CONTABILIZÁ-LA TB
				if solution_values.var_k:
					b_redirected_rrhs.append(len(solution_values.var_k))
				else:
					b_redirected_rrhs.append(0)
				#counts the current activated nodes, lambdas, DUs and switches
				self.countNodes(ilp_module)
				#counting each single vBBU migration - new method - Updated 2/12/2018
				self.extSingleMigrations(bestSolution, bestSolution.old_network_state)
				#count migration only when all load from fog ndoe is migrated - old method
				#self.extMigrations(ilp_module, copy_state)
				for i in bestSolution.nodeState:
					if i == 1:
						count_nodes += 1
				b_activated_nodes.append(count_nodes)
				for i in bestSolution.lambda_state:
					if i == 1:
						count_lambdas += 1
				b_activated_lambdas.append(count_lambdas)
				for i in bestSolution.du_state:
					for j in i:
						if j == 1:
							count_dus += 1
				b_activated_dus.append(count_dus)
				for i in ilp_module.switch_state:
					if i == 1:
						count_switches += 1
				b_activated_switchs.append(count_switches)
				#count DUs and lambdas usage
				if count_lambdas > 0:
					lambda_usage.append((len(actives)*614.4)/(count_lambdas*10000.0))
				if count_dus > 0:
					proc_usage.append(len(actives)/self.getProcUsage(bestSolution))
				print("Found the best solution for {} actives RRHs".format(len(actives)))
				return solution
			else:
				print("No Solution")
				#print(plp.du_processing)
				if r != None:
					rrhs.append(r)
					actives.remove(r)
					np.shuffle(rrhs)
				#print("Batch Blocking")
				#print("Cant Schedule {} RRHs".format(len(actives)))
				#print("Nodes state {}".format(copy_state))
				#print("Lambdas nodes {}".format(cp_l))
				#print("DUs load {}".format(cp_d))
				batch_power_consumption.append(self.util.getPowerConsumption(ilp_module))
				batch_blocking.append(1)

		


	#incremental scheduling
	def incSched(self, r, antenas, ilp_module, incremental_power_consumption, redirected_rrhs, 
		activated_nodes, activated_lambdas, activated_dus, activated_switchs, inc_blocking):
		#global sucs_reqs
		#count_nodes = 0
		#count_lambdas = 0
		#count_dus = 0
		#count_switches = 0
		#print("Calling Incremental")
		#block = 0
		#call the relaxations
		print(ilp_module.rrhs_on_nodes)
		self.runRelaxation(self.relaxHeuristic, self.postProcessingHeuristic, ilp_module, self.metric, self.method, antenas)
		

	#batch scheduling
	def batchSched(self, r, ilp_module, batch_power_consumption,b_redirected_rrhs,
		b_activated_nodes, b_activated_lambdas, b_activated_dus, b_activated_switchs, batch_blocking):
		global sucs_reqs
		#count_nodes = 0
		#count_lambdas = 0
		#count_dus = 0
		#count_switches = 0
		#block = 0
		#call the relaxations
		self.runRelaxation(self.relaxHeuristic, self.postProcessingHeuristic, ilp_module, self.metric, self.method, None, r)
		

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
			#print("Entering batch")
			#calls the batch scheduling
			s = self.batchSched(r, ilp_module,inc_batch_power_consumption,inc_batch_redirected_rrhs,inc_batch_activated_nodes, 
				inc_batch_activated_lambdas,inc_batch_activated_dus,inc_batch_activated_switchs, inc_batch_blocking)
			count_rrhs = 0
		else:
			#print("entrou inc")
			#print(count_rrhs)
			s = self.incSched(r, antenas, ilp_module,inc_batch_power_consumption,inc_batch_redirected_rrhs,inc_batch_activated_nodes, 
				inc_batch_activated_lambdas,inc_batch_activated_dus,inc_batch_activated_switchs, inc_batch_blocking)
			count_rrhs += 1

	#this method performs the incremental scheduling until a certain load of RRHs is activated on the network
	#and above that load, only the batch scheduling is performed
	#the incremental scheduling is only performed again when the load is under certain threshold
	def loadIncBatchSched(self, r, antenas, ilp_module):
		#verifies if is it time to call the batch scheduling
		s = self.incSched(r, antenas, ilp_module,inc_batch_power_consumption,inc_batch_redirected_rrhs,inc_batch_activated_nodes, 
				inc_batch_activated_lambdas,inc_batch_activated_dus,inc_batch_activated_switchs, inc_batch_blocking)
		#if s == None:
		#	print("Trying Batch")
		#	print("Trying again {}".format(r.id))
		#	s = self.batchSched(r, ilp_module,inc_batch_power_consumption,inc_batch_redirected_rrhs,inc_batch_activated_nodes, 
		#		inc_batch_activated_lambdas,inc_batch_activated_dus,inc_batch_activated_switchs, inc_batch_blocking)
		#	if s!= None:
		#		print("Fez o batch")
		#		print(r.id)
		#if len(actives) >= load_threshold:
			#calls the batch scheduling
		#	s = self.batchSched(r, ilp_module,inc_batch_power_consumption,inc_batch_redirected_rrhs,inc_batch_activated_nodes, 
		#		inc_batch_activated_lambdas,inc_batch_activated_dus,inc_batch_activated_switchs)
		#else:
		#	s = self.incSched(r, antenas, ilp_module,inc_batch_power_consumption,inc_batch_redirected_rrhs,inc_batch_activated_nodes, 
		#		inc_batch_activated_lambdas,inc_batch_activated_dus,inc_batch_activated_switchs)

	#count resources during the execution
	def count_inc_resources(self, ilp_module, incremental_power_consumption, activated_nodes, activated_lambdas, activated_dus, activated_switchs):
		count_nodes = 0
		count_lambdas = 0
		count_dus = 0
		count_switches = 0
		incremental_power_consumption.append(self.util.getPowerConsumption(ilp_module))
		self.countNodes(ilp_module)
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
		#count DUs and lambdas usage
		if count_lambdas > 0:
			lambda_usage.append((len(actives)*614.4)/(count_lambdas*10000.0))
		if count_dus > 0:
			proc_usage.append(len(actives)/self.getProcUsage(plp))


	def count_batch_resources(self, ilp_module, batch_power_consumption, b_activated_nodes, b_activated_lambdas, b_activated_dus, b_activated_switchs):
		count_nodes = 0
		count_lambdas = 0
		count_dus = 0
		count_switches = 0
		batch_power_consumption.append(self.util.getPowerConsumption(ilp_module))
		#counts the current activated nodes, lambdas, DUs and switches
		self.countNodes(ilp_module)
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
		#count DUs and lambdas usage
		if count_lambdas > 0:
			lambda_usage.append((len(actives)*614.4)/(count_lambdas*10000.0))
		if count_dus > 0:
			proc_usage.append(len(actives)/self.getProcUsage(plp))


	def count_inc_batch_resources(self, ilp_module, inc_batch_power_consumption,inc_batch_activated_nodes, 
		inc_batch_activated_lambdas,inc_batch_activated_dus,inc_batch_activated_switchs):
		count_nodes = 0
		count_lambdas = 0
		count_dus = 0
		count_switches = 0
		#print("Calling Incremental")
		inc_batch_power_consumption.append(self.util.getPowerConsumption(ilp_module))
		#count the activeresources
		self.countNodes(ilp_module)
		for i in ilp_module.nodeState:
			if i == 1:
				count_nodes += 1
		inc_batch_activated_nodes.append(count_nodes)
		for i in ilp_module.lambda_state:
			if i == 1:
				count_lambdas += 1
		inc_batch_activated_lambdas.append(count_lambdas)
		for i in ilp_module.du_state:
			for j in i:
				if j == 1:
					count_dus += 1
		inc_batch_activated_dus.append(count_dus)
		for i in ilp_module.switch_state:
			if i == 1:
				count_switches += 1
		inc_batch_activated_switchs.append(count_switches)
		#count DUs and lambdas usage
		if count_lambdas > 0:
			lambda_usage.append((len(actives)*614.4)/(count_lambdas*10000.0))
		if count_dus > 0:
			proc_usage.append(len(actives)/self.getProcUsage(ilp_module))

	#starts the deallocation of a request
	def depart_request(self, ilp_module):
		global rrhs
		global served_requests
		#global actives
		while True:
			proc_loads = [0,0,0]
			batch_done = False
			r = yield self.departs.get()
			print("Departing for ",r.id)
			print(r.var_x)
			print(r.node)
			print(r.wavelength)
			print(r.var_x)
			print(r.blocked)
			print("Departing {}".format(r.id))
			self.ilp.deallocateRRH(r)
			#self.ilp.resetValues()
			r.wavelength = None
			r.du = None
			r.node = None
			r.var_x = None
			r.var_u = None
			r.enabled = False
			rrhs.append(r)
			np.shuffle(rrhs)
			actives.remove(r)
			served_requests += 1
			#pdb.set_trace()#debugging breakpoint
			#account resourcesand consumption
			if self.type == "inc":
				self.count_inc_resources(ilp_module, incremental_power_consumption, activated_nodes, activated_lambdas, activated_dus, activated_switchs)
			elif self.type == "batch":
				count_nodes = 0
				count_lambdas = 0
				count_dus = 0
				count_switches = 0
				block = 0
				#print("Size", len(actives))
				#for i in actives:
				#	print(i.id)
				self.runRelaxation(self.relaxHeuristic, self.postProcessingHeuristic, ilp_module, self.metric, self.method)
				'''
				#print("Calling Batch")
				batch_list = copy.copy(actives)
				#batch_list.append(r)
				#actives.append(r)
				self.ilp = plp.ILP(actives, range(len(actives)), plp.nodes, plp.lambdas, True)
				#copy the actual state of nodes to account the possible migrations
				copy_state = copy.copy(plp.nodeState)
				self.ilp.resetValues()
				solution = self.ilp.run()
				if solution == None:
				#	rrhs.append(r)
				#	actives.remove(r)
				#	np.shuffle(rrhs)
					print("Batch Blocking")
					print("Cant Schedule {} RRHs".format(len(actives)))
					batch_power_consumption.append(self.util.getPowerConsumption(plp))
					batch_blocking.append(1)
				else:
					#print(solution.solve_details.time)
					solution_values = self.ilp.return_solution_values()
					self.ilp.updateValues(solution_values)
					batch_time.append(solution.solve_details.time)
					time_b.append(solution.solve_details.time)
				#	r.updateWaitTime(self.env.now+solution.solve_details.time)
					#print("Gen is {} ".format(r.generationTime))
					#print("NOW {} ".format(r.waitingTime))
				#	self.env.process(r.run())
					#print("After Load balancing")
					#print(plp.nodeState)
					#print(len(actives))
					#print("Nodes actives are: {}".format(plp.nodeState))
					#print("Lambdas actives are: {}".format(plp.lambda_node))
					#print("DUs load are: {}".format(plp.du_processing))
					#print("Load is {} in {}".format(proc_loads[i], i))
					#print("########")
					#counts the external migrations
					self.extMigrations(plp, copy_state)
					batch_power_consumption.append(self.util.getPowerConsumption(plp))
					batch_rrhs_wait_time.append(self.averageWaitingTime(actives))
					if solution_values.var_k:
						b_redirected_rrhs.append(len(solution_values.var_k))
					else:
						b_redirected_rrhs.append(0)
					#counts the current activated nodes, lambdas, DUs and switches
					for i in plp.nodeState:
						if i == 1:
							count_nodes += 1
					b_activated_nodes.append(count_nodes)
					for i in plp.lambda_state:
						if i == 1:
							count_lambdas += 1
					b_activated_lambdas.append(count_lambdas)
					for i in plp.du_state:
						for j in i:
							if j == 1:
								count_dus += 1
					b_activated_dus.append(count_dus)
					for i in plp.switch_state:
						if i == 1:
							count_switches += 1
					b_activated_switchs.append(count_switches)
					#batch_done = True
					#count DUs and lambdas usage
					if count_lambdas > 0:
						lambda_usage.append((len(actives)*614.4)/(count_lambdas*10000.0))
					if count_dus > 0:
						proc_usage.append(len(actives)/self.getProcUsage(plp))
				#self.count_batch_resources(plp,batch_power_consumption, b_activated_nodes, b_activated_lambdas, b_activated_dus, b_activated_switchs)
				'''
			elif self.type == "inc_batch":
				self.count_inc_batch_resources(plp, inc_batch_power_consumption,inc_batch_activated_nodes, 
		inc_batch_activated_lambdas,inc_batch_activated_dus,inc_batch_activated_switchs)
			elif self.type == "load_inc_batch":
				self.count_inc_batch_resources(plp, inc_batch_power_consumption,inc_batch_activated_nodes, 
			inc_batch_activated_lambdas,inc_batch_activated_dus,inc_batch_activated_switchs)
			#new line - verify if some node is light loaded
			for i in range(len(plp.du_processing)):
				#print(proc_loads)
				proc_loads[i] = (sum(plp.du_processing[i]))/ sum(plp.dus_total_capacity[i])
			for i in range(len(proc_loads)):
				if proc_loads[i] >= network_threshold and proc_loads[i] < 1.0 and batch_done == False: #adicionei and self.type != "batch", pois o batch ja faz o 
				#load balancing sempre que alguém sai da rede (se der algum problema, tirar essa linha que disse que adicionei (and self.type != "batch"))
					self.check_load.put(r)
					#print("NODE {} STARTING LOAD BALANCING".format(i))
					batch_done = True
				else:
					pass
					#print("Normal Operation")

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
		self.fog = None
		self.node = None
		self.wavelength = None
		self.du = None
		self.blocked = False

	#updates the generation time
	def updateGenTime(self, gen_time):
		self.generationTime = gen_time

	#updates the waiting time
	def updateWaitTime(self, wait_time):
		self.waitingTime = wait_time - self.generationTime

	def run(self):
		t = np.uniform((next_time -self.env.now)/4, next_time -self.env.now)
		#t = np.expovariate(1/1000)
		#print("Interval time is {}".format(next_time -self.env.now))
		#print("Service is {}".format(t))
		yield self.env.timeout(t)
		self.cp.departs.put(self)
		#print("Put on depart RRH {}".format(self.id))

#Utility class
class Util(object):

	#to count the usage of wavelengthson each solution
	def wavelengthUsage(self, ilp_module):
		pass

	#print all active nodes
	def printActiveNodes(self):
		for i in pns:
			if i.state == 1:
				i.printNode()

	#create a list of RRHs with its own connected processing nodes
	def createRRHs(self, amount,env, service_time, cp):
		#rrhs = []
		#for i in range(amount):
		#	r = RRH(i, [1,0,0,0,0], env, service_time, cp)
		#	rrhs.append(r)
		#self.setMatrix(rrhs)
		#return rrhs

		rrhs = []
		for i in range(amount):
			r = RRH(i, [1,0,0], env, service_time, cp)
			rrhs.append(r)
		self.setMatrix(rrhs)
		self.fogNodeRRH(rrhs)
		return rrhs

	#update which is the fog node of each RRH
	def fogNodeRRH(self, rrhs):
		for r in rrhs:
			for i in range(len(r.rrhs_matrix)):
				if i != 0 and r.rrhs_matrix[i] == 1:
					r.fog = i

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

		avg_total_allocated = []

		total_service_availability = []
		avg_service_availability = []

		count_ext_migrations = []
		lambda_usage = []
		avg_lambda_usage = []
		proc_usage = []
		avg_proc_usage = []

		external_migrations = 0
		internal_migrations = 0
		avg_external_migrations = []
		avg_internal_migrations = []
		served_requests = 0
		
		daily_migrations = 0

		act_cloud = []
		act_fog = []
		avg_act_cloud = []
		avg_act_fog = []

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

		#variables for counting the blocking
		inc_blocking = []
		total_inc_blocking = []
		batch_blocking = []
		total_batch_blocking  = []
		inc_batch_blocking = []
		total_inc_batch_blocking = []

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
	#def countNodes(self, ilp):
	#	global act_cloud, act_fog
	#	for i in range(len(ilp.nodeState)):
	#		if ilp.nodeState[i] == 1:
	#			if i == 0:
	#				act_cloud.append(1)
	#			else:
	#				act_fog.append(1)


#Relaxation testing
number_of_rrhs = 15
util = Util()
env = simpy.Environment()
cp = Control_Plane(env, plp, util, "batch", 1, "firstFitRelaxMinVPON", "mostProbability", "power", "min")
rrhs = util.createRRHs(number_of_rrhs, env, service_time, cp)
#sim.rrhs = u.newCreateRRHs(number_of_rrhs, env, sim.service_time, cp)
np.shuffle(rrhs)
t = Traffic_Generator(env, distribution, service_time, cp)
print("\Begin at "+str(env.now))
env.run(until = 86401)
print("\End at "+str(env.now))
print("#|#|#|#|#|#|#|#|#|#|#|#|#|#|#|#|#|#|#|#|#|#|#|#|##|#|#|#|")



'''
#Testing
util = Util()
u = plp.Util()
number_of_rrhs = 20
env = simpy.Environment()
cp = Control_Plane(env, util, "batch")
rrhs = util.createRRHs(number_of_rrhs, env, service_time, cp)
for i in rrhs:
	print(i.rrhs_matrix)
actives = rrhs
cp.batchSched2(rrhs, plp)
'''



#sim.rrhs = u.newCreateRRHs(number_of_rrhs, env, sim.service_time, cp)
#np.shuffle(rrhs)
#t = Traffic_Generator(env, distribution, service_time, cp)
#print("\Begin at "+str(env.now))
#env.run(until = 86401)
#print("\End at "+str(env.now))

'''





u = plp.Util()
#antenas = u.newCreateRRHs(1000, None, None, None)
#np.shuffle(antenas)
ilp = plp.ILP(rrhs, range(len(rrhs)), plp.nodes, plp.lambdas, True)
s = ilp.run()
print(s)
#sol = ilp.return_solution_values()
dec = ilp.return_decision_variables()
#for i in dec.var_x:
#	print(i)
#ilp.print_var_values()
#ilp.updateValues(sol)
#for i in ilp.y:
#	print("{} is {}".format(ilp.y[i],ilp.y[i].solution_value))
print("Solving time: {}".format(s.solve_details.time))
#for x in dec.var_x:
#	print(x, dec.var_x[x].solution_value)
rlx.mostProbability(dec,ilp)
#for i in dec.var_x:
#	print(i[0])
ilp.relaxUpdate(dec)
'''





















#util = Util()
#env = simpy.Environment()
#cp = Control_Plane(env, util, "inc")
#cp.getProcUsage(plp)
#rrhs = util.createRRHs(10, env, service_time, cp)
#np.shuffle(rrhs)
#t = Traffic_Generator(env, distribution, service_time, cp)
#print("\Begin at "+str(env.now))
#env.run(until = 86401)
#print("\End at "+str(env.now))
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
#for i in loads:
#	print(i)