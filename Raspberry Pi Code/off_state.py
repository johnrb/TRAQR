# program with functions that can be called when the pi is turning off

import time
import os
import sys
import upload
import check_wifi
import beeper
import led

def turnoff():
#Runs shutoff procedures: checks for wifi, and if there's a connection, 
#uploads the data and powers off. If there's no wifi connection or if the
#data upload is unsuccessful for whatever reason, it still shuts off,
#but the data is stored for later upload.
    if (check_wifi.is_connected()):	
        led.wifi_success()
	if (upload.upload()):
            led.upload_success()
	    print ("***powering off...***""")
	    led.poweroff()
	    os.system("sudo shutdown -h now")
	else:
	    led.upload_failure()
	    print ("***powering off...***")
	    os.system("sudo shutdown -h now")
    else:
	print("***powering off...***")  
	os.system("sudo shutdown -h now")	    
			
	
