# -*- coding: utf-8 -*-
"""
Created on Wed Jul 31 14:32:14 2019

@author: raymo
"""

import pandas as pd
from matplotlib import pyplot
import math
from scipy.stats import norm
from prettytable import PrettyTable

data = pd.read_excel (r'C:\Users\raymo\OneDrive\Desktop\CustomData4.xlsx')
df = pd.DataFrame(data, columns = ['000001.SH', 'Time'])
list = df['000001.SH']
time = df['Time']


n = 1940
run_test1 = [0]*(n - 1)
change1 = [0]*(n - 1)

for i in range(n - 1):
    change1[i] = list[i + 1] - list[i]
    if change1[i] > 0:
        run_test1[i] = 1
    else:
        run_test1[i] = 0
    change1[i] = format(change1[i], '.2f')
 

data2 = pd.read_excel (r'C:\Users\raymo\OneDrive\Desktop\CustomData5.xlsx')
df2 = pd.DataFrame(data2, columns = ['000001.SH', 'Time'])

x = PrettyTable()
x.field_names = ["Date", "Increase/Decrease", "Change"]
for i in range(n - 1):
    x.add_row([str(time[i + 1])[0:10] + " - " + str(time[i])[0:10], run_test1[i], change1[i]])
print(x)