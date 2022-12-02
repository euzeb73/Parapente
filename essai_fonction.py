# -*- coding: utf-8 -*-

import numpy as np
import scipy.optimize as sp
import matplotlib.pyplot as plt


xdata,ydata=[0,20,70,80],[1.2,1,1,1.3]
#Définition de la fonction qui doit décrire les données

n=4
coeffs=np.polyfit(xdata,ydata,n)

x=np.arange(min(xdata),max(xdata))
ymodele=0
for coeff in coeffs:
    ymodele+=coeff*x**n
    n-=1

plt.plot()
plt.plot(xdata,ydata,'.r')
plt.plot(x,ymodele)
plt.show()
print(coeffs)