from abc import abstractmethod

import pandas as pd
import BetaFactory
import os
import sys
import numpy as np
import time
import datetime as dt
import yfinance as yf
import logging

sys.path.insert(0, os.path.abspath(r'C:\Users\raymo\OneDrive\Desktop\Playground\Financial-Modelling-Playground\Quant_Trading'))
from ReferentialData import polygonData

def estimate_coef(x, y):
    # number of observations/points
    n = np.size(x)

    # mean of x and y vector
    m_x = np.mean(x)
    m_y = np.mean(y)

    # calculating cross-deviation and deviation about x
    SS_xy = np.sum(y*x,axis=0) - n*m_y*m_x
    SS_xx = np.sum(x*x,axis=0) - n*m_x*m_x

    # calculating regression coefficients
    b_1 = SS_xy / SS_xx
    b_0 = m_y - b_1*m_x

    return (b_0, b_1)

class BetaCovFactory(BetaFactory.BetaFactory):

    def __init__(self, benchmark):
        self._benchmark = benchmark
        self._beta = None
        self._universe:pd.DataFrame = None

    def calculateBeta(self, ticker_universe: pd.DataFrame):
        totalUniverse = ticker_universe.join(self._benchmark, how = "left")
        Covar = np.cov(totalUniverse,rowvar=False)
        cols = totalUniverse.columns
        beta = estimate_coef(totalUniverse[[cols[0]]], totalUniverse[[cols[1]]])
        return beta[1][ticker_universe.columns[0]]
    
    def calcBetaFromUniverse(self):
        betaPairRes = {}
        if self._universe is None:
            return betaPairRes
        columns = self._universe.columns

        for i in range(len(columns)):
            for j in range(len(columns)):
                if i >= j:
                    continue
                keyname = ",".join([columns[i], columns[j]])
                if columns[i] == columns[j]: ### shouldn't happen but we want to avoid duplicates
                    continue
                elif keyname in betaPairRes:
                    continue
                else:
                    pairBeta = BetaCovFactory.calculatePairBeta(self._universe[[columns[i]]], self._universe[[columns[j]]])
                    betaPairRes[keyname] = pairBeta
        return betaPairRes

    @staticmethod
    def calculatePairBeta(ticker2: pd.DataFrame, ticker1: pd.DataFrame):
        totalUniverse = ticker2.join(ticker1, how = "left")
        Covar = np.cov(totalUniverse,rowvar=False)
        cols = totalUniverse.columns
        beta = estimate_coef(totalUniverse[[cols[0]]], totalUniverse[[cols[1]]])
        return beta[1][totalUniverse.columns[0]]
    
    def joinUniverse(self, df:pd.DataFrame):
        if self._universe is None:
            self._universe = df
        else:
            self._universe = self._universe.join(df, how = "left")
        return None

    def _loadUniverse(self, df: pd.DataFrame):
        # self._universe = df[df.columns != ]
        return None
    
    def calculateBetaPairs(ticker_universe: pd.DataFrame):
        return None

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
    # df = pd.read_csv(os.path.join(root_dir, 'tickers.csv'))
    # _tickers = list(df[df.columns[0]])
    
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
    # save_format = "{0}_{1}_{2}".format(ticker,
    #             from_.replace("-",""),
    #             to_.replace("-",""))
    save_format = "{0}_{1}".format(bm_ticker, "histo")
    polygonData.PolygonAPI._saveData(bm_data, 
                            bm_ticker, save_format,
                            savDir)
    
    beta_res = {}

    betaFactory = BetaCovFactory(bm_data)

    ### preload data
    #Client.getPrices(tickers=_tickers, _parallel = True, override=override, logDir=savDir)
    ###

    for ticker in _tickers:
        loaded = True #False
        if ticker == bm_ticker:
            continue
            
        save_format = "{0}_{1}.csv.csv".format(ticker, "histo")
        if os.path.exists(os.path.join(savDir, ticker)):
            try:
                temp = pd.read_csv(os.path.join(savDir, ticker, 
                                            save_format))
                temp['timestamp'] = temp['timestamp'].apply(lambda str: dt.datetime.strptime(str, "%Y-%m-%d"))
                temp = temp.set_index("timestamp")
                loaded = True
            except:
                logging.info("{0} failed to load...".format(ticker))
                continue
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
                            ticker, save_format,
                            savDir)
            loaded = True
            # truncate ticker 
        if loaded:
            beta_res[ticker] = betaFactory.calculateBeta(temp)
            betaFactory.joinUniverse(temp)
    pd.DataFrame(beta_res.items(), columns=['Ticker', 'Beta']).to_csv(os.path.join(savDir, "{0}_beta.csv".format(bm_ticker)))
    ### calculate pairwise beta
    betaPairs = betaFactory.calcBetaFromUniverse()
    pd.DataFrame(betaPairs.items(), columns=['Ticker Pair', "Cross Beta"]).to_csv(os.path.join(savDir, "{0}_beta.csv".format("pairwise")))
    return pd.DataFrame(beta_res.items(), columns=['Ticker', 'Beta'])

if __name__=="__main__":
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s: %(message)s',
                        level=logging.INFO,
                        datefmt="%H:%M:%S")
    main()