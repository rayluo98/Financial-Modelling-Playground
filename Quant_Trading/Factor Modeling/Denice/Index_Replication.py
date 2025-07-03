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
# DIR = r'~\Cache'
class IndexFactory:
    # def __init__(self,
    #              price:pd.DataFrame, 
    #              reference_idx:pd.DataFrame,
    #              statics:pd.DataFrame, 
    #              rule:Callable=None):
    #     self.px = price
    #     self.static = statics
    #     self.reference_idx = reference_idx
    #     ## define universe from price data frame
    #     self.tickers:list[str] = list(set(price['Tickers']))
    #     ## instantiate initial weights
    #     self.wt = pd.DataFrame()
    #     ## initiate list for rebal dates
    #     self.rebal_dates: list[str] = []
    #     ## TODO in future - define function rule for calculation
    #     self.rule = None
    
    def __init__(self, price_csv_path, iwf_csv_path):
        """Initialize IndexFactory with data sources"""
        self.ticker_list = utils.get_ticker_list()
        self.price_df = pd.read_csv(price_csv_path)
        self.iwf_df = pd.read_csv(iwf_csv_path)
        # convert date 
        self.price_df['Date'] = pd.to_datetime(self.price_df['Date'])
        self.iwf_df['date'] = pd.to_datetime(self.iwf_df['date'])
    
    # def getRebalDates(self):
    #     return self.rebal_dates

    # def setRebalDates(self, dates:list[datetime.date|str]):
    #     self.rebal_dates = utils.ConvertDt(dates)

    def calcWeights(self, reference_date):
        ### TODO ####
        ## find the weights - you can do this using rules based or some kind of fitting
        # My suggestion is you do rules based first, then try fitting
        """calculate SP500 capped weights for a reference date"""
        ref_dt = pd.to_datetime(reference_date)
        
        # Get data for reference date
        price_data = self.price_df[self.price_df['Date'] == ref_dt].copy()
        iwf_data = self.iwf_df[self.iwf_df['date'] == ref_dt].copy()
        merged_data = pd.merge(price_data, iwf_data, left_on='Ticker', right_on='ticker', how='inner')
        
        if merged_data.empty:
            return None
        
        # calculate FMC and apply capping (price*shares_outstanding*iwf)
        merged_data['fmc'] = merged_data['Close'] * merged_data['shares_outstanding'] * merged_data['iwf']
        merged_data = self._apply_capping_methodology(merged_data)
        
        result = merged_data[['ticker', 'uncapped_weight_pct', 'capped_weight_pct', 'awf']].copy()
        return result.sort_values('capped_weight_pct', ascending=False)
    
    def calcDailyWeights(self, date, awf_factors):
        """calculate daily weights (between rebalancings) using existing AWF factors"""

        date_dt = pd.to_datetime(date)
        price_data = self.price_df[self.price_df['Date'] == date_dt].copy()
        iwf_data = self.iwf_df[self.iwf_df['date'] == date_dt].copy()
        merged_data = pd.merge(price_data, iwf_data, left_on='Ticker', right_on='ticker', how='inner')
        merged_data = pd.merge(merged_data, awf_factors, on='ticker', how='inner')
        
        if merged_data.empty:
            return None, False
        
        # calculate adjusted weights
        merged_data['adjusted_fmc'] = merged_data['Close'] * merged_data['shares_outstanding'] * merged_data['iwf'] * merged_data['awf']
        total_adjusted_fmc = merged_data['adjusted_fmc'].sum()
        merged_data['daily_weight_pct'] = (merged_data['adjusted_fmc'] / total_adjusted_fmc) * 100
        
        # check for cap breaches
        max_weight = merged_data['daily_weight_pct'].max()
        large_weight_sum = merged_data[merged_data['daily_weight_pct'] > 4.8]['daily_weight_pct'].sum()
        caps_breached = (max_weight > 24.0) or (large_weight_sum > 50.0)
        
        if caps_breached:
            # trigger full recalculation (step 2-7 again)
            merged_data['fmc'] = merged_data['Close'] * merged_data['shares_outstanding'] * merged_data['iwf']
            merged_data = self._apply_capping_methodology(merged_data)
            return merged_data[['ticker', 'capped_weight_pct', 'awf']].copy(), True
        else:
            # use drifted weights
            result = merged_data[['ticker', 'daily_weight_pct', 'awf']].copy()
            result.rename(columns={'daily_weight_pct': 'capped_weight_pct'}, inplace=True)
            return result, False
    
    def generateFullYearWeights(self, rebalancing_schedule, start_date, end_date):
        """generate daily weights for the full year"""
        
        # get all trading dates 
        all_dates = pd.date_range(start=start_date, end=end_date, freq='D')
        trading_dates = [date.strftime('%Y-%m-%d') for date in all_dates 
                        if not self.price_df[self.price_df['Date'] == date].empty]
        
        # pre-calculate all reference weights, run calcWeights() quarterly
        reference_weights = {}
        for schedule in rebalancing_schedule:
            ref_date = schedule['reference']
            eff_date = schedule['effective']
            weights = self.calcWeights(ref_date)
            if weights is not None:
                reference_weights[eff_date] = weights
        
        # Find initial weights for start_date
        start_dt = pd.to_datetime(start_date)
        current_awf_factors = None
        
        for schedule in rebalancing_schedule:
            eff_dt = pd.to_datetime(schedule['effective'])
            if eff_dt <= start_dt:
                current_awf_factors = reference_weights[schedule['effective']][['ticker', 'awf']].copy()
        
        if current_awf_factors is None:
            raise ValueError(f"No weights found for start date {start_date}")
        
        # Generate daily weights
        all_daily_weights = []
        
        for date_str in trading_dates:
            # Check if this is an effective date
            is_effective_date = False
            for schedule in rebalancing_schedule:
                if date_str == schedule['effective']:
                    # Apply new weights
                    new_weights = reference_weights[schedule['effective']]
                    current_awf_factors = new_weights[['ticker', 'awf']].copy()
                    
                    result_df = new_weights[['ticker', 'capped_weight_pct']].copy()
                    result_df['date'] = date_str
                    result_df['is_rebalancing'] = True
                    all_daily_weights.append(result_df)
                    is_effective_date = True
                    break
            
            if not is_effective_date:
                # Calculate daily weights
                daily_weights, caps_breached = self.calcDailyWeights(date_str, current_awf_factors)
                
                if daily_weights is not None:
                    if caps_breached:
                        current_awf_factors = daily_weights[['ticker', 'awf']].copy()
                    
                    result_df = daily_weights[['ticker', 'capped_weight_pct']].copy()
                    result_df['date'] = date_str
                    result_df['is_rebalancing'] = caps_breached
                    all_daily_weights.append(result_df)
        
        return pd.concat(all_daily_weights, ignore_index=True) if all_daily_weights else pd.DataFrame()
    
    def _apply_capping_methodology(self, merged_data):
        """
        apply SP500 capping
        single company cap 24% -> 23%
        """
        # calculate uncapped weights
        total_fmc = merged_data['fmc'].sum()
        merged_data['uncapped_weight_pct'] = (merged_data['fmc'] / total_fmc) * 100
        # 24% -> 23%
        max_weight = merged_data['uncapped_weight_pct'].max()
        if max_weight > 24.0:
            merged_data['temp_weight'] = np.minimum(merged_data['uncapped_weight_pct'], 23.0)
            merged_data = self._redistribute_weight(merged_data, 'temp_weight', 23.0)
        else:
            merged_data['temp_weight'] = merged_data['uncapped_weight_pct']
        
        # concentration limit (>4.8% companies ≤ 50% total)
        large_companies = merged_data['temp_weight'] > 4.8
        large_weight_sum = merged_data.loc[large_companies, 'temp_weight'].sum()
        if large_weight_sum > 50.0:
            merged_data = self._apply_concentration_cap(merged_data)
        
        # final redistribution
        merged_data['capped_weight_pct'] = merged_data['temp_weight']
        merged_data = self._final_redistribution(merged_data)
        
        # calculate AWF = capped weights/uncapped weights
        merged_data['capped_weight'] = merged_data['capped_weight_pct'] / 100
        merged_data['uncapped_weight'] = merged_data['uncapped_weight_pct'] / 100
        merged_data['awf'] = merged_data['capped_weight'] / merged_data['uncapped_weight']
        
        return merged_data
    
    def _redistribute_weight(self, df, weight_col, cap):
        """Redistribute excess weight proportionally"""
        df = df.copy()
        for _ in range(100):
            over_cap = df[weight_col] > cap
            if not over_cap.any():
                break
            excess = (df.loc[over_cap, weight_col] - cap).sum()
            df.loc[over_cap, weight_col] = cap
            under_cap = df[weight_col] < cap
            if not under_cap.any():
                break
            under_cap_sum = df.loc[under_cap, weight_col].sum()
            if under_cap_sum > 0:
                factor = 1 + (excess / under_cap_sum)
                df.loc[under_cap, weight_col] *= factor
        return df
    
    def _apply_concentration_cap(self, df):
        """Apply concentration limit capping"""
        df = df.copy()
        large_companies = df['temp_weight'] > 4.8
        if large_companies.any():
            large_weight_sum = df.loc[large_companies, 'temp_weight'].sum()
            for idx in df[large_companies].index:
                wi = df.loc[idx, 'temp_weight']
                # max(45% × Wi / ΣWi, 4.5%)
                capped_weight = max((45.0 * wi) / large_weight_sum, 4.5)
                df.loc[idx, 'temp_weight'] = capped_weight
        return df
    
    def _final_redistribution(self, df):
        """Final redistribution with 4.5% upper bound"""
        df = df.copy()
        current_total = df['capped_weight_pct'].sum()
        excess = current_total - 100.0 # if negative, need to add weight
        # redistribute proportionally with 4.5% upper bound
        if abs(excess) > 0.01:
            small_companies = df['capped_weight_pct'] < 4.8 # companies that weren't capped
            if small_companies.any():
                small_weight_sum = df.loc[small_companies, 'capped_weight_pct'].sum()
                if small_weight_sum > 0:
                    # proportionally increase small comapnies to absorb the weight
                    factor = (small_weight_sum - excess) / small_weight_sum
                    df.loc[small_companies, 'capped_weight_pct'] *= factor
                    df.loc[small_companies, 'capped_weight_pct'] = np.minimum(
                        df.loc[small_companies, 'capped_weight_pct'], 4.5)
        
        # normalize to 100%
        total_weight = df['capped_weight_pct'].sum()
        df['capped_weight_pct'] = (df['capped_weight_pct'] / total_weight) * 100
        return df

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
    # ## load existing data - all SP500 names over the last 10 years

    # # we want to define our univesrse
    # sp_current, sp_past = utils.getSPXConstituents()

    # history = pd.read_csv(os.path.join(DIR, "data.csv"))
    # ## pull static data
    # static = pd.read_csv(os.path.join(DIR, "static.csv"))

    # ### scrape index data
    # # https://www.spglobal.com/spdji/en/indices/equity/sp-500-financials-sector/#overview
    # ## you can scrape price data here: https://www.marketwatch.com/investing/index/ixm/download-data?startDate=6/27/2023&endDate=6/27/2024&countryCode=xx
    # indx_hist = pd.read_csv(os.path.join(DIR, "index.csv"))


    # ## create index replication object
    # index_factory = IndexFactory(history, indx_hist, static)

    # ## store rebal dates here <--
    # REBAL_DATES = []
    # index_factory.setRebalDates(REBAL_DATES)

    # ## TODO ###
    # DUMMY_INPUT = None
    # index_factory.predictWeights(DUMMY_INPUT)

    # etf_child = index_factory.CreateETF()

    # ### then do some price impact analysis to get a signal
    # index_factory.predictRebalImpact()
    PRICE_CSV_PATH = 'all_close_prices.csv'
    IWF_CSV_PATH = 'iwf_data.csv'
    START_DATE = '2024-01-01'
    END_DATE = '2024-12-31'
    OUTPUT_FILE = 'sp500_daily_weights_2024.csv'
    REBALANCING_SCHEDULE = [
        {'reference': '2023-12-06', 'effective': '2023-12-15'},
        {'reference': '2024-03-06', 'effective': '2024-03-15'},
        {'reference': '2024-06-12', 'effective': '2024-06-21'},
        {'reference': '2024-09-11', 'effective': '2024-09-20'},
        {'reference': '2024-12-11', 'effective': '2024-12-20'}
    ]
    
    factory = IndexFactory(PRICE_CSV_PATH, IWF_CSV_PATH)
    
    # generate whole year weights
    full_weights_df = factory.generateFullYearWeights(REBALANCING_SCHEDULE, START_DATE, END_DATE)
    # generate only rebalanced weights
    rebalancing_weights_df = full_weights_df[full_weights_df['is_rebalancing'] == True].copy()

    # save results
    full_weights_df.to_csv(OUTPUT_FILE, index=False)
    # save rebalancing weights only
    rebalancing_weights_df = full_weights_df[full_weights_df['is_rebalancing'] == True].copy()
    REBALANCING_OUTPUT_FILE = 'sp500_rebalancing_weights_2024.csv'
    rebalancing_weights_df.to_csv(REBALANCING_OUTPUT_FILE, index=False)

    # check: top 10 companies by average weight
    avg_weights = full_weights_df.groupby('ticker')['capped_weight_pct'].mean().sort_values(ascending=False)
    print(f"\nTop 10 companies by avg weight:")
    for i, (ticker, avg_weight) in enumerate(avg_weights.head(10).items()):
        print(f"{i+1:2d}. {ticker}: {avg_weight:.2f}%")
    pass


if __name__ == "__main__":
    main()