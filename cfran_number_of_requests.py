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
        self.generated_request = False
    #Main method, generates packets considering the time returned from the distribution
    def traffic_generation(self):
        global id_generated_packet
        global total_requests
        #Always running
        self.packet_id = 0
        print("Started Traffic Generator " + str(self.id) + " At Time " + str(self.env.now))
        #reqs = 0
        while self.generated_request == False:
        #while True:
        #while total_requests >  id_generated_packet: #It was while True
            #Wait for the time to generate the packet
            yield self.env.timeout(self.distribution_type(self))
            packet = Packet(env, id_generated_packet, self.packet_size, self.env.now)
                #store the generated packet to be retrieved by the RRH
            self.hold.put(packet)
            self.packet_generated += 1
            id_generated_packet += 1
            total_requests -= 1
            self.packet_id += 1
            #self.generated_request = True
            #reqs += 1
            #self.stop_generating()
    def stop_generating(self):
        self.generated_request = True
       
 
#Packet Class
class Packet(object):
    def __init__(self, env, packet_id, packet_size, packet_time_of_generation):
        self.env = env
        self.id = packet_id
        self.size = packet_size
        self.time_of_generation = packet_time_of_generation
        self.cp = 3
        self.up = 3
 
#Packets generation example
class ONU(object):
    def __init__(self, env, rrh_id, dist, service_time, line_rate, control_plane):
        self.env = env
        self.dist = dist
        self.rrh_id = rrh_id
        self.service = service_time
        self.line_rate = line_rate
        self.traffic_generator = Traffic_Generator(self.env, self.rrh_id, self.dist, self.line_rate)
        self.hold = simpy.Store(self.env) #to store the packet received and pass it to the ONU
        self.action = self.env.process(self.run())
        self.packet_taken = False
        self.cp = control_plane #reference to control plane
        self.reqs = []
        self.node = None #processing node that allocated this onu
        self.alloc = False
        self.vpon = None #vpon that transmits this onu
        self.du = None #du that process this onu
        global onus
        global nodes
    #run and generate packets
    def run(self):
    	global total_packets
    	while True:                
            if self.packet_taken == False:
            	#self.cp.test(self)
            	packet = yield self.traffic_generator.hold.get()
            	#print("RRH " +str(self.rrh_id)+ " Got packet " + str(packet.id) + " of Size "+str(packet.size)+ " At Time " + str(self.env.now))
            	#self.hold.put(packet)
            	self.reqs.append(packet)
            	total_packets += 1
            	#print("Packet Taken")
            	#self.stopGeneration()
            	#print("Propagating...")#time to send the request to the cloud
            	yield self.env.timeout(20000/300000000)
            	self.cp.ffAllocate(self)
            	if self.alloc == True:
            		yield self.env.timeout(self.service(self))
            		self.cp.deallocate(self)
            yield self.env.timeout(self.dist(self))
            #eu poderia criar um evento pra processar a alocação e quando esse evento terminasse, setava
            #a packet_taken como false pro rrh gerar de novo
            #print("No loop do yield")




    #tell traffic generator to not generate
    def stopGeneration(self):
        self.packet_taken = True
    #tell traffic generator to not generate
    def startGeneration(self):
        self.packet_taken = False

    #starts allocation
    def allocate(self, request, nodes):
    	r = request
    	for i in range(len(nodes)):
    		#print(" Accessing pn "+str(nodes[i].node_id))
    		pass
    	print("Allocating request "+str(r.id)+" at "+str(self.env.now))

    def deallocate(self, request):
    	r = request
    	print("Request "+str(r.id)+" Exit the VPON at "+str(self.env.now))


    #starts deallocation
	
            

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
#class ONU(RRH):
 #   def __init__(self, env, onu_id, enabled, distribution, line_rate):
  #      self.env = env
   #     self.hold = simpy.Store(self.env)
    #    self.onu_id = onu_id
     #   self.line_rate = line_rate
      #  self.enabled = enabled
       # self.distribution = distribution
        #self.rrh = RRH(self.env, self.onu_id, self.distribution, self.line_rate)
        #self.action = env.process(self.run())
        #self.reqs = []

    #run method
    #def run(self):
     #   #while True:
      #  packet = yield self.rrh.hold.get()
       # self.rrh.hold.put(packet)
       # #print("ONU "+str(self.onu_id)+ " has Packet " +str(packet.id)+ " From RRH "+str(self.rrh.rrh_id))
       # request = Request(env, self.onu_id, "Cloud", packet, packet.size)
       # self.hold.put(request)
       # self.reqs.append(request)
        #print("ONU " +str(self.onu_id)+" has VPON request "+str(request.id))

    #Starts ONU
    #def starts(self):
    #    self.enabled = True

    #Ends ONU
    #def ends(self):
    #    self.enabled = False

