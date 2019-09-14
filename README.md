LED Matrix Server
==========
This is the code for an LED matrix server built with a Raspberry Pi and WS2812 addressable LEDs

### Neopixel:
To install neopixel do the following:

First, install the dependencies required to download and install the library:
```
sudo apt-get update
sudo apt-get install build-essential python-dev git scons swig

Next, download the files and build the library:
```
git clone https://github.com/jgarff/rpi_ws281x.git
cd rpi_ws281x
scons

Finally, install the Python wrapper:
```
cd python
sudo python setup.py install
