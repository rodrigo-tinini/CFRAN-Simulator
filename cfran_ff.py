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
            packet = Packet(env, id_generated_packet, self.packet_size, self.env.now, self.id)
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
    def __init__(self, env, packet_id, packet_size, packet_time_of_generation, onu_id):
        self.env = env
        self.id = packet_id
        self.size = packet_size
        self.time_of_generation = packet_time_of_generation
        self.onu = onu_id
        for i in range(3):
        	cp = CP_Processing(self.env, i, self.onu)
        	self.cp_functions.insert(i, cp)
        for i in range(3):
        	up = UP_Processing(self.env, i, self.onu)
        	self.up_functions.insert(i, up)
 
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
        self.enabled = False
        self.processing_queue = []
        self.cp_capacity = cp_cap
        self.up_capacity = up_cap
        self.allocated_ups = {} #list of ups allocated indexed by its onu
        self.allocated_cps = {} #list of cps allocated indexed by its onu


    #Starts the DU
    def startDU(self):
        self.enabled = True

    #Turn the DU off
    def endDU(self):
        self.enabled = False

#this class represents a single up processing function
class UP_Processing(object):
	def __init__(self, env, up_id, onu):
		self.env = env
		self.id = up_id
		self.onu = onu

#this class represents a single up processing function
class CP_Processing(object):
	def __init__(self, env, cp_id, onu):
		self.env = env
		self.id = up_id
		self.onu = onu

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
        self.VPONs = [] #vpons prsent in this node, indexed by its wavelength
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
        allocated = False
        request = onu.reqs.pop()
        onu.reqs.append(request)
        #search the activated nodes
        if activated_nodes:
            #search the nodes and tries to allocate - if not possible, activates another node - taking the node from the list of deactivated and activating it - if thsi lsit is empty, there are no more nodes to be activated
            print("Tem nó")
            #implementar a alocação para quando há nó ativado e ativar nó quando não há capacidade nos disponíveis - sempre criar primeiro o vpon e então colocar o du pra ele - se não tiver du disponível, passa pra outro nó
            #activate the cloud node
            for i in range(len(activated_nodes)):
                p = activated_nodes[i]
                #tries to allocate on this node
                #first check the vpons
                if p.VPONs:
                	#check all vpons and allocates on the first possible
                	if not allocated:
	                	for i in range(len(p.VPONs)):
	                		vpon = p.VPONs[i]
	                		if vpon.vpon_capacity >= request.size:
	                			#tries to allocate on the vpons du
	                			if vpon.vpon_du.cp_capacity >= request.cp:
	                				if vpon.vpon_du.up_capacity >= len(request.up):
	                					#put each cp and up function on the du
	                					for i in range(len(request.cp)):

	                					vpon.vpon_du.cp_capacity -= 3
                                    	vpon.vpon_du.up_capacity -= 15




	                				#the vpon du fits the cp and up, put the request on this du and confirms the allocation to the vpon
	                				vpon.onus[str(onu.rrh_id)] = onu
	                				vpon.vpon_du.cp_capacity -= 3
                                    vpon.vpon_du.up_capacity -= 15
                                    #update information on onu
					                onu.node = p
					                onu.vpon = vpon
					                onu.du = vpon.vpon_du
					                onu.alloc = True
					                #put the vpon on the node
					                p.VPONs.append(vpon)
					                #put the du to the lsit of active
					                p.active_dus[str(vpon.vpon_du.du_id)] = vpon.vpon_du
					                allocated = True
					                break
					            else: #try to put the cp on the original du or in other if is the case - same with du
					            	
                else:
                #no vpons
                pass	

        else:
            p = nodes[0]
            p.startNode
            activated_nodes.insert(p.node_id, p)
            #creates a vpon and put the request into it and on the DU on the cloud
            if wavelengths:
                w = wavelengths.pop()
                vpon = VPON(self.env, str(w), w, lambda_bitrate, None)
                #create the DU for the VPON and index by the wavelength
                #d = Digital_Unit(self.env, str(w), cp_capacity, up_capacity)
                #take the du corresponding to the wavelength - in this case the cardinality of vpons and DUs is equal
                d = p.DUs[w]
                #activate du
                d.startDU()
                #index the du to the vpon
                vpon.vpon_du = d
                vpon.onus[str(onu.rrh_id)] = onu
                #put the cps and ups on the du respective list(dictionaries, actually)
                vpond.vpon_du.allocated_cps[str(onu.rrh_id)] = request.cp_functions
                vpond.vpon_du.allocated_ups[str(onu.rrh_id)] = request.up_functions
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
                p.VPONs.append(vpon)
                #put the du to the lsit of active
                p.active_dus[str(vpon.vpon_du.du_id)] = vpon.vpon_du
                #remove the node from the list of deactivated nodes
                del deactivated_nodes[p.node_id]
                print("ONU "+str(onu.rrh_id)+" Allocated on Node "+str(p.node_id)+" "+str(p.type)+" on VPON "+str(vpon.vpon_id)+ " in DU "+str(vpon.vpon_du.du_id))
                for k in deactivated_nodes:
                	print(str(deactivated_nodes[k].type))

    #activates the cloud
    def activateCloud(self):
        p = nodes[0]
        p.startNode
        activated_nodes[str(p.node_id)] = p
        del deactivated_nodes[str(p.node_id)]





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
activated_nodes = []
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
	deactivated_nodes[p.node_id] = p


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
