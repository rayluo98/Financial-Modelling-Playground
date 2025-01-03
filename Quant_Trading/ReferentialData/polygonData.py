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
from DataAnalysis import DataExtensions
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
                    to_="2023-06-13",
                    field_:str|None=None,
                    _parallel = False,
                    override=False,
                    logDir:str=r'C:\Users\raymo\OneDrive\Desktop\Ray Stuff\_ErrorLogs'):
        statics = {}
        errors = []
        lock = RLock()
        if _parallel:
            with lock:
                foundCache = False
                if not override and logDir != None:
                    files = glob.glob(os.path.join(logDir, ticker, "*_histo.csv"))
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
        else:
            for ticker in tickers:
                statics[ticker], errors[ticker] = self.getStatic(self, 
                    ticker, 
                    from_, 
                    to_,
                    field_)
        return statics, errors

    def getStatic(self, 
                ticker:str, 
                from_="2023-01-01", 
                to_="2023-06-13",
                field_:str|None=None):
        statics = {}
        hasErr: bool = False
        _error = []
        start_dt = pd.Timestamp(from_)
        end_dt = pd.Timestamp(to_)
        while(start_dt <= end_dt):
            date = start_dt.strftime("%Y-%m-%d")
            err = ""
            try:
                res =self._client.get_ticker_details(ticker, date)
                if field_ == None:
                    statics[date] = res
                else:
                    statics[date] = getattr(res, field_)
            except AttributeError:
                err = "{0} does not exist in statics!".format(field_)
            except:
                err = "Ticker {0} Statics unable to be loaded for {1}!".format(ticker, date)
            if err != "":
                logging.info(err)
                _error.append(err)
            start_dt += pd.offsets.BusinessDay(1)
            
        return pd.DataFrame(statics.items(), columns=['Timestamp', 'Static']), _error
            
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
                    files = glob.glob(os.path.join(logDir, ticker, "*_histo.csv"))
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

    def getSplitTs(self, tickers: list,
                logDir:str|None = None, # r'C:\Users\raymo\OneDrive\Desktop\Ray Stuff\_ErrorLogs',
                _parallel = False,
                override=False):
        LE_SPLITS = {}
        def getSplit(ticker, LE_SPLITS:dict, logDir:str|None=None, override:bool|None=None,lock:RLock=None):
            with lock:
                foundCache = False
                if not override and logDir != None:
                    files = glob.glob(os.path.join(logDir, ticker, "*_split.csv"))
                    if len(files) > 0:
                        foundCache = True
                        split = pd.read_csv(files[0])
                # get historical market data
                if not foundCache:
                    split = pd.DataFrame(json.loads(self._client.list_splits(ticker, raw=True).data)['results'])
                if logDir != None and not foundCache and len(split) > 1:
                    save_format = "{0}_{1}".format(ticker, "split")
                    self._saveData(split, ticker, save_format, logDir, override)
                if len(split) > 1:
                    LE_SPLITS[ticker] = split ## to replace with struct
                return split
        lock = RLock()
        if _parallel:
            func = lambda x: getSplit(x, LE_SPLITS, logDir, override, lock)
            with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
                #result = executor.map(functools.partial(loadHistory , tickers, LE_HISTO, lock))
                executor.map(func, tickers)
        else:
            for ticker in tickers:
                hist = getSplit(ticker, LE_SPLITS, logDir, lock=lock)
                if len(hist) > 0:
                    LE_SPLITS[ticker] = hist
        return LE_SPLITS

    def getOutstandingTs(self, tickers: list,
                from_="2023-01-01", 
                to_="2023-06-13", 
                logDir:str|None = None, # r'C:\Users\raymo\OneDrive\Desktop\Ray Stuff\_ErrorLogs',
                _parallel = False,
                override=False):
        LE_STATIC = {}
        def getOutstandings(ticker, from_, to_, LE_STATIC:dict, logDir:str|None=None, override:bool|None=None,lock:RLock=None):
            with lock:           
                dt = from_
                res = {}
                curr_outstanding = 0
                _KEY = "share_class_shares_outstanding"
                foundCache = False
                if not override and logDir != None:
                    files = glob.glob(os.path.join(logDir, ticker, "*_oa.csv"))
                    if len(files) > 0:
                        foundCache = True
                        static = pd.read_csv(files[0])
                # get historical market data
                if not foundCache:
                    static, _err = self.getStatic(ticker, from_, to_, _KEY)
                if logDir != None and not foundCache and len(static) > 1:
                    save_format = "{0}_{1}_{2}".format(ticker,
                                    from_.replace("-",""),
                                    to_.replace("-",""))
                    save_format = "{0}_{1}".format(ticker, "oa")
                    self._saveData(static, ticker, save_format, logDir, override)
                if len(static) > 1:
                    LE_STATIC[ticker] = static ## to replace with struct
                return static
        if _parallel:
            lock = RLock()
            func = lambda x: getOutstandings(x, from_, to_, LE_STATIC, logDir, override, lock)
            with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
                #result = executor.map(functools.partial(loadHistory , tickers, LE_HISTO, lock))
                executor.map(func, tickers)
        else:
            for ticker in tickers:
                hist = getOutstandings(ticker, LE_STATIC)
                if len(hist) > 0:
                    LE_STATIC[ticker] = hist
        return LE_STATIC

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
        df.to_csv(Path(loc_dir) / f"{file_name}.csv", index=False)
        logging.info("Finished Saving {0}".format(file_name))
        
