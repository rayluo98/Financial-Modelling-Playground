# -*- coding: utf-8 -*-
"""
Created on Fri Aug  9 15:29:25 2019

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

data = pd.read_excel(r'C:\Users\raymo\OneDrive\Desktop\Ray Stuff\Internships\Summer 2019\Runs 2008-2019.xlsx')
df = pd.DataFrame(data, columns = ['000001.SH', 'Date'])
N = 5
alpha = 2/(N + 1)
list = df['000001.SH']
time = df['Date']
n = list.size

#Initiates Exponential Moving Average with alpha 
EMA = [0]*n
EMA[0] = list[0]

#Initiates Simple Moving Average with alpha
MA = [0]*n
MA[0] = list[0]

window = 5

#Initiates List with Binary values keeping track of changes in price
E_binary = [0]*(n - 1)
S_binary = [0]*(n - 1)

#Fills in MA + EMA values 
for i in range(1, n):
    EMA[i] = EMA[i - 1]*(1 - alpha) + alpha*list[i]
    if (EMA[i] - list[i] > EMA[i - 1] - list[i - 1]):
        E_binary[i - 1] = 1
    else:
        E_binary[i - 1] = 0
    if i < window - 1:
        MA[i] = -1
    else:
        for j in range(window):
            MA[i] += list[i - j]
        MA[i] = MA[i] / window
    if (MA[i] - list[i] > MA[i - 1] - list[i - 1]):
        S_binary[i - 1] = 1
    else:
        S_binary[i - 1] = 0

    
#observation intervals is semiannual, 26 weeks     
interval = 26  
#shift length between observation
shift = 1
#number of observation samples
obs_no = 500

table = PrettyTable()
table.field_names = ["Time Period", "+", "-", "Number of Runs", "Expected Number of Runs", "SD of Runs", "Z", "Randomness (T/F)"]

MA_table = PrettyTable()
MA_table.field_names = ["Time Period", "Number of Runs", "Expected Number of Runs", "SD of Runs", "Z", "Randomness (T/F)"]
sheet1.write(0,0, "Results for EMA - Actual Data")
sheet1.write(1, 1, "Time Period")
sheet1.write(1, 2, "n1")
sheet1.write(1, 3, "n2")
sheet1.write(1, 4, "Number of Runs")
sheet1.write(1, 5, "Expected Number of Runs")
sheet1.write(1, 6, "SD of Runs")
sheet1.write(1, 7, "Z")
sheet1.write(1, 8, "Random (T/F)")

trend_time = 3
for k in range(1, obs_no):
    data = [0]*25
    data_change = [0]*25
    Time_period = "[" + str(time[k*shift + 52])[0:10] + "," + str(time[k*shift + 77])[0:10] + "]"
    sheet1.write(k + 1, 1, Time_period)
    Random = False
    data[0] = E_binary[k*shift + 52]
    for l in range(1, 25):
        data[l] = E_binary[k*shift + l + 52]
        data_change[l] = abs(data[l] - data[l - 1])
    data_change[0] = 1
    runs = data_change.count(1)
    n1 = data.count(1)
    n2 = data.count(0)
    mean = run_mean(n1, n2)
    sd = run_sd(n1, n2)
    if sd == 0:
        z = "NaN"
        Random = False
    else:
        z = (runs - mean)/sd
    mean = format(mean, '.2f')
    sd = format(sd, '.2f')
    if z != "NaN":
        if abs(z) < 1.69:
            Random = True
            sheet3.write(trend_time, 3, Time_period)
            trend_time += 1
        z = format(z, '.2f')
    MA_table.add_row([Time_period, runs, mean, sd, z, Random])
    sheet1.write(k + 1, 2, n1)
    sheet1.write(k + 1, 3, n2)
    sheet1.write(k + 1, 4, runs)
    sheet1.write(k + 1, 5, mean)
    sheet1.write(k + 1, 6, sd)
    sheet1.write(k + 1, 7, z)
    sheet1.write(k + 1, 8, Random)
    
sheet2.write(0,0, "Results for SMA - Actual Data")
sheet2.write(1, 1, "Time Period")
sheet2.write(1, 2, "n1")
sheet2.write(1, 3, "n2")
sheet2.write(1, 4, "Number of Runs")
sheet2.write(1, 5, "Expected Number of Runs")
sheet2.write(1, 6, "SD of Runs")
sheet2.write(1, 7, "Z")
sheet2.write(1, 8, "Random (T/F)")

trend_time = 3
sheet3.write(1, 1, "Non-random time frame")
sheet3.write(2, 1, "Smooth Average")
sheet3.write(2, 3, "Exponential Average")

for k in range(1, obs_no):
    data = [0]*25
    data_change = [0]*25
    #Time Period
    Time_period = "[" + str(time[k*shift + 52])[0:10] + "," + str(time[k*shift + 77])[0:10] + "]"
    sheet2.write(k + 1, 1, Time_period)
    Random = False
    data[l] = S_binary[k*shift + 52]
    for l in range(1, 25):
        data[l] = S_binary[k*shift + l + 52]
        data_change[l] = abs(data[l] - data[l - 1])
    #number of runs in data
    data_change[0] = 1
    runs = data_change.count(1) 
    #number of positive values
    n1 = data.count(1)
    #number of negative values
    n2 = data.count(0)
    #Expectation
    mean = run_mean(n1, n2)
    #Std Deviation
    sd = run_sd(n1, n2)
    #Calculates Z score
    if sd == 0:
        z = "NaN"
        Random = False
    else:
        z = (runs - mean)/sd
    mean = format(mean, '.2f')
    sd = format(sd, '.2f')
    if z != "NaN":
        if abs(z) < 1.69:
            Random = True
            sheet3.write(trend_time, 1, Time_period)
            trend_time += 1
        z = format(z, '.2f')
    table.add_row([Time_period, n1, n2, runs, mean, sd, z, Random])
    sheet2.write(k + 1, 2, n1)
    sheet2.write(k + 1, 3, n2)
    sheet2.write(k + 1, 4, runs)
    sheet2.write(k + 1, 5, mean)
    sheet2.write(k + 1, 6, sd)
    sheet2.write(k + 1, 7, z)
    sheet2.write(k + 1, 8, Random)

wb.save('EMA - Data Runs Test (2).xls')
        
        
        
        
        
        
        
        

