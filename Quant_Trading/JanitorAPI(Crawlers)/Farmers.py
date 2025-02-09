from kafka import KafkaProducer as kp
from bs4 import BeautifulSoup as bs
import requests
import time
import re
import mechanize
import pandas as pd

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
            value_serializer=lambda x: dumps(x).encode('utf-8'))

def scrape_product_price():
    # Make HTTP request to fetch the product page
    cookiesJar = {'cal-custom-range':'2024-02-15|2024-02-16',
                  'cal-timezone-offset':'-300',
                  'calendar-importance':'3'}
    response = requests.get(product_url, headers=headers,
                            cookies=cookiesJar)
    
    # # Parse the HTML response
    soup = bs(response.content, 'html.parser')
    
    # # Extract the product price from the parsed HTML
    table = soup.find('table', 'table table-hover table-condensed')
    # The first tr contains the field names.
    headings = ["Timestamp", "Country", "Flag", "Event",
                "Actual", "Previous","Consensus", "Forecast"]

    datasets = []
    for row in table.find_all("tr")[1:]:
        temp = row.find_all("td")
        temp = list(filter(lambda x: len(x.text.strip()) > 0, temp))
        if (len(temp) < len(headings)):
            continue
        dataset = dict(zip(headings, (td.get_text().strip() 
                                      for td in temp)))
        datasets.append(dataset)
    # for dataset in datasets:
    #     for field in dataset:
    #         print("{0:<16}: {1}".format(field[0], field[1]))
    price = pd.DataFrame(datasets)
    # Create a scraping event message
    scraping_event = {
        'timestamp': int(time.time()),
        'product_url': product_url,
        'price': price
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