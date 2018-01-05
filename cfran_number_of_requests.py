import simpy
import functools
import random
import time
from enum import Enum
 

class Traffic_Generator(object):
    #constructor
    def __init__(self, env, id, distribution_type, packet_size):
        self.env = env
        self.id = id
        self.distribution_type = distribution_type
        self.packet_size = packet_size
        self.packet_generated = 0
        self.hold = simpy.Store(self.env)
        #self.num_requests = number_of_requests
        self.action = env.process(self.traffic_generation())
 
    #Main method, generates packets considering the time returned from the distribution
    def traffic_generation(self):
        global id_generated_packet
        global total_requests
        #Always running
        self.packet_id = 0
        print("Started Traffic Generator " + str(self.id) + " At Time " + str(self.env.now))
        #reqs = 0
        #while True:
        #while total_requests >  id_generated_packet: #It was while True
            #Wait for the time to generate the packet
        yield self.env.timeout(self.distribution_type(self))
        packet = Packet(env, id_generated_packet, self.packet_size, self.env.now)
            #store the generated packet to be retrieved by the RRH
        self.hold.put(packet)
        self.packet_generated += 1
        id_generated_packet += 1
            #total_requests -= 1
            #self.packet_id += 1
            #reqs += 1
       
 
#Packet Class
class Packet(object):
    def __init__(self, env, packet_id, packet_size, packet_time_of_generation):
        self.env = env
        self.id = packet_id
        self.size = packet_size
        self.time_of_generation = packet_time_of_generation
 
#Packets generation example
class RRH(Traffic_Generator):
    def __init__(self, env, rrh_id, dist):
        self.env = env
        self.dist = dist
        self.rrh_id = rrh_id
        self.traffic_generator = Traffic_Generator(self.env, self.rrh_id, self.dist, 614.4,)
        self.hold = simpy.Store(self.env) #to store the packet received and pass it to the ONU
    #run and generate packets
    def run(self):
        #while True: #It was while True
            #print("Started Receiving Packets from Traffic Generator at " + str(self.env.now))
        packet = yield self.traffic_generator.hold.get()
        print("RRH " +str(self.rrh_id)+ " Got packet " + str(packet.id) + " of Size "+str(packet.size)+ " At Time " + str(self.env.now))
        self.hold.put(packet)

#Packet Generator - Control the generation of packets based on a quantity to be generated
#class Packet_Generator(object):
 #   def __init__(self, env, rrhs, number_of_requests):
  #      self.env = env
   #     self.rrhs = rrhs
    #    self.number_of_requests = number_of_requests
     #   self.action = env.process(self.generate())

    #generate specific amount of packets regarding number_of_requests
    #def generate(self):
     #   reqs = 0;
      #  while reqs <= self.number_of_requests:
       #     rrhs.run()

#This class represents an Optical Network Unit that is connected to one or more RRHs
class ONU(object):
    def __init__(self, env, onu_id, rrh, enabled):
        self.env = env
        self.onu_id = onu_id
        self.rrh = rrh
        self.enabled = enabled
        self.action = env.process(self.run())

    #run method
    def run(self):
        while True:
            packet = yield self.rrh.hold.get()
            print("ONU "+str(self.onu_id)+ " has Packet " +str(packet.id)+ " From RRH "+str(self.rrh.rrh_id))
            request = Request(env, self.onu_id, "Cloud", packet)
            #print("Generated VPON request "+str(request.id))

#This class represents a VPON request
class Request(object):
    def __init__(self, env, src, dst, packet):
        self.env = env
        self.src = src
        self.dst = self.packet = packet
        self.id =  self.packet.id

#This class represents a VPON
class VPON(object):
    def __init__(self, env, vpon_id, wavelength, vpon_capacity, vpon_du):
        self.env = env
        self.vpon_id = vpon_id
        self.vpon_wavelength = wavelength #operating wavelength of this VPON
        self.vpon_capacity = vpon_capacity
        self.vpon_du = vpon_du #DU attached to this vpon
        self.rrhs = [] #rrhs served by this vpon

