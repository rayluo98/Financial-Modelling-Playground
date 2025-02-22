import pandas as pd
import numpy as np
from dataclasses import dataclass
from matplotlib import pyplot as plt
import BacktestEngine.order_book as order_book
import logging
import tqdm
from concurrent.futures import ThreadPoolExecutor

### Intuition Behind Backtest Class ###
# we want to create a module backtest class on an generic strategy
# return a central metric for optimization (option of Sharpe Ratio or DWL)
# we assume that we recieve a signal for the backtest

class backtestEngine(object):
    ## Date is tradedate
    ## signal is feature used to determine trade (could be vol, corr, px etc)
    ## signal is best to be a mean-reverting signal
    ## buy level is the bid threshold, sell level is the ask threshold (buy cannot cross sell)
    bt_cols = ['signal', 'buy_level', 'sell_level']
    # cols to merge on
    id_cols = ['Date', 'Ticker']
    bt_hist:pd.DataFrame
    hasSignal: bool = False

    def __init__(self, btHist: pd.DataFrame):
        self.bt_hist = btHist

    def reloadEngine(self, btHist: pd.DataFrame):
        self.bt_hist = btHist

    def simulateTrade():
        return None

    def pairsTradeSignal(self, ticker1: str, ticker2: str, tradeQty: float|pd.DataFrame,
                         signal:pd.DataFrame)->pd.DataFrame:
        ## initiate orderbook 
        BBO = order_book.Book()
        split_idx = np.array_split(df.columns, 16)
        tasks = [df[i] for i in split_idx]
        # run do_describe fucntions in the process pool
        with ThreadPoolExecutor() as executor:
            result = executor.map(do_describe, tasks)
        return None

    def singleTradeSignal(bdf: pd.DataFrame, ticker: str, signal:pd.DataFrame, 
                          tradeQty: float| pd.DataFrame=1)->pd.DataFrame:
        # now combine all the triggers to see when we are holding or shorting.
        # with somewhat-continuity of the signal, we can just assume that after a buy, the end-buy will occur BEFORE starting a new sale, and the same for sell->endsell->newbuy.
        # note, for signing purposes, the end-buy is actually selling.
        if isinstance(tradeQty, float):
            bdf['holding_action'] = tradeQty*(1*bdf['trigger_buy'] - 1*bdf['trigger_end_buy'] - 1*bdf['trigger_sell'] + 1*bdf['trigger_end_sell'])
        else: ## if its dataframe type, check logic here
            bdf['holding_action'] = tradeQty*(1*bdf['trigger_buy'] - 1*bdf['trigger_end_buy'] - 1*bdf['trigger_sell'] + 1*bdf['trigger_end_sell'])
        # by design of the boolean triggers and the continuity assumption, the cumulative sum of the actions should range within [1, -1]. check it in the plot.
        bdf['position'] = bdf['holding_action'].cumsum()
        return None

    def applySignal(self, tickers: list[str], signal: pd.DataFrame,
                          tradeQty: float | pd.DataFrame  = 1, isMeanRevert: bool=False):
        ## removes existing signal
        if ("signal" in self.bt_hist):
            self.bt_hist.drop(self.bt_cols, errors='ignore', inplace=True, axis=1)
        self.bt_hist = self.bt_hist.merge(signal, on ="Date", how='left')
        # compute boolean masks for when to trigger open position buy/sell
        bdf = self.bt_hist
        bdf['start_buy'] = bdf['signal'] >= bdf['buy_level']
        bdf['start_sell'] = bdf['signal'] <= bdf['sell_level']
        # combine into a single boolean mask.
        # we cannot take the same position twice.
        bdf['cstarts'] = (1*bdf['start_buy']) - (1*bdf['start_sell'])
        bdf.loc[bdf['cstarts'] == 0, 'cstarts'] = pd.NA
        # need to fillNA in order to maintain the most recent action.
        bdf['cstarts'] = bdf['cstarts'].fillna(method='ffill').fillna(0)
        # use leq and geq because we start most likely from a zero-state.
        # other than the initialization, the diff should be +2 or -2.
        # to take care of non-zero initial state (see AAPL on 6/2/2023) we catch the NA diff and starting values of +1 and -1.
        bdf['trigger_buy'] = (bdf['cstarts'].diff() >= 1) | (pd.isna(bdf['cstarts'].diff()) & bdf['cstarts']==1)
        bdf['trigger_sell'] = (bdf['cstarts'].diff() <= -1) | (pd.isna(bdf['cstarts'].diff()) & bdf['cstarts']==-1)

        #if we're considering a mean reverting signal, we consider mean as threshold 
        # this is a forward looking metric to be replaced 
        mean: float
        if isMeanRevert:
            mean = bdf['signal'].mean()
        # figure out when to buy/sell back from an opened position
        bdf['end_buy'] = (bdf['signal'] < (mean if isMeanRevert else bdf['sell_level'])) & (bdf['cstarts'] == 1)
        bdf['end_sell'] = (bdf['signal'] > (mean if isMeanRevert else bdf['buy_level'])) & (bdf['cstarts'] == -1)
        # need to combine the above to determine triggers. can't end the same position twice.
        bdf['cends'] = (1*bdf['end_buy']) - (1*bdf['end_sell'])
        bdf.loc[bdf['cends'] == 0, 'cends'] = pd.NA
        # need to fillNA in order to maintain the most recent action.
        bdf['cends'] = bdf['cends'].fillna(method='ffill').fillna(0)
        # use leq and geq because we will start from a zero-state (cstarts==0).
        # other than the initialization, the diff should be +2 or -2.
        bdf['trigger_end_buy'] = bdf['cends'].diff() >= 1
        bdf['trigger_end_sell'] = bdf['cends'].diff() <= -1
        if (len(tickers)==1):
            bdf = backtestEngine.singleTradeSignal(bdf, tickers, signal, tradeQty)
        elif (len(tickers)==2):
            bdf = backtestEngine.pairsTradeSignal(tickers[0], tickers[1], bdf)
        else:
            logging.Logger.error("Don't have a handler for strategy more than 2 assets")

        return bdf

    # calculates the strength of the signal
    def calcSigStr(self):
        return None
        
    def printResult(self, isMeanRevert: bool=False):
        bdf = self.bt_hist
        plt.figure(figsize=(12,8), dpi=200)
        plt.plot(bdf.index, bdf['signal'])
        if isMeanRevert:
            plt.plot(bdf['buy_level'], label='buy signal')
            plt.plot(bdf['sell_level'], label='sell signal')
        else:
            plt.axhline(bdf['signal'].mean(), label='mean signal')
        plt.ylabel('signal')
        plt.tick_params(axis='y', labelcolor='C0')

        plt.gca().twinx()
        plt.plot(bdf.index, bdf['position'], color='C1')
        plt.ylabel('position')
        plt.tick_params(axis='y', labelcolor='C1')
        plt.tight_layout()
        plt.show()

    def getProfit(self):
        bdf = self.bt_hist
        #compute profit over time, plot the buys and sells on top of the stock price.
        # costs the half spread each time we trade. thus enter+exit position costs 1 entire spread (ask-bid).bdf['tcost'] = (bdf['ask0'] - bdf['bid0']) / 2 * (bdf['trigger_buy'] | bdf['trigger_end_buy'] | bdf['trigger_sell'] | bdf['trigger_end_sell'])
        bdf['mid'] = (bdf['ask0'] + bdf['bid0']) / 2
        bdf['profit'] = (bdf['position'].shift(1) * (bdf['mid'] - bdf['mid'].shift(1))).fillna(0)

        bdf['cum_profit_no_tcost'] = bdf['profit'].cumsum()
        bdf['cum_profit'] = (bdf['profit'] - bdf['tcost']).cumsum()
        return bdf



