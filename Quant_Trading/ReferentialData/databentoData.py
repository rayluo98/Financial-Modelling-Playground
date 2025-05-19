import databento as db
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

SCHEMA_DICT = {
               'L0':['status', 'statistics' ,'definition', 'ohlcv-1s','ohlcv-1m','ohlcv-1h','ohlcv-1d'],
               'L1':['tbbo','mbp-1', 'trades', 'bbo-1s', 'bbo-1m'],
               'L2':['mbp-10'],
               'L3':['mbo', 'imbalance']
               }

class databentoAPI(object):
    def __init__(self) -> None:
        f = open(r"C:\Users\raymo\OneDrive\Desktop\Playground\Financial-Modelling-Playground\Quant_Trading\ReferentialData\databentoApiKey.txt", "r")
        API_KEY = f.read()
        self._histoClient = db.Historical(API_KEY)
        self._liveClient = db.Live(API_KEY)
        self._statics = db.Reference(API_KEY)
        pass

    def __repr__(self) -> str:
        return self.get__repr__()
    
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
                    hist['ID'] = ticker + "_" + hist['timestamp'] + "_" + timespan
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