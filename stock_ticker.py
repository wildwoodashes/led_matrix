import time
from multiprocessing import Process

import sqlite3

#Import datareader for fetching stock info
import urllib.request
import json
import sys
from datetime import datetime, date, timedelta

class stockTicker():

    def __init__(self, stocks):
        self.tickers = stocks



    #---------------------------------------------------------------------
    # Stock fetch functions
    #---------------------------------------------------------------------
    def stockGet(self, symbol):
        url = "https://cloud.iexapis.com/stable/stock/"
        auth = "/quote?token="
        with open('token.txt') as f:
            token = f.readline()
    
    
        command = url + symbol + auth + token.strip()
        quote = urllib.request.urlopen(command).read().decode('utf-8')
        return quote
    
    def stockPrice(self, symbol):
        data = json.loads(self.stockGet(symbol))
        return str(data["latestPrice"])
    
    def isStockUp(self, symbol):
        data = json.loads(self.stockGet(symbol))
        if(data['change'] > 0):
            return True
        else:
            return False

    def displayStock(self, stock, fb):
        if(self.isStockUp(stock)):
            fb.setTextColor(64, 0, 0)
        else:
            fb.setTextColor(0, 64, 0)
        fb.writeString(stock, 0)
        fb.writeString(self.stockPrice(stock), 1)

    def getTickers(self):
        return self.tickers
