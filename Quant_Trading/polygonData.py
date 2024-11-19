from polygon import RESTClient
import datetime as dt
import json
import pandas as pd
import os
import logging
import time
from pathlib import Path

class PolygonAPI(object):
    def __init__(self) -> None:
        f = open("polygonApiKey.txt", "r")
        API_KEY = f.read()
        self._client = RESTClient(api_key=API_KEY)
        pass

    def __repr__(self) -> str:
        return self.get__repr__()
    
    def getData(self, 
                ticker: str, multiplier:int = 1, 
                timespan:str="minute", 
                from_="2023-01-01", 
                to="2023-06-13", 
                limit=50000,
                logDir=r'C:\Users\raymo\OneDrive\Desktop\Ray Stuff\_ErrorLogs'):
    # List Aggregates (Bars)
        aggs = []
        hasErr: bool = False
        _error = []
        try:
            for a in self._client.list_aggs(ticker=ticker, multiplier=1, timespan="minute", from_="2023-01-01", to="2023-06-13", limit=50000):
                aggs.append(a)
        except:
            logging.info("Ticker {0} unable to be loaded!".format(ticker))

        return aggs

    def getLastTrade(self, ticker: str):
        # Get Last Trade
        trade = self._client.get_last_trade(ticker=ticker)
        print(trade)

    def getListTrades(self, ticker: str, timestamp: str):
        # List Trades
        trades = self._client.list_trades(ticker=ticker, timestamp="2022-01-04")
        trade_res = []
        for trade in trades:
            trade_res.append(trade)
        return trade_res
    
    def getLastQuote(self, ticker: str):
        # Get Last Quote
        return self._client.get_last_quote(ticker=ticker)

    def listQuotes(self, ticker: str, timestamp: str):
        # List Quotes
        quotes = self._client.list_quotes(ticker=ticker, timestamp="2022-01-04")
        quote_res = []
        for quote in quotes:
            quote_res.append(quote)
        return quote_res
    
    def _removeCache():
        return None
    
    @staticmethod
    def _removeEmptyFiles(path: str=r'D:\DB_feed\AggData', threshold: str = 1000):
        for root, dirs, files in os.walk(path, topdown=True, onerror=None, followlinks=False):
            if (len(files) == 0):
                continue
            df_temp = pd.read_csv(root + "\\" + files[0])
            if len(df_temp) < threshold:
                os.remove(root + "\\" + files[0])
                os.removedirs(root)
        return None
    
    @staticmethod
    def _jsonToDf(json:dict):
        return pd.DataFrame(json['result'])

    @staticmethod
    def _saveData(df: pd.DataFrame, ticker:str, file_name: str, path: str=r'D:\DB_feed\AggData'):
        loc_dir = os.path.join(path, ticker)
        if not os.path.exists(loc_dir):
            os.mkdir(loc_dir)
        df.to_csv(Path(loc_dir) / f"{file_name}.csv")
        logging.info("Finished Saving {0}".format(file_name))
        

# Defining main function
def main():
    Client = PolygonAPI()
    ## Load names to load 
    ## End Date
    end_dt = "2024-11-15"
    ## Start date
    start_dt = "2019-07-10"
    ## Frequency
    freq = "Hour"
    ### root folder
    root_dir = r'C:\Users\raymo\OneDrive\Desktop\Playground\Financial-Modelling-Playground\Quant_Trading\Histo'
    savDir=r'C:\Users\raymo\OneDrive\Desktop\Ray Stuff\_Cache'#'D:\DB_feed\AggData'
    override=False

    Tickers to Load
    _tickers = list(pd.read_csv(os.path.join(root_dir, 'clean_names.csv'))['0'])
    df = pd.read_csv(os.path.join(root_dir, 'tickers.csv'))
    _tickers = list(df[df.columns[0]])

    # truncate ticker 
    startFrom = ""
    
    if startFrom != "":
        try:
            _startIndex = _tickers.index(startFrom)
        except:
            _startIndex = 0
        _tickers = _tickers[_startIndex:]

    ## loading [avoid multithreading due to data parsing limit
    for ticker in _tickers:
        if not override and os.path.exists(os.path.join(savDir, ticker)):
            continue
        PolygonAPI._saveData(pd.DataFrame(Client.getData(ticker)), 
                             ticker, "{0}_{1}_{2}".format(ticker,
                                        start_dt.replace("-",""),
                                        end_dt.replace("-","")),
                            savDir)
        time.sleep(12) ## limit 5 api calls per minute

    # PolygonAPI._removeEmptyFiles(savDir)


# Using the special variable 
# __name__
if __name__=="__main__":
    main()