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
from datetime import date,timedelta
from pandas.tseries.offsets import BusinessDay as BDay
import numpy as np

####################################################################################################
# This is a wrapper to crawl the economic calendar data off of TradingEconomics.com
# PLEASE NOTE THAT YOU CAN ONLY PULL DATA UP TO 10 YEARS IN THE PAST (in intervals less than 1 month)
####################################################################################################


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
        self.cookiesJar = {'cal-custom-range':f'{dt}|{dt}',
                  'cal-timezone-offset':'-300',
                  'calendar-importance':'1'}
        self.dt = dt

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
        if tableExtract == None:
            return pd.DataFrame()
        for row in tableExtract.find_all("tr")[1:]:
            temp = row.find_all("td")
            temp = list(filter(lambda x: len(x.text.strip()) > 0, temp))
            if (len(temp) < len(headers)):
                continue
            dataset = dict(zip(headers, (td.get_text().strip() 
                                        for td in temp)))
            datasets.append(dataset)
        res = pd.DataFrame(datasets)
        return res

    def janitorsCheckpoint(self, savDir, fileName, df):
        df.to_csv(os.path.join(savDir, "Economic_Calendar", fileName + "_scraps.csv"))

    def scrape(self):
        url = self.url
        headers = self.headers
        underlying = []
        with requests.Session() as req:
            req.headers.update(headers)
            for key in self.dates:
                ## don't api to get killed for botting 
                rnd_wait = random.uniform(5,10)
                time.sleep(rnd_wait)
                self.updateCrawlDate(key)
                if self.cookiesJar == None:
                    r = req.get(url)
                else:
                    r = req.get(url,
                                headers=self.headers,
                                cookies=self.cookiesJar)
                # json_extract = json.loads(r.text)
                print(f"Extracting: {r.url} on {self.dt}")
                goal = self.macroEventScrapper(r.content)
                if (goal.empty):
                    print(f"No events for {self.dt}")
                    continue
                self.janitorsCheckpoint(self.savDir,
                                        "Economic_Calendar_{0}".format(key), goal)
        print("oh... so you're done scrapping?")
        return underlying
    
def get_all_days_between_dates(start_date, end_date):
    """
    Returns a list of dates between two dates (inclusive).

    Args:
        start_date (date): The start date.
        end_date (date): The end date.

    Returns:
        list: A list of dates between start_date and end_date.
    """
    dates = []
    current_date = start_date
    while current_date <= end_date:
        dates.append(current_date.strftime("%Y-%m-%d"))
        current_date += pd.DateOffset(days=1)
    return dates

def main():
    ## End Date
    # end_dt = date(2025,1,1)
    end_dt = pd.to_datetime("2025-02-09")
    ## Start date
    start_dt = pd.to_datetime("2015-06-08")
    dt_list = get_all_days_between_dates(start_dt, end_dt)
    janitorDos = EconCalendarCrawler(dt_list)
    print(janitorDos.scrape())

if __name__=="__main__":
    main()