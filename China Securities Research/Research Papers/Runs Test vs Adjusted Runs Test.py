# -*- coding: utf-8 -*-
"""
Created on Fri Aug  9 15:43:27 2019

@author: raymo
"""

import pandas as pd
from matplotlib import pyplot
import math
from scipy.stats import norm
from prettytable import PrettyTable
import numpy as np

# Writing to an excel  
# sheet using Python 
from xlwt import Workbook 
# Workbook is created 
wb = Workbook() 
  
# add_sheet is used to create sheet. 
sheet1 = wb.add_sheet('Sheet 1')
sheet2 = wb.add_sheet('Sheet 2')
sheet3 = wb.add_sheet('Sheet 3') 


#Expected Average in Number of Runs in Observation Period
def run_mean(n1, n2):
    return (2*n1*n2)/(n1 + n2) + 1

#Standard Deviation in Number of Runs in Observation Period
def run_sd(n1, n2):
    return math.sqrt(2*n1*n2*(2*n1*n2 - n1 - n2)/((math.pow(n1 + n2, 2))*(n1 + n2 - 1)))

data = pd.read_excel(r'C:\Users\raymo\OneDrive\Desktop\Ray Stuff\Internships\Summer 2019\EMA Runs 2009-2019.xlsx')
df = pd.DataFrame(data, columns = ['000001.SH', 'Date'])

N = 5
alpha = 2/(N + 1)
list = df['000001.SH']
time = df['Date']
n = list.size

#Initiates List with Binary values keeping track of changes in price
binary = [0]*(n - 1)

for i in range(n - 1):
    if (list[i + 1] > list[i]):
        binary[i] = 1
    else:
        binary[i] = 0

#Keeps track of how many times our values change
binary_change = [0]*(n - 2)

for j in range(n - 2):
    binary_change[j] = abs(binary[j + 1] - binary[j])
    
#observation intervals is semiannual, 26 weeks     
interval = 26
#shift length between observation
shift = 1
#number of observation samples
obs_no = math.floor((n - 80) / shift) - 5

data = PrettyTable()

data.field_names = ["Time Period", "n1", "n2", "runs", 
                    "expected number of runs", "variance", "z-score", "Randomness", "adjusted z", "adjusted Randomness"]


sheet1.write(0, 0, "Runs Test + Adjusted Runs Test")
sheet1.write(1, 1, "Time Period")
sheet1.write(1, 2, "n1")
sheet1.write(1, 3, "n2")
sheet1.write(1, 4, "Number of Runs")
sheet1.write(1, 5, "Expected Number of Runs")
sheet1.write(1, 6, "SD of Runs")
sheet1.write(1, 7, "Z")
sheet1.write(1, 8, "Random (T/F)")
sheet1.write(1, 9, "Adjusted Z")
sheet1.write(1, 10, "Adjusted Random (T/F)")

trend_time = 2

for k in range(1, obs_no): 
    field = [0]*25
    field_change = [0]*25
    Time_period = "[" + str(time[(k - 1)*shift + 52])[0:10] + "," + str(time[(k - 1)*shift + 77])[0:10] + "]"
    sheet1.write(k + 1, 1, Time_period)
    Random = False
    adj_Random = False
    for l in range(25):
        field[l] = binary[(k - 1)*shift + l + 52]
        field_change[l] = binary_change[(k - 1)*shift + l + 52]
    runs = field_change.count(1) + 1
    n1 = field.count(1)
    n2 = field.count(0)
    mean = run_mean(n1, n2)
    sd = run_sd(n1, n2)
    if sd == 0:
        adjusted_z = "NaN"
        z = "NaN"
        Random = False
        adj_Random = False
    else:
        z = (runs - mean)/sd
        adjusted_z = (abs(runs - mean) - 0.5)/sd
    mean = format(mean, '.2f')
    sd = format(sd, '.2f')
    if z != "NaN":
        if abs(z) < 1.69:
            Random = True
            sheet3.write(trend_time, 3, Time_period)
            trend_time += 1      
        z = format(z, '.2f')
    if adjusted_z != "NaN":
        if abs(adjusted_z < 1.69):
            adj_Random = True
        adjusted_z = format(adjusted_z, '.2f')
    data.add_row([Time_period, n1, n2, runs, mean, sd, z, Random, adjusted_z, adj_Random])
    sheet1.write(k + 1, 2, n1)
    sheet1.write(k + 1, 3, n2)
    sheet1.write(k + 1, 4, runs)
    sheet1.write(k + 1, 5, mean)
    sheet1.write(k + 1, 6, sd)
    sheet1.write(k + 1, 7, z)
    sheet1.write(k + 1, 8, Random)
    sheet1.write(k + 1, 9, adjusted_z)
    sheet1.write(k + 1, 10, adj_Random)

wb.save('原数据 Runs Test Data.xls')
    
    
    