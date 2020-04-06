import time

#Import neopixel, this is for the LED control
from neopixel import *

#Import font structure
from font import px56

# LED strip configuration:
LED_PIN        = 19      # GPIO pin connected to the pixels (18 uses PWM!).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 5       # DMA channel to use for generating signal (try 5)
LED_BRIGHTNESS = 128     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL    = 1       # set to '1' for GPIOs 13, 19, 41, 45 or 53
LED_STRIP      = ws.WS2811_STRIP_GRB   # Strip type and colour ordering

class frameBuffer():

    def __init__(self, x_dim, y_dim):
        self.x_total = x_dim
        self.y_total = y_dim
        #this is the picture data buffer
        self.fb = self.createBuffer(x_dim, y_dim)
        #this is the string data buffer
        self.sb = [self.createBuffer(x_dim, 7), self.createBuffer(x_dim, 7)]

        # String definitions
        self.font = px56()
        self.draw_string = [True, True]
        self.max_rows = y_dim//self.font.getCharHeight()
        self.y2 = self.font.getCharHeight()+1 
        self.string = ["",""]
        self.scroll = [False,False]
        self.pix_offset = [0,0]
        self.string_len = [0,0]

        #set color option
        self.bkgnd_color = Color(0,64,0)
        self.txt_color   = Color(32,0,0)
        
            # Create NeoPixel object with appropriate configuration.
        self.strip = Adafruit_NeoPixel(x_dim*y_dim, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL, LED_STRIP)
            # Intialize the library (must be called once before other functions).
        self.strip.begin()


    def createBuffer(self, x, y):
        buffer = []
        #Fill Y lists to X size
        for i in range(y):
            buffer.append([])
            for j in range(x):
                buffer[i].append(0)
        return buffer
        
    def clearBuffer(self):
        for i in range(self.y_total):
            for j in range(self.x_total):
                self.fb[i][j] = 0

    def printXY(self):
        print('x = ', self.x_total, ',y = ', self.y_total, '\n')

    def setBackgroundColor(self, r, g, b):
        self.bkgnd_color = Color(r, g, b)

    def setTextColor(self, r, g, b):
        self.txt_color = Color(r, g, b)

    def insertData(self, buffer, x_orig, y_orig, data, data_width):
        x_size = data_width
        y_size = len(data)
        #print(y_orig, x_orig)
        #print(y_size, x_size)
        for y in range(y_size):
            for x in range(x_size):
                buffer[y_orig + y][x_orig + x] = data[y][x]
        return buffer
    
    def insertStrBufWithRoll(self, buffer, x_orig, y_orig, data, xshift):
        buf_xsize = len(buffer[0])
        img_xsize = len(data[0])
        y_size = len(data)
        #print(y_orig, x_orig)
        #print(y_size, x_size)
        for y in range(y_size):
            for x in range(buf_xsize):
                if(x<img_xsize):
                    #Deal with pixel wrapping
                    if(x+xshift >= img_xsize):
                        x_pos = (x+xshift) - img_xsize
                    else: 
                        x_pos = x+xshift
                    buffer[y_orig + y][x_orig + x] = data[y][x_pos]
                else:
                    buffer[y_orig + y][x_orig + x] = 0
        return buffer

    def updateStringBuffer(self, buffer, row):
        x = 0
        y = row*self.y2 
        for i in range(len(self.string[row])):
            char_wid, char_data = self.font.get_char(self.string[row][i])
            self.insertData(buffer, x, y, char_data, char_wid)
            self.insertData(buffer, x+5, y, self.font.get_gap(), char_wid)
            x += 6
        #print(self.fb)
        return buffer

    def clearString(self, row):
            self.string[row] = ''
            self.draw_string = False


    def writeString(self, string, row):
        self.string[row] = string
        self.draw_string = True
        self.scroll[row] = False #start with assuming string fits
        row_width = 0
        for i in range(len(string)):
            if(string[i] == " "):
                row_width += 1 #Just add a space
            else:
                char_wid, char_data = self.font.get_char(string[i])
                if(row_width + char_wid + 1 > self.x_total):
                    self.scroll[row] = True
                    row_width += 5 # add a bunch of space at the end
                row_width += char_wid + 1 #Add space plus character width
                #print(string[i], char_wid, row_width)
        self.sb[row] = self.createBuffer(row_width, self.font.getCharHeight())
        self.string_len[row] = row_width
        currx=0
        for i in range(len(string)):
            char_wid, char_data = self.font.get_char(string[i])
            self.sb[row] = self.insertData(self.sb[row], currx, 0, char_data, char_wid)
            currx += char_wid + 1

        #if we're scrolling, add a space to the end to keep text seperate
        if(self.scroll[row] == True):
            char_wid, char_data = self.font.get_char(" ")
            self.sb[row] = self.insertData(self.sb[row], currx, 0, char_data, 1)
        
        return

    def drawPixel(self, x, y):
        if(self.fb[y][x]):
            if(y%2 == 0):
                #self.strip.setPixelColor((y*26)+x, Color(32,32,32))
                self.strip.setPixelColor((y*26)+x, self.txt_color)
            else:
                #self.strip.setPixelColor((y*26)+(25-x), Color(32,32,32))
                self.strip.setPixelColor((y*26)+(25-x), self.txt_color)
        else:
            if(y%2 == 0):
                #self.strip.setPixelColor(y*26+x, Color(0,0,0))
                self.strip.setPixelColor(y*26+x, self.bkgnd_color)
            else:
                #self.strip.setPixelColor(y*26+(25-x), Color(0,0,0))
                self.strip.setPixelColor(y*26+(25-x), self.bkgnd_color)

    def updateOffset(self, amount):
        #print(self.pix_offset[row], amount, self.string_len[row])
        wrap_complete = [False, False]
        for row in range(len(self.sb)):
            #only roll if the buffer is bigger than the display
            if(self.scroll[row]  == True):
                if((self.pix_offset[row] + amount) > self.string_len[row]):
                    #if((self.pix_offset[row] + amount + self.x_total) > self.string_len[row]):
                    # Wrap once we reach the end of the buffer. This will just scroll text in a circle
                    self.pix_offset[row] = 0
                    wrap_complete[row] = True
                else:
                    self.pix_offset[row] =  self.pix_offset[row] + amount;
            else:
                self.pix_offset[row] = 0
                wrap_complete[row] = True
                
        return wrap_complete 

    def drawDisplay(self, enable):
        if(enable == True):
            if(self.draw_string):
                #for row in range(2):
                #    self.sb[row] = self.updateStringBuffer(self.sb[row], row)
                self.fb = self.insertStrBufWithRoll(self.fb, 0, 0, self.sb[0], self.pix_offset[0])
                self.fb = self.insertStrBufWithRoll(self.fb, 0, self.y2, self.sb[1], self.pix_offset[1])
            
            for i in range(self.y_total):
                for j in range(self.x_total):
                    self.drawPixel(j, i)
        else:
            for i in range(self.strip.numPixels()):
                self.strip.setPixelColor(i, Color(0,0,0))

        self.strip.show()