#This class represents a VPON request
class Request(object):
    def __init__(self, env, src, dst, packet, bandwidth):
        self.env = env
        self.src = src
        self.dst = dst
        self.packet = packet
        self.id =  self.packet.id
        self.bandwidth = bandwidth
        self.cp = 3
        self.up = 15

#This class represents a VPON
class VPON(object):
    def __init__(self, env, vpon_id, wavelength, vpon_capacity, vpon_du):
        self.env = env
        self.vpon_id = vpon_id
        self.vpon_wavelength = wavelength #operating wavelength of this VPON
        self.vpon_capacity = vpon_capacity
        self.vpon_du = vpon_du # original DU attached to this vpon
        self.onus = {} #onus served by this vpon, attached by its id
        self.additional_dus = {} #all dus assigned to the vpon

#This class represents a Digital Unit that deploys baseband processing or other functions
class Digital_Unit(object):
    def __init__(self, env, du_id, cp_cap, up_cap):
        self.env = env
        self.du_id = du_id
        #self.du_wavelength = wavelength #initial wavelength of the DU - i.e., when it is first established to a VPON
        #self.processing_capacity = processing_capacity #here in terms of number of RRHs (in a spliut scenarion, can be in numbers of CP and UP operations
        self.enabled = False
        self.VPONs = {} #VPONs attached to this DU indexed by its wavelength
        self.ONUS = {} #onus on this du
        self.processing_queue = []
        self.cp_capacity = cp_cap
        self.up_capacity = up_cap

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
    def __init__(self, env, node_id, du_amount):
        self.env = env
        self.node_id = node_id
        if node_id == 0:
        	self.type = "Cloud"
        else:
        	self.type = "Fog"
        #self.node_type = node_type
        self.du_amount = du_amount
        self.active_dus = {} #list of active DUs on this node, attached to a vpon tha can be used as additional vpons for functions redirection when du of vpon is exhausted in capacity
        #self.available_wavelengths = available_wavelengths
        #self.used_wavelengths = used_wavelengths
        self.DUs = {} #dus instantiated on this node, indexed by its id
        self.VPONs = {} #vpons prsent in this node, indexed by its wavelength
        self.enabled = False
        self.load_power_ratio = 0 #ratio between load and power to the heuristic?
        for i in range(self.du_amount):
        	d = Digital_Unit(self.env, i, 27, 135)
        	self.DUs[i] = d

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
    def __init__(self, env):
        self.env = env
        self.id = "CP 1"

    #allocate a ONU request with first fit policy to the node and the dus and vpon - Put cp and up only on the same du
    def firstFitAllocation(self, onu):
        global nodes
        global wavelengths
        global cpri_line_rate
        global lambda_bit_rate
        global blocked
        o = onu
        #request = yield o.hold.get()
        request = o.reqs.pop()
        o.reqs.append(request)
        #print("Allocating request "+str(request.id))
        allocated = False
        #search the nodes and put the request on the first available
        for i in range(len(nodes)):
                if not allocated:
                        p = nodes[i]#print("Checking node "+str(p.node_id))
                        for j in p.DUs:
                                if not allocated:
                                        d = p.DUs[j]
                                        #verify the cp and up processing availability
                                        if request.cp <= d.cp_capacity and request.up <= d.up_capacity:
                                                #verify the vpons availability
                                                #first verify if there are active vpons to use them first - if not, create a new one
                                                if  bool(p.VPONs) == True:
                                                        #print("There active VPONs in this node")
                                                        #search for a vpon
                                                        for key in p.VPONs:
                                                                v = nodes[i].VPONs[key]
                                                                #verify if vpon has capacity
                                                                if request.size <= v.vpon_capacity:
                                                                        #allocate the request in this vpon
                                                                        v.onus[str(onu.rrh_id)] = request
                                                                        #print("Request "+str(request.id)+" Assigned to VPON "+str(v.vpon_id)+" in DU "+str(d.du_id)+" at node "+str(p.node_id))
                                                                        #allocate the request to this DU
                                                                        d.VPONs[str(v.vpon_id)] = v
                                                                        d.ONUS[str(request.id)] = request
                                                                        #add the du to eh vpon du's list if is a different du from the operating
                                                                        if v.vpon_du.du_id != d.du_id:
                                                                        	print("Additional DU "+str(d.du_id)+" for VPON "+str(v.vpon_id)+" with operating DU "+str(v.vpon_du.du_id))
                                                                        	v.additional_dus[str(d.du_id)] = d
                                                                        v.vpon_capacity -= cpri_line_rate
                                                                        d.cp_capacity -= 3
                                                                        d.up_capacity -= 15
                                                                        o.node = p
                                                                        o.vpon = v
                                                                        o.du = d
                                                                        allocated = True
                                                                        o.alloc = True
                                                                        print("Allocated "+str(request.id)+" !!!")
                                                                        break #eu tirei todos os breaks por conta da verificação do if not allocated já fazer sair do loop - parece estar funcionando corretamente
                                                        if not allocated:
                                                                #print("No room on existing VPONs at node "+str(p.node_id))
                                                                #print("Creating a new VPON on node "+str(p.node_id)+" to DU "+str(d.du_id))
                                                                #create a new vpon if there is wavelength available
                                                                if wavelengths:#print("Creating a new VPON")
                                                                        w = wavelengths.pop()
                                                                        print("Creating new VPON "+str(w)+" on node "+str(p.node_id)+" to DU "+str(d.du_id))
                                                                        vpon = VPON(self.env, str(w), w, lambda_bitrate, d)
                                                                        #put the onu on the vpon
                                                                        vpon.onus[str(onu.rrh_id)] = request
                                                                        #assign vpon to the node
                                                                        p.VPONs[str(w)] = vpon
                                                                        #print("Request "+str(request.id)+" Assigned to VPON "+str(vpon.vpon_id)+" in DU "+str(d.du_id)+" at Node "+str(p.node_id)+" at time "+str(self.env.now))
                                                                        d.VPONs[str(vpon.vpon_id)] = vpon
                                                                        d.ONUS[str(request.id)] = request
                                                                        #add the du to the vpon operating du
                                                                        vpon.vpon_du = d
                                                                        #vpon.additional_dus[str(d.du_id)] = d
                                                                        vpon.vpon_capacity -= cpri_line_rate
                                                                        d.cp_capacity -= 3
                                                                        d.up_capacity -= 15
                                                                        o.node = p
                                                                        o.vpon = vpon
                                                                        o.du = d
                                                                        o.alloc = True
                                                                        allocated = True
                                                                        print("Allocated "+str(request.id)+" !!!")
                                                                        break
                                                                else:
                                                                        pass
                                                                                #there is no available wavelengths to be assigned
                                                                                #print("No wavelength available to new VPON")
                                                else:
                                                        #create a new VPON if there is available wavelengths in general 
                                                        if wavelengths:
                                                                #print("Creating a new VPON on node "+str(p.node_id)+" to DU "+str(d.du_id))
                                                                w = wavelengths.pop()
                                                                print("Creating new VPON "+str(w)+" on node "+str(p.node_id)+" to DU "+str(d.du_id))
                                                                vpon = VPON(self.env, str(w), w, lambda_bitrate, d)
                                                                #put the onu on the vpon
                                                                vpon.onus[str(onu.rrh_id)] = request
                                                                #assign vpon to the node
                                                                p.VPONs[str(w)] = vpon
                                                                #print("Request "+str(request.id)+" Assigned to VPON "+str(vpon.vpon_id)+" in DU "+str(d.du_id)+" at Node "+str(p.node_id)+" at time "+str(self.env.now))
                                                                d.VPONs[str(vpon.vpon_id)] = vpon
                                                                d.ONUS[str(request.id)] = request
                                                                #add the du to eh vpon du's list
                                                                vpon.vpon_du = d
                                                                #vpon.additional_dus[str(d.du_id)] = d
                                                                vpon.vpon_capacity -= cpri_line_rate
                                                                d.cp_capacity -= 3
                                                                d.up_capacity -= 15
                                                                o.node= p
                                                                o.vpon = vpon
                                                                o.du = d
                                                                o.alloc = True
                                                                allocated = True
                                                                print("Allocated "+str(request.id)+" !!!")
                                                                break
                                                        else:
                                                                #there is no available wavelengths to be assigned
                                                                #print("No wavelength available to new VPON")
                                                                pass
                                        else:
                                                pass

                else:
                    break                                    #print("No capacity on this DU "+str(d.du_id)+ " at node "+str(p.node_id))
        if not allocated:
            print("No possible to allocate request "+str(request.id))
            blocked += 1

        #test
    def test(self, onu):
        o = onu
        print("I am ONU "+str(o.rrh_id)+" at "+str(self.id))

    #deallocate ONU from nodes, vpons and du
    def deallocate(self, onu):
        print("Starting deallocating ONU "+str(onu.rrh_id)+" from VPON "+str(onu.vpon.vpon_id))
        global wavelengths
        global cpri_line_rate
        o = onu
        #retrieve the node that this onu is allocated
        node = o.node
        r = o.reqs.pop()
        #remove the request and onu from vpon and du of the node
        v = o.vpon
        del v.onus[str(o.rrh_id)]
        v.vpon_capacity += cpri_line_rate
        d = o.du
        del d.ONUS[str(r.id)]
        d.cp_capacity += 3
        d.up_capacity += 15
        o.node = None
        o.vpon = None
        o.du = None
        o.alloc = False
        print("Removed ONU "+str(o.rrh_id)+" and Request "+str(r.id)+"From VPON "+str(v.vpon_id)+" and DU "+str(d.du_id))


    #first fit with one specific du per vpon (additional du if necesary) - as the majority of papers does
    def ffAllocate(self, onu):
        global deactivated_nodes
        global activated_nodes
        global wavelengths
        global cpri_line_rate
        global lambda_bitrate
        global blocked
        global cp_capacity
        global up_capacity
        request = onu.reqs.pop()
        onu.reqs.append(request)
        #search the activated nodes
        if activated_nodes:
    	    #search the nodes and tries to allocate - if not possible, activates another node - taking the node from the list of deactivated and activatin it - if thsi lsit is empty, there are no more nodes to be activated
    	    print("Tem nó")
    	    #implementar a alocação para quando há nó ativado e ativar nó quando não há capacidade nos disponíveis - sempre criar primeiro o vpon e então colocar o du pra ele - se não tiver du disponível, passa pra outro nó
	    #activate the cloud node
        else:
            p = nodes[0]
            p.startNode
            activated_nodes[str(p.node_id)] = p
            #creates a vpon and put the request into it and on the DU on the cloud
            if wavelengths:
                w = wavelengths.pop()
                vpon = VPON(self.env, str(w), w, lambda_bitrate, None)
                #create the DU for the VPON and index by the wavelength
                d = Digital_Unit(self.env, str(w), cp_capacity, up_capacity)
                #index the du to the vpon
                vpon.vpon_du = d
                vpon.onus[str(onu.rrh_id)] = onu
                #update the vpon and du capacities
                vpon.vpon_capacity -= cpri_line_rate
                vpon.vpon_du.cp_capacity -= 3
                vpon.vpon_du.up_capacity -= 15
                #update information on onu
                onu.node = p
                onu.vpon = vpon
                onu.du = vpon.vpon_du
                onu.alloc = True
                #put the vpon on the node
                p.VPONs[str(w)] = vpon
                #put the du to the lsit of active
                p.active_dus[str(vpon.vpon_du.du_id)] = vpon.vpon_du
                #update the number of available dus on the node
                p.du_amount -= 1
                #remove the node from the list of deactivated nodes
                del deactivated_nodes[str(p.node_id)]
                print("ONU "+str(onu.rrh_id)+" Allocated on Node "+str(p.node_id)+" "+str(p.type)+" on VPON "+str(vpon.vpon_id)+ " in DU "+str(vpon.vpon_du.du_id))
                for k in deactivated_nodes:
                	print(str(deactivated_nodes[k].type))

    #activates the cloud
    def activateCloud(self):
        p = nodes[0]
        p.startNode
        activated_nodes[str(p.node_id)] = p
        del deactivated_nodes[str(p.node_id)]


    #Heuristic method that receives the traffic load from the RRHs and activate or deactivate nodes
    #and establish or remove VPONs
    def mainHeuristic(self):
        pass

    #Random node activation and VPON creation - Could be a energy efficient node activation but random VPON creation
    def random(self):
        pass

