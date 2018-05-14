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
			global activated_nodes
			global activated_dus
			global activated_lambdas
			global activated_switchs
			global b_activated_nodes
			global b_activated_dus
			global b_activated_lambdas
			global b_activated_switchs
			global redirected_rrhs
			global b_redirected_rrhs
			global time_inc
			global time_b
			global count_cloud
			global count_fog
			global b_count_cloud
			global b_count_fog
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
			#calculates the average of activation of both cloud and fog nodes
			#activation of cloud nodes
			if self.cp.type == "inc_batch":
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
				if power_consumption:
					average_power_consumption.append(round(numpy.mean(power_consumption),4))
					power_consumption = []
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
				#count the resources for batch case
				#activated nodes for the incremental case
			elif self.cp.type == "inc":
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
			self.action = self.action = self.env.process(self.run())
			print("Arrival rate now is {} at {} and was generated {}".format(arrival_rate, self.env.now/3600, total_period_requests))
			total_period_requests = 0

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
		while True:
			if self.type == "inc_batch":
				count_nodes = 0
				count_lambdas = 0
				count_dus = 0
				count_switches = 0
				count_rrhs = 0
				#to count the activated fog nodes on the solution
				fog = 0
				b_fog = 0
				#create a list for the incremental with batch solution
				batch_list = []
				#list for the only incremental solution
				only_inc_list = []
				r = yield self.requests.get()
				#create a list containing the rrhs
				antenas = []
				antenas.append(r)
				#put the rrh on the batch list for the batch scheduling
				#batch_list.append(r)
				#print("Allocating request {}".format(r.id))
				#as soon as it gets the request, allocates it into a RRH
				#if x RRHs are active, calls the batch, else, continues running the incremental
				#----------------------CALLS THE ILP-------------------------
				if count_rrhs < 20:
					self.ilp = plp.ILP(antenas, range(len(antenas)), plp.nodes, plp.lambdas)
					#print("Calling ILP")
					#calling the incremental ILP
					s = self.ilp.run()
					if s != None:
						#print("Optimal solution is: {}".format(s.objective_value))
						sol = self.ilp.return_solution_values()
						self.ilp.updateValues(sol)
						#take the time spent on the solution
						time_inc.append(s.solve_details.time)
						#count the type of activated nodes
						for i in range(len(plp.nodeState)):
							if plp.nodeState[i] == 1:
								if i == 0:
									count_cloud.append(1)
								else:
									fog += 1
							count_fog.append(fog)
						for i in antenas:
							self.env.process(i.run())
							actives.append(i)
							#print("ACTIVE IS {}".format(len(actives)))
							antenas.pop()
							count_rrhs += 1
							power_consumption.append(self.util.getPowerConsumption(plp))
						if redirected_rrhs:
							redirected_rrhs.append(sum((redirected_rrhs[-1], len(sol.var_k))))
						else:
							redirected_rrhs.append(len(sol.var_k))
						#counts the current activated nodes, lambdas, DUs and switches
						for i in plp.nodeState:
							if i == 1:
								count_nodes += 1
						activated_nodes.append(count_nodes)
						for i in plp.lambda_state:
							if i == 1:
								count_lambdas += 1
						activated_lambdas.append(count_lambdas)
						for i in plp.du_state:
							for j in i:
								if j == 1:
									count_dus += 1
						activated_dus.append(count_dus)
						for i in plp.switch_state:
							if i == 1:
								count_switches += 1
						activated_switchs.append(count_switches)
					else:
						#print("Can't find a solution!! {}".format(len(rrhs)))
						rrhs.append(r)
						np.shuffle(rrhs)
						antenas.pop()
						incremental_blocking +=1
				else:
					count_rrhs = 0
					#calls the batch ilp
					count_nodes = 0
					count_lambdas = 0
					count_dus = 0
					count_switches = 0
					batch_list = copy.copy(actives)
					batch_list.append(r)
					#creates the input rrhs taking all that are active
					#for i in actives:
					#	copy_of_rrh = copy.copy(i)
					#	batch_list.append(copy_of_rrh)
					#if s == None:
					#	copy_of_r = copy.copy(r)
					#	batch_list.append(copy_of_r)
					self.ilpBatch = plp.ILP(batch_list, range(len(batch_list)), plp.nodes, plp.lambdas)
					#reset the data structure values to find the optimal solution
					self.ilpBatch.resetValues()
					b_s = self.ilpBatch.run()
					if b_s != None:
						#take the time spent on the solution
						time_inc.append(b_s.solve_details.time)
						b_sol = self.ilpBatch.return_solution_values()
						self.ilpBatch.updateValues(b_sol)
						power_consumption.append(self.util.getPowerConsumption(plp))
						#count the occurrence of cloud and fog nodes activated
						for i in range(len(plp.nodeState)):
							if plp.nodeState[i] == 1:
								if i == 0:
									count_cloud.append(1)
								else:
									fog += 1
							count_fog.append(fog)
						#counts the current activated nodes, lambdas, DUs and switches
						if redirected_rrhs:
							redirected_rrhs.append(sum((redirected_rrhs[-1], len(b_sol.var_k))))
						else:
							redirected_rrhs.append(len(b_sol.var_k))
						for i in plp.nodeState:
							if i == 1:
								count_nodes += 1
						activated_nodes.append(count_nodes)
						for i in plp.lambda_state:
							if i == 1:
								count_lambdas += 1
						activated_lambdas.append(count_lambdas)
						for i in plp.du_state:
							for j in i:
								if j == 1:
									count_dus += 1
						activated_dus.append(count_dus)
						for i in plp.switch_state:
							if i == 1:
								count_switches += 1
						activated_switchs.append(count_switches)
						#self.ilpBatch.resetValues()
						#print("batch {}".format(lp.du_processing))
						#finally, put the RRH that triggered the batch execution to run
						self.env.process(r.run())
						actives.append(r)
						batch_list = []
					else:
						#print("Cant Batch allocate")
						#print(plp.lambda_node)
						batch_blocking += 1
			elif self.type == "inc":
				count_nodes = 0
				count_lambdas = 0
				count_dus = 0
				count_switches = 0
				count_rrhs = 0
				#to count the activated fog nodes on the solution
				fog = 0
				b_fog = 0
				#create a list for the incremental with batch solution
				batch_list = []
				#list for the only incremental solution
				only_inc_list = []
				r = yield self.requests.get()
				#create a list containing the rrhs
				antenas = []
				antenas.append(r)
				#now, run the incremental alone
				#-----------#-----------------
				#as soon as it gets the request, allocates it into a RRH
				#----------------------CALLS THE ILP-------------------------
				#only_inc_list.append(copy.copy(r))
				self.ilp = lp.ILP(antenas, range(len(antenas)), lp.nodes, lp.lambdas)
				#print("Calling ILP")
				#calling the incremental ILP
				s = self.ilp.run()
				if s != None:
					#print("Optimal solution is: {}".format(s.objective_value))
					sol = self.ilp.return_solution_values()
					self.ilp.updateValues(sol)
					#take the time spent on the solution
					time_b.append(s.solve_details.time)
					#count the type of activated nodes
					for i in range(len(lp.nodeState)):
						if lp.nodeState[i] == 1:
							if i == 0:
								b_count_cloud.append(1)
							else:
								fog += 1
						b_count_fog.append(fog)
					for i in antenas:
						self.env.process(i.run())
						actives.append(i)
						#print("ACTIVE IS {}".format(len(actives)))
						antenas.pop()
						count += 1
						batch_power_consumption.append(self.util.getPowerConsumption(lp))
					if b_redirected_rrhs:
						b_redirected_rrhs.append(sum((b_redirected_rrhs[-1], len(sol.var_k))))
					else:
						b_redirected_rrhs.append(len(sol.var_k))
					#counts the current activated nodes, lambdas, DUs and switches
					for i in lp.nodeState:
						if i == 1:
							count_nodes += 1
					b_activated_nodes.append(count_nodes)
					for i in lp.lambda_state:
						if i == 1:
							count_lambdas += 1
					b_activated_lambdas.append(count_lambdas)
					for i in lp.du_state:
						for j in i:
							if j == 1:
								count_dus += 1
					b_activated_dus.append(count_dus)
					for i in lp.switch_state:
						if i == 1:
							count_switches += 1
					b_activated_switchs.append(count_switches)
				else:
					#print("Can't find a solution!! {}".format(len(rrhs)))
					rrhs.append(r)
					np.shuffle(rrhs)
					antenas.pop()
					incremental_blocking +=1
					#print("Inc blocking")
				#print(lp.du_processing)
				#calls the batch ilp
				count_nodes = 0
				count_lambdas = 0
				count_dus = 0
				count_switches = 0




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
			r = RRH(i, [1,0,0,0,0,0,0,0,0,0], env, service_time, cp)
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




