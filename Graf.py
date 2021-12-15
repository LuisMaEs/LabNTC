import numpy as np
import matplotlib.pyplot as plt
import math
import pandas as pd
from scipy.optimize import curve_fit
values = np.genfromtxt('lab1.out', delimiter=',')
wavelength = np.arange(1540,1560,0.025)
plt.plot(wavelength, 10*np.log10(values)+30)
plt.ylabel('Power(dBm)')
plt.xlabel('Wavelength(nm)')
plt.show()

df = pd.read_csv('Resultados2.csv', sep=",", names=['Longitud de onda(nm)','Potencia(W)'  ])
values1 = np.genfromtxt('lab1.out', delimiter=',')
wavelength = np.arange(1540,1560,0.025)
plt.plot(wavelength, 10*np.log10(values)+30)
plt.ylabel('Power(dBm)')
plt.xlabel('Wavelength(nm)')
plt.show()


