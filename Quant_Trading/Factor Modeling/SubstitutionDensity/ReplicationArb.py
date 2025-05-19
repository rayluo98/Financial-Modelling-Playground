from importlib import reload
import BacktestEngine.backtest as backtest
import BacktestEngine.order_book as order_book
import scipy.odr as odr
import pandas as pd
from numpy import arange
from sklearn.linear_model import Ridge
from sklearn.linear_model import RidgeCV
from sklearn.linear_model import ElasticNetCV
from sklearn.model_selection import RepeatedKFold#define cross-validation method to evaluate model

import numpy as np
import pandas as pd
import tensorflow as tf
import matplotlib.pyplot as plt
import seaborn as sns
import datetime as dt
import yfinance as yf
import pickle
import os
import math
from ReferentialData.polygonData import PolygonAPI
from DataAnalysis import DataExtensions
from Filtering.KalmanFilter import KalmanFilter

def loadHisto(BUCKETS, start_dt, end_dt, DIR):
        # Concatenating dictionary value lists
    UNIVERSE=[]
    for i in list(BUCKETS.values()):
        UNIVERSE.extend(i)

    colnames = ["Close", "Volume"]
    DataLoader = PolygonAPI()
    ### loading in low frequency data
    if len(mid_df) == 0:
        mid_df = DataLoader.getPrices(UNIVERSE, timespan= "day", from_ = start_dt, 
                                        to_=end_dt,
                                    logDir=os.path.join(DIR,"Beta_Callibration"), _parallel=True)

    ### loading in high frequency data
    if len(high_df) == 0:
        high_df = DataLoader.getPrices(UNIVERSE,from_ = start_dt, 
                                        to_=end_dt, timespan="minute", logDir=DIR, _parallel=True)

    return high_df, mid_df

def getBenchmarkData():
    beta = pd.read_csv(r'C:\Users\raymo\OneDrive\Desktop\Ray Stuff\_Cache\Beta_Callibration\^FTW5000_beta.csv')
    beta = beta.loc[:, ~beta.columns.str.contains('^Unnamed')]
    beta['Beta'] = [float(x.split(",")[0][1:]) for x in beta['Beta']]
    beta = beta.set_index("Ticker")
    beta = beta.to_dict()['Beta']

    bm_data = pd.read_csv(r'C:\Users\raymo\OneDrive\Desktop\Playground\Financial-Modelling-Playground\Quant_Trading\BetaModels\FTW5000.csv')

    return beta, bm_data

def getCorrData(BUCKETS):
    corr = pd.read_csv(r'C:\Users\raymo\OneDrive\Desktop\Ray Stuff\_Cache\Beta_Callibration\pairwise_corr.csv')
    corr = corr.loc[:, ~corr.columns.str.contains('^Unnamed')]
    bucket_corr_mask = lambda price_data: len(set(price_data[0].split(',')).intersection(set(BUCKETS[list(BUCKETS.keys())[0]])))==2
    corr = corr[corr.apply(bucket_corr_mask, axis=1)]
    corr = corr.sort_values(by="Cross Correlation")
    return corr


def processData(hf_bucket, mf_bucket, beta):
    daily_dt = 10e3*60*60*24
    min_dt = 10e3*60
    dt_ratio = daily_dt / min_dt 

import time
def datetime_to_ms_epoch(dt):
    microseconds = time.mktime(dt.timetuple()) * 1000000 + dt.microsecond
    return int(round(microseconds / float(1000)))

def get_unixtime(dt64):
    return dt64.astype('datetime64[s]').astype('int')

def shift(xs, n):
    if n >= 0:
        return np.concatenate((np.full(n, np.nan), xs[:-n]))
    else:
        return np.concatenate((xs[-n:], np.full(-n, np.nan)))
    
def getTimeDiffs(dt_list: np.array):
    ## case to ms unix tyime
    if type(dt_list[0]) == np.datetime64:
        dt_list = get_unixtime(dt_list)
    shifted_dt = np.roll(dt_list, 1)
    res = dt_list - shifted_dt
    res[0] = 0 ## as this makes no sense
    return res

logReturnTransform = lambda df : np.log(df.loc[:,~df.columns.str.contains('timestamp')]) - np.log(df.loc[:,~df.columns.str.contains('timestamp')].shift(1))
def logRetDtDailyTransform(df):
    return logReturnTransform(df.loc[:,~df.columns.str.contains('timestamp')]).apply(
        lambda col: np.asarray(col) / getTimeDiffs(np.asarray(df.index.values)) *math.sqrt(dt_ratio))

# print('Beta Adjustment on Mid-Frequency is: {0}.'.format(mf_betaAdj))
def print_summary(mf_bucket, hf_bucket, data):
    mf_summary = {}
    for data in mf_bucket:
        mu = logReturnTransform(mf_bucket[data].drop('otc',axis=1))['close'].mean()
        std = logReturnTransform(mf_bucket[data].drop('otc',axis=1))['close'].std()
        mu_hf = logRetDtDailyTransform(hf_bucket[data].drop('otc',axis=1))['close'].mean()
        std_hf = logRetDtDailyTransform(hf_bucket[data].drop('otc',axis=1))['close'].std()
        mf_summary[data] = {"Mu": mu, "Sigma":std, "Beta":beta[data],
                            "Mu_Min": mu_hf, "Sigma_Min": std_hf}
    mf_summary = pd.DataFrame(mf_summary)
    return mf_summary