util = Util()
env = simpy.Environment()
cp = Control_Plane(env, util, "inc")
rrhs = util.createRRHs(25, env, service_time, cp)
np.shuffle(rrhs)
t = Traffic_Generator(env, distribution, service_time, cp)
print("\Begin at "+str(env.now))
env.run(until = 86401)
#print("Total generated requests {}".format(t.req_count))
#print("Allocated {}".format(total_aloc))
#print("Optimal solution got: {}".format(op))
#print("Non allocated {}".format(total_nonaloc))
#print("Size of Nonallocated {}".format(len(no_allocated)))
print("\End at "+str(env.now))
#print(len(actives))
#print(lp.du_processing)
#print(lp.wavelength_capacity)
#print(lp.rrhs_on_nodes)
#print("Daily power consumption (Incremental) were: {}".format(average_power_consumption))
#print("Daily power consumption (Batch) were: {}".format(batch_average_consumption))
#print("Inc redirection {}".format(average_redir_rrhs))
#print("Batch redirection {}".format(b_average_redir_rrhs))

#---------------------------NEW RUN------------------------------------------
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



env = simpy.Environment()
cp = Control_Plane(env, util, "inc_batch")
rrhs = util.createRRHs(40, env, service_time, cp)
np.shuffle(rrhs)
t = Traffic_Generator(env, distribution, service_time, cp)
print("\Begin at "+str(env.now))
env.run(until = 86401)
#print("Total generated requests {}".format(t.req_count))
#print("Allocated {}".format(total_aloc))
#print("Optimal solution got: {}".format(op))
#print("Non allocated {}".format(total_nonaloc))
#print("Size of Nonallocated {}".format(len(no_allocated)))
print("\End at "+str(env.now))

