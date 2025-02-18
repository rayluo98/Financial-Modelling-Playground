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
from DataAnalysis.DataExtensions import *
from Filtering.KalmanFilter import KalmanFilter
import logging
import glob

from enum import Enum

class Weekday(Enum):
    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6

def get_unixtime(dt64):
    return dt64.astype('datetime64[s]').astype('int')

daily_dt = 10e3*60*60*24
min_dt = 10e3*60
dt_ratio = daily_dt / min_dt 


def getTimeDiffs(dt_list: np.array):
    ## case to ms unix tyime
    if type(dt_list[0]) == np.datetime64:
        dt_list = get_unixtime(dt_list)
    shifted_dt = np.roll(dt_list, 1)
    res = dt_list - shifted_dt
    res[0] = 0 ## as this makes no sense
    return res

logReturnTransform = lambda df : np.log(df.loc[:,~df.columns.str.contains('timestamp')]) - np.log(df.loc[:,~df.columns.str.contains('timestamp')]).shift(1)
def logRetDtDailyTransform(df):
    return logReturnTransform(df.loc[:,~df.columns.str.contains('timestamp')]).apply(
        lambda col: np.asarray(col) / getTimeDiffs(np.asarray(df.index.values)) *math.sqrt(dt_ratio))


def main():
    DIR = r'C:\Users\raymo\OneDrive\Desktop\Ray Stuff\_Cache'
    root_dir = r'C:\Users\raymo\OneDrive\Desktop\Playground\Financial-Modelling-Playground\Quant_Trading\Histo'
    COR_DIR = r'\Users\raymo\OneDrive\Desktop\Playground\Financial-Modelling-Playground\Quant_Trading\Clustering'
    # Tickers to Load
    UNIVERSE = list(pd.read_csv(os.path.join(root_dir, 'clean_names.csv'))['0'])
    # UNIVERSE = ['AAPL']
    ## End Date
    end_dt = "2025-01-01"
    ## Start date
    start_dt = "2020-01-01"

    colnames = ["Close", "Volume"]
    DataLoader = PolygonAPI()
    MID_LOADED = False
    HIGH_LOADED = False
    if not MID_LOADED:
        mid_df = {}
    if not HIGH_LOADED:
        high_df = {}
    # ### loading in low frequency data
    # if len(mid_df) == 0:
    #     mid_df = DataLoader.getPrices(UNIVERSE, "day", logDir=os.path.join(DIR,"Beta_Callibration"), _parallel=True)
    #     MID_LOADED = True

    ### loading in high frequency data
    if len(high_df) == 0:
        high_df = DataLoader.getPrices(UNIVERSE, timespan="hour", 
                                    from_ = start_dt, 
                                    to_=end_dt, logDir=DIR, override=False, _parallel=True)
        HIGH_LOADED = True

    master_df = pd.DataFrame()
    master_df = pd.concat(high_df[0].values())
    master_df.sort_values('timestamp', inplace=True)
    master_df
    # for ticker in high_df[0]:
        # master_df = pd.concat([high_df[0][ticker], master_df])
    # master_df

    ### Cross-Sectional Analysis 

    ### time delta indication that it's CLOSE - OPEN (standard day): 9am = 33:00, 4:30pm = 16:30
    CLOSE_OPEN_DELTA = (33 - 16.5) * 60
    ### time delta indication that it's WEEKEND: CLOSE_OPEN_DELTA + 48 HRS
    CLOSE_OPEN_WEEKEND_DELTA = CLOSE_OPEN_DELTA + 48 * 60

    WeekdayDeltaMask = lambda dt: dt < CLOSE_OPEN_WEEKEND_DELTA and dt > CLOSE_OPEN_DELTA
    WeekendDeltaMask = lambda dt: dt > CLOSE_OPEN_WEEKEND_DELTA

    def EODvEOW(test, name):
        test['DtBucket'] = test.apply(lambda dr: int(WeekdayDeltaMask(dr['TimeDelta'])) + 2*int(WeekendDeltaMask(dr['TimeDelta'])), axis=1)
        # test = test[test['TimeDelta'] > 1]
        scatterHeat('DtBucket', 'close', 'timestamp', test, True, name + "_close_EODvEOW")
        scatterHeat('DtBucket', 'vwap', 'timestamp', test, True, name + "_vwap_EODvEOW")
        scatterHeat('DtBucket', 'volume', 'timestamp', test, True, name + "_volume_EODvEOW")

    def WEEKDAY_EOD(test, name):
        test['WeekdayBucket'] = [pd.to_datetime(date, unit='ms').weekday() for date in test['timestamp']]
        scatterHeat('WeekdayBucket', 'close', 'timestamp', test, True, name + "_close_EOD")
        scatterHeat('WeekdayBucket', 'close', 'timestamp', test, True, name + "_vwap_EOD")
        scatterHeat('WeekdayBucket', 'close', 'timestamp', test, True, name + "_volume_EOD")

    def INTRADAY_ANALYSIS(test, name):
        ### intraday filter
        intra_test = test[test['TimeDelta'] <= 60]
        intra_test['WeekdayBucket'] = [pd.to_datetime(date, unit='ms').weekday() for date in intra_test['timestamp']]
        # plt.scatter(intra_test['WeekdayBucket'], intra_test['close'])
        scatterHeat('WeekdayBucket', 'close', 'timestamp', intra_test, True, name + "_close_intra")
        scatterHeat('WeekdayBucket', 'close', 'timestamp', intra_test, True, name + "_vwap_intra")
        scatterHeat('WeekdayBucket', 'close', 'timestamp', intra_test, True, name + "_volume_intra")

        weekday_vol_summary = {}
        for i in range(0,6):
            weekday_df = intra_test[intra_test['WeekdayBucket']==i]
            weekday_vol_summary[Weekday(i)] = weekday_df['close'].describe()

        res = pd.DataFrame(weekday_vol_summary).transpose()
        res.reset_index(names="Weekday", inplace=True)
        res['Ticker'] = name
        return res
    
    def INTERDAY_ANALYSIS(test, name):
        ### interday filter
        inter_test = test[test['TimeDelta'] > 60]
        inter_test['WeekdayBucket'] = [pd.to_datetime(date, unit='ms').weekday() for date in inter_test['timestamp']]
        # plt.scatter(intra_test['WeekdayBucket'], intra_test['close'])
        scatterHeat('WeekdayBucket', 'close', 'timestamp', inter_test, True, name + "_close_inter")
        scatterHeat('WeekdayBucket', 'close', 'timestamp', inter_test, True, name + "_vwap_inter")
        scatterHeat('WeekdayBucket', 'close', 'timestamp', inter_test, True, name + "_volume_inter")
        weekday_vol_summary = {}
        for i in range(0,6):
            weekday_df = inter_test[inter_test['WeekdayBucket']==i]
            weekday_vol_summary[Weekday(i)] = weekday_df['close'].describe()

        res = pd.DataFrame(weekday_vol_summary).transpose()
        res.reset_index(names="Weekday", inplace=True)
        res['Ticker'] = name
        return res

    intraday_summary = pd.DataFrame()
    interday_summary = pd.DataFrame()

    for ticker in high_df[0]:
        try:
            test = logReturnTransform(high_df[0][ticker].drop('otc',axis=1))
            test['timestamp'] = high_df[0][ticker]['timestamp']
            test['TimeDelta'] =  (high_df[0][ticker]['timestamp'] - high_df[0][ticker]['timestamp'].shift(1)).values / (60 * 1000)
            EODvEOW(test, ticker)
            WEEKDAY_EOD(test, ticker)
            intraday_summary = pd.concat([intraday_summary, INTRADAY_ANALYSIS(test, ticker)])
            interday_summary = pd.concat([interday_summary, INTERDAY_ANALYSIS(test, ticker)])
        except:
            print(f"Error loading {ticker}")
        
    intraday_summary.to_csv(r'C:\Users\raymo\OneDrive\Desktop\Ray Stuff\EDA\INTRADAY_SUMMARY.csv')
    interday_summary.to_csv(r'C:\Users\raymo\OneDrive\Desktop\Ray Stuff\EDA\INTERDAY_SUMMARY.csv')


if __name__ == "__main__":

    main()