import os
import shutil
import time

sourcefile = '/home/pi/traqr/recording/traqr_data_f1_20170711_140432.json'
dstdir = '/home/pi/traqr/archive'

#dstdir = os.path.join(dstroot, os.path.dirname(sourcefile))

# excecute the program to upload the datafile in the current direcrory to the website
def upload():
    global sourcefile
    global dstroot
    try:
        shutil.copy(sourcefile, dstdir) # Copy the datafile to the archive
        print "file copied to archive"
        os.system("./upload_anywhere.sh ~/traqr/recording/traqr_data_*.json") # Upload the data to the website
        os.remove(sourcefile) # Remove the datafile
        print ("***upload successful***")
        return True

    except:
        print ("***unable to upload***")
        return False
