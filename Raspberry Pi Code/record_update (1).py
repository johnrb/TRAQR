#!/usr/bin/env python2

##
#
# General framework script for recording data. Triggers data collection
# on all of the sensors every 5 minutes or so. 
#
# TODO:
#
# We'll have to determinte how often to write data to a file.
#
# Future work should be done to see if we can turn some sensors off in the
# intermediate sleeping time, when no measurments are being taken. 
#
##

import time
import json
from gps import *
import Adafruit_DHT  # for temp/humidity
import Adafruit_ADS1x15  # analog-digital converter
import threading
import sys
import RPi.GPIO as GPIO  # for managing regulator
import upload
import check_wifi
import os
import led



# -----------------  Global Variables ----------------------

sleep_time = 10   # time to wait between readings (in seconds)
    
gpsd = None  # GPS daemon
gpsp = None  # GPS poller object

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
        self.sensor_status = "off"

    def run(self):
        while self.running:
            self.voltage = adc.read_adc(3, gain=GAIN) * 4.096 / 32767
            time.sleep(1)
            self.new_voltage = adc.read_adc(3, gain=GAIN) * 4.096 / 32767
            time.sleep(1)
            v_change = (self.new_voltage - self.voltage)
            
            if (v_change < -0.10): # adjusted for adc conversion. the *real* change we are looking for is +-0.5V 
                # car is off, turn sensors off
                print ("a voltage drop has indicated that the car has turned off. voltage drop: " + str(abs(v_change)) + "V")
                if (self.sensor_status == "on"):
                    print ("***turning sensors off***")
                    self.sensor_status = "off"
                    GPIO.output(4,0)  # setting pin 12 low turns the regulator off
                    if (check_wifi.is_connected()):
			led.wifi_success()
                        if (upload.upload()):
			    led.uplaod_success()
                            print ("***powering off...***")
			    led.poweroff()
                            os.system("sudo shutdown -h now")
                        else:
			    led.upload_failure()
                            print ("***powering off...***")
                            os.system("sudo shutdown -h now")
                    else:
                        print("***powering off...***")
                        os.system("sudo shutdown -h now")
                            
            elif (self.voltage > 1.0):
                # car is on, switch regulator on
                if (self.sensor_status == "off"):
                	print ("the battery voltage indicates that the car has turned on")   
                    	print ("***turning sensors on***")
                    	self.sensor_status = "on"
                    	GPIO.output(4,1)

            # if neither of the if/elif conditions are satisfied, then the pi continues to read the voltage from the adc every second, and record.py carries on

# ----------------------------------------------------------


# --------------- Functions to take readings ---------------

def ti():
    #print "--> recording Time"
    t = time.localtime()
    return time.strftime("%Y%m%d%H%M%S",t)  # use year, month, day, hour, minute, second format

def temp_hum():
    #print "--> recording Temperature & Humidity"
    sensor = Adafruit_DHT.DHT22
    pin = '17'
    humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)  # read_retry will try multiple times if it can't get a reading
    temperature = temperature *9/5.0 + 32  # convert to F
    t_h = [float("%.1f" % temperature), float("%.1f" % humidity)]  # format to 1 decimal place
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
	    print "we have a fix"
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
    return ppm

def voc():
    #print "--> recording Volatile Organics"
    value = adc.read_adc(VOC_PIN, gain=GAIN)
    voltage = value * v_factor
    Rs = (Vc/voltage-1)*VOC_RL   # internal resistence of the sensor
    ppm = 15 * (Rs / VOC_Ro)**(-1.5)
    ppm = float("%.4f" % ppm)
    return ppm


def ozone():
    """
    #print "--> recording Ozone"
    value = adc.read_adc(OZ_PIN, gain=GAIN)
    voltage = value * v_factor
    Rs = (Vc/voltage-1)*OZ_RL   # internal resistence of the sensor
    ppm = 400 * (Rs / OZ_Ro)**(-3)
    ppm = float("%.4f" % ppm)
    return ppm
    """
    return "none"

def pm():
    #print "--> recording Particulate Matter"
    return "none"

# ------------------------------------------------------------------


# -------------------- Other Functions -------------------------------

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
    Writes the specified dictionary object to a json file
    """
    print("\nWRITING TO FILE")
    with open(fname, 'w') as out:
    	out.write(json.dumps(data, indent=2))
    print("DONE WRITING\n")

def main():
    global gpsp
    gpsp = GpsPoller() # create GPS thread
    p_minder = PowerMinder() # create thread to switch sensors on/off

    try:
        gpsp.start()  # start thread to monitor GPS
        p_minder.start() # start thread to monitor car power

        base = {"type":"FeatureCollection","features":[]}  # initialize the data object

        i=0
        while i<10:

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
                base["features"].append(entry)
                print "==> Recordings Done\n"

            else:
                print "==> Car Voltage Low - Sensors are Off\n"

            # wait a while before trying the next reading
            time.sleep(sleep_time)
            i+=1

        # Save to a file
        write_data(base, "traqr_data_%s.json" % int(time.time()))  # use a unique file name
        sys.exit(0)  # actually exit so things shut down properly

    except (KeyboardInterrupt, SystemExit):
        # Stop GPS thread
        gpsp.running = False
        gpsp.join() # wait for the thread to finish what it's doing

        # Stop PowerMinder thread
        gpsp.join() # wait for the thread to finish what it's doing
        p_minder.running = False
        p_minder.join() # wait for the thread to finish what it's doing

        # relieve GPIO pins of their status
        GPIO.cleanup()

if __name__=="__main__":
    main()  # run the main function by default
