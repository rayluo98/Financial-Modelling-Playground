import requests
import re
import json
import os
import io
import pandas as pd
import xmltodict
import random
import time


DIR = r'C:\Users\raymo\OneDrive\Desktop\Ray Stuff\_Cache'

class IndexCrawler(object):
    def __init__(self, _indices:list[str]):
        self.indices = _indices
        # Updated headers for macOS Sonoma and Apple M3 Pro
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Apple M3 Pro Mac OS X 14_6_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
        }
        self.url = "https://www.zacks.com/funds/etf/{}/holding"
        self.savDir = DIR

    def componentWtScrapper(self, txtResponse: str):
        # Extract Regex Identifiers
        tableExtract = re.findall(r'<\\/span><\\/span><\\/a>",(.*?)" alt=\\"View Report\\', txtResponse)
        ### Manual Table Headers
        headers = ['Shares', 'Pct Weight', 'YoY Change']
        res = {}
        errors = {}
        for row in tableExtract:
            row_extract = {}
            ticker_delimiter_idx = row.rfind('/')
            if (ticker_delimiter_idx == -1):
                errors[row] = "Couldn't find ticker name in extract!"
                continue
            ticker = row[ticker_delimiter_idx + 1:].replace("\\","")
            table_delimiter_idx = row.find("<")
            row = row[:table_delimiter_idx].replace(",","")
            row_split = row.split('\"')
            for i in range(len(headers)):
                row_extract[headers[i]] = float(row_split[2*i + 1] if row_split[2*i+1] != "NA" else 0)
            res[ticker] = row_extract
        return res

    def componentScrapper(self, txtResponse: str):
        # Extract Regex Identifiers
        return re.findall(r'etf\\\/(.*?)\\', txtResponse)
    
    def janitorsCheckpoint(self, savDir, fileName, df):
        df.to_csv(os.path.join(savDir, fileName, fileName + "_scraps.csv"))
        print("oh... so you're done scrapping?")


    def scrape(self):
        url = self.url
        headers = self.headers
        underlying = []
        with requests.Session() as req:
            req.headers.update(headers)
            for key in self.indices:
                r = req.get(url.format(key))
                # json_extract = json.loads(r.text)
                print(f"Extracting: {r.url}")
                subquest = pd.DataFrame(self.componentWtScrapper(r.text)).transpose()
                # self.janitorsCheckpoint(self.savDir, key, subquest)
                goal = self.componentScrapper(r.text)
                print(goal)
                underlying.append(goal)
                print(len(goal))
                ## don't api to get killed for botting 
                rnd_wait = random.uniform(0,3)
                time.sleep(rnd_wait)
        return underlying

def main():
    janitorUno = IndexCrawler(['SPY','QQQ'])
    print(janitorUno.scrape())

if __name__=="__main__":
    main()