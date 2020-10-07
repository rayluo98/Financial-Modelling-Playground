import pandas as pd
from matplotlib import pyplot
import math
from scipy.stats import norm
from prettytable import PrettyTable

data = pd.read_excel (r'C:\Users\raymo\OneDrive\Desktop\CustomData4.xlsx')
df = pd.DataFrame(data, columns = ['000001.SH', 'Time'])
list = df['000001.SH']
time = df['Time']


h = 90
#Initialize an map for the factorials
fact_map = [0]*(h + 1)
for i in range(0,h + 1):
    fact_map[i] = [0]*(h + 1)

for i in range(0, h + 1):
    fact_map[i][i] = 1
    fact_map[i][0] = 1
    fact_map[i][i - 1] = i
#iteratively fills in our factorial map
for i in range(1, h + 1):
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
    i = 2
    sum = 0
    sum += prob(pos, neg, size, i)
    while sum < alpha / 2:
        sum += prob(pos, neg, size, i)
        i += 1
    return i

#Finds the upper critical value
def up_crit(pos, neg, size, alpha):
    i = 2*min(pos, neg) + 1
    sum = 0
    sum += prob(pos, neg, size, i)
    while sum  < alpha / 2:
        i -= 1
        sum += prob(pos, neg, size, i)
    return i

def run_mean(n1, n2):
    return (2*n1*n2)/(n1 + n2) + 1
def run_sd(n1, n2):
    return math.sqrt(2*n1*n2*(2*n1*n2 - n1 - n2)/((math.pow(n1 + n2, 2))*(n1 + n2 - 1)))

#x = PrettyTable()
#x.field_names = ["Time Frame", "Number of Runs", "Expected Average", "Variance", "Critical Range", "Random (T/F)"]
#for i in range(0, 1 - len_obs):
#    random = False
#    Time_frame = str(2006 + i) + " - " + str(2006 + len_obs + i)
#    for j in range(0,h):
#        if list[12*i + j] > 0:
#            run_test[j] = 1
#        else:
#            run_test[j] = 0
#    n1 = run_test.count(1)
#    n2 = run_test.count(0)
#    runs = 1
#    for j in range(0, h - 1):
#        if run_test[j + 1] != run_test[j]:
#            runs += 1
#    mean = run_mean(n1, n2)
#    var = run_var(mean, n1, n2)
#    low = low_crit(n1, n2, n1 + n2, 0.05)
#    hi = up_crit(n1, n2, n1 + n2, 0.05)
#    if (runs <= hi and runs >= low):
#        random = True
#    else:
#        random = False
#    x.add_row([Time_frame, runs, mean, var, "[" + str(low) + "," + str(hi) + "]", random])

print("--------------------------------------------------------------------")
print("Daily Analysis")

#Sets up Run Test in Samples of 90
run_test = [0]*90

x = PrettyTable()
x.field_names = ["Time Frame", "Number of Runs", "Expected Average", "Std Deviation", "Z-value", "Random (T/F)"]
for i in range(0, 30):
    random = False
    t_test = False
    Time_frame = 60*i
    for j in range(Time_frame, Time_frame + 89):
        if list[j + 1] > list[j]:
            run_test[j - Time_frame] = 1
        else:
            run_test[j - Time_frame] = 0
    n1 = run_test.count(1)
    n2 = run_test.count(0)
    runs = 0
    total  = 0
    for j in range(0, 30):
        total += math.pow(run_test[j] - n1 / 27, 2)
    S_hat = math.sqrt(total / 29)
    for j in range(0, 89):
        if run_test[j + 1] != run_test[j]:
            runs += 1
    runs += 1
    mean = run_mean(n1, n2)
    sd = run_sd(n1, n2)
    z = (runs - mean)/sd
    if (abs(z) < 1.645):
        random = True
    Time = str(time[Time_frame])[0:10] + " - " + str(time[Time_frame + 89])[0:10]
    z = "["  + str(low_crit(n1, n2, n1 + n2, 0.05)) + "," + str(up_crit(n1, n2, n1 + n2, 0.05)) + "]"
    if (runs < up_crit(n1, n2, n1 + n2, 0.05) and runs > low_crit(n1, n2, n1 + n2, 0.05)):
        random = True
    else:
        random = False
    if ((runs - mean)/(90 * S_hat / math.sqrt(30)) < 2.0555):
        t_test = True
    mean = format(mean, '.2f')
    sd = format(sd, '.2f')
    #z = format(z, '.2f')
    S_hat = format(S_hat, '.2f')

    x.add_row([Time, runs, mean, sd, z, random])
    
print(x)
    

print("--------------------------------------------------------------------")
print("Weekly Analysis")

#Set up Run Test in Samples of 27
run_test = [0]*26

data2 = pd.read_excel (r'C:\Users\raymo\OneDrive\Desktop\CustomData5.xlsx')
df2 = pd.DataFrame(data2, columns = ['000001.SH', 'Time'])
list = df2['000001.SH']
time = df2['Time']

y = PrettyTable()
y.field_names = ["Time Frame", "Number of Runs", "Expected Average", "Std Deviation", "Z-value", "Random (T/F)"]
for i in range(0, 26):
    random = False
    t_test = False
    Time_frame = 13*i
    for j in range(Time_frame, Time_frame + 25):
        if list[j + 1] > list[j]:
            run_test[j - Time_frame] = 1
        else:
            run_test[j - Time_frame] = 0
    n1 = run_test.count(1)
    n2 = run_test.count(0)
    runs = 0
    total = 0
    for j in range(0, 26):
        total += math.pow(run_test[j] - n1 / 26, 2)
    S_hat = math.sqrt(total / 25)
    for j in range(0, 25):
        if run_test[j + 1] != run_test[j]:
            runs += 1
    runs += 1
    mean = run_mean(n1, n2)
    sd = run_sd(n1, n2)
    z = (runs - mean)/sd
    if (abs(z) < 1.645):
        random = True
    Time = str(time[Time_frame])[0:10] + " - " + str(time[Time_frame + 26])[0:10]
    if ((runs - mean)/(27 * S_hat/math.sqrt(27)) < 2.0555):
        t_test = True
    mean = format(mean, '.2f')
    sd = format(sd, '.2f')
    z = "["  + str(low_crit(n1, n2, n1 + n2, 0.05)) + "," + str(up_crit(n1, n2, n1 + n2, 0.05)) + "]"
    #z = format(z, '.2f')
    S_hat = format(S_hat, '.2f')
    y.add_row([Time, runs, mean, sd, z, random])
print(y)
    