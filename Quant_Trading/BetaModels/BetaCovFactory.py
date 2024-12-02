from abc import abstractmethod

import pandas as pd
import BetaFactory
import os
import sys
import numpy as np
import time
import datetime as dt
import yfinance as yf

sys.path.insert(0, os.path.abspath(r'C:\Users\raymo\OneDrive\Desktop\Playground\Financial-Modelling-Playground\Quant_Trading'))
from ReferentialData import polygonData

def estimate_coef(x, y):
    # number of observations/points
    n = np.size(x)

    # mean of x and y vector
    m_x = np.mean(x)
    m_y = np.mean(y)

    # calculating cross-deviation and deviation about x
    SS_xy = np.sum(y*x) - n*m_y*m_x
    SS_xx = np.sum(x*x) - n*m_x*m_x

    # calculating regression coefficients
    b_1 = SS_xy / SS_xx
    b_0 = m_y - b_1*m_x

    return (b_0, b_1)

class BetaCovFactory(BetaFactory.BetaFactory):

    def __init__(self, benchmark):
        self._benchmark = benchmark
        self._beta = None

    def calculateBeta(self, ticker_universe: pd.DataFrame):
        totalUniverse = ticker_universe.join(self._benchmark, how = "left")
        Covar = np.cov(totalUniverse,rowvar=False)
        cols = totalUniverse.columns
        beta = estimate_coef(totalUniverse[[cols[0]]], totalUniverse[[cols[1]]])
        return beta[1][ticker_universe.columns[0]]

    @abstractmethod
    def getBeta(self):
        return self._beta
    
def main():
    ## Load names to load 
    ## End Date
    end_dt = "2024-11-22"
    ## Start date
    start_dt = "2022-11-22"
    ## Frequency
    freq = "day"
    ### root folder
    root_dir = r'C:\Users\raymo\OneDrive\Desktop\Playground\Financial-Modelling-Playground\Quant_Trading\Histo'
    savDir=r'C:\Users\raymo\OneDrive\Desktop\Ray Stuff\_Cache\Beta_Callibration'#'D:\DB_feed\AggData'
    override=False
    bm_ticker = "^FTW5000"
    Client = polygonData.PolygonAPI()
    # Tickers to Load
    _tickers = list(pd.read_csv(os.path.join(root_dir, 'clean_names.csv'))['0'])
    df = pd.read_csv(os.path.join(root_dir, 'tickers.csv'))
    _tickers = list(df[df.columns[0]])
    
    ## extract benchmark data 
    yf_res = yf.Ticker(bm_ticker)
    info = yf_res.info
    # get historical market data
    hist = yf_res.history(interval="1D", period='2y').rename(columns={'Close':bm_ticker})
    hist = hist.tz_localize(None)
    #hist.index = hist.index.normalize()
    bm_data = hist[[bm_ticker]]

    # bm_data = pd.DataFrame(Client.getData(bm_ticker, 1, 
    #                 freq, 
    #                 start_dt, 
    #                 end_dt, 
    #                 50000))
    # bm_data['timestamp'] = pd.to_datetime(bm_data['timestamp'], unit='ms').dt.normalize()
    # bm_data = bm_data.set_index("timestamp")[["close"]].rename(columns={"close":bm_ticker})
    bm_data[bm_ticker] = np.log(bm_data[bm_ticker]) - np.log(bm_data[bm_ticker].shift(1))
    bm_data = bm_data[1:]
    polygonData.PolygonAPI._saveData(bm_data, 
                            bm_ticker, "{0}_{1}_{2}".format(bm_ticker,
                                        start_dt.replace("-",""),
                                        end_dt.replace("-","")),
                            savDir)
    
    beta_res = {}

    betaFactory = BetaCovFactory(bm_data)

    for ticker in _tickers:
        loaded = False
        if ticker == bm_ticker:
            continue
        if os.path.exists(os.path.join(savDir, ticker)):
            temp = pd.read_csv(os.path.join(savDir, ticker, 
                                        "{0}_{1}_{2}.csv".format(ticker,
                                        start_dt.replace("-",""),
                                        end_dt.replace("-",""))))
            temp['timestamp'] = temp['timestamp'].apply(lambda str: dt.datetime.strptime(str, "%Y-%m-%d"))
            temp = temp.set_index("timestamp")
            loaded = True
        elif override:
            temp = pd.DataFrame(Client.getData(ticker, 1, 
                        freq, 
                        start_dt, 
                        end_dt))
            if (len(temp) == 0):
                continue
            
            temp['timestamp'] = pd.to_datetime(temp['timestamp'], unit='ms').dt.normalize()
            temp = temp.set_index("timestamp")[["close"]].rename(columns={"close":ticker})
            temp[ticker] = np.log(temp[ticker]) - np.log(temp[ticker].shift(1))
            temp = temp[1:]
            polygonData.PolygonAPI._saveData(temp, 
                            ticker, "{0}_{1}_{2}".format(ticker,
                                        start_dt.replace("-",""),
                                        end_dt.replace("-","")),
                            savDir)
            loaded = True
            time.sleep(20)
            # truncate ticker 
        if loaded:
            beta_res[ticker] = betaFactory.calculateBeta(temp)
    pd.DataFrame(beta_res.items(), columns=['Ticker', 'Beta']).to_csv(os.path.join(savDir, "{0}_beta.csv".format(bm_ticker)))
    return pd.DataFrame(beta_res.items(), columns=['Ticker', 'Beta'])

if __name__=="__main__":
    main()