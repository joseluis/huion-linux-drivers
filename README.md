# Hacky Linux support for Huion Kamvas GT-221 PRO

This is a modified version of [kyledayton's GT-220 v2 Driver](https://github.com/kyledayton/HuionKamvasGT220v2LinuxDriver) (which was a modified version of [benthor's GT-191 Driver](https://github.com/benthor/HuionKamvasGT191LinuxDriver)). It is updated to work correctly with the Huion Kamvas GT-221 PRO.

## Status

 * Cursor positioning works
 * Pressure sensitivity works (over all 8191 steps)
 * Stylus buttons work
 * Multi-monitor works
 * Device needs to be initialized once per boot using `uclogic-probe`, see [here](https://github.com/benthor/HuionKamvasGT191LinuxDriver/issues/1#issuecomment-351207116)


## Usage

 * Install dependencies

 * Clone this repository

 * Run `./start-driver.sh`

 * *(Optionally)* Run `./map-monitor.sh`

_**Note** that it is not necessary to install this driver, just execute with superuser privileges (i.e., as root)_


## Requirements

### Dependencies

 * [uclogic-tools](https://github.com/DIGImend/uclogic-tools) while [Issue #1](https://github.com/benthor/HuionKamvasGT191LinuxDriver/issues/1) is still unresolved


    ```
    # Installation Steps:

    git clone https://github.com/DIGImend/uclogic-tools
    cd uclogic-tools
    ./bootstrap && ./configure --prefix=/usr/local/ && make
    sudo make install
    ```

 * [xinput](https://wiki.archlinux.org/index.php/Xinput) (Archlinux package `xorg-xinput`) (Ubuntu package `xinput`)
 * [evdev](https://wiki.gentoo.org/wiki/Evdev) (Archlinux package `xf86-input-evdev`) (Ubuntu package `xserver-xorg-input-evdev`)
 * [python-evdev](https://github.com/gvalkov/python-evdev) (`pip3 install evdev` or Archlinux package `python-evdev` or Ubuntu package `python3-evdev`)
 * [pyusb](https://walac.github.io/pyusb/) (`pip3 install pyusb` or ArchLinux package `python-pyusb` or Ubuntu package `python3-usb`)


### Xorg Configuration

You will likely also need to add some code to the Xorg server. Create a new file in` /etc/X11/xorg.conf.d/evdev-tablet.conf` with the following content:

```
Section "InputClass"
	Identifier "evdev tablet catchall"
	MatchIsTablet "on"
	MatchDevicePath "/dev/input/event*"
	Driver "evdev"
EndSection
```

### Fix Tablet Pen Name

It is assumed that the name that your system assigns to your tablet pen is `Tablet Monitor Pen`.
In case your system assigns a different name the scripts will fail, so you'll have to fix like this:

1. Firstly run the command `xinput list` with your tablet unplugged.
2. Then plug your tablet's USB cable, and run again the command `xinput list`. Notice the device name of your pen that should have appeared now.
3. Finally edit the `PEN_DEVICE_NAME` variable at the beginning of the scripts `kamvas.py` and `map-monitor.sh` with the correct name.


## Multi-Monitor

If you have a multi-monitor setup, edit `map-monitor.sh` with the correct values for your setup, and execute this script **AFTER** starting the driver.


### Pre-configured Example

The default `map-monitor.sh` script is configured for a specific setup with 3 monitors, with the tablet being the rightmost, like this:

```
   [Left:2560x1440] - [Middle:1920x1080] - [Right:1920x1080](TABLET)
```

**You will have to edit the values at the beginning of the script to match your specific setup:**

```
TOTAL_SCREEN_WIDTH=$((2560 + 1920 + TABLET_WIDTH)) # 6400
TOTAL_SCREEN_HEIGHT=1440

TABLET_OFFSET_X=$((2560 + 1920)) # 4480
TABLET_OFFSET_Y=0
```

This pre-configured setup matches the following [`xrandr`](https://wiki.archlinux.org/index.php/xrandr) script (automatically created with [`arandr`](https://christian.amsuess.com/tools/arandr/))

```
#!/bin/sh
xrandr --output VGA-0 --mode 1920x1080 --pos 4480x0 --rotate normal --output DVI-D-0 --mode 1920x1080 --pos 2560x0 --rotate normal --output HDMI-0 --mode 2560x1440 --pos 0x0 --rotate normal
```

For example, after booting the system you should run the scripts in the following order:

1. Run your xrandr script
2. Run `start-driver.sh`
3. Run `map-monitor.sh`

