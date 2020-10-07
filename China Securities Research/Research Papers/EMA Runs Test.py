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

data = pd.read_excel(r'C:\Users\raymo\OneDrive\Desktop\Ray Stuff\Internships\Summer 2019\EMA Runs 2009-2019.xlsx')
df = pd.DataFrame(data, columns = ['000001.SH', 'Date'])
N = 5
alpha = 2/(N + 1)
list = df['000001.SH']
time = df['Date']
n = list.size

#Initiates Exponential Moving Average with alpha 
EMA = [0]*n
EMA[0] = list[0]

#Initiates List with Binary values keeping track of changes in price
binary = [0]*(n - 1)
EMA[0] = list[0]
for i in range(1,n - 1):
    EMA[i] = EMA[i - 1]*(1 - alpha) + alpha*list[i]
    if (EMA[i] > EMA[i - 1]):
        binary[i] = 1
    else:
        binary[i] = 0

EMA[n - 1] = EMA[n - 2]*(1 - alpha) + alpha*list[n - 1]
    
#observation intervals is semiannual, 26 weeks     
interval = 26  
#shift length between observation
shift = 1
#number of observation samples
obs_no = 500

#Initiates EMA Diff (counting number of times our EMA intersects our original line)
MA_diff = EMA - list

MA_diff_b = [0]*(n - 1)
MA_diff_change = [0]*(n - 2)

if MA_diff[0] > 0:
        MA_diff_b[0] = 1
else:
    MA_diff_b[0] = 0


for i in range(2, n - 2):
    if MA_diff[i] > 0:
        MA_diff_b[i] = 1
    else:
        MA_diff_b[i] = 0



table = PrettyTable()
table.field_names = ["Time Period", "+", "-", "Number of Runs", "Expected Number of Runs", "SD of Runs", "Z", "Randomness (T/F)"]

MA_table = PrettyTable()
MA_table.field_names = ["Time Period", "Number of Runs", "Expected Number of Runs", "SD of Runs", "Z", "Randomness (T/F)"]

sheet1.write(0, 0, "Runs Test on EMA 5 - Actual Data")
sheet1.write(1, 1, "Time Period")
sheet1.write(1, 2, "n1")
sheet1.write(1, 3, "n2")
sheet1.write(1, 4, "Number of Runs")
sheet1.write(1, 5, "Expected Number of Runs")
sheet1.write(1, 6, "SD of Runs")
sheet1.write(1, 7, "Z")
sheet1.write(1, 8, "Random (T/F)")

trend_time = 2
for k in range(1, obs_no):
    data = [0]*26
    data_change = [0]*26
    Time_period = "[" + str(time[k*shift + 28])[0:10] + "," + str(time[k*shift + 53])[0:10] + "]"
    sheet1.write(k + 1, 1, Time_period)
    Random = False
    data[0] = MA_diff_b[k*shift + 28 + 1]    
    for l in range(1, 26):
        data[l] = MA_diff_b[k*shift + 28 + l + 1]
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
    

sheet2.write(0, 0, "Runs Test on EMA 5")
sheet2.write(1, 1, "Time Period")
sheet2.write(1, 2, "n1")
sheet2.write(1, 3, "n2")
sheet2.write(1, 4, "Number of Runs")
sheet2.write(1, 5, "Expected Number of Runs")
sheet2.write(1, 6, "SD of Runs")
sheet2.write(1, 7, "Z")
sheet2.write(1, 8, "Random (T/F)")

trend_time = 2
sheet3.write(1, 1, "Non-random time frame")

for k in range(1, obs_no):
    data = [0]*26
    data_change = [0]*26
    #Time Period
    Time_period = "[" + str(time[k*shift + 28])[0:10] + "," + str(time[k*shift + 53])[0:10] + "]"
    sheet2.write(k + 1, 1, Time_period)
    Random = False
    data[0] = binary[k*shift + 28 + 1]
    for l in range(1, 26):
        data[l] = binary[k*shift + l + 28 + 1]
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

wb.save('EMA 5 Runs Test.xls')
#print(table)
        
        
        
        
        
        
        