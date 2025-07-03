from datetime import datetime as dt
import pandas as pd
import requests
from bs4 import BeautifulSoup
import os
import yfinance as yf


# ## ASSUMES DATE FORMAT IN DD-MM-YYYY
# def ConvertDt(dates_as_str:list[str]):
#     return [dt.strptime(date_string, "%d-%m-%Y") for date_string in dates_as_str]

## Scraped from Wikipedia
def getSPXConstituents(start_yr=""):

    url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
    soup = BeautifulSoup(requests.get(url).content, 'html.parser')

    # Get the current list
    table = soup.find('table', {'id': 'constituents'})
    df = pd.read_html(str(table))[0]

    # Get historical changes
    tables = soup.find_all('table', {'class': 'wikitable'})
    for t in tables:
        if 'Date' in str(t):
            changes = pd.read_html(str(t))[0]
    # changes = changes.filter(lambda df: int(df['Date added'][:4]) < int(start_yr))

    return df, changes

def get_ticker_list():
    """Get and cache financial sector tickers from S&P 500"""
    if os.path.exists('ticker_list.csv'):
        df = pd.read_csv('ticker_list.csv')
        return df['ticker'].tolist()
    
    curr, old = getSPXConstituents()
    df = curr[curr["GICS Sector"] == "Financials"]

    ticker_df = pd.DataFrame({'ticker': df["Symbol"].tolist()})
    ticker_df.to_csv('ticker_list.csv', index=False)
    
    return ticker_df['ticker'].tolist()

def getIWF(ticker_list, start_date, end_date):
    """
    Get shares outstanding, float shares, and calculate IWF = float shares/shares outstanding
    """
    sample_ticker = ticker_list[0]
    sample_stock = yf.Ticker(sample_ticker)
    sample_hist = sample_stock.history(start=start_date, end=end_date)
    trading_dates = [date.strftime('%Y-%m-%d') for date in sample_hist.index]
    all_results = []
    
    for ticker in ticker_list:
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            shares_outstanding = info.get('sharesOutstanding', None)
            float_shares = info.get('floatShares', None)
            
            # calculate IWF
            if float_shares and shares_outstanding and shares_outstanding > 0:
                iwf = float_shares / shares_outstanding
            else:
                # if no float data available, assume full float (IWF = 1.0)
                iwf = 1.0
                if shares_outstanding:
                    float_shares = shares_outstanding
        
            for date in trading_dates:
                all_results.append({
                    'ticker': ticker,
                    'date': date,
                    'shares_outstanding': shares_outstanding,
                    'float_shares': float_shares,
                    'iwf': iwf
                })
            
        except Exception as e:
            print(f"Error processing {ticker}: {e}")
            continue

    df_iwf = pd.DataFrame(all_results)
    # df_iwf.to_csv('iwf_data.csv', index=False)
    return df_iwf

def getAllClose(l1_cache_path):
    """
    Extract all close prices from cached CSV files
    """
    result = []

    for root, _, files in os.walk(l1_cache_path):
        if "_Errors" in root:
            continue  

        for fname in files:
            if not fname.endswith('.csv'):
                continue
            ticker = fname.split("_")[0]
            fpath = os.path.join(root, fname)
            df = pd.read_csv(fpath)

            if "timestamp" not in df.columns or "close" not in df.columns:
                continue  
            df["datetime"] = pd.to_datetime(df["timestamp"], unit="ms", errors="coerce")
            df = df[df["datetime"].notna()] 
            df["date"] = df["datetime"].dt.date

            # Group by date and get the last close price for each date
            daily_closes = df.groupby("date")["close"].last().reset_index()
            
            for _, row in daily_closes.iterrows():
                result.append({
                    "Date": row["date"],
                    "Ticker": ticker,
                    "Close": row["close"]
                })
    # df_result.to_csv("all_close_prices.csv")
    df_result = pd.DataFrame(result)
    return df_result

### DRIVER FUNCTION TO TEST
def test():
    curr, old = getSPXConstituents() 
    print(curr)

    # extract close prices from l1_cache
    price_df = getAllClose("l1_cache")
    print(f"Extracted prices for {price_df['Ticker'].nunique()} unique tickers")
    print(f"Date range: {price_df['Date'].min()} to {price_df['Date'].max()}")
    print(price_df.head())

    # ticker list
    ticker_list = get_ticker_list()
    print(f"Financial tickers: {len(ticker_list)}")
    print(ticker_list)

    df_iwf = pd.read_csv("iwf_data.csv")
    print(df_iwf)


    # result = list(set(list(curr['Symbol']) + list(old['Added']['Ticker']) + list(old['Removed']['Ticker'])))
    # result = [str(x) for x in result]
    # with open(r'/home/rayluo98/temp.txt', "w") as file:
    #     file.write('\n'.join(result))

if __name__ == '__main__':
    test()