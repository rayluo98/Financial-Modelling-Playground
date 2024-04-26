from random import seed
from random import random
import pandas as pd
from matplotlib import pyplot
import math
from scipy.stats import norm
from prettytable import PrettyTable
import numpy as np
seed(123)

def expected_num_rlength(size, pos, neg, length): 
    pos = pos / size
    neg = neg / size
    return size * math.pow(pos, length) * math.pow(neg, 2)

def var_num_rlength(size, pos, neg, length):
    mu = expected_num_rlength(size, pos, neg, length)
    pos = pos / size
    neg = neg / size
    var = mu *(1 - mu / size * (math.pow(length, 2) / pos + 2 / neg -  math.pow(length + 1, 2)))
    return var

data = pd.read_excel (r'C:\Users\raymo\OneDrive\Desktop\指标导出(1).xlsx')
df = pd.DataFrame(data, columns = ['Application Software'])

list= df['Application Software']

n = df['Application Software'].size

print("Size")
print(n)
run_test = [0]*(n - 1)


pyplot.plot(list)

for i in range(0, n - 1):
    if list[i + 1] > list[i]:
        run_test[i] = 1
    else:
        run_test[i] = 0


growth = [0]*(n - 1)

for j in range(0,83): 
    growth[j] = 100*(list[j + 1] - list[j])/list[j]

print()
print("Test for Statistical Randomness") 
print()
n1 = run_test.count(1)
n2 = run_test.count(0)
runs = 0
for k in range(0, 82):
    if run_test[k + 1] != run_test[k]:
        runs += 1

mean = (2*n1*n2)/(n1 + n2) + 1
variance = (mean - 1)*(mean - 2)/(n1 + n2 - 1)

z_score = (runs - mean)/math.sqrt(variance)
print("mean")
print(mean)
print("Number of Runs")
print(runs)
print("Z-score")
print(z_score)
        

print()
print("Runs Length Distribution")
length_dist = [0]*20
run_type = run_test[0]
run_length = 1
for k in range(1,83):
    if run_test[k] == run_type:
        run_length += 1
    else:
        length_dist[run_length] += 1
        run_type = run_test[k]
        run_length = 1
#pyplot.close()   
#pyplot.plot(length_dist) 


x = PrettyTable()
x.field_names = ["Runs with Length i", "Expectation", "Empirical", "Variance"]

x.add_row([2, expected_num_rlength(n, n1, n2, 2), length_dist[2], 
           var_num_rlength(n, n1, n2, 2)])
    
x.add_row([3, expected_num_rlength(n, n1, n2, 3), length_dist[3], 
           var_num_rlength(n, n1, n2, 3)])

x.add_row([4, expected_num_rlength(n, n1, n2, 4), length_dist[4], 
           var_num_rlength(n, n1, n2, 4)])

x.add_row([5, expected_num_rlength(n, n1, n2, 5), length_dist[5], 
           var_num_rlength(n, n1, n2, 5)])
    
    
y = PrettyTable()
y.field_names = ["Monthly", "Quarterly", "Semi-annually"]
print(x)