#Simulation main class, initiates all process
class Simulation(object):
    def __init__(self, env, onus, traffic_load, cpri_rate):
        self.env = env
        self.traffic_load = traffic_load
        self.cpri_rate = cpri_rate
        self.onus = onus
        load_distributor = Load_Distribution(self.env, self.traffic_load, self.onus)

    def run(self):
        pass


#Class that distributes the traffic to RRHs according to the total traffic pattern
class Load_Distribution(object): #modify to create the ONU, not only the rrh
    def __init__(self, env, traffic_pattern, onus):#traffic pattern is the load of a given time, rrhs is the total
    #number of rrhs regarding the full load scenatio
        self.env = env
        self.traffic_pattern = traffic_pattern
        self.onus = onus
        self.action = self.env.process(self.run())
        self.traffic = []

    def run(self):
        t = 0
        p = 0
        true = 0;
        false = 0;
        #while self.traffic_pattern > t:
        for i in range(len(self.onus)):
            #rrh generates cpri traffic
            if self.traffic_pattern > t:
                #Get the request from ONU
                #o = self.onus[i]
                #Activate the ONU
                self.onus[i].starts()
                #o = self.onus.pop()
                pck = yield self.onus[i].reqs[0]
                self.traffic.append(pck)
                t += pck.bandwidth
                print("Load Distributor has took Request "+str(pck.id)+" From ONU "+str(o.onu_id))
                p += 1
        print(str(p)+ " Requests stored")
        print("Total Network Load for Time " +str(self.env.now)+ " is "+str(self.traffic_pattern/1000)+ " Gbps")
        for i in range(len(self.onus)):
            if self.onus[i].enabled == True:
                true += 1
            else:
                false += 1
            print("ONU "+str(self.onus[i].onu_id)+ " is "+str(self.onus[i].enabled))
        print("Actives ONU "+str(true))
        print("ONUs turned off "+str(false))




