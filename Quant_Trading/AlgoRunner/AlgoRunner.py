### imports
import requests
from timer import timer
import logging
import schwabdev

def main():
    SERVER_ENDPOINT = r"https://api.schwabapi.com/"
    with timer() as t:
        MARKET_DATA_ENDPOINT = r"marketdata/v1/"
        ACCOUNT_ENDPOINT = r"trader/v1"
        TIME_STOPPER = 9.5 * 3600 ## imprecise
        while True:
        ### establish schwab connection
        
        ### initialize base model based on cached data
        
        ### identifies tickers of interest to pull market data
            FOCUS_TICKERS = []
        ### recallibrate base model every {2} hours

        ### send requests to pull market data every minute (to prevent api overload)
        
        ### pull account data

        ### calculate market impact

        ### execute trade 

        ### send email notification regarding decision
            if t.elapse > TIME_STOPPER:
                return

if __name__=="__main__":
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s: %(message)s',
                    level=logging.INFO,
                    datefmt="%H:%M:%S")
    main()