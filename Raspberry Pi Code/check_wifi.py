import socket
import time

# the server that it attempts to connect to
REMOTE_SERVER = "www.google.com"

def is_connected():
	try:
    		# see if we can resolve the host name -- tells us if there is
    		# a DNS listening
    		host = socket.gethostbyname(REMOTE_SERVER)
    		# connect to the host -- tells us if the host is actually reachable
    		s = socket.create_connection((host, 80), 2)
    		print ("wifi connected")
    		return True

	except:
    		print ("unable to connect to wifi")
    		pass
		return False


