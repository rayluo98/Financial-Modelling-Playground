# Import libraries
import numpy as np
import os

#Calculates Stationary Distribution
def stat_dist(p, tol=1e-10):
    if(len(p) != len(p[0])):
        quit() #"The transition matrix not symmetric!"
    count = 0
    mat_1 = p
    mat_2 = np.dot(mat_1, p)
    while(matrix_diff(mat_1, mat_2) > tol): ## until p^n = p^(n+1)
        mat_1 = mat_2
        mat_2 = np.dot(mat_1, p) ## p^(n+1)
        count = count + 1
        if(count > 1000):
            break #("Stationary distribution not found until 1000th iteration!")\
    out = mat_1[0]
    return out

#Calculates difference in matrix value
def matrix_diff(mat_1, mat_2):
    sum = 0
    for i in range(len(mat_1)):
        for j in range(len(mat_1[i])):
            sum += abs(mat_1[i][j] - mat_2[i][j])
    return sum

# function that generates transition matrix
def gen_trans(F,OT,d) : ## d : demand distribution
    out = np.zeros((F + 1, F + 1))
    D = len(d)
    print(F)
    d_prime = np.zeros(F + 1)
    if(D >= F + 1):    ##If the maximum number of customers is greater than the max fill amount
        #d_prime = d
        for i in range(F + 1): ##the quantity remaining is demand distribution in reverse from the max value
            d_prime[i] = d[D - i - 1]
        if(D > F + 1):
            for j in range(D - F - 1):
                d_prime[0] += d[F+ j + 1]
    if(D < F + 1):     ##If the maximum number of customers is less than the max fill amount
            for j in range(D):
                d_prime[j + F - D + 1] = d[D - j - 1]
            print("D<F")
            print(d_prime)
        #if(OT  > D):
        #   for j in range(D):
        #       d_prime[j + OT + 1 - D] = d[D - j - 1]
    if(F <= OT + 1): ##If the refill amount is greater than the max fill then all equal demand distribution
        for i in range(F + 1):
            out[i] = d_prime
    if(F > OT + 1): ##otherwise, rows equal d when the initial value is less than equal to the threshold
        for i in range(OT + 1):
            out[i] = d_prime
        for k in range(OT + 1, F): ##note that the for all values greater than consumption are combined at 0
            for j in range(F + 1 - k):
                out[k][0] += d_prime[j]
            for h in range(F + 1 - k, F + 1): ##the remaining distribution is shifted down
                out[k][h - F  + k] = d_prime[h]
    out[F] = d_prime
    return out

 # profit function
def profit(p,d,F,OT,pi,margin):
     p0 = gen_trans(F, F-1, d) ## base case where store is always full
     pi0 = stat_dist(p0)
     max = 0
     for i in range(F):
         max += margin*((F-i)*pi0[i])
     ## profit when store is always full
     ## when OT is smaller than the maximum demand, some sales are not made even when there is demand : (OT + 2 < D)
     ## the loss should be taken into account when dealing with total profit
     ## loss = ABCD
     ## A. the number of items for which demand existed but couldn't sell because of lack of supply : (k-j)
     ## B. the probability that given number of items are in the store : pi[j]
     ## C. the total demand : demand[k]
     ## D. margin
     sum = 0
     loss = 0
     D = len(d)
     if(OT + 1 < D):
         for j in range (OT + 1, D):
             for k in range(OT + 1, D):
                 if (k > j):
                     loss += margin*(k-j)*pi[j]*d[k]
     out = max - loss
     return out

## cost function
def cost(pi,F,margin):
    sum = 0
    for i in range(1,F + 1):
        sum += margin*(i)*pi[i]
    return sum

##--------------------------------------------------------------------------##
##                                Scenario 1                                            ##
##--------------------------------------------------------------------------##

demand = np.array([0.3,0.4,0.2,0.1])
policies = np.array(["OT=2,F=3","OT=1,F=3","OT=0,F=3"])

## OT=2,F=3 policy
p = gen_trans(3,2,demand)
pi = stat_dist(p)

LR23 = profit(p,demand,3,2,pi,12) - cost(pi,3,2)

## OT=1,F=3 policy
p = gen_trans(3,1,demand)
pi = stat_dist(p)

LR13 = profit(p,demand,3,1,pi,12) - cost(pi,3,2)

## OT=0,F=3 policy
p = gen_trans(3,0,demand)
pi = stat_dist(p)

LR03 = profit(p,demand,3,0,pi,12) - cost(pi,3,2)
## optimal policy
opt = np.array([LR23,LR13,LR03])
print(opt);

opt_policy = policies[np.argmax(opt)]
print(opt_policy); ## optimal policy is "OT = 1, F = 3"


## this exactly matches the values and the conclusion from the textbook!




##--------------------------------------------------------------------------##
##                                Scenario 2
##
##--------------------------------------------------------------------------##

## set new demand, F, OT, and margin
## profit per product : $100, cost per product : $15

F = np.array([6,7,8,9,10])
OT = np.array([0,1,2,3,4,5])

demand = np.array ([.1,.2,.3,.25,.1,.05])
LR = np.zeros((len(F),len(OT)))
LR_policy = np.zeros((len(F), len(OT)))
for i in range(len(F)):
    for j in range(len(OT)):
        LR_policy[i,j] = i*(len(F) + 1) + j 
print(LR_policy)

p = gen_trans(6,0,demand)
pi = stat_dist(p)

print(p)
print(pi)

for i in range(len(F)):
    for j in range(len(OT)):
        p = gen_trans(F[i],OT[j],demand)
        pi = stat_dist(p)
        LR[i,j] = profit(p,demand,F[i],OT[j],pi,100) - cost(pi,F[i],15)

print(LR); ## all outcomes
opt = np.max(LR)
for i in range(len(F)):
    for j in range(len(OT)):
        if (LR[i][j] == opt):
            opt_policy = LR_policy[i][j]
print(opt)
print (opt_policy)
##opt = which(LR.mat == max(LR.mat), arr.ind=TRUE)
##opt.policy = paste0("F=", F[opt[1]], " OT=", OT[opt[2]], " profit =", round(max(LR.mat),3))
##opt.policy;
## optimal policy: "OT = 1, F = 6"
## optimal profit : 174.567
