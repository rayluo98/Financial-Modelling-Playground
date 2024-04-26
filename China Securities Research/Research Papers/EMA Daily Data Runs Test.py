# -*- coding: utf-8 -*-
"""
Created on Sun Aug 11 23:24:59 2019

@author: raymo
"""

# -*- coding: utf-8 -*-
"""
Created on Wed Aug  7 15:40:12 2019

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

data = pd.read_excel(r'C:\Users\raymo\OneDrive\Desktop\Ray Stuff\Internships\Summer 2019\Daily Analysis MA Runs Test 2008 - 2019.xlsx')
df = pd.DataFrame(data, columns = ['000001.SH', 'Date'])
N = 20
alpha = 2/(N + 1)
list = df['000001.SH']
time = df['Date']
n = list.size

#Initiates Exponential Moving Average with alpha 
EMA = [0]*n
EMA[0] = list[0]

SMA = [0]*n


#Initiates List with Binary values keeping track of changes in price
binary = [0]*(n)
SMA[0] = list[0]
EMA_diff = [0]*(n)
for i in range(n):
    if (i != 0):
        EMA[i] = EMA[i - 1]*(1 - alpha) + alpha*list[i]
    else:
        EMA[i] = list[0]
    window = min(N, i + 1)
    for j in range(window):
        SMA[i] += list[i - j]
    SMA[i] = SMA[i] / window
    if (SMA[i] > list[i]):
        binary[i] = 1
    else:
        binary[i] = 0
    if (EMA[i] > list[i]):
      EMA_diff[i] = 1
    else: 
      EMA_diff[i] = 0


    
#observation intervals is 90 days     
interval = 90
#shift length between observation
shift = 15
#number of observation samples
obs_no = math.floor((n - 90) / shift) - 10


#EMA_diff_change = [0]*n

#EMA_diff_change[0] = 1
EMA_diff[0] = -1

#if EMA[1] > EMA[0]:
#    EMA_diff[1] = 1
#else:
#    EMA_diff[1] = 0

table = PrettyTable()
table.field_names = ["Time Period", "+", "-", "Number of Runs", "Expected Number of Runs", "SD of Runs", "Z", "Randomness (T/F)"]

MA_table = PrettyTable()
MA_table.field_names = ["Time Period", "Number of Runs", "Expected Number of Runs", "SD of Runs", "Z", "Randomness (T/F)"]


sheet1.write(0, 0, "EMA > Data Daily Runs Test")
sheet1.write(1, 1, "Time Period")
sheet1.write(1, 2, "n1")
sheet1.write(1, 3, "n2")
sheet1.write(1, 4, "Number of Runs")
sheet1.write(1, 5, "Expected Number of Runs")
sheet1.write(1, 6, "SD of Runs")
sheet1.write(1, 7, "Z")
sheet1.write(1, 8, "Random (T/F)")
sheet1.write(1, 9, "Adjusted Z")
sheet1.write(1, 10, "Adjusted Random")

trend_time = 2
adj_time = 2
for k in range(1, obs_no):
    data = [0]*90
    data_change = [0]*90
    Time_period = "[" + str(time[(k - 1)*shift + 83])[0:10] + "," + str(time[(k - 1)*shift + 172])[0:10] + "]"
    sheet1.write(k + 1, 1, Time_period)
    Random = False
    adj_rand = False
    data[0] = EMA_diff[(k - 1)*shift + 83]
    for l in range(90):
        data[l] = EMA_diff[(k - 1)*shift + l + 83]
        data_change[l] = abs(data[l] - data[l - 1])
    data_change[0] = 1
    runs = data_change.count(1)
    n1 = data.count(1)
    n2 = data.count(0)
    mean = run_mean(n1, n2)
    sd = run_sd(n1, n2)
    if sd == 0:
        z = "NaN"
        adj_z = "NaN"
        adj_rand = False
        Random = False
    else:
        z = (runs - mean)/sd
        adj_z = (abs(runs - mean) - 0.5) /sd
    mean = format(mean, '.2f')
    sd = format(sd, '.2f')
    if z != "NaN":
        if abs(z) < 1.69:
            Random = True
            sheet3.write(trend_time, 5, Time_period)
            trend_time += 1
        z = format(z, '.2f')
        if abs(adj_z) < 1.69:
            adj_rand = True
            sheet3.write(adj_time, 7, Time_period)
            adj_time += 1
        adj_z = format(adj_z, '.2f')
    MA_table.add_row([Time_period, runs, mean, sd, z, Random])
    sheet1.write(k + 1, 2, n1)
    sheet1.write(k + 1, 3, n2)
    sheet1.write(k + 1, 4, runs)
    sheet1.write(k + 1, 5, mean)
    sheet1.write(k + 1, 6, sd)
    sheet1.write(k + 1, 7, z)
    sheet1.write(k + 1, 8, Random)
    sheet1.write(k + 1, 9, adj_z)
    sheet1.write(k + 1, 10, adj_rand)
    
sheet2.write(0, 0, "SMA > Data Daily Runs Test")
sheet2.write(1, 1, "Time Period")
sheet2.write(1, 2, "n1")
sheet2.write(1, 3, "n2")
sheet2.write(1, 4, "Number of Runs")
sheet2.write(1, 5, "Expected Number of Runs")
sheet2.write(1, 6, "SD of Runs")
sheet2.write(1, 7, "Z")
sheet2.write(1, 8, "Random (T/F)")
sheet2.write(1, 9, "Adjusted Z")
sheet2.write(1, 10, "Adjusted Random")

adj_time = 2
trend_time = 2
sheet3.write(1, 1, "Non-random time frame")

for k in range(1, obs_no):
    data = [0]*90
    data_change = [0]*90
    #Time Period
    Time_period = "[" + str(time[(k - 1)*shift + 83])[0:10] + "," + str(time[(k - 1)*shift + 172])[0:10] + "]"
    sheet2.write(k + 1, 1, Time_period)
    Random = False
    adj_rand = False
    data[0] = binary[(k - 1)*shift + 83]
    for l in range(90):
        data[l] = binary[(k - 1)*shift + l + 83]
        data_change[l] = abs(data[l] - data[l - 1])
    data_change[0] = 1
    #number of runs in data
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
        adj_z = "NaN"
        adj_rand = False
        Random = False
    else:
        z = (runs - mean)/sd
        adj_z = (abs(runs - mean) - 0.5)/sd
    mean = format(mean, '.2f')
    sd = format(sd, '.2f')
    if z != "NaN":
        if abs(z) < 1.69:
            Random = True
            sheet3.write(trend_time, 1, Time_period)
            trend_time += 1
        if abs(adj_z) < 1.69:
            adj_rand = True
            sheet3.write(adj_time, 3, Time_period)
            adj_time += 1
        z = format(z, '.2f')
        adj_z = format(adj_z, '.2f')
    table.add_row([Time_period, n1, n2, runs, mean, sd, z, Random])
    sheet2.write(k + 1, 2, n1)
    sheet2.write(k + 1, 3, n2)
    sheet2.write(k + 1, 4, runs)
    sheet2.write(k + 1, 5, mean)
    sheet2.write(k + 1, 6, sd)
    sheet2.write(k + 1, 7, z)
    sheet2.write(k + 1, 8, Random)
    sheet2.write(k + 1, 9, adj_z)
    sheet2.write(k + 1, 10, adj_rand)

wb.save('日频 （MA - 原数据） 涨跌 Data Runs Test.xls')
        
#print(table)
        
        
        
        
        
        
        