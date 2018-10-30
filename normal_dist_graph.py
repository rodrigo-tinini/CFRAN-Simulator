import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import norm
'''
mu, sigma = 12, 3 # mean and standard deviation
s = np.random.normal(mu, sigma, 1000)

count, bins, ignored = plt.hist(s, 50, normed=True)
print(count.size) # eh nesse vetor que fica a probabilidade de geração de tráfego para cada x
#print(count[0])
#print(count[1])
#print(count[2])
print(count[24])
#print(count[75])
plt.plot(bins, 1/(sigma * np.sqrt(2 * np.pi)) * np.exp( - (bins - mu)**2 / (2 * sigma**2) ), linewidth=2, color='r')
plt.show()
'''
loads = []
for i in range(24):
	x = norm.pdf(i, 12, 3)
	x *= 50
	#x= round(x,4)
	#if x != 0:
	#	loads.append(x)
	loads.append(x)
print(loads)

with open('/home/tinini/Área de Trabalho/Simulador/CFRAN-Simulator/traffic_load.txt', 'a') as filehandle:  
		    filehandle.write("{}\n\n".format(i))
		    filehandle.writelines("%s\n" % p for p in loads)
		    filehandle.write("\n")
		    filehandle.write("\n")