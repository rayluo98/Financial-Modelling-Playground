from matplotlib import pyplot as plt
import numpy as np
from logging import Logger
from statsmodels.tsa.stattools import adfuller
from statsmodels.graphics import tsaplots 
import pandas as pd
import seaborn as sns
import statsmodels as sm
from hurst import compute_Hc

@staticmethod
def scatterByDate(names, prices):
    """
    Create a scatterplot of the two ETF prices, which is
    coloured by the date of the price to indicate the 
    changing relationship between the sets of prices    
    """
    # Create a yellow-to-red colourmap where yellow indicates
    # early dates and red indicates later dates
    plen = len(prices)
    colour_map = plt.cm.get_cmap('jet')    
    colours = np.linspace(0.1, 1, plen)
    
    # Create the scatterplot object
    scatterplot = plt.scatter(
        prices[names[0]], prices[names[1]], 
        s=30, c=colours, cmap=colour_map, 
        edgecolor='k', alpha=0.8
    )
    
    # Add a colour bar for the date colouring and set the 
    # corresponding axis tick labels to equal string-formatted dates
    colourbar = plt.colorbar(scatterplot)
    colourbar.ax.set_yticklabels(
        [str(p.date()) for p in prices[::plen//9].index]
    )
    plt.xlabel(prices.columns[0])
    plt.ylabel(prices.columns[1])
    plt.show()

@staticmethod
def adfTest(self):
    Logger.info('Results of Dickey-Fuller Test:')
    dftest = adfuller(self.data, autolag='AIC')
    dfoutput = pd.Series(dftest[0:4], index=['Test Statistic','p-value','#Lags Used','Number of Observations Used'])
    for key,value in dftest[4].items():
        dfoutput['Critical Value (%s)'%key] = value
    return dfoutput

@staticmethod
def draw_slope_intercept_changes(prices, state_means):
    """
    Plot the slope and intercept changes from the 
    Kalman Filter calculated values.
    """
    pd.DataFrame(
        dict(
            slope=state_means[:, 0], 
            intercept=state_means[:, 1]
        ), index=prices.index
    ).plot(subplots=True)
    plt.show()

@staticmethod
def findCointegratedPairs(df: pd.DataFrame, critical_level = 0.05):
    n = df.shape[1] # the length of dateframe
    pvalue_matrix = np.ones((n, n)) # initialize the matrix of p
    keys = df.columns # get the column names
    pairs = [] # initilize the list for cointegration
    for i in range(n):
        for j in range(i+1, n): # for j bigger than i
            stock1 = df[keys[i]] # obtain the price of "stock1"
            stock2 = df[keys[j]]# obtain the price of "stock2"
            result = sm.tsa.stattools.coint(stock1, stock2) # get conintegration
            pvalue = result[1] # get the pvalue
            pvalue_matrix[i, j] = pvalue
            if pvalue < critical_level: # if p-value less than the critical level
                pairs.append((keys[i], keys[j], pvalue)) # record the contract with that p-value
    return pvalue_matrix, pairs

@staticmethod
def calcHurst(df:pd.DataFrame, x_name: str, y_name: str, mu: float):
    """
    Calculates Hurst Exponent of two time-series within a dataframe 
    """
    resid = df[y_name]-df[x_name]*mu
    return compute_Hc(resid)
    
@staticmethod
def calcHurst(df:pd.DataFrame, df2:pd.DataFrame, mu: float):
    """
    Calculates Hurst Exponent of two time-series within a dataframe 
    """
    resid = df-df2*mu
    return compute_Hc(resid)
    

@staticmethod
def hurst(ts):
    """Calculates the Hurst Exponent of the time series vector ts"""

    # Create the range of lag values
    lags = range(2, 100)

    # Calculate the array of the variances of the lagged differences
    tau = [np.sqrt(np.std(np.subtract(ts[lag:], ts[:-lag]))) for lag in lags]

    # Use a linear fit to estimate the Hurst Exponent
    poly = np.polyfit(np.log(lags), np.log(tau), 1)

    # Return the Hurst exponent from the polyfit output
    return poly[0] * 2.0