#print(average_power_consumption)
#print("--------")
#print(batch_average_consumption)
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
print(average_act_switch)
print(average_redir_rrhs)
print("--------")
print(b_average_act_switch)
print(b_average_redir_rrhs)
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
plt.savefig('/home/hextinini/Área de Trabalho/simulador/CFRAN-Simulator/plots/power_consumption.png', bbox_inches='tight')
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
plt.savefig('/home/hextinini/Área de Trabalho/simulador/CFRAN-Simulator/plots/activated_lambdas.png', bbox_inches='tight')
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
plt.savefig('/home/hextinini/Área de Trabalho/simulador/CFRAN-Simulator/plots/activated_nodes.png', bbox_inches='tight')
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
plt.savefig('/home/hextinini/Área de Trabalho/simulador/CFRAN-Simulator/plots/activated_DUs.png', bbox_inches='tight')
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
plt.savefig('/home/hextinini/Área de Trabalho/simulador/CFRAN-Simulator/plots/activated_switches.png', bbox_inches='tight')
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
plt.savefig('/home/hextinini/Área de Trabalho/simulador/CFRAN-Simulator/plots/redirected_rrhs.png', bbox_inches='tight')
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
plt.savefig('/home/hextinini/Área de Trabalho/simulador/CFRAN-Simulator/plots/solution_time.png', bbox_inches='tight')
plt.clf()

