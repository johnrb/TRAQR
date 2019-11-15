
# the code for when you want an LED to blink with various styles--all in one place!

import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# pin numbers for different LED colors
blue = 27
red = 18
green = 22  

# set LED pins to output
GPIO.setup(blue, GPIO.OUT)	
GPIO.setup(red, GPIO.OUT)
GPIO.setup(green, GPIO.OUT)

GPIO.output(blue, 0)
GPIO.output(red, 0)
GPIO.output(green, 0)

# LED blink/color functions for different situations

def high_concentration():
	GPIO.setup([red, green, blue], GPIO.OUT)
	i = 0
	while i < 10:
		GPIO.output([red, green, blue],1)
		time.sleep(0.25)
		GPIO.output([red, green, blue],0)
		time.sleep(0.25)
	time.sleep(5)
	

def wifi_success():
	GPIO.setup(green,GPIO.OUT)
	GPIO.output(green, 1)
	time.sleep(5)
	GPIO.output(green, 0)
	time.sleep(2)

def upload_success():
	GPIO.setup(blue, GPIO.OUT)
	i = 0
	while i < 4:
		GPIO.output(blue, 1)
		time.sleep(.4)
		GPIO.output(blue, 0)
		time.sleep(.4)
		i += 1

def upload_failure():
	GPIO.setup(blue, GPIO.OUT)
	i = 0
	while i < 50:
		GPIO.output(blue, 1)
		time.sleep(0.05)
		GPIO.output(blue, 0)
		time.sleep(0.05)
		i += 1

def poweroff():
	GPIO.setup(red, GPIO.OUT)
	i = 0
	while i < 3:
		GPIO.output(red, 1)
		time.sleep(1)
		GPIO.output(red, 0)
		time.sleep(1)
		i += 1
	GPIO.output(red, 1)
	time.sleep(3)
	GPIO.output(red, 0)

GPIO.cleanup()
