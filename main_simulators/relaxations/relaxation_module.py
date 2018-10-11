#this module contains algorithms for the scheduling of the relaxed version of the ILP
from docplex.mp.model import Model
import functools
import random as np
import operator
from scipy.stats import norm
import matplotlib.pyplot as plt
import relaxation_test as rlx

#This algorith takes the output of the relaxed ILP (solution object) and treat constraints that
#needed to be removed from the ILP formulation in order to relax the formulation and run it
#It solves the capacities (DU and lambda) and rrh-fog connection constraints
#It returns a new solution object with only possible valid scheduling solutions
def cleanSolution(solution, ilp):
	#take each decision variable from the solution
	x = solution.x
	u = solution.u
	k = solution.k
	rd = solution.rd
	s = solution.s
	e = solution.e
	y = solution.y
	g = solution.g
	xn = solution.xn
	z = solution.z
	#keep keys to remove
	del_keys = []
	#first, discard decision variables  in which the RRH is not connected to the fog node (vars x and u)
	for i in x:
		#print(i)
		#print("{} : {}" .format(x[i],x[i].solution_value))
		if x[i].solution_value > 0 and ilp.fog[i[0]][i[1]] == 0:
			#print("{} : {}".format(antenas[i[0]].id, antenas[i[0]].rrhs_matrix))
			del_keys.append(i)
	for i in del_keys:
		del x[i]
		#print("Removed {}".format(i))
	del_keys = []
	for i in u:
		#print(i)
		#print("{} : {}" .format(x[i],x[i].solution_value))
		if u[i].solution_value > 0 and ilp.fog[i[0]][i[1]] == 0:
			#print("{} : {}".format(antenas[i[0]].id, antenas[i[0]].rrhs_matrix))
			del_keys.append(i)
	for i in del_keys:
		del u[i]
		#print("Removed {}".format(i))
	del_keys = []
	for i in y:
		#print(i)
		#print("{} : {}" .format(x[i],x[i].solution_value))
		if y[i].solution_value > 0 and ilp.fog[i[0]][i[1]] == 0:
			#print("{} : {}".format(antenas[i[0]].id, antenas[i[0]].rrhs_matrix))
			del_keys.append(i)
	for i in del_keys:
		del y[i]
		#print("Removed {}".format(i))
	#now, remove the decision variables in which a wavelength can not be allocated to a processing node
	del_keys = []
	for i in z:
		if z[i].solution_value > 0 and rlx.lambda_node[i[0]][i[1]] == 0:
			del_keys.append(i)
	for i in del_keys:
		del z[i]

	clean_vars = rlx.DecisionVariables(x, u, k, rd, s, e, y, g, xn, z)
	return clean_vars

#keeps only inclusive index in a list
def getInclusive(var):
	inclusive = []
	for i in var:
		inclusive.append(i[0])
	inclusive = set(inclusive)
	inclusive = list(inclusive)
	return inclusive

#keeps only higher values from a decision variable
def getHigherValues(var):
	indexes = getInclusive(var)
	values = []
	higher_values = {}
	for i in indexes:
		values.append({})
		#higher_values[i] = {}
	for i in indexes:
		for j in var:
			if j[0] == i:
				values[i][j] = var[j].solution_value
	#now, gets the maximum value for each variable
	for i in range(len(values)):
		#higher_values[max(values[i].items(), key=operator.itemgetter(1))[0]] = var[max(values[i].items(), key=operator.itemgetter(1))[0]] #Aqui eu retornava o valor real da solução do ILP
		higher_values[max(values[i].items(), key=operator.itemgetter(1))[0]] = max(values[i].items(), key=operator.itemgetter(1))[0] #aqui eu retorno só a variavel com o maior valor e depois seto ela como 1
	for i in higher_values:
		#set the higher decision variables as 1
		higher_values[i]= 1
		#remove the high value variables from the decision var
		print("REOMVED {}".format(var[i]))
		del var[i]
		#print(higher_values)
		#print(higher_values[i].solution_value)
	return higher_values




#This algorithms takes solution values and consider them as probabilities
#For each decision variable, it consider the higher value, perform the scheduling and discard the other values for the same variable
#Does this to every variable and DO NOT run the ILP again
def mostProbability(solution, ilp_module):
	sol = cleanSolution(solution, ilp_module)
	#to keep the high values of each decision variable after the relaxation
	x_high = {}
	#choose the higher value of variable x
	#first, take inclusive values of rrhs represented in var x
	rrhs = getInclusive(sol.x)
	x_high = getHigherValues(sol.x)

	#now, checks with value for var x has the higher value, set it as 1 and discard the others
		#print(sol.x[i].solution_value)

#This algorithms takes solutions values and consider them as probabilities
#it takes the first decision variable (in a first-fit manner), consider its higher value and discard the other values for the same variable
#Schedule the decision variable and, outside this function, the relaxation module is executed again, and then, 
#this algorithm is executed for the remaining variables, schedule one, run ILP relaxaed again, and so on
def incMostProbability(solution, ilp_module):
	sol = cleanSolution(solution, ilp_module)

#This algorithms takes solution values and consider them as probabilities
#For each decision variable, a value between 0 and 1 is sorted from a uniform distribution, find the value of the decision variable where the sorted value fits within 
#(e.g., sorted value is 0.3, variables has 0.1 and 0.5, so we define it will be fit in the interval between the first value and the second, śo, the first value for the decision variable is chosen,
#perform the scheduling and discard the other values for the same variable
#Does this to every variable and DO NOT run the ILP again
def sortProbability(solution, ilp_module):
	sol = cleanSolution(solution, ilp_module)

#This algorithms takes solutions values and consider them as probabilities
#it takes the first decision variable (in a first-fit manner),a value between 0 and 1 is sorted from a uniform distribution, find the value of the decision variable where the sorted value fits within 
#(e.g., sorted value is 0.3, variables has 0.1 and 0.5, so we define it will be fit in the interval between the first value and the second, śo, the first value for the decision variable is chosen,
# then discard the other values for the same variable
#Schedule the decision variable and, outside this function, the relaxation module is executed again, and then, 
#this algorithm is executed for the remaining variables, schedule one, run ILP relaxaed again, and so on
def incSortProbability(solution, ilp_module):
	sol = cleanSolution(solution, ilp_module)

u = rlx.Util()
antenas = u.newCreateRRHs(2)
np.shuffle(antenas)
ilp = rlx.ILP(antenas, range(len(antenas)), rlx.nodes, rlx.lambdas, True)
s = ilp.run()
sol = ilp.return_solution_values()
dec = ilp.return_decision_variables()
#ilp.print_var_values()
#ilp.updateValues(sol)
#for i in ilp.y:
#	print("{} is {}".format(ilp.y[i],ilp.y[i].solution_value))
print("Solving time: {}".format(s.solve_details.time))
#cleanSolution(dec, ilp)
#for i in antenas:
#	print("{} is {}" .format(i.id,i.rrhs_matrix))
mostProbability(dec, ilp)