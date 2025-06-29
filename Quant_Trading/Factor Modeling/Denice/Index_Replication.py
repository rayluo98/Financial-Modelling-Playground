import datetime

import pandas as pd
from collections.abc import Callable
import os
import numpy as np
import utils
import matplotlib.pyplot as plt

'''
The following script is to be applied to ETF index replication (specifically observing XLF)
    and attempts to achieve the following goals:
1. Determine the historical weights that go into the ETF (XLF) to match the underlying index (Select S&P Financial)
    - we can observe recent weights through a fact sheet on XLF
    - the underlying rules to the index is transparent
2. Minimize tracking error by handling corporate actions correctly on the underlyings
3. Capture flow-price impact on the rebalance for the Index/ETF
    - introduce some kind of price movement metric on the usnderlying flow - think ADV 
'''


## GLOBALS
DIR = r'~\Cache'
class IndexFactory:
    def __init__(self,
                 price:pd.DataFrame, 
                 reference_idx:pd.DataFrame,
                 statics:pd.DataFrame, 
                 rule:Callable=None):
        self.px = price
        self.static = statics
        self.reference_idx = reference_idx
        ## define universe from price data frame
        self.tickers:list[str] = list(set(price['Tickers']))
        ## instantiate initial weights
        self.wt = pd.DataFrame()
        ## initiate list for rebal dates
        self.rebal_dates: list[str] = []
        ## TODO in future - define function rule for calculation
        self.rule = None

    def getRebalDates(self):
        return self.rebal_dates

    def setRebalDates(self, dates:list[datetime.date|str]):
        self.rebal_dates = utils.ConvertDt(dates)

    def calcWeights(self):
        ### TODO ####
        ## find the weights - you can do this using rules based or some kind of fitting
        # My suggestion is you do rules based first, then try fitting
        pass

    def predictWeights(self, time):
        ### TODO ####
        # we want to predict the weights for the next rebalance period 
        pass

    ### APPLY WEIGHTS AT REBAL DATES TO REPLICATE ETF
    def CreateETF(self):
        if self.rebal_dates == None:
            raise ValueError("NO REBALANCE DATES FOUND")
        #### TODO #####
        pass

    def predictRebalImpact(self, metric:Callable=None):
        ### TODO ###
        # fill in some price impact metric to predict price/flow impact on rebal
        pass

def main():
    ## load existing data - all SP500 names over the last 10 years

    # we want to define our univesrse
    sp_current, sp_past = utils.getSPXConstituents()

    history = pd.read_csv(os.path.join(DIR, "data.csv"))
    ## pull static data
    static = pd.read_csv(os.path.join(DIR, "static.csv"))

    ### scrape index data
    # https://www.spglobal.com/spdji/en/indices/equity/sp-500-financials-sector/#overview
    ## you can scrape price data here: https://www.marketwatch.com/investing/index/ixm/download-data?startDate=6/27/2023&endDate=6/27/2024&countryCode=xx
    indx_hist = pd.read_csv(os.path.join(DIR, "index.csv"))


    ## create index replication object
    index_factory = IndexFactory(history, indx_hist, static)

    ## store rebal dates here <--
    REBAL_DATES = []
    index_factory.setRebalDates(REBAL_DATES)

    ## TODO ###
    DUMMY_INPUT = None
    index_factory.predictWeights(DUMMY_INPUT)

    etf_child = index_factory.CreateETF()

    ### then do some price impact analysis to get a signal
    index_factory.predictRebalImpact()

    pass


if __name__ == "__main__":
    main()