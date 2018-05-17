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
import incrementalWithBatchILP as sim

util = sim.Util()

env = simpy.Environment()
cp = sim.Control_Plane(env, util, "inc")
sim.rrhs = util.createRRHs(20, env, sim.service_time, cp)
np.shuffle(sim.rrhs)
t = sim.Traffic_Generator(env, sim.distribution, sim.service_time, cp)
print("\Begin at "+str(env.now))
env.run(until = 86401)
print("\End at "+str(env.now))