def applySplitPricing(df: pd.DataFrame, splits: pd.DataFrame):
    splits = splits.loc[:,~splits.columns.str.contains("^Unnamed")]   
    splits['execution_date'] = pd.to_datetime(splits['execution_date'])
    splits.loc[len(splits)] = [pd.to_datetime(df.loc[0,'timestamp'], unit = 'ms'),
                            "DUMMY",
                            1,
                            1,
                            "DUMMY"]
    splits = splits.sort_values('execution_date')
    splits = splits[splits['execution_date'] >= pd.to_datetime(df.loc[0,'timestamp'], unit = 'ms')]
    splits['ratio'] = splits['split_from']/splits['split_to']
    splits['ratio'] = splits['ratio']
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df = pd.merge_asof(df,splits,   
                        right_on = 'execution_date',
                        left_on = 'timestamp')
    def applySplit(dr):
        return dr * df['ratio']
    df['open'] = applySplit(df['open'])
    df['close'] = applySplit(df['close'])
    df['high'] = applySplit(df['high'])
    df['low'] = applySplit(df['low'])
    df['vwap'] = applySplit(df['vwap'])
    return df

def adjust_histo_to_splits(histo: dict, splits: dict):
    adjusted_res = {}
    for ticker in histo:
        if ticker in splits:
            adjusted_res[ticker] = applySplitPricing(histo[ticker], splits[ticker])
    return adjusted_res
    
# Defining main function
def main():
    Client = PolygonAPI()
    ## Load names to load 
    ## End Date
    end_dt = "2024-12-10"
    ## Start date
    start_dt = "2019-12-10"
    ## Frequency
    freq = "hour"
    ### root folder
    root_dir = r'C:\Users\raymo\OneDrive\Desktop\Playground\Financial-Modelling-Playground\Quant_Trading\Histo'
    savDir=r'C:\Users\raymo\OneDrive\Desktop\Ray Stuff\_Cache'#'D:\DB_feed\AggData'
    override=False

    # Tickers to Load
    _tickers = list(pd.read_csv(os.path.join(root_dir, 'clean_names.csv'))['0'])
    # _tickers = ['VIXY']
    # f = open(r'C:\Users\raymo\OneDrive\Desktop\russell_1000_companies.json',)
    # _tickers = [x['ticker'] for x in json.load(f)]
    # f.close()
    # df = pd.read_csv(os.path.join(root_dir, 'tickers.csv'))
    # _tickers = list(df[df.columns[0]])

    # truncate ticker 
    startFrom = ""
    
    if startFrom != "":
        try:
            _startIndex = _tickers.index(startFrom)
        except:
            _startIndex = 0
        _tickers = _tickers[_startIndex:]

    cheat_check = [x[1] for x in os.walk(savDir)][0]
    # _tickers = list(set(cheat_check).intersection(set(_tickers)))
    files = glob.glob(os.path.join(savDir))
    prices = Client.getPrices(tickers=_tickers, from_ = start_dt, to_ = end_dt, 
                           timespan=freq, _parallel = True, override=override, logDir=savDir)
    # res = Client.getOutstandingTs(_tickers, start_dt, end_dt, savDir, True, False)
    splits = Client.getSplitTs(_tickers, savDir, False, False)

    res = adjust_histo_to_splits(prices, splits)
    ## loading [avoid multithreading due to data parsing limit
    for ticker in _tickers:
        if False and os.path.exists(os.path.join(savDir, ticker)):
            continue
        if ticker not in res:
            continue
        Client._saveData(pd.DataFrame(res[ticker]), 
                             ticker, "{0}_{1}_{2}_{3}".format(ticker,
                                        start_dt.replace("-",""),
                                        end_dt.replace("-",""),
                                        "SplitAdjusted"),
                            savDir)
    #     time.sleep(12) ## limit 5 api calls per minute

    # PolygonAPI._removeEmptyFiles(savDir)


## test
def test():
    Client = PolygonAPI()
    ## Load names to load 
    ## End Date
    end_dt = "2024-12-10"
    ## Start date
    start_dt = "2014-12-10"
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