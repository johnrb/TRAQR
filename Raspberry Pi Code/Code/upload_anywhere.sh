#!/bin/bash

##
# Use scp to copy a given data file to the people server. Uses an ssh tunnel
# through maxx.goshen.edu so that the file upload can be done from anywhere.
#
# Requires:
#   - ssh keys for vjkurtz@maxx.goshen.edu installed. 
#   - the script upload_anywhere.exp
#   - /usr/bin/expect
#
# Things that would make this easier/better: 
#      - using another maxx.goshen.edu account: mine (vjkurtz) might expire at some point
#      - using ftp instead of scp (ftp server needs installed on people)
#      - using ssh keys instead of manually inserting password (ssh keys not allowed on people)
#
##

datafile=$1
port=22   # port to use for ssh tunnel

# Check args
if [[ -z $datafile ]];
then
    echo "Specify a file"
    exit 1;
fi

fname=$(basename $datafile)
dest="stu_phys@people.goshen.edu:~/mypages/traqr/datafiles/$fname"

# Establish ssh tunnel
#ssh -nNT -L $port:people.goshen.edu:22 vjkurtz@maxx.goshen.edu &
#PID=$!

echo "Copying $datafile to $dest"
#echo $PID

sleep 2  # make sure the tunnel is properly initialized

# Use this expect script to enter password
./upload_anywhere.exp $datafile $dest $port

sleep 1

# Close our ssh tunnel
#kill $PID
#trap "kill $PID" 1 2 15
