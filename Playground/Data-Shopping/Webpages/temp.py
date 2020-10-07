# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import socket
mysock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
mysock.connect( ('data.pr4e.org', 80)) #Host + Port

cmd = 'GET http://data.pr4e.org/romeo.txt HTTP/1.0\n\n'.encode()
mysock.send(cmd)

while True:
    data = mysock.recv(512)
    if (len(data) < 1):
        break
    print(data.decode())
mysock.close()

import re
hand = open("regex_sum_961198.txt") #Our input file
count = 0
for line in hand:
    line = line.rstrip()
    stuff = re.findall('[0-9]+',line) #Find all numerals 
    for i in stuff:
        count += int(i)
print(count)