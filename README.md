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

You will likely also need to add the following to your `/etc/X11/xorg.conf`

```
Section "InputClass"
	Identifier "evdev tablet catchall"
	MatchIsTablet "on"
	MatchDevicePath "/dev/input/event*"
	Driver "evdev"
EndSection
```

## Usage

Not necessary to install this driver, just execute with superuser privileges (i.e., as root)

## 

## Known Bugs & Troubleshooting

- Sometimes when replugging the display, the driver stops working until the next reboot


