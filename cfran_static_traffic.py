import simpy
import functools
import random
import time
from enum import Enum
      

#This class represents an Optical Network Unit that is connected to one or more RRHs
class ONU(object):
    def __init__(self, onu_id, line_rate):
        self.enabled = False
        self.onu_id = onu_id
        self.line_rate = line_rate
        self.reqs = []
        self.vpon = None

    #run method
    def getRequest(self):
        request = Request( self.onu_id, "Cloud", self.line_rate, self.onu_id)
        self.reqs.append(request)

    #Starts ONU
    def starts(self):
        self.enabled = True

    #Ends ONU
    def ends(self):
        self.enabled = False

    #add the ONU's VPON reference to the ONU itself
    def addVPON(self, vpon):
    	self.vpon = vpon

    #print reqs
    def printReqs(self):
        for i in range(len(self.reqs)):
            print("Requisition " +str(self.reqs[i].id))

#This class represents a VPON request
class Request(object):
    def __init__(self,  src, dst, bandwidth):
       
        self.src = src
        self.dst = dst
        #self.id = req_id
        self.bandwidth = bandwidth
        self.cp = 3
        self.up = 15

#This class represents a VPON
class VPON(object):
    def __init__(self,  vpon_id, wavelength, vpon_capacity, vpon_du):
        
        self.vpon_id = vpon_id
        self.vpon_wavelength = wavelength #operating wavelength of this VPON
        self.vpon_capacity = vpon_capacity
        self.vpon_du = vpon_du #DU attached to this vpon
        self.onus = [] #ONUs served by this vpon

#This class represents a Digital Unit that deploys baseband processing or other functions
class Digital_Unit(object):
    def __init__(self, du_id, processing_capacity):
        
        self.du_id = du_id
        #self.du_wavelength = wavelength #initial wavelength of the DU - i.e., when it is first established to a VPON
        self.processing_capacity = processing_capacity #here in terms of number of RRHs (in a spliut scenarion, can be in numbers of CP and UP operations
        self.enabled = False
        self.VPONs = {} #VPONs attached to this DU. The index is the wavelength of the vpon
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
    def __init__(self,  node_id, node_type, du_amount, used_wavelengths):
        
        self.node_id = node_id
        self.node_type = node_type
        self.du_amount = du_amount
        self.used_wavelengths = used_wavelengths
        self.DUs = []
        self.enabled = False
        self.VPONs = {} #List of all vpons on this node (vpons of all DUs), indexed by its wavelength

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
    def __init__(self,list_of_requests, list_of_nodes, available_wavelengths):
        
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
    def __init__(self, env, onus, nodes, traffic_load, cpri_rate):
        self.env = env
        self.traffic_load = traffic_load
        self.cpri_rate = cpri_rate
        self.onus = onus
        self.nodes = nodes
        load_distributor = Load_Distribution(self.env, self.traffic_load, self.onus)

    def run(self):
        pass


#Class that activates the ONUs according to the total traffic pattern
class ONUs_Management(object):
    def __init__(self):
        global nodes
        global onus
        global traffic_pattern
        global cpri_line
        global requests
        #self.onus = onus
        #self.traffic_pattern = traffic_pattern
        #self.cpri_line = cpri_line

    #activates the ONUs according to the given traffic load
    def manageONUs(self, number_of_onus):
        #get the necessarynumber of active ONUs to serve the traffic
        os = number_of_onus
        #activate the necessary onus
        for i in range(len(onus)):
        	if i <= os - 1:
        		if onus[i].enabled == True:
        			pass
        		else:
        			onus[i].starts()
        	else:
        		onus[i].ends()

    def verifyEnabled(self):
        t = 0;
        f = 0;
        for i in range(len(onus)):
            if onus[i].enabled == True:
                t += 1       
            else:
                f += 1
        print("There are " +str(t)+ " active ONUs and "+str(f)+" deactivated ONUs")

    #removes an ONU from a VPON
    def removeONUfromVPON(self):
    	#take the off ONUs, take its processing node, search for the VPON and remove the ONU from the VPONs ONU's list
    	pass
    	
    #calculates the number of necessary active ONUs
    def numOfActiveONUs(self):
    	num_of_active_onus = []
    	for i in range(len(traffic_pattern)):
    		x = traffic_pattern[i]/cpri_line
    		num_of_active_onus.append(x)
    	return num_of_active_onus

    #get the numer of requests for the given period
    def getRequests(self):	
    	for i in range(len(onus)):
    		if onus[i].enabled == True:
    			r = Request(onus[i].onu_id, None, onus[i].line_rate)
    			requests.append(r)


#Main loop
number_of_onus = 100
cpri_line = 614.4
traffic_pattern = [61440, 30720]
#global variables that will be modified by the heuristics
nodes = []
onus = []
wavelengths = []
number_of_nodes = 2
number_of_dus = 10
requests = []
activated_onus = []
#create the onus
for i in range(100):
    o = ONU(i, cpri_line)
    #print("Created ONU "+str(o.onu_id))
    #print("ONU "+str(o.onu_id)+ " is "+str(o.enabled))
    onus.append(o)
    #o.getRequest()
    #o.printReqs()

#create the nodes
for i in range(number_of_nodes):
	if i < 1:
		#cloud node
		p = Processing_Node(i, "Cloud", number_of_dus, used_wavelengths = [])
		nodes.append(p)
	else:
		#fog node
		p = Processing_Node(i, "Fog", number_of_dus, used_wavelengths = [])
		nodes.append(p)
om = ONUs_Management()
#x = om.numOfActiveONUs()
#for i in range(len(x)):
	#print(str(x[i]))
om.manageONUs(50)
#om.getRequests()
#for i in range(len(requests)):
	#print(str(requests[i].src))
om.verifyEnabled()
om.manageONUs(70)
om.verifyEnabled()
#om.manageONUs(3)
#om.verifyEnabled()
#om.manageONUs(10)
#om.verifyEnabled()
#om.manageONUs(1)
#om.verifyEnabled()
#om.manageONUs(0)
#om.verifyEnabled()
#om.manageONUs(100)
#om.verifyEnabled()