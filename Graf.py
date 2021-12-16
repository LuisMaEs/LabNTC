import numpy as np
import matplotlib.pyplot as plt
import math
import pandas as pd
from scipy.optimize import curve_fit

df=pd.read_csv('Resultados_coef.csv')
wavelengthreal=df.to_numpy()[:,0]
potencia = df.to_numpy()[:,1]
maxpot=np.amax(potencia)
plt.plot(wavelengthreal, 10*np.log10(potencia/maxpot))
plt.ylabel('Power(dBm)')
plt.xlabel('Wavelength(nm)')
plt.show()
