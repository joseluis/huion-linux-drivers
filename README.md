# User Space Linux Drivers for Huion (Kamvas) Tablets

## Supported Features

 * Multiple Models (Kamvas GT-191, GT-220-v2, GT-221-PRO…)
 * Screen Monitor
 * Cursor Positioning
 * Pressure Sensitivity
 * Stylus Buttons
 * Tablet Buttons 
 * Scroll bar
 * Multi-Monitor Setup


## Usage

 * Install the dependencies.
 * Clone or download this repository (You only need `huion-tablet-driver.py` and `config.ini` files).
 * Edit `config.ini` to match your tablet, multi-monitor setup and desired shortcuts.
 * Run `./huion-tablet-driver.py` with **superuser** privileges (e.g. as root or with sudo).


## Requirements

### Dependencies

 * [python](https://www.python.org/) version 3.5 or greater
 * [uclogic-tools](https://github.com/DIGImend/uclogic-tools) ([read why](https://github.com/benthor/HuionKamvasGT191LinuxDriver/issues/1#issuecomment-351207116))

    ```
    # Installation Steps:

    git clone https://github.com/DIGImend/uclogic-tools
    cd uclogic-tools
    ./bootstrap && ./configure --prefix=/usr/local/ && make
    sudo make install
    ```

 * [xinput](https://wiki.archlinux.org/index.php/Xinput)
 * [evdev](https://wiki.gentoo.org/wiki/Evdev)
 * [python-evdev](https://github.com/gvalkov/python-evdev)
 * [pyusb](https://walac.github.io/pyusb/)
 * [xdotool](http://www.semicomplete.com/projects/xdotool/) (optional for button shorcuts)
 * [notify-send](https://wiki.archlinux.org/index.php/Desktop_notifications) (optional for desktop notifications)


Install packages in Archlinux:

```
$  pacman -S xorg-xinput xf86-input-evdev python-evdev python-pyusb xdotool libnotify
```

Install packages in Ubuntu:
```
$ sudo apt install xinput xserver-xorg-input-evdev python3-evdev python3-usb xdotool libnotify-bin
```


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

## Multi-Monitor

If you have a multi-monitor setup, edit `config.ini` with the correct values for your setup.

```
# Multi Monitor Configuration

enable_multi_monitor = true
total_screen_width  = 2560 + 1920 + ${tablet_width}
total_screen_height = 1440
tablet_offset_x     = 2560 + 1920
tablet_offset_y     = 0
```

The default example is configured for a specific setup with 3 monitors, with the tablet being the rightmost, like this:
```
   [Left:2560x1440] - [Middle:1920x1080] - [Right:1920x1080](TABLET)
```

Matching the following example [`xrandr`](https://wiki.archlinux.org/index.php/xrandr) script (automatically created with [`arandr`](https://christian.amsuess.com/tools/arandr/))

```
#!/bin/sh
xrandr --output VGA-0 --mode 1920x1080 --pos 4480x0 --rotate normal --output DVI-D-0 --mode 1920x1080 --pos 2560x0 --rotate normal --output HDMI-0 --mode 2560x1440 --pos 0x0 --rotate normal
```

## Buttons Shortcuts

To customize the shortcuts associated with the buttons, edit the file `config.ini`, and use the xdotool syntax for the buttons actions.

First, assign the menu you're going to use as the starting menu.


### Example with a Single Buttons Menu

```
start_menu = [menu_simple]

[menu_simple]
b0 = key Tab           # hide interface
b1 = key r             # rect select (gimp) & pick layer (krita)
b2 = key ctrl+x        # cut
b3 = key ctrl+c        # copy
b4 = key ctrl+v        # paste
#
b5 = key ctrl+z        # undo
b6 = key ctrl+y        # redo (gimp)
b7 = key ctrl+shift+z  # redo (krita)
b8 = key 4             # turn left (krita)
b9 = key 6             # turn right (krita)
```

### Example with Multiple Buttons Menus

```
start_menu = [menu_main]

[menu_main]
title = % Main Menu %
b0 = [menu_krita]
b1 = [menu_gimp]
b2 = key ctrl+s        # save
b3 = key ctrl+o        # open
b4 = key ctrl+w        # close
#
b5 = ctrl+x            # cut
b6 = ctrl+c            # copy
b7 = ctrl+v            # paste
b8 = key Return
b9 = key Escape

[menu_krita]
title = % Krita %
b0 = key Tab           # hide interface
b1 = key b             # draw tool
b2 = key r             # pick layer
b3 = key w             # wrap mode
b4 = key e             # erase mode
#
b5 = key ctrl+z        # redo
b6 = key ctrl+shift+z  # undo
b7 = key 4             # turn left
b8 = key 6             # turn right
i9 = [menu_main]


[menu_gimp]
title = % Gimp %
b0 = key Tab           # hide interface
b1 = key p             # paintbrush
b2 = key r             # rect select
b3 = key c             # clone
b4 = key shift+e       # eraser
#
b5 = key ctrl+z        # undo
b6 = key ctrl+y        # redo
b7 = key x             # swap colors
b8 = key shift+r       # rotate
b9 = [menu_main]
```


