import time
import RPi.GPIO as GPIO
import ctypes
from ctypes import cdll

#-----------------import wiringPi stuff and c code---------------#
wpi = cdll.LoadLibrary('/home/pi/traqr/wiringPi/wiringPi/libwiringPi.so.2.44') # Library for SPI reading
adc = cdll.LoadLibrary('/home/pi/traqr/adc_comm.so') # C program that actually does the reading
#----------------------------------------------------------------#
GPIO.setmode(GPIO.BCM)
GPIO.setup(25, GPIO.OUT)

#adc.init_spi() #designates the CS channel and transfer speed

def read_pm():
	adc.init_spi()
	elapsed = 10000
	cycle_delay_us = 300
	tolerance = 20
	i = 0

	while (i <= 100): # keep attempting transfers until the transfer time is short enough
	#print elapsed
		start = time.clock()
		GPIO.output(25,1)
		time.sleep(cycle_delay_us/(10**6))
		response = adc.transfer()# take reading with c code
		GPIO.output(25,0)
		stop = time.clock()
		elapsed = stop - start
		i+=1
		if (elapsed*(10**6) < (cycle_delay_us+tolerance)):
			response = float(response/1726.0)
			return response
			break
	if (i >=100):
		print "pm read error"
		return 999

def main():
	#adc.init_spi()
	while True:
		response = read_pm()
		time.sleep(0.3)
		print response
GPIO.cleanup()
