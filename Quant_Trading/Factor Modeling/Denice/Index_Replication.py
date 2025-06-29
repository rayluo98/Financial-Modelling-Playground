import datetime

import pandas as pd
from collections.abc import Callable
import os
import numpy as np
import utils
import matplotlib.pyplot as plt

## GLOBALS
DIR = r'~\Cache'
class IndexFactory:
    def __init__(self, 
                 bm_ticker:str,
                 price:pd.DataFrame, 
                 statics:pd.DataFrame, 
                 rule:Callable=None):
        self.bm_ticker = bm_ticker
        self.px = price
        self.static = statics
        ## define universe from price data frame
        self.tickers:list[str] = list(set(price['Tickers']))
        ## instantiate initial weights
        self.wt = [1.0 / len(self.tickers)]*len(self.tickers)
        ## initiate list for rebal dates
        self.rebal_dates: list[str] = []
        ## TODO in future - define function rule for calculation
        self.rule = None

    def setRebalDates(self, dates:list[datetime.date|str]):
        self.rebal_dates = utils.ConvertDt(dates)

    ### APPLY WEIGHTS AT REBAL DATES TO REPLICATE ETF
    def CreateETF(self):
        if self.rebal_dates == None:
            raise ValueError("NO REBALANCE DATES FOUND")
        #### TODO #####
        pass

def main():
    ## load existing data - all SP500 names over the last 10 years

    # we want to define our univesrse
    sp_current, sp_past = utils.getSPXConstituents()

    history = pd.read_csv(os.path.join(DIR, "data.csv"))
    ## pull static data
    static = pd.read_csv(os.path.join(DIR, "static.csv"))

    ## create index replication object
    index_factory = IndexFactory(history, static)



    pass


if __name__ == "__main__":
