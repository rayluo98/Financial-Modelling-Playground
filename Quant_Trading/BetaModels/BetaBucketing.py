#%%
import pandas as pd
import BetaCovFactory
import numpy as np
from matplotlib import pyplot as plt
from Clustering.DBSCAN import DBSCANwrapper
from sklearn.preprocessing import StandardScaler 
from sklearn.preprocessing import normalize
from sklearn.decomposition import PCA 


beta = pd.read_csv(r'C:\Users\raymo\OneDrive\Desktop\Ray Stuff\_Cache\Beta_Callibration\^FTW5000_beta.csv').set_index('Ticker')
beta = beta.loc[:, ~beta.columns.str.contains('^Unnamed')]
# dbModel = DBSCANwrapper(beta)
# dbModel._optimize("SC")
# %%
mu = beta['Beta'].mean()
sigma = beta['Beta'].std()
beta = beta[abs(beta['Beta'] - mu) < 3*sigma]
plt.plot(beta["Beta"], np.zeros_like(beta["Beta"]), '.')
plt.show()


# %%
