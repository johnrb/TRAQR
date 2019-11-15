import time
import RPi.GPIO as GPIO
import ctypes
from ctypes import cdll

#-----------------import wiringPi stuff and c code---------------#
wpi = cdll.LoadLibrary('/home/pi/traqr/wiringPi/wiringPi/libwiringPi.so.2.44') # c program that reads from the second adc using SPI
adc = cdll.LoadLibrary('/home/pi/traqr/adc_comm.so')
#----------------------------------------------------------------#
GPIO.setmode(GPIO.BCM)
GPIO.setup(25, GPIO.OUT)

adc.init_spi()

def read_pm():
	cycle_delay_us = 300
	tolerance = 20
	elapsed = 10000
	i = 0
	while (elapsed > cycle_delay_us + tolerance):
		start = time.clock()
		GPIO.output(25,1)
		time.sleep(cycle_delay_us/(10**6))
		response = adc.transfer()# take reading somehow with c code
		GPIO.output(25,0)
		stop = time.clock()
		elapsed = stop - start
		i += 1
		if (i>20):
			print "pm read error"
			break
	return response

def main():
	while True:
		time.sleep(0.3)
		response = read_pm()
		print response

main()
GPIO.cleanup()
