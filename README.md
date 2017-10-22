# Quick and Dirty Linux support for Huion Kamvas GT-191
This is a very quick and dirty but working user space evdev driver for Huion Kamvas GT-191 for Linux.

Cobbled together in Python as a workaround while waiting for [digimend-kernel-drivers#78](https://github.com/DIGImend/digimend-kernel-drivers/issues/78) to be closed. 50% of the code is borrowed from [dannytaylor's driver](https://github.com/dannytaylor/pinspiroy) for the Huion Inspiroy G10T. Consequently, this code inherits the former's (MIT) License.

## Status

 * Cursor positioning works
 * Pressure sensitivity works (over all 8191 steps)
 * Stylus buttons work


## Requirements

 * [pyusb](https://walac.github.io/pyusb/) (`pip install pyusb` or ArchLinux package `python-pyusb`)
 * [python-evdev](https://github.com/gvalkov/python-evdev) (`pip install evdev` or Archlinux package `python-evdev`)
 * xf86-input-evdev (Archlinux package `xf86-input-evdev`)

You will likely also need to add the following to your `/etc/X11/xorg.conf` (create the file if it's not already present):

```
Section "InputClass"
	Identifier "evdev tablet catchall"
	MatchIsTablet "on"
	MatchDevicePath "/dev/input/event*"
	Driver "evdev"
EndSection
```

## Usage

 * Just checkout (clone) this repository into some directory of your choice.

 * Make sure the DIGImend kernel drivers are unloaded by running `sudo rmmod hid-uclogic`.

 * Then run `sudo python3 kamvas.py` 
 
The stylus should now be moving the cursor on screen and the python process should report a lot of cursor events. 
If the cursor doesn't move, check out the "Known Bugs & Troubleshooting" section below

Note that it is not necessary to install this driver, just execute with superuser privileges (i.e., as root)

## Known Bugs & Troubleshooting

### Unresponsive cursor

In case of unresponsive cursor, look for error messages begining with `kamvas-pen` in /var/log/Xorg.0.log. Errors may indicate that you need to create and populate your `/etc/X11/xorg.conf` (see above)

You should still see driver messages for each cursor event. If the touch of the stylus against the screen surface does not produce an event, you have a bigger problem. In this case, go [here](http://digimend.github.io/support/howto/trbl/diagnostics/) and follow the steps.

### Other problems

- The driver is a bit laggy in default mode because every event is printed. Simply edit the code and comment-out or delete the line that says `print("X %6d Y%6d PRESS %4d (%s %s %s))" % (X, Y, PRESS, TOUCH, BTN1, BTN2))`
- If you want to use your Kamvas GT-191 as a secondary display, you will have to constrain the stylus input to the screen area keep stylus input and mouse pointer in sync. See `scripts/offsettest.sh` for an example (developed from [this page](https://wiki.archlinux.org/index.php/Calibrating_Touchscreen) in the ArchWiki) that works in a screen arrangement where the Kamvas is sitting next to a 1440p display.
- Sometimes when replugging the display, the driver stops working until the next reboot. The reasons for this are unknown.

