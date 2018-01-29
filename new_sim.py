import simpy
import functools
import random
import time
from enum import Enum

#number of onus
onus_amount = 10
#number of wavelengths and creation of available wavelengths
lambdas = 10
wavelengths = []
for i in range(lambdas):
	wavelengths.append(i)
#list of network onus
onus = []
#generated requests counter
reqs_gen = 0
#ups number of functions
up_chain = 3
#cpri line rate
cpri_rate = 614.4
#service time of the requisition
service_time = lambda x: random.expovariate(1)
#distribution for arrival of packets
distribution = lambda x: random.expovariate(10)
#environment
env = simpy.Environment()

#request generated by the ONU
class Request(object):
	def __init__(self, env, req_id, onu_id, up_chain, cpri_rate, service_time, nodes):
		self.env = env
		self.id = req_id
		self.onu_id = onu_id
		self.node = None
		self.vpon = None
		self.cpri_rate = cpri_rate
		self.service_time = service_time #time that the requisition remains active on the node
		self.nodes = nodes #list of nodes that are connected to the ONU - for instance, the cloud (for all, and a fog node - 1 fog node at most for each ONU as default)
		self.up_functions = []
		for i in range(up_chain):
			up = UP_Processing(self.env, i, self.id)
			self.up_functions.append(up)
		self.du = []

	#run method - initiates the requisition and after a certain time, starts the deallocation of it - this method is called when the requisition is succesfull allocated
	def run(self):
		yield self.env.timeout(self.service_time(self))
		print("Starts deallocation of "+str(self.id)+" from ONU "+str(self.onu_id)+" at "+str(self.env.now))

#ONU that generates a request
class ONU(object):
	def __init__(self, env, onu_id, distribution, nodes, power_consumption, service_time, control_plane):
		self.env = env
		self.onu_id = onu_id
		self.distribution = distribution #interarrival time of generation of packets
		self.nodes = nodes
		self.power_consumption = power_consumption
		self.service_time = service_time
		self.cp = control_plane
		self.action = self.env.process(self.run())

	#always running - waits for the distribution time interval and generates a request that demands allocation to the control plane
	def run(self):
		global reqs_gen
		while True:
			yield self.env.timeout(self.distribution(self)) #interarrival waiting time
			req = Request(self.env, reqs_gen, self.onu_id, up_chain, cpri_rate, self.service_time, None)
			print("ONU "+str(self.onu_id)+" Generated Requisition "+str(req.id)+" at "+str(self.env.now))
			reqs_gen += 1
			#put request to run
			self.env.process(req.run())


#Processing Node
class Processing_Node(object):
	def __init__(self, env, pn_id, power_consumption):
		self.env = env
		self.id = pn_id
		self.power_consumption = power_consumption
		self.dus = [] #dus of this node
		for i in range(du_amount):
			d = DU(self.env, i, up_capacity, cp_capacity, du_consumption)
			self.dus.append(d)
		self.vpons = [] #list of vpons indexed by its wavelength
		self.enabled = False
		self.power_ratio = 0
		self.network_usage_ratio = 0

	def startNode(self):
		self.enabled = True

	def endNode(self):
		self.enabled = False


#VPON
class VPON(object):
	def __init__(self, env, wavelength, node, du):
		self.env = env
		self.wavelength = wavelength #resonating wavelength of this vpon
		self.node = node #node that hosts this vpon
		self.du = du #hosting du of this vpon
		self.additional_dus = [] #additional dus for redirected traffic, indexed by its id
		self.onus = [] #list of onus allocated on this VPON

#DU
class DU(object):
	def __init__(self, env, du_id, up_capacity, cp_capacity, power_consumption):
		self.env = env
		self.id = du_id
		self.up_capacity = up_capacity
		self.cp_capacity = cp_capacity
		self.enabled = False
		self.up = {} #up functions allocated here, indexed by the requisition id
		self.cp = {} #phycell functions, indexed by the onu id
		self.power_consumption = power_consumption

	def startDU(self):
		self.enabled = True

	def endDU(self):
		self.enabled = False

#UP processing function
class UP_Processing(object):
	def __init__(self, env, up_id, req):
		self.env = env
		self.id = up_id
		self.req = req

#cp processing function object
class CP_Processing(object):
	def __init__(self, env, onu_id):
		self.env = env
		self.onu_id = onu_id

for i in range(onus_amount):
	o = ONU(env, i, distribution, None, 0, service_time, None)
	onus.insert(o.onu_id, o)
env.run()