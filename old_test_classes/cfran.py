import simpy
import functools
import random
import time
from enum import Enum

#ONU class
class Traffic(object):
    def __init__ (self, env, dist, line_rate):
        self.env = env
        self.dist = dist
        self.line_rate = line_rate
        self.requests = simpy.Store(self.env)
        self.action = self.env.process(self.run())
        self.generated = False
    #generate traffic
    def run(self):
        while True:
            #if self.generated == False:
            yield self.env.timeout(self.dist(self))
            req = Request(self.env, self.id, self.line_rate)
            self.requests.put(req)
            print("To aqui")
            #else:
                #continue

#ONU class
class ONU(Traffic):
    def __init__(self, env, onu_id, dist, line_rate):
        Traffic.__init__(self, env, dist, line_rate)
        self.onu_id = onu_id
        #self.action = self.env.process(self.run())

    #gets its request
    def run(self):
        r = yield self.requests.get()
        self.allocate(r)
        yield self.env.timeout(self.dist(self))
        self.deallocate(r)

    #starts allocation
    def allocate(self, request):
        r = request
        print("Starting allocation of "+str(r.id))

    #starts deallocation
    def deallocate(self, request):
        r = request
        print(str(r.id)+" is exiting the VPON")

#a request
class Request(object):
    def __init__(self, env, req_id, line_rate):
        self.env = env
        self.id = req_id
        self.line_rate = line_rate


#main loop
env = simpy.Environment()
distribution = lambda x: random.expovariate(10)
num_onus = 10
o = ONU(env, 1, distribution, 614.4)
env.run()
