import matplotlib.pyplot as plt
import numpy as np

mu, sigma = 12, 2 # mean and standard deviation
s = np.random.normal(mu, sigma, 1000)

count, bins, ignored = plt.hist(s, 150, normed=True)
print(count.size) # eh nesse vetor que fica a probabilidade de geração de tráfego para cada x
print(count[0])
print(count[1])
print(count[2])
print(count[12])
print(count[75])
plt.plot(bins, 1/(sigma * np.sqrt(2 * np.pi)) * np.exp( - (bins - mu)**2 / (2 * sigma**2) ), linewidth=2, color='r')
plt.show()