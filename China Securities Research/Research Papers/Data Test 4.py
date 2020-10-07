# -*- coding: utf-8 -*-
"""
Created on Wed Aug  7 08:38:31 2019

@author: raymo
"""

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

def std_num_rlength(size, pos, neg, length):
    mu = expected_num_rlength(size, pos, neg, length)
    pos = pos / size
    neg = neg / size
    var = mu *(1 - mu / size * (math.pow(length, 2) / pos + 2 / neg -  math.pow(length + 1, 2)))
    return math.sqrt(var)

data = pd.read_excel (r'C:\Users\raymo\OneDrive\Desktop\CustomData7.xlsx')
df = pd.DataFrame(data, columns = ['000001.SH', 'Date'])
list = df['000001.SH']
time = df['Date']

n = list.size

binary = [0]*(n - 1)

for i in range(n - 1):
    if list[i + 1] > list[i]:
        binary[i] = 1
    else:
        binary[i] = 0
        
binary_change = [0]*(n - 2)

for j in range(n - 2):
    binary_change[j] = abs(binary[j + 1] - binary[j])
    
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


runs = binary_change.count(1) + 1
run_dist = [0]*20

x = PrettyTable()
x.field_names = ["length of run", "expected number of runs", "actual number of runs", "CI"]
print()
print("Runs Length Distribution")
length_dist = [0]*20

    
run_length = 1
for i in range(n - 2):
    if(binary_change[i] != 1):
        run_length += 1
    else:
        length_dist[run_length] += 1
        run_length = 1
n1 = binary.count(1)
n2 = binary.count(0) 
k = 7
for l in range(1,k):
    mean = expected_num_rlength(n, n1, n2, l)
    x.add_row([l, mean, length_dist[l],
           "[" + str(format(mean - std_num_rlength(n, n1, n2, l), '.2f')) + "," + str(format(mean + std_num_rlength(n, n1, n2, l), '.2f')) + "]" ])
print(x)