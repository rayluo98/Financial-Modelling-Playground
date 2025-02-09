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
    def __init__(self):
        # Updated headers for macOS Sonoma and Apple M3 Pro
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Apple M3 Pro Mac OS X 14_6_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
        }
        self.url = ""
        self.savDir = DIR
    
    def scrape(self):
        url = self.url
        headers = self.headers
        underlying = []
        with requests.Session() as req:
            req.headers.update(headers)
            for key in self.indices:
                r = req.get(url.format(key))
        return underlying