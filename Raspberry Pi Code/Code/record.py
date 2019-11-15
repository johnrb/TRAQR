#!/usr/bin/env python2

##
#
# General framework script for recording data. Triggers data collection
# on all of the sensors.
#
##

import pm_module
import time
import json
from gps import *
import Adafruit_DHT  # for temp/humidity
import Adafruit_ADS1x15  # analog-digital converter
import threading
import sys
import RPi.GPIO as GPIO  # for managing input/output pins on the Pi
import upload
import check_wifi
import os
import led
import sys # import a foreign directory
sys.path.insert(0, '/home/pi/traqr/interface')
import beeper # from the foreign directory
import off_state
import filename_gen
import config as cfg


# -----------------  Global Variables (see config file)  ----------------------

formatted = False
fname = filename_gen.main() # designate a filename
sleep_time = cfg.main['sleep_time']   # time to wait between readings (in seconds)
    
gpsd = None  # GPS daemon
gpsp = None  # GPS poller object

adc = Adafruit_ADS1x15.ADS1115()
GAIN = 1   # read voltages from 0 to 4.9V. See datasheet for more info

# Where things are connected to the ADC
CO_PIN = cfg.ADC_pins['CO_PIN'] 
VOC_PIN = cfg.ADC_pins['VOC_PIN']
OZ_PIN = cfg.ADC_pins['OZ_PIN']
Vin_PIN = cfg.ADC_pins['ADC_Vin']

# Stuff for converting from ADC readings to concentration
v_factor = cfg.ADC_conversion['v_factor'] # Conversion factor between ADC reading and voltage 
Vc = cfg.ADC_conversion['Vc']  # the voltage we're powering everything with
CO_RL = cfg.ADC_conversion['CO_RL'] # 10k resistor connected to the CO sensor
OZ_RL = cfg.ADC_conversion['OZ_RL']  # 39k resistor connected to the OZ sensor
VOC_RL = cfg.ADC_conversion['VOC_RL']  # 10k resistor connected to the VOC sensor (built into the board)

# Resistences at some known conditions. NEED TO BE CALIBRATED
CO_Ro = cfg.Ro['CO_Ro']  
OZ_Ro = cfg.Ro['OZ_Ro']
VOC_Ro = cfg.Ro['VOC_Ro']   # datasheet says this ranges from 100 to 1500 kOhm

# Direct pin control for managing the voltage regulator
GPIO.setmode(GPIO.BCM) # use the GPIO pin numbering scheme
GPIO.setup(4, GPIO.OUT) # set pin 4 as output
GPIO.setup(25, GPIO.OUT) #set pin 25 as output

# ----------------------------------------------------------


# ------------------ Multi-threading Setup -----------------

