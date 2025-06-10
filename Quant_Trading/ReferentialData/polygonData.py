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
    
    def getFundamentals(self, 
                ticker:str, 
                from_="2023-01-01", 
                to_="2023-06-13",
                limit:float=100,
                field_:str|None=None)->str:
        fundamentals = {}
        hasErr: bool = False
        _error = []
        start_dt = pd.Timestamp(from_)
        end_dt = pd.Timestamp(to_)
        res = {}
        stock_financials =self._client.vx.list_stock_financials(ticker, 
                                                filing_date_gte=start_dt,
                                                filing_date_lte=end_dt,
                                                include_sources=True)
        for financial in stock_financials:
            res[financial['count']] = financial
            if financial['status'] != 'OK':
                _error.append(ticker + "_" + financial['count'])
                logging.info(ticker + "_" + financial['count'] + ": financials not loaded...")
            
        return json.dumps(res)

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
                from_="2015-05-18", 
                to_="2025-05-18", 
                include_splits=True,
                limit=50000,
                logDir:str|None = None, # r'C:\Users\raymo\OneDrive\Desktop\Ray Stuff\_ErrorLogs',
                _parallel = False,
                override=False):
        format = "%(asctime)s: %(message)s"
        #need to make sure items are unique as race conditions are not handled  for multithreading
        # keys: ticker name
        # values: (info, history)
        LE_HISTO = dict() 
        _error = dict()
        result = {}
        startDt_ = dt.datetime.strptime(from_,"%Y-%m-%d")
        endDt_ = dt.datetime.strptime(to_, "%Y-%m-%d")
         ## inline loadHistory - TODO: make this function abstract factory class
        def loadHistory(ticker: str, startDate: str, endDate: str, histo: dict, error:dict,
                        lock:RLock=None, override:bool=False, include_splits=True):
            with lock:
                foundCache = False
                foundPartial = False
                if not override and logDir != None:
                    files = glob.glob(os.path.join(logDir, ticker, "*.csv"))
                    files.sort(reverse=True)
                    for _file in files:
                        file_traits = _file.split("\\")[-1].split("_")
                        if (len(file_traits) == 4):
                            ### means we found at least a partial match
                            startDt = file_traits[1]
                            endDt = file_traits[2]
                            freqDt = file_traits[3].replace(".csv","")
                            if freqDt == timespan:
                                foundPartial = True
                        else:
                            continue
                        if (dt.datetime.strptime(startDt,"%Y%m%d") <= startDt_ and
                            dt.datetime.strptime(endDt,"%Y%m%d") >= endDt_ and 
                            foundPartial):
                            foundCache = True
                            hist = pd.read_csv(_file)
                            break
                        elif ((dt.datetime.strptime(startDt,"%Y%m%d") > startDt_) ^
                            (dt.datetime.strptime(endDt,"%Y%m%d") < endDt_) and foundPartial):
                            if (dt.datetime.strptime(startDt,"%Y%m%d") < startDt_):
                                startDate = startDt
                            if (dt.datetime.strptime(endDt,"%Y%m%d") > endDt_):
                                endDate = endDt
                            old_hist = pd.read_csv(_file)
                            break
                # get historical market data
                if not foundCache:
                    hist = pd.DataFrame(self.getData(ticker, multiplier, timespan, 
                                                     from_, to_, limit, include_splits, attemptNo=0))
                    ### create unique ids for data entries
                    hist['ID'] = ticker + "_" + hist['timestamp'].astype(str) + "_" + timespan
                    if foundPartial: ## merge existing data set with new data set
                        new_dates = hist['timestamp']
                        old_dates = old_hist['timestamp']
                        dates_to_insert = list(set(new_dates).difference(set(old_dates)))
                        hist = pd.concat([old_hist, hist[hist['timestamp'].isin(dates_to_insert)]], ignore_index=True)
                        hist.sort_values(by='timestamp', inplace=True)
                        foundCache = False ## to replace old data with new
                if logDir != None and not foundCache and len(hist) > 1: 
                    save_format = "{0}_{1}_{2}_{3}".format(ticker,
                                    startDate.replace("-",""),
                                    endDate.replace("-",""),
                                    timespan)
                    # save_format = "{0}_{1}".format(ticker, "histo")
                    self._saveData(hist, ticker, save_format, logDir, override)
                if len(hist) > 1:
                    histo[ticker] = hist ## to replace with struct
                else:
                    _error[ticker] = "Failed to load data for {ticker}"
                return hist

        if _parallel:
            lock = RLock()
            func = lambda x: loadHistory(x, from_, to_,
                                         LE_HISTO, _error, lock, override, include_splits)
            with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
                #result = executor.map(functools.partial(loadHistory , tickers, LE_HISTO, lock))
                executor.map(func, tickers)
        else:
            for ticker in tickers:
                hist = loadHistory(ticker, LE_HISTO, _error, include_splits=include_splits)
                if len(hist) > 0:
                    LE_HISTO[ticker] = hist
                time.sleep(12) ## limit 5 api calls per minute
        return LE_HISTO,  _error


    def getData(self, 
                ticker: str, multiplier:int = 1, 
                timespan:str="minute", 
                from_="2023-01-01", 
                to_="2023-06-13", 
                limit=50000,
                include_splits=True,
                attemptNo = 0):
    # List Aggregates (Bars)
        aggs = []
        try:
            for a in self._client.list_aggs(ticker=ticker, multiplier=1, 
                                            timespan=timespan, from_=from_, to=to_, 
                                            limit=limit, adjusted=include_splits):
                aggs.append(a)
            if len(aggs) == 0:
                if attemptNo > 2:
                    # logging.info("No data loaded for Ticker {0}".format(ticker))
                    logging.info("No data loaded for Ticker {0}".format(ticker))
                else:
                    time.sleep(5)
                    logging.info("Retrying for ticker {0}... Attempt {1}".format(ticker, attemptNo + 2))
                    return self.getData(ticker, timespan=timespan, from_=from_, to_=to_, limit=limit, include_splits=include_splits, attemptNo=attemptNo + 1)
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
    def _removeFilesByName(path: str=r'D:\DB_feed\AggData',
                           name: str="", threshold: str = 1000):
        for root, dirs, files in os.walk(path, topdown=True, onerror=None, followlinks=False):
            if (len(files) == 0):
                continue
                path = os.path.join(root, dirs, files)
                os.remove(path)
        return None
    
    @staticmethod
    def _saveErrors(path,
                    _errors: dict,
                    valueDate):
        error_path = os.path.join(path, "_Errors")
        if not os.path.exists(error_path):
            os.makedirs(error_path)
        pd.DataFrame(_errors.items(), columns=['Ticker','Logs']).to_csv(os.path.join(error_path, "Errors_{valueDate}.csv"))
    
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
        

    @staticmethod
    def _saveParquet(df: pd.DataFrame, 
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
    start_dt = '1990-01-01' #pd.to_datetime(df.loc[0,'timestamp']
    splits.loc[len(splits)] = [pd.to_datetime(start_dt),
                            "DUMMY",
                            1,
                            1,
                            "DUMMY"]
    splits = splits.sort_values('execution_date')
    # splits = splits[splits['execution_date'] >= pd.to_datetime(df.loc[0,'timestamp'], unit = 'ms')]
    splits['ratio'] = splits['split_from']/splits['split_to']
    splits['ratio'] = splits['ratio'].cumprod()
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
    end_dt = "2025-05-15"
    ## Start date
    start_dt = "2015-05-15"
    ## Frequency
    freq = "hour"
    ### root folder
    root_dir = r'C:\Users\raymo\OneDrive\Desktop\Playground\Financial-Modelling-Playground\Quant_Trading\Histo'
    savDir=r'D:\_Cache'#'D:\DB_feed\AggData'
    override=True
    include_splits=True

    # Tickers to Load
    _tickers = list(pd.read_csv(os.path.join(root_dir, 'clean_names.csv'))['0'])

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
    prices, _errors = Client.getPrices(tickers=_tickers, from_ = start_dt, to_ = end_dt, 
                           timespan=freq, _parallel = True, 
                           include_splits=include_splits,override=override, logDir=savDir)
    res = prices
    # res = Client.getOutstandingTs(_tickers, start_dt, end_dt, savDir, True, False)
    # if include_splits:
    #     splits = Client.getSplitTs(_tickers, None, False, False)
    #     res = adjust_histo_to_splits(prices, splits)

    Client._saveErrors(savDir, _errors, start_dt)
    # loading [avoid multithreading due to data parsing limit
    for ticker in _tickers:
        if override and os.path.exists(os.path.join(savDir, ticker)):
            continue
        if ticker not in res:
            continue
        Client._saveData(pd.DataFrame(res[ticker]), 
                             ticker, "{0}_{1}_{2}_{3}".format(ticker,
                                        start_dt.replace("-",""),
                                        end_dt.replace("-",""),
                                        "SplitAdjusted" if include_splits else ""),
                            savDir,
                            override=override)
        # time.sleep(12) ## limit 5 api calls per minute
    # update security mapping
    # PolygonAPI._removeEmptyFiles(savDir)


## test
def test():
    Client = PolygonAPI()
    ## Load names to load 
    ## End Date
    end_dt = "2025-02-25"
    ## Start date
    start_dt = "2020-03-01"
    ### root folder
    root_dir = r'D:\Histo'
    savDir=r'D:\_Cache'#'D:\DB_feed\AggData'
    override=False
    ticker = "AGG"
    temp = Client.getStatic(ticker,
                         start_dt,
                         end_dt)
    
### file renaming script
def rename():
    root_dir = r'D:\Histo'
    savDir=r'D:\_Cache'#'D:\DB_feed\AggData'    
    _tickers = list(pd.read_csv(os.path.join(root_dir, 'clean_names.csv'))['0'])
    for ticker in _tickers:
        if not os.path.exists(os.path.join(savDir, ticker)):
            continue
        new_name = "{0}_histo.csv".format(ticker)
        end_dt = "2025-05-15"
        start_dt = "2015-05-15"
        old_name = "{0}_{1}_{2}_{3}".format(ticker,
                                            start_dt.replace("-",""),
                                            end_dt.replace("-",""),
                                            "SplitAdjusted.csv")
        file_temp = pd.read_csv(os.path.join(savDir, ticker, old_name))
        file_temp.to_csv(os.path.join(savDir,ticker,new_name), index=False)

# Using the special variable 
# __name__
if __name__=="__main__":
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s: %(message)s',
                        level=logging.INFO,
                        datefmt="%H:%M:%S")
    main()