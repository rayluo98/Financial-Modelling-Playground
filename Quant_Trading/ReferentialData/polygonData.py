from polygon import RESTClient
import datetime as dt
import json
import pandas as pd
import os
import logging
import time
import concurrent.futures
from threading import Thread
from threading import RLock
from pathlib import Path
import glob

class PolygonAPI(object):
    def __init__(self) -> None:
        f = open(r"C:\Users\raymo\OneDrive\Desktop\Playground\Financial-Modelling-Playground\Quant_Trading\ReferentialData\polygonApiKey.txt", "r")
        API_KEY = f.read()
        self._client = RESTClient(api_key=API_KEY)
        pass

    def __repr__(self) -> str:
        return self.get__repr__()
    
    def getStatics(self, 
                   tickers:list,
                   from_="2023-01-01", 
                to_="2023-06-13"):
        return []

    def getStatic(self, 
                ticker:str, 
                from_="2023-01-01", 
                to_="2023-06-13"):
        statics = {}
        hasErr: bool = False
        _error = []
        start_dt = pd.Timestamp(from_)
        end_dt = pd.Timestamp(to_)
        while(start_dt < end_dt):
            date = start_dt.strftime("%Y-%m-%d")
            try:
                statics[date]=self._client.get_ticker_details(ticker, date)
            except:
                logging.info("Ticker {0} Statucs unable to be loaded for {1}!".format(ticker, date))
            start_dt += pd.offsets.BusinessDay(1)
            
        return pd.DataFrame(statics)
        
    def getPrices(self, 
                tickers: list, multiplier:int = 1, 
                timespan:str="minute", 
                from_="2023-01-01", 
                to_="2023-06-13", 
                limit=50000,
                logDir:str|None = None, # r'C:\Users\raymo\OneDrive\Desktop\Ray Stuff\_ErrorLogs',
                _parallel = False,
                override=False):
        format = "%(asctime)s: %(message)s"
        #need to make sure items are unique as race conditions are not handled  for multithreading
        # keys: ticker name
        # values: (info, history)
        LE_HISTO = dict() 
        result = {}

         ## inline loadHistory - TODO: make this function abstract factory class
        def loadHistory(ticker: str, histo: dict, lock:RLock=None, override:bool=False):
            with lock:
                foundCache = False
                if not override and logDir != None:
                    files = glob.glob(os.path.join(logDir, ticker, "*.csv"))
                    if len(files) > 0:
                        foundCache = True
                        hist = pd.read_csv(files[0])
                # get historical market data
                if not foundCache:
                    hist = pd.DataFrame(self.getData(ticker, multiplier, timespan, from_, to_, limit, attemptNo=0))
                if logDir != None and not foundCache and len(hist) > 1:
                    save_format = "{0}_{1}_{2}".format(ticker,
                                    from_.replace("-",""),
                                    to_.replace("-",""))
                    save_format = "{0}_{1}".format(ticker, "histo")
                    self._saveData(hist, ticker, save_format, logDir, override)
                if len(hist) > 1:
                    histo[ticker] = hist ## to replace with struct
                return hist

        if _parallel:
            lock = RLock()
            func = lambda x: loadHistory(x, LE_HISTO, lock, override)
            with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
                #result = executor.map(functools.partial(loadHistory , tickers, LE_HISTO, lock))
                executor.map(func, tickers)
        else:
            for ticker in tickers:
                hist = loadHistory(ticker, LE_HISTO)
                if len(hist) > 0:
                    LE_HISTO[ticker] = hist
                time.sleep(12) ## limit 5 api calls per minute
        return LE_HISTO


    def getData(self, 
                ticker: str, multiplier:int = 1, 
                timespan:str="minute", 
                from_="2023-01-01", 
                to_="2023-06-13", 
                limit=50000,
                attemptNo = 0):
    # List Aggregates (Bars)
        aggs = []
        hasErr: bool = False
        _error = []
        try:
            for a in self._client.list_aggs(ticker=ticker, multiplier=1, timespan=timespan, from_=from_, to=to_, limit=limit):
                aggs.append(a)
            if len(aggs) == 0:
                if attemptNo > 2:
                    # logging.info("No data loaded for Ticker {0}".format(ticker))
                    logging.info("No data loaded for Ticker {0}".format(ticker))
                else:
                    time.sleep(5)
                    logging.info("Retrying for ticker {0}... Attempt {1}".format(ticker, attemptNo + 2))
                    return self.getData(ticker, timespan=timespan, from_=from_, to_=to_, limit=limit, attemptNo=attemptNo + 1)
        except:
            if attemptNo > 2:
                logging.info("No data loaded for Ticker {0}".format(ticker))
            else:
                time.sleep(5)
                logging.info("Retrying for ticker {0}... Attempt {1}".format(ticker, attemptNo + 2))
                return self.getData(ticker, timespan=timespan, from_=from_, to_=to_, limit=limit, attemptNo=attemptNo + 1)
        return aggs

    def getLastTrade(self, ticker: str):
        # Get Last Trade
        trade = self._client.get_last_trade(ticker=ticker)
        # logging.info(trade)

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
    def _saveData(df: pd.DataFrame, 
                  ticker:str, 
                  file_name: str, 
                  path: str|None=r'D:\DB_feed\AggData',
                  override:bool=False):
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
    end_dt = "2024-12-01"
    ## Start date
    start_dt = "2019-06-01"
    ## Frequency
    freq = "Hour"
    ### root folder
    root_dir = r'C:\Users\raymo\OneDrive\Desktop\Playground\Financial-Modelling-Playground\Quant_Trading\Histo'
    savDir=r'C:\Users\raymo\OneDrive\Desktop\Ray Stuff\_Cache'#'D:\DB_feed\AggData'
    override=False

    # Tickers to Load
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

    res = Client.getPrices(tickers=_tickers, _parallel = True, override=override, logDir=savDir)

    # ## loading [avoid multithreading due to data parsing limit
    # for ticker in _tickers:
    #     if not override and os.path.exists(os.path.join(savDir, ticker)):
    #         continue
    #     Client._saveData(pd.DataFrame(Client.getData(ticker)), 
    #                          ticker, "{0}_{1}_{2}".format(ticker,
    #                                     start_dt.replace("-",""),
    #                                     end_dt.replace("-","")),
    #                         savDir)
    #     time.sleep(12) ## limit 5 api calls per minute

    # PolygonAPI._removeEmptyFiles(savDir)


## test
def test():
    Client = PolygonAPI()
    ## Load names to load 
    ## End Date
    end_dt = "2024-11-15"
    ## Start date
    start_dt = "2022-07-10"
    ### root folder
    root_dir = r'C:\Users\raymo\OneDrive\Desktop\Playground\Financial-Modelling-Playground\Quant_Trading\Histo'
    savDir=r'C:\Users\raymo\OneDrive\Desktop\Ray Stuff\_Cache'#'D:\DB_feed\AggData'
    override=False
    ticker = "AGG"
    temp = Client.getStatic(ticker,
                         start_dt,
                         end_dt)
# Using the special variable 
# __name__
if __name__=="__main__":
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s: %(message)s',
                        level=logging.INFO,
                        datefmt="%H:%M:%S")
    main()