#%%
import functools
import subprocess
import pandas as pd
import sys
import yfinance as yf
import concurrent.futures
import logging
from threading import Thread
from threading import RLock
import os 
import json
import path_signature

lock = RLock()

def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])
install("cntk")

#%%
tickers = pd.read_csv(r"C:\Users\raymo\OneDrive\Desktop\Playground\Financial-Modelling-Playground\Basket Trade\tickers.csv", header=None)
tickers = tickers.values
print(tickers)
yf.set_tz_cache_location(r"C:\Users\raymo\OneDrive\Desktop\Playground\Financial-Modelling-Playground\Basket Trade")

format = "%(asctime)s: %(message)s"
logging.basicConfig(format=format, level=logging.INFO,
                    datefmt="%H:%M:%S")
#need to make sure items are unique as race conditions are not handled  for multithreading
# keys: ticker name
# values: (info, history)
LE_HISTO = dict() 
def loadHistory(ticker: list, histo: dict, lock:RLock):
    with lock:
        ts = yf.Ticker(ticker[0])
        # get all stock info
        info = ts.info
        # get historical market data
        hist = ts.history(interval="1h", period='2y')
        histo[ticker[0]] = (info, hist) ## to replace with struct
func = lambda x: loadHistory(x, LE_HISTO, lock)
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
    #result = executor.map(functools.partial(loadHistory , tickers, LE_HISTO, lock)
    result = executor.map(func, tickers)

# %%
try:
    import tqdm
except:
    install("tqdm")

#%%
'''
# add a range of values to the dictionary [to immediate concurrent dictionary]
def add_items(shared_dict, start_value, num_values):
    # enumerate block of values
    for i in range(start_value, start_value+num_values):
        # add to the dict
        shared_dict[i] = i

shared_dict = dict()

# configure threads
threads = list()
for i in range(0, 1000000, 1000):
    thread = Thread(target=add_items, args=(shared_dict, i, 1000))
    threads.append(thread)
print(f'Created {len(threads)} threads')
# start threads
for thread in threads:
    thread.start()
# wait for threads to finish
for thread in threads:
    thread.join()
print(f'Dict has {len(shared_dict)} items')
'''

# %%
LE_HISTO['CMDO.U']
# %%
filtered_Histo = dict()
for sym in LE_HISTO:
    if len(LE_HISTO[sym][1]) != 0:
        filtered_Histo[sym]= LE_HISTO[sym]

#for filtered_ts in filtered_Histo:
    

# %%

for sym in filtered_Histo:
    try:
        if (not os.path.isfile("Histo//"+sym+"//"+sym+".txt")):
            #os.mkdir("Histo//"+sym)
            file=open("Histo//"+sym+"//"+sym+".txt", "x")
        else:
            file=open("Histo//"+sym+"//"+sym+".txt", "w")
        file.write(json.dumps(filtered_Histo[sym][0]))
        file.close()
        filtered_Histo[sym][1].to_csv("Histo//"+sym+"//"+sym+".csv")
    except FileNotFoundError as e:
        print(f'An error occurred: {e}')

filtered_Histo
# %%
filtered_Histo[sym][1]

# %%
