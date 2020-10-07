from random import seed
from random import random
from matplotlib import pyplot
import math
from scipy.stats import norm
import numpy as np
seed(123)

##Random Times Series
num1 = 0
num0 = 0
random_walk = [0]*1000
value = [0]*1000
random_walk.append(-1 if random() < 0.5 else 1)
for i in range(1, 1000):
    movement =  -1 if random() < 0.5 else 1
    if movement > 0:
        num1 += 1
    else:
        num0 += 1
    value[i] = movement
    random_walk[i] = random_walk[i - 1] + value[i]
pyplot.plot(random_walk)
pyplot.show()

run_type = value[0]
run = 0
for i in range(1 , 1000):
    if value[i - 1] != run_type:
        run += 1
        run_type = value[i - 1]

#average runs
n = num1
m = num0
print("n:")
print(n)
print("m:")
print(m)
mean = 2*n*m/(n + m) + 1
var = 2*n*m*(2*n*m - n - m)/(pow(n + m, 2)*(n + m -1))
print("var")
print(var)
z = (run - mean)/math.sqrt(var)
cdf = norm.ppf(0.975)
#Note that for alpha = 0.05, if abs(z) > 1.96, we have to reject our null hypothesis
#The data is not random
print("Z:")
print(z)

##Times Series with Linear Function
##Initializing TimeSampler
##linear_walk.
linear_walk = [0]*1000
for i in range(1,1000):
    linear_walk[i - 1] = i
    linear_walk[i - 1] += np.random.normal(0, math.sqrt(i))
num1 = 0
num0 = 0
run_type = 0
run = 0
run_2 = 0
mnum_1 = 0
mnum_0 = 0
for i in range(1 , 1000):
    if linear_walk[i] > linear_walk[i - 1]:
        if run_type == 0:
            run += 1
            run_type = 1
        num1 += 1
    else:
        if run_type == 1:
            run += 1
            run_type == 0
        num0 += 1
run_type = 0
for i in range(1, 1000):
    if linear_walk[i] > 0:
        if run_type == 0:
            run_2 += 1
            run_type = 1
        mnum_1 += 1
    else:
        if run_type == 1:
            run_2 += 1
            run_type == 0
        mnum_0 += 1 
##average runs
n = num1
m = num0
print("n:")
print(n)
print("m:")
print(m)

mean = 2*n*m/(n + m) + 1
var = (mean - 1)*(mean - 2)/(n + m - 1)
print("var")
print(var)
z = (run - mean)/math.sqrt(var)
pyplot.plot(linear_walk)
print("Z_1")
print(z)
mean_2 = 2*mnum_1*mnum_0/(mnum_1 + mnum_0) + 1
var_2 = (mean_2 -  1)*(mean_2 - 2)/(mnum_1 + mnum_0 - 1)
z2 = (run_2 - mean_2)/math.sqrt(var_2)
print("Z_2")
print(z2)