def RidgeRegression(X,y):
    cv = RepeatedKFold(n_splits=10, n_repeats=3, random_state=1)

    #define model
    model = RidgeCV(alphas=arange(0, 1, 0.01), 
                    cv=cv, 
                    scoring='neg_mean_absolute_error',
                    fit_intercept=False)

    #fit model
    model.fit(X, y)

    #display lambda that produced the lowest test MSE
    print(model.coef_)

    return model

def main():
    ## End Date
    end_dt = "2025-02-10"
    ## Start date
    start_dt = "2020-01-20"
    # Loading "pairs trade" buckets
    DIR = r'C:\Users\raymo\OneDrive\Desktop\Ray Stuff\_Cache'
    COR_DIR = r'\Users\raymo\OneDrive\Desktop\Playground\Financial-Modelling-Playground\Quant_Trading\Clustering'
    with open(os.path.join(COR_DIR, "correlation_buckets_no_shorts.pkl"), "rb") as file:
        BUCKETS = pickle.load(file)

    high_df, mid_df = loadHisto(BUCKETS, start_dt, end_dt, DIR)

    beta, bm_data = getBenchmarkData()
    bm_ticker = "^FTW5000"
    corr = getCorrData()

    for ref_ticker in BUCKETS:
        bucket_mask = lambda price_data: price_data[0] in BUCKETS[ref_ticker]
        hf_bucket = dict(filter(bucket_mask, high_df[0].items()))
        mf_bucket = dict(filter(bucket_mask, mid_df[0].items()))
    
        hf_df, mf_df = pd.DataFrame(), pd.DataFrame()
        for ticker in hf_bucket:
            if len(hf_df) == 0:
                temp = hf_bucket[ticker].rename(columns={'close':ticker})[['timestamp',ticker]]
                temp['timestamp'] = pd.to_datetime(temp['timestamp'], unit='ms')
                hf_df = temp.set_index('timestamp')
            else:
                temp = hf_bucket[ticker].rename(columns={'close':ticker})[['timestamp',ticker]]
                temp['timestamp'] = pd.to_datetime(temp['timestamp'], unit='ms')
                hf_df = hf_df.join(temp.set_index('timestamp'),
                            how = 'left')
        hf_df = hf_df.fillna(method='ffill')
        hf_df = hf_df.dropna() ## removes dates where not all components are present
        for ticker in mf_bucket:
            if len(mf_df) == 0:
                temp = mf_bucket[ticker].rename(columns={'close':ticker})[['timestamp',ticker]]
                temp['timestamp'] = pd.to_datetime(temp['timestamp'], unit='ms')
                mf_df = temp.set_index('timestamp')
            else:
                temp = mf_bucket[ticker].rename(columns={'close':ticker})[['timestamp',ticker]]
                temp['timestamp'] = pd.to_datetime(temp['timestamp'], unit='ms')
                mf_df = mf_df.join(temp.set_index('timestamp'),
                            how = 'left')
        print_summary(mf_bucket, hf_bucket, ticker)
        mf_df = mf_df.fillna(method='ffill')
        mf_df = mf_df.dropna()

        ### merge back hf price data to mf signal
        # neutralizeBeta = lambda dcol: dcol[ticker] - mf_summary[ticker] for ticker in df)
        mf_log = logReturnTransform(mf_df)
        mf_log = pd.merge_asof(mf_log.reset_index(), logReturnTransform(bm_data), on = 'timestamp').dropna().set_index('timestamp')
        components = list(mf_log.columns.values)
        components.remove(bm_ticker)
        ### remove beta from FTW5000
        mf_log[components] = mf_log[components].apply(lambda dcol: dcol - mf_summary.loc['Beta', dcol.name] 
                                                            *mf_log[bm_ticker] , axis = 0)
        mf_log.drop(bm_ticker, axis=1, inplace=True) ## remove benchmark data
        x_temp = mf_log.loc[:, ~mf_log.columns.str.contains(ref_ticker)]
        x_temp = -1*x_temp.iloc[1:]
        # ElasticNet(x,y, 0)
        x = np.array(x_temp)
        y = np.array(mf_log[ref_ticker].iloc[1:])
        coeffs_ = RidgeRegression(x,y).coef_

        elementExp = lambda row, coeffs: np.power(np.array(row), coeffs_)
        positive_legs = mf_df.loc[:, ~mf_df.columns.str.contains(ref_ticker)]
        signal = positive_legs.apply(lambda dr:elementExp(dr, coeffs_).sum(), axis = 1)
        signal = signal.add(-1*mf_df[ref_ticker])
        Signal = pd.DataFrame(signal, columns=['Signal'])
        means, covs = KalmanFilter.KalmanFilter.UnivariateKF('Signal', Signal, 
                                                     1,
                                                     1)
        mean, std = means.squeeze(), np.std(covs.squeeze())
        state_means0 = np.array(pd.DataFrame(means)[0])
        resid = Signal['Signal'] - state_means0
        stdev = []
        for i in range(len(resid)):
            stdev.append(math.sqrt(covs[i][0][0]))










if __name__ == "__main__":
    main()