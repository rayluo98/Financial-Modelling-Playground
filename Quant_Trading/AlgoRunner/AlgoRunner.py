### imports
import requests
import timer
import logging
from client import Client
### pip install python-dotenv
from dotenv import load_dotenv
import datetime
import json
import time
from time import sleep
from OrderHandler import *
import os

def main():
    SERVER_ENDPOINT = r"https://api.schwabapi.com/"

    with timer.timer() as t:
        MARKET_DATA_ENDPOINT = r"marketdata/v1/"
        ACCOUNT_ENDPOINT = r"trader/v1"
        TIME_STOPPER = 9.5 * 3600 ## imprecise
        
        ### establish schwab connection
        client = Client(os.getenv('app_key'), os.getenv('app_secret'), os.getenv('callback_url'))

        ### retrieve account info 
        _, account_hash = OrderHandler(client).getAccs()

        # define a variable for the steamer:
        streamer = client.stream

        # Stream up to 500 keys.
        # By default all shortcut requests (below) will be "ADD" commands meaning the list of symbols will be added/appended
        # to current subscriptions for a particular service, however if you want to overwrite subscription (in a particular
        # service) you can use the "SUBS" command. Unsubscribing uses the "UNSUBS" command. To change the list of fields use
        # the "VIEW" command.
        #define a response handler
        shared_list = []
        def response_handler(message):
            shared_list.append(message)

        # start the stream and send in what symbols we want.
        streamer.start(response_handler)

        ### initialize base model based on cached data
        

        ### identifies tickers of interest to pull market data
        FOCUS_TICKERS = []

        ### test 
        FOCUS_TICKERS = ['AAPL', 'AMC']

        ### send requests to pull market data every minute (to prevent api overload)
        streamer.send(streamer.level_one_equities(','.join(FOCUS_TICKERS), "0,1,2,3,4,5,6,7,8"))

        ### recallibrate base model every {2} hours

        while True: #proccessing on list is done here
            #print the most recent message
            while len(shared_list) > 0: # while there is still data to consume from the list
                oldest_response = json.loads(shared_list.pop(0)) # get the oldest data from the list
                #print(oldest_response)
                for rtype, services in oldest_response.items():
                    if rtype == "data":
                        for service in services:
                            service_type = service.get("service", None)
                            service_timestamp = service.get("timestamp", 0)
                            contents = service.get("content", [])
                            for content in contents:
                                symbol = content.pop("key", "NO KEY")
                                fields = content
                                print(f"[{service_type} - {symbol}]({datetime.fromtimestamp(service_timestamp//1000)}): {fields}")
                    elif rtype == "response":
                        pass # this is a "login success" or "subscription success" or etc
                    elif rtype == "notify":
                        pass # this is a heartbeat (usually) which means that the stream is still alive
                    else:
                        #unidentified response type
                        print(oldest_response)
            time.sleep(0.5) # slow down difference checking

            ### pull account data

            ### calculate market impact

            ### EXECUTE TRADE
            # # this currently means nothing
            # order = schwabOrder() ### should make this compatible with order book backtesting
            # OrderHandler.placeOrder(client, account_hash, order)

            ### send email notification regarding decision
            if t.elapse > TIME_STOPPER:
                return

if __name__=="__main__":
    load_dotenv()
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s: %(message)s',
                    level=logging.INFO,
                    datefmt="%H:%M:%S")
    main()