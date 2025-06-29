from datetime import datetime as dt
import pandas as pd
import requests
from bs4 import BeautifulSoup


## ASSUMES DATE FORMAT IN DD-MM-YYYY
def ConvertDt(dates_as_str:list[str]):
    return [dt.strptime(date_string, "%d-%m-%Y") for date_string in dates_as_str]

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


### DRIVER FUNCTION TO TEST
def test():
    curr, old = getSPXConstituents() 
    print(curr)
    result = list(set(list(curr['Symbol']) + list(old['Added']['Ticker']) + list(old['Removed']['Ticker'])))
    result = [str(x) for x in result]
    with open(r'/home/rayluo98/temp.txt', "w") as file:
        file.write('\n'.join(result))

if __name__ == '__main__':
    test()