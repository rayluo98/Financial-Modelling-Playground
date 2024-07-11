import pandas as pd
import numpy as np


## basically create static functions to be passed to realize trade idea. Backtest engine will pick up strategy and backpopulate orderbook
# Below methods should all enrich at least with df['Trade_']
class Ideas:
    @staticmethod
    def dummyAlpha(df: pd.DataFrame, ticker_1:str="TSLA", ticker_2: str="GS")->pd.DataFrame:
        return df
    
    @staticmethod
    def pairSigAlpha(df: pd.DataFrame, ticker_1: str="TSLA", ticker_2: str = "GS")->pd.DataFrame:
        df['GS_MA_5d'] = df['GS'].rolling(35).mean()
        df['TSLA_MA_5d'] = df['TSLA'].rolling(35).mean()
        df['GS_MA_30d'] = df['GS'].rolling(210).mean()
        df['TSLA_MA_30d'] = df['TSLA'].rolling(210).mean()

        df['GS_sd_5d'] = df['GS'].rolling(210).std()
        df['TSLA_sd_5d'] = df['TSLA'].rolling(210).std()
        df['GS_pct_sd'] = df['GS_sd_5d']/df['GS_MA_5d']
        df['TSLA_pct_sd'] = df['TSLA_sd_5d']/df['TSLA_MA_5d']
        for index, row in df.iterrows():
            if row['trade_sig']:
                if row['vol_GS']:
                    if row['GS_MA_30d'] > row['GS_MA_5d']:
                        sim_book.short('GS', row, DOLLAR_AMOUNT)
                        sim_book.long('TSLA', row, DOLLAR_AMOUNT)
                    else:
                        sim_book.short('GS', row, DOLLAR_AMOUNT)
                        sim_book.long('TSLA', row, DOLLAR_AMOUNT)
                else:
                    if row['TSLA_MA_30d'] > row['TSLA_MA_5d']:
                        sim_book.short('GS', row, DOLLAR_AMOUNT)
                        sim_book.long('TSLA', row, DOLLAR_AMOUNT)
                    else:
                        sim_book.short('GS', row, DOLLAR_AMOUNT)
                        sim_book.long('TSLA', row, DOLLAR_AMOUNT)
            else:
                if sim_book.orders:
                    sim_book.sell_all(row)