# -*- coding: utf-8 -*-
"""
Created on Fri Aug  9 09:25:23 2019

@author: raymo
"""

import pandas as pd
from mpl_toolkits import mplot3d
import numpy as np
import matplotlib.pyplot as plt
import math
from scipy.stats import norm
from prettytable import PrettyTable


#Expected Average in Number of Runs in Observation Period
def run_mean(n1, n2):
    return (2*n1*n2)/(n1 + n2) + 1

#Standard Deviation in Number of Runs in Observation Period
def run_var(n1, n2):
    return 2*n1*n2*(2*n1*n2 - n1 - n2)/(((n1 + n2)**2)*(n1 + n2 - 1))

ax = plt.axes(projection="3d")
def z_function(x, y):
    return run_mean(x, y)

def w_function(x,y):
    return run_var(x, y)

x = np.linspace(0, 30, 200)
y = np.linspace(0, 30, 200)

X, Y = np.meshgrid(x, y)
Z = z_function(X, Y)
W = w_function(X, Y)

ax.plot_wireframe(X, Y, Z, color='green')
ax.plot_wireframe(X, Y, W, color='blue')
ax.set_xlabel('x')
ax.set_ylabel('y')
ax.set_zlabel('z')



#ax = plt.axes(projection='3d')
#ax.plot_surface(X, Y, Z, rstride=1, cstride=1,
#                cmap='winter', edgecolor='none')
#ax.set_title('surface');

plt.show()