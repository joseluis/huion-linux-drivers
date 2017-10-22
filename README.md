# Quick and Dirty Linux support for Huion Kamvas GT-191

![Huion Kamvas GT-191](https://www.huiontablet.com/media/catalog/product/cache/1/image/9df78eab33525d08d6e5fb8d27136e95/g/t/gt-191.jpg)

## Backstory

In the summer of 2017, I bought a [Huion Kamvas GT-191](https://www.huiontablet.com/all-products/pen-tablet-monitor/kamvas-gt-191.html). It's a device that combines a stylus digitizer tablet with a full HD display. The idea is that you use the stylus to draw right on the screen.

Huion has historically had [pretty decent Linux support](https://docs.krita.org/List_of_Tablets_Supported). It seemed likely that support for this latest manifestation would be added soon. Unfortunately however, the [DIGImend](http://digimend.github.io/) project that has been the primary force behind driver support for touch devices [is in trouble](http://spbnick.github.io/2016/07/31/Wrapping-up-DIGImend-work.html). [Nikolai](https://github.com/spbnick), the lead dev [writes](http://spbnick.github.io/2016/07/31/Wrapping-up-DIGImend-work.html):

> Starting today, I’m stopping all research on specific tablet interfaces and protocols required for implementing drivers. I.e. I’m not going to respond to any diagnostics, or requests to make new tablets work. I’m not going to support users, or investigate their problems either. However, I will still be reviewing and accepting patches, including ones already submitted.

This is sad but also problematic on a larger scale. Free Software is still highly relevant for those with low income. This especially means artists, who may not be able to afford the latest Wacom (which has decent Linux support btw) and who'd prefer to use affordable devices from the Asian competition. If the availability of drivers for current hardware is declining, more artists may remain stuck on proprietary platforms in future. (And the vast majority of photoshop users have never even heard of [Krita](https://krita.org)...)


## Driver

This is a working user space evdev driver for Linux

It is very quick and dirty but it is also *tiny*. Literally just **64 lines of Python**. So you could actually read the entire thing and be sure it does nothing nasty with your machine before executing it with super user privileges.

Cobbled together in an afternoon as a workaround while waiting for activity in [digimend-kernel-drivers#78](https://github.com/DIGImend/digimend-kernel-drivers/issues/78). More than half of the code is borrowed from [dannytaylor's driver](https://github.com/dannytaylor/pinspiroy) for the (much more complicated) [Huion Inspiroy G10T](https://www.huiontablet.com/all-products/graphic-tablets/g10t.html). This code also inherits the former's (MIT) License. 

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

## PS:

In the [blog post](http://spbnick.github.io/2016/07/31/Wrapping-up-DIGImend-work.html) I mentioned above, Nikolai goes on to write:

> I will [...] be available for coaching and support of any able person willing to take my place, as a top priority. Write to me, if you would like to step in, know C well, have experience with kernel and system programming and interest in reverse-engineering USB devices, plus you have the patience to deal with users of widely-varied experience and background.

> Lastly, if anybody wishes to employ me to continue working on DIGImend, I’m open to the offers, and I will gladly continue working on the project, provided I’m appropriately compensated.

Maybe the [Krita Foundation](https://krita.org/en/about/krita-foundation/) could consider supporting the guy? Just a thought.
