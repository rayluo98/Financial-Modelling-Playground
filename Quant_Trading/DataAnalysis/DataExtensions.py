from matplotlib import pyplot as plt
import numpy as np
from logging import Logger
from statsmodels.tsa.stattools import adfuller
from statsmodels.graphics import tsaplots 
from sklearn.preprocessing import MinMaxScaler
import pandas as pd
import seaborn as sns
import statsmodels as sm
from hurst import compute_Hc
import time

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
def scatterHeat(name1, name2, heat, df):
    """
    Create a scatterplot of the two ETF prices, which is
    coloured by the date of the price to indicate the 
    changing relationship between the sets of prices    
    """
    # Create a yellow-to-red colourmap where yellow indicates
    # early dates and red indicates later dates
    plen = len(df[heat])
    colour_map = plt.cm.get_cmap('jet')    
    # Create a MinMaxScaler instance
    scaler = MinMaxScaler()

    # Fit the scaler to the data
    scaler.fit(df[[heat]])

    # Transform the data
    colours = scaler.transform(df[[heat]])
    
    # Create the scatterplot object
    scatterplot = plt.scatter(
        df[name1], df[name2], 
        s=30, c=colours, cmap=colour_map, 
        edgecolor='k', alpha=0.8
    )
    
    # Add a colour bar for the date colouring and set the 
    # corresponding axis tick labels to equal string-formatted dates
    colourbar = plt.colorbar(scatterplot)
    plt.xlabel(name1)
    plt.ylabel(name2)
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

@staticmethod
def findOutliers(ts: pd.Series,
                 mode: str='ZScore',
                 params: dict={}
                 )->list:
    """
    Finds the indices of values where there is an outlier
    Returns a list of tuples of beginning of outlier to end 
    """
    match mode:
        case _:
            return zscoreOutliers(ts, params)
    return

@staticmethod
def zscoreOutliers(ts: pd.Series,
                   params: dict={}):
    res = []
    mu = np.mean(ts)
    sigma = np.std(ts)
    if 'std' in params:
        sigma *= params['std']
    outlierFlag = False
    start = 0
    end = 0
    for key, val in ts.items():
        if (abs(val - mu) > sigma):
            if not outlierFlag:
                start = key 
                outlierFlag = True
        else:
            if outlierFlag:
                end = key
                outlierFlag = False
                res.append((start, end))
    return res

@staticmethod
def datetime_to_ms_epoch(dt):
    microseconds = time.mktime(dt.timetuple()) * 1000000 + dt.microsecond
    return int(round(microseconds / float(1000)))

@staticmethod
def get_unixtime(dt64):
    return dt64.astype('datetime64[s]').astype('int')

@staticmethod
def shift(xs, n):
    if n >= 0:
        return np.concatenate((np.full(n, np.nan), xs[:-n]))
    else:
        return np.concatenate((xs[-n:], np.full(-n, np.nan)))
    
@staticmethod
def getTimeDiffs(dt_list: np.array):
    ## case to ms unix tyime
    if type(dt_list[0]) == np.datetime64:
        dt_list = get_unixtime(dt_list)
    shifted_dt = np.roll(dt_list, 1)
    res = dt_list - shifted_dt
    res[0] = 0 ## as this makes no sense
    return res