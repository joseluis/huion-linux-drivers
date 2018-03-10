#!/usr/bin/env bash

# Adjust these as needed
DRIVER="kamvas.py"
UCLOGIC_BINS="/usr/local/bin/"


T="256c:006e"
BUS=$(lsusb | grep "$T" | sed -e 's|Bus \([0-9]*\) Device \([0-9]*\):.*$|\1|g')
DEV=$(lsusb | grep "$T" | sed -e 's|Bus \([0-9]*\) Device \([0-9]*\):.*$|\2|g')


MODULE_OLD=hid_uclogic
MODULE_NEW=uinput

if lsmod | grep "$MODULE_OLD" &> /dev/null ; then
	sudo rmmod "$MODULE_OLD"
fi

if lsmod | grep "$MODULE_NEW" &> /dev/null ; then
	sudo rmmod "$MODULE_NEW"
fi
sudo modprobe "$MODULE_NEW"


sudo "$UCLOGIC_BINS/uclogic-probe" "$BUS" "$DEV" | "$UCLOGIC_BINS/uclogic-decode"

sudo python3 "$DRIVER"
