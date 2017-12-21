# Quick and Dirty Linux support for Huion Kamvas GT-220 v2

This is a modified version of [benthor's GT-191 Driver](https://github.com/benthor/HuionKamvasGT191LinuxDriver). It is updated to work correctly with the Huion Kamvas GT-220 v2. 

## Status

 * Device needs to be initialized once per boot using `uclogic-probe`, see [here](https://github.com/benthor/HuionKamvasGT191LinuxDriver/issues/1#issuecomment-351207116)
 * Cursor positioning works
 * Pressure sensitivity works (over all 8191 steps)
 * Stylus buttons work


## Requirements

 * [uclogic-tools](https://github.com/DIGImend/uclogic-tools) while [Issue #1](https://github.com/benthor/HuionKamvasGT191LinuxDriver/issues/1) is still unresolved
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

 * Install dependencies

 * Clone this repository

 * Run `./start-driver.sh` 

Note that it is not necessary to install this driver, just execute with superuser privileges (i.e., as root)

If you have a multi-monitor setup, edit `map-monitor.sh` with the correct values for your setup, and execute it **after** starting the driver.