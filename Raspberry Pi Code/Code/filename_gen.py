import time

def serial_no():
  # Extract pi's serial number from cpuinfo file
    cpuserial = "0000000000000000"
    try:
      f = open('/proc/cpuinfo','r')
      for line in f:
        if line[0:6]=='Serial':
          cpuserial = line[10:26]
      f.close()
    except:
      cpuserial = "ERROR000000000"

    return str(cpuserial[-2:])

def date():
# Get the date and time into a recognizable format
    raw_date = time.localtime()
    current_time = time.strftime("%Y%m%d%H%M%S", raw_date)
    return str(current_time)

#def status():
    
def main():
    sn = serial_no()
    date_string = date()
    filename = "traqr_data_" + sn + "_" + date_string[0:8] + "_" + date_string[8:] + ".json"
  
    return filename 
  
