# -*- coding: utf-8 -*-
"""
Created on Wed Sep 16 04:11:16 2020

@author: raymo
"""

import urllib.request, urllib.parse, urllib.error
from bs4 import BeautifulSoup
import ssl

#Ignore SSL Certificate Errors
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

import re 

url = input('Enter - ')
n = int(input('Position -'))
t = int(input('Number of Times -'))

for i in range(t):
    html = urllib.request.urlopen(url, context = ctx).read()
    soup = BeautifulSoup(html, 'html.parser')
    tags = soup('a')
    url = tags[n-1].get('href', None)
    print(re.findall('known_by_([a-z A-Z]+)\.html', url))


##Retrieve all of the anchor tags

#tags = soup('span')
#for tag in tags:     # Look at the parts of a tag
    #print(tag.get('href', None))
    #print('TAG:', tag)
    #print('URL:', tag.get('href', None))
    #print('Contents:', tag.contents[0])
    #print('Attrs:', tag.attrs)
    
    
##Scraping
'''
import re
hand = tags
numlist = list()
count = 0
for line in hand:
    line = line.contents[0]
    line = line.rstrip()
    stuff = re.findall('[0-9]+',line) #Find all numerals 
    for i in stuff:
        count += int(i)
print(count)
'''