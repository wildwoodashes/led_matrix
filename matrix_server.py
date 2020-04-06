import time
from multiprocessing import Process

#Import flash, this is python webserver
from flask import Flask, render_template

import sqlite3

#Import neopixel, this is for the LED control
from neopixel import *

#Import custom frame buffer
from frame_buffer import frameBuffer

#Import datareader for fetching stock info
import urllib.request
import json
import sys
from datetime import datetime, date, timedelta

# LED strip configuration:
LED_COUNT      = 500      # Number of LED pixels.
LED_PIN        = 19      # GPIO pin connected to the pixels (18 uses PWM!).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 5       # DMA channel to use for generating signal (try 5)
LED_BRIGHTNESS = 128     # Set to 0 for darkest and 255 for brightest LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL    = 1       # set to '1' for GPIOs 13, 19, 41, 45 or 53
LED_STRIP      = ws.WS2811_STRIP_GRB   # Strip type and colour ordering


#---------------------------------------------------------------------
# LED Control functions
#---------------------------------------------------------------------
#create frame_buffer object
fb = frameBuffer(26, 15)


#---------------------------------------------------------------------
# Stock fetch functions
#---------------------------------------------------------------------
def stockGet(symbol):
    url = "https://cloud.iexapis.com/stable/stock/"
    auth = "/quote?token="
    with open('token.txt') as f:
        token = f.readline()


    command = url + symbol + auth + token.strip()
    quote = urllib.request.urlopen(command).read().decode('utf-8')
    return quote

def stockPrice(symbol):
    data = json.loads(stockGet(symbol))
    return str(data["latestPrice"])

def isStockUp(symbol):
    data = json.loads(stockGet(symbol))
    if(data['change'] > 0):
        return True
    else:
        return False

#Need to make stocks dyanmic. Will add to SQL later
tickers = ['TSLA', 'AMZN', 'FTV', 'BDC', 'AAPL']
today = datetime.today()
if(today.isoweekday() == 6):
    close = today-timedelta(days=1)
elif(today.isoweekday() == 7):
    close = today-timedelta(days=2)
else:
    close = today
close_string = close.strftime('%Y-%m-%d')

for stock in tickers:
    current_price = stockPrice(stock)
    print(stock + " = " + current_price, isStockUp(stock))

#---------------------------------------------------------------------
# Webserver functions
#---------------------------------------------------------------------
#Create flask webserver object
app = Flask(__name__)

#Create database for status
db = sqlite3.connect('database.db')
cursor=db.cursor()
cursor.execute('''UPDATE dispstat SET status = ? where display = ?''', (0,0))
db.close()



def server():
    @app.route('/')
    def index():
        return 'Hello world'

    @app.route('/strand/<name>')
    def hello(name):
        if(name == 'on'):
            setStatus(0,1)
            print("turn display on")
        elif(name == 'off'):
            setStatus(0,0)
        return render_template('page.html', name=name)

    app.run(debug=False, host='0.0.0.0')

    db.close()


#create thread
web_process = Process(target=server)

def setStatus(disp, status):
    db = sqlite3.connect('database.db')
    cursor=db.cursor()
    cursor.execute('''UPDATE dispstat SET status = ? where display = ?''', (status,disp))
    db.commit()
    db.close()


def getStatus(disp):
    db = sqlite3.connect('database.db')
    cursor=db.cursor()
    cursor.execute('''SELECT status FROM dispstat WHERE display=?''', (disp,))
    disp_stat = cursor.fetchone()
    db.close()
    return disp_stat[0]

def displayStock(stock):
    if(isStockUp(stock)):
        fb.setTextColor(64, 0, 0)
    else:
        fb.setTextColor(0, 64, 0)
    fb.writeString(stock, 0)
    fb.writeString(stockPrice(stock), 1)


if __name__ == '__main__':
    web_process.start()
    #fb.writeString('Xmas Test', 0)
    #fb.writeString('Test', 1)
    fb.setBackgroundColor(0, 0, 0)

    #setup stock ticker stuff
    seconds = 0
    stock_index = 2
    stock_string = tickers[stock_index]
    displayStock(stock_string)

    while(True):
        enable = getStatus(0)
        fb.drawDisplay(enable)
        wrap_complete = fb.updateOffset(1)
        #time.sleep(0.030)
        time.sleep(0.5)

        # Wait for at least 5 seconds and for the price to stop wrapping
        seconds += 1;
        if(wrap_complete[1] == True and seconds > 5):
            if(stock_index < len(tickers)-1):
                stock_index = stock_index + 1;
            else:
                stock_index = 0
            stock_string = tickers[stock_index]
            #print(stock_string, stockPrice(stock_string))
            displayStock(stock_string)
            seconds = 0



