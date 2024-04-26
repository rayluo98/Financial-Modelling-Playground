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
    x = 1
    for i in range(1, length):
        x *= pos
        pos -= 1
    y = 1
    for i in range(1, length + 1):
        y *= size
        size -= 1
    return (neg + 1)*(neg)*x/y

def var_num_rlength(size, pos, neg, length):
    mu = expected_num_rlength(size, pos, neg, length)
    pos = pos / size
    neg = neg / size
    var = mu *(1 - mu / size * (math.pow(length, 2) / pos + 2 / neg -  math.pow(length + 1, 2)))
    return var

data = pd.read_excel (r'C:\Users\raymo\OneDrive\Desktop\CustomData1.xlsx')
df = pd.DataFrame(data, columns = ['Data'])

data2 = pd.read_excel (r'C:\Users\raymo\OneDrive\Desktop\CustomData3.xlsx')
df2 = pd.DataFrame(data2, columns = ['Quarterly'])

data3 = pd.read_excel (r'C:\Users\raymo\OneDrive\Desktop\CustomData2.xlsx')
df3 = pd.DataFrame(data3, columns = ['Semi-annual'])


#Initialize an map for the factorials
fact_map = [0]*163
for i in range(0, 163):
    fact_map[i] = [0]*163
    
for i in range(0, 163):
    fact_map[i][i] = 1
    fact_map[i][0] = 1
    fact_map[i][i - 1] = i
#iteratively fills in our factorial map
for i in range(1, 163):
    for j in range(1, i - 1):
        fact_map[i][j] = fact_map[i - 1][j - 1] + fact_map[i - 1][j]
#Calculates our combinatorial problem using direct location in our map
def perm(n, k):
    return fact_map[int(n)][int(k)]

#Finds the probability of a given number of runs in our data
def prob(pos, neg, size, run_num):
    if(run_num % 2 == 0):
        k = run_num / 2
        return 2*perm(pos - 1, k - 1)*perm(neg - 1, k - 1)/perm(size, pos)
    else:
        k = (run_num - 1)/2
        return (perm(pos - 1, k - 1)*perm(neg - 1, k) + perm(pos - 1, k)*perm(neg - 1, k - 1))/perm(size, pos)

#Finds the lower critical value
def low_crit(pos, neg, size, alpha):
    #if(size > 100)
    i = 2
    sum = 0
    while sum < alpha / 2:
        sum += prob(pos, neg, size, i)
        i += 1
    return i - 1

#Finds the upper critical value
def up_crit(pos, neg, size, alpha):
    i = 2*min(pos, neg) + 1
    sum = 0
    while sum < alpha / 2:
        sum += prob(pos, neg, size, i)
        i -= 1
    return i + 1

print("MONTHLY ANALYSIS")

list= df['Data']

n = df['Data'].size

print("Size")
print(n)
run_test = [0]*(n)


pyplot.plot(list)

for i in range(0, n):
    if list[i] > 0:
        run_test[i] = 1
    else:
        run_test[i] = 0
        
print()
print("Test for Statistical Randomness")
print()
n1 = run_test.count(1)
n2 = run_test.count(0)
runs = 0
for k in range(0, n - 1):
    if run_test[k + 1] != run_test[k]:
        runs += 1
runs += 1
mean = (2*n1*n2)/(n1 + n2) + 1
variance = (mean - 1)*(mean - 2)/(n1 + n2 - 1)

UB = up_crit(n1, n2, n1 + n2, 0.05)
LB = low_crit(n1, n2, n1 + n2, 0.05)
print("mean")
print(mean)
print("Number of Runs")
print(runs)
print("Critical Values")
print("[" + str(LB) + "," + str(UB) + "]")


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

x.add_row([1, expected_num_rlength(n, n1, n2, 1), length_dist[1],
           var_num_rlength(n, n1, n2, 1)])

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

print()
print("--------------------------------------------------------------------------------------")
print("QUARTERLY ANALYSIS")
list2 = df2['Quarterly']
n = df2['Quarterly'].size
print("Size")
print(n)

run_test = [0]*(n - 1)

for i in range(0, n - 1):
    if list2[i] > 0:
        run_test[i] = 1
    else:
        run_test[i] = 0

print()
print("Test for Statistical Randomness")
print()
n1 = run_test.count(1)
n2 = run_test.count(0)
runs = 0
for k in range(0, n - 2):
    if run_test[k + 1] != run_test[k]:
        runs += 1

mean = (2*n1*n2)/(n1 + n2) + 1
variance = (mean - 1)*(mean - 2)/(n1 + n2 - 1)

UB = up_crit(n1, n2, n1 + n2, 0.05)
LB = low_crit(n1, n2, n1 + n2, 0.05)
print("mean")
print(mean)
print("Number of Runs")
print(runs)
print("Critical Values")
print("[" + str(LB) + "," + str(UB) + "]")


print()
print("Runs Length Distribution")
length_dist = [0]*20
run_type = run_test[0]
run_length = 1
for k in range(1,n - 1):
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

x.add_row([1, expected_num_rlength(n, n1, n2, 1), length_dist[1],
           var_num_rlength(n, n1, n2, 1)])

x.add_row([2, expected_num_rlength(n, n1, n2, 2), length_dist[2],
           var_num_rlength(n, n1, n2, 2)])

x.add_row([3, expected_num_rlength(n, n1, n2, 3), length_dist[3],
           var_num_rlength(n, n1, n2, 3)])

x.add_row([4, expected_num_rlength(n, n1, n2, 4), length_dist[4],
           var_num_rlength(n, n1, n2, 4)])

x.add_row([5, expected_num_rlength(n, n1, n2, 5), length_dist[5],
           var_num_rlength(n, n1, n2, 5)])

print(x)

print()
print("--------------------------------------------------------------------------------------")
print("SEMIANNUAL ANALYSIS")
list3 = df3['Semi-annual']
n = df3['Semi-annual'].size
print("Size")
print(n)

run_test = [0]*(n - 1)

for i in range(0, n - 1):
    if list3[i] > 0:
        run_test[i] = 1
    else:
        run_test[i] = 0

print()
print("Test for Statistical Randomness")
print()
n1 = run_test.count(1)  
n2 = run_test.count(0)
runs = 0
for k in range(0, n - 2):
    if run_test[k + 1] != run_test[k]:
        runs += 1

mean = (2*n1*n2)/(n1 + n2) + 1
variance = (mean - 1)*(mean - 2)/(n1 + n2 - 1)

UB = up_crit(n1, n2, n1 + n2, 0.05)
LB = low_crit(n1, n2, n1 + n2, 0.05)
print("mean")
print(mean)
print("Number of Runs")
print(runs)
print("Critical Values")
print("[" + str(LB) + "," + str(UB) + "]")


print()
print("Runs Length Distribution")
length_dist = [0]*20
run_type = run_test[0]
run_length = 1
for k in range(1,n - 1):
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

x.add_row([1, expected_num_rlength(n, n1, n2, 1), length_dist[1],
           var_num_rlength(n, n1, n2, 1)])


x.add_row([2, expected_num_rlength(n, n1, n2, 2), length_dist[2],
           var_num_rlength(n, n1, n2, 2)])

x.add_row([3, expected_num_rlength(n, n1, n2, 3), length_dist[3],
           var_num_rlength(n, n1, n2, 3)])

x.add_row([4, expected_num_rlength(n, n1, n2, 4), length_dist[4],
           var_num_rlength(n, n1, n2, 4)])

x.add_row([5, expected_num_rlength(n, n1, n2, 5), length_dist[5],
           var_num_rlength(n, n1, n2, 5)])

print(x)
