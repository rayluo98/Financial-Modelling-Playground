from bs4 import BeautifulSoup as bs
import requests
import time
import re
import mechanize
import json
import os
import io
import pandas as pd
import xmltodict
import random


DIR = r'C:\Users\raymo\OneDrive\Desktop\Ray Stuff\_Cache'

class EconCalendarCrawler(object):
    def __init__(self, _dates:list[str]):
        self.dates = _dates
        # Updated headers for macOS Sonoma and Apple M3 Pro
        self.url = 'https://tradingeconomics.com/calendar'
        self.headers = {'user-agent': 'Mozilla/5.0 (WIndows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0',
            }
        self.savDir = DIR
        self.cookiesJar = None
        self.dt = None

    def updateCrawlDate(self, dt):
        self.cookiesJar = {'cal-custom-range':'{}|{}'.format(self.dt),
                  'cal-timezone-offset':'-300',
                  'calendar-importance':'3'}

    def macroEventScrapper(self, Response):
        ### Manual Table Headers
        headers = ["Timestamp", "Country", "Flag", "Event",
                    "Actual", "Previous","Consensus", "Forecast"]
        # Parse the HTML response
        soup = bs(Response, 'html.parser')
        # Extract Regex Identifiers
        tableExtract = soup.find('table', 'table table-hover table-condensed')
        # The first tr contains the field names.
        datasets = []
        for row in tableExtract.find_all("tr")[1:]:
            temp = row.find_all("td")
            temp = list(filter(lambda x: len(x.text.strip()) > 0, temp))
            if (len(temp) < len(headers)):
                continue
            dataset = dict(zip(headers, (td.get_text().strip() 
                                        for td in temp)))
            datasets.append(dataset)
        # for dataset in datasets:
        #     for field in dataset:
        #         print("{0:<16}: {1}".format(field[0], field[1]))
        res = pd.DataFrame(datasets)
        return res

    def janitorsCheckpoint(self, savDir, fileName, df):
        df.to_csv(os.path.join(savDir, fileName, fileName + "_scraps.csv"))
        print("oh... so you're done scrapping?")


    def scrape(self):
        url = self.url
        headers = self.headers
        underlying = []
        with requests.Session() as req:
            req.headers.update(headers)
            for key in self.dates:
                self.updateCrawlDate(key)
                if self.cookiesJar == None:
                    r = req.get(url)
                else:
                    r = req.get(url,
                                headers=self.headers,
                                cookies=self.cookiesJar)
                # json_extract = json.loads(r.text)
                print(f"Extracting: {r.url} on {self.dt}")
                goal = self.macroEventScrapper(r)
                print(goal)
                ## don't api to get killed for botting 
                rnd_wait = random.uniform(0,3)
                time.sleep(rnd_wait)
        return underlying

def main():
    start_dt = ""
    end_dt = ""
    janitorDos = EconCalendarCrawler()
    print(janitorDos.scrape())

if __name__=="__main__":
    main()