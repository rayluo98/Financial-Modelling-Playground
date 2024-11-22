from abc import abstractmethod

import pandas as pd
import BetaFactory
import os
import sys
import numpy as np
import time

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
        beta = estimate_coef(totalUniverse[[cols[1]]], totalUniverse[[cols[2]]])
        return Covar

    @abstractmethod
    def getBeta(self):
        return self._beta
    

def main():
    Client = polygonData.PolygonAPI()
    ## Load names to load 
    ## End Date
    end_dt = "2024-07-10"
    ## Start date
    start_dt = "2019-07-10"
    ## Frequency
    freq = "day"
    ### root folder
    root_dir = r'C:\Users\raymo\OneDrive\Desktop\Playground\Financial-Modelling-Playground\Quant_Trading\Histo'
    savDir=r'C:\Users\raymo\OneDrive\Desktop\Ray Stuff\_Cache\Beta_Callibration'#'D:\DB_feed\AggData'
    override=False

    # Tickers to Load
    _tickers = list(pd.read_csv(os.path.join(root_dir, 'clean_names.csv'))['0'])
    df = pd.read_csv(os.path.join(root_dir, 'tickers.csv'))
    _tickers = list(df[df.columns[0]])

    ## extract benchmark data 
    bm_ticker = "ACWI"

    bm_data = pd.DataFrame(Client.getData(bm_ticker, 1, 
                    freq, 
                    start_dt, 
                    end_dt)).set_index("timestamp")[["close"]].rename(columns={"close":bm_ticker})
    bm_data[bm_ticker] = bm_data[bm_ticker].pct_change()
    bm_data = bm_data[1:]
    polygonData.PolygonAPI._saveData(bm_data, 
                             bm_ticker, "{0}_{1}_{2}".format(bm_ticker,
                                        start_dt.replace("-",""),
                                        end_dt.replace("-","")),
                            savDir)
    
    beta_res = dict()

    betaFactory = BetaCovFactory(bm_data)

    for ticker in _tickers:
        if ticker == bm_ticker:
            continue
        if os.path.exists(os.path.join(savDir, ticker)):
            temp = pd.read_csv(os.path.join(savDir, ticker, 
                                        "{0}_{1}_{2}.csv".format(ticker,
                                        start_dt.replace("-",""),
                                        end_dt.replace("-",""))))
        else:
            temp = pd.DataFrame(Client.getData(ticker, 1, 
                        freq, 
                        start_dt, 
                        end_dt))
            if (len(temp) == 0):
                continue
            else:
                temp = temp.set_index("timestamp")[["close"]].rename(columns={"close":ticker})
                temp[ticker] = temp[ticker].pct_change()
                temp = temp[1:]
                polygonData.PolygonAPI._saveData(temp, 
                                ticker, "{0}_{1}_{2}".format(ticker,
                                            start_dt.replace("-",""),
                                            end_dt.replace("-","")),
                                savDir)
                time.sleep(12)
            # truncate ticker 
        beta_res[ticker] = betaFactory.calculateBeta(temp)
    return None

if __name__=="__main__":
    main()