#Main loop
# environment
foo_delay = 0.005
env = simpy.Environment()
#distribution time
distribution = lambda x: random.expovariate(10)
srv_time = lambda x: random.expovariate(1)
#number of total requests to be generated
global cp_capacity
cp_capacity = 27
global up_capacity
up_capacity = 135
global activated_nodes
activated_nodes = {}
global total_requests
total_requests = 100000
global id_generated_packet
id_generated_packet = 1
global blocked
blocked = 0
number_onus = 100
number_nodes = 10
rs = []
onus = []
nodes = []
deactivated_nodes = {}
traffic_pattern = 30720
global lambda_bitrate
lambda_bitrate = 10000.0
global cpri_line_rate
cpri_line_rate = 614.4
num_du = 10
num_of_wavelengths = 10
wavelengths = []
for i in range(num_of_wavelengths):
	wavelengths.append(i)
global general_power_consumption
general_power_consumption = 0
global total_packets
total_packets = 0


#rrh2 = RRH(env, 2, distribution,cpri_line_rate)
#onu = ONU(env, "C3PO", rrh, True)
#env.process(rrh.run())
#env.process(rrh2.run())
#env.process(onu.run())
#for i in range (100):
 #   o = ONU(env, i, True, distribution, 614.4)
  #  onus.append(o)

#load = Load_Distribution(env, 61440, onus)
#simulation = Simulation(env, onus, traffic_pattern, cpri_line_rate)

#create the control plane instance
cp = Control_Plane(env)

#creates the RRHs 
for i in range(number_onus):
	r = ONU(env,i,distribution, srv_time, cpri_line_rate, cp)
	onus.append(r)

#create the nodes
for i in range(number_nodes):
	p = Processing_Node(env, i, num_du)
	#print(p.VPONs)
	nodes.append(p)
	deactivated_nodes[str(p.node_id)] = p


print("\tBegin at " + str(env.now))
env.run(until=3600)
#print("Total of packets generated on RRH " +str(rrh.rrh_id)+" : " +str(rrh.traffic_generator.packet_generated))
#print("Total of packets generated on RRH " +str(rrh2.rrh_id)+" : " +str(rrh2.traffic_generator.packet_generated))
print("\tEnd at " + str(env.now))
print("Total packets generated: "+str(total_packets))
print("Total of Blocked Requests: "+str(blocked))
print("Blocking probability: "+str(blocked/total_packets))
#for i in range(len(onus)):
#    print("ONU "+str(onus[i].rrh_id)+" is "+str(onus[i].alloc))
