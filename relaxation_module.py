#this module contains algorithms for the scheduling of the relaxed version of the ILP
from docplex.mp.model import Model
import functools
import random as np
from scipy.stats import norm
import matplotlib.pyplot as plt
import relaxation_test as rlx

#This algorith takes the output of the relaxed ILP (solution object) and treat constraints that
#needed to be removed from the ILP formulation in order to relax the formulation and run it
#It solves the capacities (DU and lambda) and rrh-fog connection constraints
#It returns a new solution object with only possible valid scheduling solutions
def cleanSolution(solution):
	pass

#This algorithms takes solution values and consider them as probabilities
#For each decision variable, it consider the higher value, perform the scheduling and discard the other values for the same variable
#Does this to every variable and DO NOT run the ILP again
def mostProbability(solution, ilp_module):
	pass

#This algorithms takes solutions values and consider them as probabilities
#it takes the first decision variable (in a first-fit manner), consider its higher value and discard the other values for the same variable
#Schedule the decision variable and, outside this function, the relaxation module is executed again, and then, 
#this algorithm is executed for the remaining variables, schedule one, run ILP relaxaed again, and so on
def incMostProbability(solution, ilp_module):
	pass

#This algorithms takes solution values and consider them as probabilities
#For each decision variable, a value between 0 and 1 is sorted from a uniform distribution, find the value of the decision variable where the sorted value fits within 
#(e.g., sorted value is 0.3, variables has 0.1 and 0.5, so we define it will be fit in the interval between the first value and the second, śo, the first value for the decision variable is chosen,
#perform the scheduling and discard the other values for the same variable
#Does this to every variable and DO NOT run the ILP again
def sortProbability(solution, ilp_module):
	pass

#This algorithms takes solutions values and consider them as probabilities
#it takes the first decision variable (in a first-fit manner),a value between 0 and 1 is sorted from a uniform distribution, find the value of the decision variable where the sorted value fits within 
#(e.g., sorted value is 0.3, variables has 0.1 and 0.5, so we define it will be fit in the interval between the first value and the second, śo, the first value for the decision variable is chosen,
# then discard the other values for the same variable
#Schedule the decision variable and, outside this function, the relaxation module is executed again, and then, 
#this algorithm is executed for the remaining variables, schedule one, run ILP relaxaed again, and so on
def incSortProbability(solution, ilp_module):
	pass