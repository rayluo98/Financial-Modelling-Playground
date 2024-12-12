#%%
import pandas as pd
import BetaCovFactory
import numpy as np
from matplotlib import pyplot as plt
from Clustering.DBSCAN import DBSCANwrapper
from sklearn.preprocessing import StandardScaler 
from sklearn.preprocessing import normalize
from sklearn.decomposition import PCA 


beta = pd.read_csv(r'C:\Users\raymo\OneDrive\Desktop\Ray Stuff\_Cache\Beta_Callibration\pairwise_beta.csv').set_index('Ticker Pair')
beta = beta.loc[:, ~beta.columns.str.contains('^Unnamed')]
# dbModel = DBSCANwrapper(beta)
# dbModel._optimize("SC")

# %%
mu = beta['Cross Beta'].mean()
sigma = beta['Cross Beta'].std()
# beta = beta[abs(beta['Cross Beta'] - mu) < 3*sigma]
plt.plot(beta["Cross Beta"], np.zeros_like(beta["Cross Beta"]), '.')
plt.show()


# %%
corr = pd.read_csv(r'C:\Users\raymo\OneDrive\Desktop\Ray Stuff\_Cache\Beta_Callibration\pairwise_corr.csv').set_index('Ticker Pair')
corr = corr.loc[:, ~corr.columns.str.contains('^Unnamed')]
corr['Cross Correlation'] = corr['Cross Correlation']
plt.plot(corr["Cross Correlation"], np.zeros_like(corr["Cross Correlation"]), '.')
plt.show()

# %%
plt.hist(abs(corr["Cross Correlation"]))
plt.show()
# %%
"""
MATH: Correlation Bounding 
Definition of Corr = <x,y>/sqrt(<x,x><y,y>) where <x,y> is the inner product defined by <x,y> = E[XY]
We have by defn of regression: 
X = beta_x*Y + epsilon_x, Z = beta_z*Y + epsilon_y
By Cauchy-Schwartz:
rho_x,z <= rho_x,y*rho_y,z + sqrt((1-rho^2_x,y)(1-rho^2_y,z))
rho_x,z >= rho_x,y*rho_y,z - sqrt((1-rho^2_x,y)(1-rho^2_y,z))

It follows that corr(X,Y)= b, corr(X,Z) = c, corr(Y,Z) = a
we have a >= bc - sqrt(1-b^2)sqrt(1-c^2)

To establish correlation groups, we can either look up directly or... 
use this bound as heuristic. We want a to be bounded below by 0.9. 

0.9b - sqrt(0.19)*sqrt(1-b^2) <= 0.9
"""

candidate_pairs = corr["Cross Correlation"]
candidate_pairs = dict(filter(lambda item: abs(item[1]) > 0.9, candidate_pairs.items()))

### build graph relations between correlated names
corr_graph = {}
for pair in candidate_pairs:
    ticker_list = pair.split(",")
    if ticker_list[0] not in corr_graph:
        corr_graph[ticker_list[0]] = [ticker_list[0]]
    corr_graph[ticker_list[0]].append(ticker_list[1])
    

## build cycles from graphs
cycles = []
visited = []
for root in corr_graph:
    if root in visited:
        continue
    visited.append(root)
    ### check neighbor of neighbors for smallest subset
    nbrs = corr_graph[root]
    for nbr in corr_graph[root]:
        if nbr in visited:
            continue
        if nbr not in corr_graph:
            nbrs = []
        else:
            nbrs = list(set(nbrs) & set(corr_graph[nbr]))
        visited.append(nbr)
    if len(nbrs) > 1:
        cycles.append(nbrs)

cycles
# %%
corr_graph
# %%
len(cycles)
# %%
