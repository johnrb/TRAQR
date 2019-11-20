#!/bin/bash

##
#
# Push the most recent changes in ./jekyll/_site/ up to the live site at
# http://people.goshen.edu/~stu_phys/traqr/
#
##

port=1235   # port to use for ssh tunnel

src="_site/*"
dest="stu_phys@127.0.0.1:mypages/traqr/"

# Check to make sure
echo "Uploading all content at $PWD/$src to the live site at http://people.goshen.edu/~stu_phys/traqr"
read -p "Are you sure? [y/N] " -r
echo    # (optional) move to a new line
if [[ $REPLY =~ ^[Yy]$ ]]
then
    # do the uploading

	echo "==> establishing ssh tunnel"
	# Establish ssh tunnel
	ssh -nNT -L $port:people.goshen.edu:22 vjkurtz@maxx.goshen.edu &
	PID=$!
    sleep 2  # wait for tunnel to initialize
	echo "tunnel PID is $PID"

	echo "==> Copying $src to $dest"
    scp -r -P $port $src $dest
    echo "==> done copying"

    echo "==> closing tunnel"
	# Close our ssh tunnel
	kill $PID
	trap "kill $PID" 1 2 15

    echo "==> tunnel closed"
fi
