import requests
import re
import json
import os
import io
import xmltodict


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

    def crawlerContentCapture(self, response, file_name:str='test.xml'):
         # saving the xml file 
        with open(os.path.join(self.savDir, file_name), 'wb') as f: 
            f.write(response) 

    def componentWtScrapper(self, response, file_name:str='test.xml', elementSearch = r"\<\\ span\>\<\\ span\>\<\\ a\>"):
        ## custom splitting of html response
        junkyard = response.split(elementSearch)
        return junkyard

    def scrape(self):
        url = self.url
        headers = self.headers
        underlying = []
        with requests.Session() as req:
            req.headers.update(headers)
            for key in self.indices:
                r = req.get(url.format(key))
                ### need flag here later
                self.crawlerContentCapture(r.content, os.path.join(key, key + "_content.xml"))
                # self.componentWtScrapper(r.text, os.path.join(key, key + "_text.xml"))
                # json_extract = json.loads(r.text)
                print(f"Extracting: {r.url}")
                subquest = re.findall(r'<\\ span><\\ span><\\ a>(.*?) alt=\\"View Snapshot\\', r.text)
                goal = re.findall(r'etf\\\/(.*?)\\', r.text)
                print(goal)
                underlying.append(goal)
                print(len(goal))
        return underlying

def main():
    janitorUno = IndexCrawler(['SPY','QQQ'])
    print(janitorUno.scrape())

if __name__=="__main__":
    main()