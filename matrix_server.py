import time
from multiprocessing import Process
import os

#Import flash, this is python webserver
from flask import Flask, render_template

import sqlite3

#Import neopixel, this is for the LED control
from neopixel import *

#Import custom frame buffer
from frame_buffer import frameBuffer

#Import stock ticker functions
from stock_ticker import  stockTicker

from datetime import datetime, date, timedelta

# LED strip configuration:
LED_COUNT      = 500      # Number of LED pixels.
LED_PIN        = 19      # GPIO pin connected to the pixels (18 uses PWM!).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 5       # DMA channel to use for generating signal (try 5)
LED_BRIGHTNESS = 128     # Set to 0 for darkest and 255 for brightest LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL    = 1       # set to '1' for GPIOs 13, 19, 41, 45 or 53
LED_STRIP      = ws.WS2811_STRIP_GRB   # Strip type and colour ordering


#modes
DISPLAY = 0
STOCK_TICKER_MODE = 0
AUDIO_VISULIZER_MODE = 1

#---------------------------------------------------------------------
# LED Control functions
#---------------------------------------------------------------------
#create frame_buffer object
fb = frameBuffer(26, 15)

#Need to make stocks dyanmic. Will add to SQL later
tickers = ['TSLA', 'AMZN', 'FTV', 'BDC', 'AAPL']
st = stockTicker(tickers)
#today = datetime.today()
#if(today.isoweekday() == 6):
#    close = today-timedelta(days=1)
#elif(today.isoweekday() == 7):
#    close = today-timedelta(days=2)
#else:
#    close = today
#close_string = close.strftime('%Y-%m-%d')

#for stock in st.tickers:
#    current_price = st.stockPrice(stock)
#    print(stock + " = " + current_price, st.isStockUp(stock))

#---------------------------------------------------------------------
# Webserver functions
#---------------------------------------------------------------------
#Create flask webserver object
app = Flask(__name__)

#Create database for status
os.remove("database.db") #remove old one for simplicity
db = sqlite3.connect('database.db')
cursor=db.cursor()
#kludge, only use to add new column once
cursor.execute('''CREATE TABLE IF NOT EXISTS dispstat ( display INTEGER PRIMARY KEY AUTOINCREMENT, status INTEGER, mode INTEGER)''')
cursor.execute('''INSERT INTO dispstat VALUES (0, 1, 0)''')
db.commit()
db.close()



def server():
    @app.route('/')
    def index():
        return 'Hello world'

    @app.route('/strand/<name>')
    def setDispStat(name):
        if(name == 'on'):
            setStatus(1)
            print("turn display on")
        elif(name == 'off'):
            setStatus(0)
        return render_template('page.html', name=name)

    @app.route('/stock_ticker')
    def setDispMode():
        print("Use Stock Ticker Mode")
        setMode(0)
        return render_template('page.html', name='Stock Ticker')


    app.run(debug=False, host='0.0.0.0')

    db.close()


#create thread
web_process = Process(target=server)

def setStatus(status):
    db = sqlite3.connect('database.db')
    cursor=db.cursor()
    cursor.execute('''UPDATE dispstat SET status = ? where display = ?''', (status,DISPLAY))
    db.commit()
    db.close()


def getStatus():
    db = sqlite3.connect('database.db')
    cursor=db.cursor()
    cursor.execute('''SELECT status FROM dispstat WHERE display=?''', (DISPLAY,))
    disp_stat = cursor.fetchone()
    db.close()
    #print("display status = " + str(disp_stat[0]))
    return disp_stat[0]

def setMode(mode):
    db = sqlite3.connect('database.db')
    cursor=db.cursor()
    cursor.execute('''UPDATE dispstat SET mode = ? where display= ?''', (DISPLAY,mode))
    db.commit()
    db.close()


def getMode():
    db = sqlite3.connect('database.db')
    cursor=db.cursor()
    cursor.execute('''SELECT mode FROM dispstat WHERE mode=?''', (DISPLAY,))
    mode_stat = cursor.fetchone()
    db.close()
    return mode_stat[0]


if __name__ == '__main__':
    web_process.start()
    #fb.writeString('Xmas Test', 0)
    #fb.writeString('Test', 1)
    fb.setBackgroundColor(0, 0, 0)

    #setup stock ticker stuff
    seconds = 0
    stock_index = 2
    stock_string = tickers[stock_index]
    st.displayStock(stock_string, fb)

    while(True):
        enable = getStatus()
        fb.drawDisplay(enable)
        if(getMode() == STOCK_TICKER_MODE):
            # Stock Ticker
            wrap_complete = fb.updateOffset(1)
            #time.sleep(0.030)
            time.sleep(0.5)

            # Wait for at least 5 seconds and for the price to stop wrapping
            seconds += 1;
            if(wrap_complete[1] == True and seconds > 5):
                if(stock_index < len(st.getTickers())-1):
                    stock_index = stock_index + 1;
                else:
                    stock_index = 0
                stock_string = st.getTickers()[stock_index]
                #print(stock_string, stockPrice(stock_string))
                st.displayStock(stock_string, fb)
                seconds = 0
        else:
            # Other modes not supported yet
            time.sleep(0.5)