#This class represents a Digital Unit that deploys baseband processing or other functions
class Digital_Unit(object):
    def __init__(self, env, du_id, processing_capacity):
        self.env = env
        self.du_id = du_id
        #self.du_wavelength = wavelength #initial wavelength of the DU - i.e., when it is first established to a VPON
        self.processing_capacity = processing_capacity #here in terms of number of RRHs (in a spliut scenarion, can be in numbers of CP and UP operations
        self.enabled = False
        self.VPONs = [] #VPONs attached to this DU
        self.processing_queue = []

    #Adds a VPON to the DU
    def addVPON(self, vpon):
        self.VPONs.append(vpon)

    #Starts the DU
    def startDU(self):
        self.enabled = True

    #Turn the DU off
    def endDU(self):
        self.enabled = False

#This class represents a Processing Node
#available wavelengths is the global wavelengths available for use, used is the ones allocated to this node
class Processing_Node(object):
    def __init__(self, env, node_id, node_type, du_amount, available_wavelengths, used_wavelengths):
        self.env = env
        self.node_id = node_id
        self.node_type = node_type
        self.du_amount = du_amount
        self.available_wavelengths = available_wavelengths
        self.used_wavelengths = used_wavelengths
        self.DUs = []
        self.enabled = False

    #Main method
    def run(self):
        pass

    #Activates the processing node
    def startNode(self):
        self.enabled = True

    #Deactivates the processing node
    def endNode(self):
        self.enabled = False

#This class represents the CF-RAN control plane entity that process the requests and activate nodes and VPONs
#It is placed on the cloud
class Control_Plane(object):
    def __init__(self, env, list_of_requests, list_of_nodes, available_wavelengths):
        self.env = env
        self.list_of_requests = list_of_requests
        self.list_of_nodes = list_of_nodes
        self.available_wavelengths = available_wavelengths

    #Heuristic method that receives the traffic load from the RRHs and activate or deactivate nodes
    #and establish or remove VPONs
    def mainHeuristic(self):
        pass

    #Random node activation and VPON creation - Could be a energy efficient node activation but random VPON creation
    def random(self):
        pass

#Simulation main class, initiates all process
class Simulation(object):
    pass

#Class that distributes the traffic to RRHs according to the total traffic pattern
class Load_Distribution(object): #modify to create the ONU, not only the rrh
    def __init__(self, env, traffic_pattern, rrhs):#traffic pattern is the load of a given time, rrhs is the total
    #number of rrhs regarding the full load scenatio
        self.env = env
        self.traffic_pattern = traffic_pattern
        self.rrhs = rrhs
        self.action = self.env.process(self.run())
        self.traffic = []

    def run(self):
        t = 0
        p = 0
        while self.traffic_pattern > t:
            #rrh generates cpri traffic
            print("Pop Element")
            r = self.rrhs.pop()
            self.action2 = self.env.process(r.run())
            t += 614.4
            pck = yield r.hold.get()
            self.traffic.append(pck)
            p += 1
        print(str(p)+ " Packets stored")

#Main loop
# environment
env = simpy.Environment()
#distribution time
distribution = lambda x: random.expovariate(10)
#distribution = lambda x: 1
#number of total requests to be generated
global total_requests
total_requests = 100000
global id_generated_packet
id_generated_packet = 1
rs = []
#tg = Traffic_Generator(env, 1, distribution, 614.4, total_requests)
#tg2 = Traffic_Generator(env, 2, distribution, 614.4)
#rrh = RRH(env, 1, distribution)
#rrh2 = RRH(env, 2, distribution)
#onu = ONU(env, "C3PO", rrh, True)
#env.process(rrh.run())
#env.process(rrh2.run())
#env.process(onu.run())
for i in range (100):
    r = RRH(env, i, distribution)
    rs.append(r)
load = Load_Distribution(env, 61440, rs)

print("\tBegin at " + str(env.now))
env.run()
#print("Total of packets generated on RRH " +str(rrh.rrh_id)+" : " +str(rrh.traffic_generator.packet_generated))
#print("Total of packets generated on RRH " +str(rrh2.rrh_id)+" : " +str(rrh2.traffic_generator.packet_generated))
print("\tEnd at " + str(env.now))