# Multi-threading for GPS
class GpsPoller(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        global gpsd #bring it in scope
        gpsd = gps(mode=WATCH_ENABLE) #starting the stream of info
        self.current_value = None
        self.running = True #setting the thread running to true

    def run(self):
        global gpsd
        while gpsp.running:
            gpsd.next() #this will continue to loop and grab EACH set of gpsd info to clear the buffer

# Multi-threading for turning sensors on/off when the car is on/off
class PowerMinder(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.running = True
        self.voltage = None
        self.new_voltage = None 
        self.sensor_status = "on"
	global fname
	global self_off_voltage
	global self_on_voltage

    def run(self):
        """
	This will constantly run in the background (definition of a 'thread'). 
	Takes voltage readings from the car battery in a loop, and initiates
	proper shutdown procedure when it senses that the car engine has turned
	off.
        """
	global fname
        while self.running:
	    # Take three independent voltage readings. If all three are below the required level, trigger shutdown.
	    voltage1 = adc.read_adc(Vin_PIN, gain = GAIN) * v_factor
            time.sleep(0.5)
	    voltage2 = adc.read_adc(Vin_PIN, gain = GAIN) * v_factor
	    time.sleep(0.5)
	    voltage3 = adc.read_adc(Vin_PIN, gain = GAIN) * v_factor
	    # Self_off_voltage adjusted for adc conversion.
            if ((voltage1 and voltage2 and voltage3) < cfg.power['self_off_voltage']):
                # car is off, turn sensors off
                print ("a voltage drop has indicated that the car has turned off.")
                if (self.sensor_status == "on"):
                    print ("***turning sensors off***")
                    self.sensor_status = "off"
                    GPIO.output(4,0)  # setting pin 12 low turns the regulator off
		    format_base() # put the list of data points into a list of features (json format)
		    off_state.turnoff()
		    
            elif (self.voltage > cfg.power['self_on_voltage']):
                # car is on, switch regulator on
                if (self.sensor_status == "off"):
                	print ("the battery voltage indicates that the car has turned on")   
                    	print ("***turning sensors on***")
                    	self.sensor_status = "on"
                    	GPIO.output(4,1)
		else:
			self.sensor_status = "on"
			GPIO.output(4, 1)

# ----------------------------------------------------------


# --------------- Functions to take readings ---------------

def ti():
    #print "--> recording Time"
    t = time.localtime()
    current_time = time.strftime("%Y%m%d%H%M%S",t)  # use year, month, day, hour, minute, second format
    return current_time

def temp_hum():
    #print "--> recording Temperature & Humidity"
    sensor = Adafruit_DHT.DHT22
    pin = '17'
    humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)  # read_retry will try multiple times if it can't get a reading
    temperature = temperature *9/5.0 + 32  # convert to F
    t_h = [float("%.1f" % temperature), float("%.1f" % humidity)]  # format to 1 decimal place
    print "temperature = %.2f C" % t_h[0], "humidity = %.2f percent" % t_h[1]
    return t_h

def gps_record():
    #print "--> recording GPS"
    start_time = time.time()
    timeout = 5  # five seconds before we give up
    while True:
        # exit the loop when we get a signal, or after a timeout
        if gpsd.fix.mode == 3:  # we have a fix
            lon = float("%.5f" % gpsd.fix.longitude)
            lat = float("%.5f" % gpsd.fix.latitude)
            return [lon, lat]
	    print "we have a fix. lat = %f" %lat, "lon = %f" %lon
        elif (time.time() - start_time) > timeout:
            print "GPS timeout - no signal"
            return ["none", "none"]

def co():
    #print "--> recording Carbon Monoxide"
    value = adc.read_adc(CO_PIN, gain=GAIN)
    voltage = value * v_factor
    Rs = (Vc/voltage-1)*CO_RL   # internal resistence of the sensor
    ppm = .8*(Rs / CO_Ro)**(-1.8)
    ppm = float("%.4f" % ppm)
    print "CO = %.2f ppm" %ppm
    return ppm

def voc():
    #print "--> recording Volatile Organics"
    value = adc.read_adc(VOC_PIN, gain=GAIN)
    voltage = value * v_factor
    Rs = (Vc/voltage-1)*VOC_RL   # internal resistence of the sensor
    ppm = (15 * (Rs / VOC_Ro)**(-1.5))
    ppm = float("%.4f" % ppm)
    print "Volitile organics = %.2f ppm" %ppm
    return ppm


def ozone():
    
    #print "--> recording Ozone"
    value = adc.read_adc(OZ_PIN, gain=GAIN)
    voltage = value * v_factor
    Rs = (Vc/voltage-1)*OZ_RL   # internal resistence of the sensor
    ppm = (400 * (Rs / OZ_Ro)**(-3))
    ppm = float("%.4f" % ppm)
    print voltage
    print "Ozone = %f ppm" %ppm
    return ppm


def pm():
    reading = pm_module.read_pm()
    print "particulate matter: %.3f mg/m^3" %reading
    return reading

# ------------------------------------------------------------------


# -------------------- Other Functions -------------------------------

def format_base():
    """    
    Puts the list of JSON-formatted data points in the file 'fname' 
    into the base data structure: ("type":"FeatureCollection","features":[]}
    """
    global fname
    global formatted
    formatted = True 
    with open(fname, "r") as f:
	filestring = f.read().replace('\n', '\n    ') # Creates indentation
    filestring = '{\n  "type": "FeatureCollection",\n  "features": [\n    '+filestring+'\n  ]\n}' # meticulously spaced newline characters to ensure proper JSON format. There's probably a better way...
    with open(fname, "w") as f:
	f.write(filestring) # Writes the formatted string back to the file 'fname'
    with open(fname, "r") as f:
	filestring = f.read()
    filestring = filestring[:-12] + filestring[-10:] # Gets rid of the dangling ',\n' characters at the end of the data list
    with open(fname, "w") as f:
	f.write(filestring) #Writes the formatted string back to the file 'fname'

def format_raw_data(time,lon,lat,co,vo,temp,hum,oz,pm):
    """
    Create a nice dictionary object that's ready to be turned into json.
    This only creates one 'feature' of the collection, i.e. an element of the
    'features' list in the base json structure: 
        {"type":"FeatureCollection","features":[]}
    """

    obj = {"type":"Feature","properties":{"time":time,"pm":pm,"co":co,"vo":vo,"oz":oz,"temp":temp,"hum":hum,"time":time},"geometry":{"type":"Point","coordinates":[lon,lat,900]}}
    return obj

def write_data(data, fname):
    """
    Writes the specified dictionary object to a json file, formats it, and puts a comma
    and new line at the end of each data point.
    """
    print("\nWRITING TO FILE")
    with open(fname, 'a') as out:
    	out.write(json.dumps(data, indent=2))
	out.write(",\n")
    print("DONE WRITING\n")

def main():
    global gpsp
    global formatted
    global fname
    gpsp = GpsPoller() # create GPS thread
    p_minder = PowerMinder() # create thread to switch sensors on/off

    try:
        gpsp.start()  # start thread to monitor GPS
        p_minder.start() # start thread to monitor car power

        i=0
        while i<=cfg.main['max_data']:

            if (p_minder.sensor_status == "on"):
                # take recordings
                print "==> Taking Recordings: " + time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
                t = ti()
                g = gps_record()
                c = co()
                v = voc()
                h = temp_hum()
                o = ozone()
                p = pm()

                # add readings to the data object
                entry = format_raw_data(t,g[0],g[1],c,v,h[0],h[1],o,p)
		# Only write to the file if format_base hasn't been called yet. If base has been formatted, this datapoint is not written to the file.
		# This if stipulation is here to fix JSON formatting issues when we write to the file after formatting has been completed.
		if (formatted == False):
		    write_data(entry, fname)
                print "==> Recordings Done\n"

            else:
                print "==> Car Voltage Low - Sensors are Off\n"
		sys.exit(0)

            # wait a while before trying the next reading
            time.sleep(sleep_time)
            i+=1

        # Save to a file
        sys.exit(0)  # actually exit so things shut down properly

    except (KeyboardInterrupt, SystemExit):
        # Stop GPS thread
        gpsp.running = False
        gpsp.join() # wait for the thread to finish what it's doing

        # Stop PowerMinder thread
        gpsp.join() # wait for the thread to finish what it's doing
        p_minder.running = False
        p_minder.join() # wait for the thread to finish what it's doing
	if (formatted == False):
	    format_base() # put the list of data points in a list of featrues (JSON format)
        # relieve GPIO pins of their status
        GPIO.cleanup()

if __name__=="__main__":
    main()  # run the main function by default
