### imports
import requests
from timer import timer
import logging
from .client import Client
### pip install python-dotenv
from dotenv import load_dotenv
import os

def main():
    SERVER_ENDPOINT = r"https://api.schwabapi.com/"
    with timer() as t:
        MARKET_DATA_ENDPOINT = r"marketdata/v1/"
        ACCOUNT_ENDPOINT = r"trader/v1"
        TIME_STOPPER = 9.5 * 3600 ## imprecise
        
        ### establish schwab connection
        client = Client(os.getenv('app_key'), os.getenv('app_secret'), os.getenv('callback_url'))

        # define a variable for the steamer:
        streamer = client.stream

        # example of using your own response handler, prints to main terminal.
        # the first parameter is used by the stream, additional parameters are passed to the handler
        def my_handler(message):
            print("test_handler:" + message)
        streamer.start(my_handler)


        # start steamer with default response handler (print):
        #streamer.start()


        # You can stream up to 500 keys.
        # By default all shortcut requests (below) will be "ADD" commands meaning the list of symbols will be added/appended
        # to current subscriptions for a particular service, however if you want to overwrite subscription (in a particular
        # service) you can use the "SUBS" command. Unsubscribing uses the "UNSUBS" command. To change the list of fields use
        # the "VIEW" command.
        while True:

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
    load_dotenv()
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s: %(message)s',
                    level=logging.INFO,
                    datefmt="%H:%M:%S")
    main()