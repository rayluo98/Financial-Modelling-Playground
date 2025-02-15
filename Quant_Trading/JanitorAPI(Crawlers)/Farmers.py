from kafka import KafkaProducer as kp
from bs4 import BeautifulSoup as bs
import requests
import time
import re
import mechanize
import pandas as pd
import CrawlerFactory
import EarningsCalendarCrawler
import json

# Kafka configuration
bootstrap_servers = ['localhost:9092']
topic = 'scraping-events'

# Web scraper configuration
product_url = 'https://tradingeconomics.com/calendar'
headers = {'user-agent': 'Mozilla/5.0 (WIndows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Cache-Control': 'max-age=0',
    }
# Create Kafka producer
producer = kp(bootstrap_servers=bootstrap_servers,
            api_version=(0,11,5),
            value_serializer=lambda x: json.dumps(x).encode('utf-8'))

def scrape_product_price():
    # Make HTTP request to fetch the product page
    cookiesJar = {'cal-custom-range':'2024-02-15|2024-02-16',
                  'cal-timezone-offset':'-300',
                  'calendar-importance':'3'}
    response = requests.get(product_url, headers=headers,
                            cookies=cookiesJar)
    
    def earningsEventScrapper(Response):
        ### Manual Table Headers
        headers = ["Company", "EPS", "Consensus",
                    "Previous", "Revenue_Nominal","Consensus_Nominal", "Previous_Nominal"]
        # Parse the HTML response
        soup = bs(Response, 'html.parser')
        # Extract Regex Identifiers
        tableExtract = soup.find('table', 'table table-hover table-condensed table-stripped')
        # The first tr contains the field names.
        datasets = []
        if tableExtract == None:
            return pd.DataFrame()
        for row in tableExtract.find_all("tr")[1:]:
            temp = row.find_all("td")
            temp = list(filter(lambda x: len(x.text.strip()) > 0, temp))
            if (len(temp) < len(headers)):
                continue
            dataset = {"Country":row.get("data-country")} | \
                    {"Ticker":row.get("data-symbol")} | \
                    dict(zip(headers, (td.get_text().strip() 
                                        for td in temp)))
            datasets.append(dataset)
        res = pd.DataFrame(datasets)
        return res

       # Create a scraping event message
    scraping_event = {
        'timestamp': int(time.time()),
        'product_url': product_url,
        'price': earningsEventScrapper(response.content).to_json()
    }
    
    # Publish the scraping event to Kafka topic
    producer.send(topic, value=scraping_event)
    producer.flush()
    print('Scraping event published:', scraping_event)

# Run the scraper at regular intervals
while True:
    scrape_product_price()
    time.sleep(300)  
# Scrapes every 5 minutes

def main():
    scrape_product_price()

if __name__=="__main__":
    main()