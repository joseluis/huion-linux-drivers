# Hacky Linux support for Huion Kamvas Tablets

## Status

 * Tested with Huion Kamvas GT-191, GT-220-v2 and GT-221-PRO
 * Cursor positioning works
 * Pressure sensitivity works
 * Stylus buttons work
 * Tablet Buttons and scroll bar works
 * Multi-monitor works
 * Depends on `uclogic-probe` for now, see [here](https://github.com/benthor/HuionKamvasGT191LinuxDriver/issues/1#issuecomment-351207116)


## Usage

 * Install dependencies
 * Clone this repository
 * Run `./kamvas-linux-driver.py`

_**Note** that it is not necessary to install this driver, just execute with superuser privileges (i.e., as root)_


## Requirements

### Dependencies

 * [python](https://www.python.org/) version 3.5 or greater
 * [uclogic-tools](https://github.com/DIGImend/uclogic-tools)

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
 * [xdotool](http://www.semicomplete.com/projects/xdotool/) (optional for )
 * [notify-send](https://wiki.archlinux.org/index.php/Desktop_notifications) (optional for Desktop notifications)


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


### Example with Single Menu

```
start_menu = [menu_simple]

[menu_simple]
b0 =
b1 =
b2 =
b3 =
b4 =
b5 =
b6 =
b7 =
b8 =
b9 =
```

### Example with Multiple Menus

```
start_menu = [menu_main]

[menu_main]
title = %% Main Menu %%
b0 = [menu_krita]
b1 = [menu_gimp]
b2 =
b3 =
b4 =
#
b5 =
b6 =
b7 =
b8 = key Return
b9 = key Escape

[menu_krita]
title = %% Krita %%
b0 = [menu_krita_draw]
b1 = [menu_krita_edit]
b2 =
b3 =
b4 =
#
b5 =
b6 =
b7 =
b8 = key Tab
i9 = [menu_main]


[menu_gimp]
title = %% Gimp %%
b0 = [menu_krita_draw]
b1 = [menu_krita_edit]
b2 =
b3 =
b4 =
#
b5 =
b6 =
b7 =
b8 = key Tab
b9 = [menu_main]
```


