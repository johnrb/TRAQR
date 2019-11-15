import time
import math
import json
from gps import *
import Adafruit_DHT  # for temp/humidity
import Adafruit_ADS1x15  # analog-digital converter
#import threading
import sys
import RPi.GPIO as GPIO  # for managing regulator
#import upload
#import check_wifi
#import os
#import led 

adc = Adafruit_ADS1x15.ADS1115()
GAIN = 1   # read voltages from 0 to 4.9V. See datasheet for more info

# Where things are connected to the ADC
CO_PIN = 0
VOC_PIN = 1
OZ_PIN = 2

# Stuff for converting from ADC readings to concentration
v_factor = 4.096 / 32767  # 4.096V = reading of 32767 on ADC
Vc = 5  # the voltage we're powering everything with
CO_RL = 10000  # 10k resistor connected to the CO sensor
OZ_RL = 39000  # 39k resistor connected to the OZ sensor
VOC_RL = 10000  # 10k resistor connected to the VOC sensor (built into the board)

# Resistences at some known conditions. NEED TO BE CALIBRATED
CO_Ro = 200000
OZ_Ro = 2000
VOC_Ro = 100000   # datasheet says this ranges from 100 to 1500 kOhm

# Direct pin control for managing the voltage regulator
GPIO.setmode(GPIO.BCM) # use the GPIO pin numbering scheme
GPIO.setup(4, GPIO.OUT) # set pin 4 as output

# ----------------------------------------------------------

while True:
    
    #print "--> recording Ozone"
    value = adc.read_adc(OZ_PIN, gain=GAIN)
    voltage = (value * v_factor) - 4.096 
    print value, voltage
    
    """if (3 < voltage < 4.1):
	ppm = (voltage - 4.08) / (-.0082)
	print ppm
    elif (voltage < 3):
	if (voltage == 0.0):
	    print "unable to read sensor"
	ppm  = math.log((voltage / 8.7448)-0.237)
	print ppm 
	
    time.sleep(2)
    """
    """
    Rs = (Vc/voltage-1)*OZ_RL   # internal resistence of the sensor
    ppm = 400 * (Rs / OZ_Ro)**(-3)
    ppm = float("%.4f" % ppm)
    print voltage
    time.sleep(2)
    """

