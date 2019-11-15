import time
import Adafruit_ADS1x15

adc = Adafruit_ADS1x15.ADS1115()
GAIN = 1

try:
    while True:
        voltage = adc.read_adc(3, gain=GAIN) * 4.096 / 32767
        print (str(voltage))
except KeyboardInterrupt():
    print ("reading stopped")

    
    
        

