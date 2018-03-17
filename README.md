# User Space Linux Drivers for Huion Tablets

## Features

 * Supports multiple models, including Kamvas
 * Compatible with multi-monitor setups
 * Precise cursor positioning
 * Full pressure sensitivity
 * Both stylus buttons
 * Customizable buttons and scrollbar shortcuts
 * Multiple sets of shortcuts
 * Easy configuration file


## Usage

 * Follow the requirements: Install the dependencies and the xorg extra code.
 * Download this repository (You only need `huion-tablet-driver.py` and `config.ini`).
 * Edit `config.ini` to match your tablet, multi-monitor setup and desired shortcuts.
 * Run `sudo ./huion-tablet-driver.py` (needs superuser privileges)


## Requirements

### Dependencies

 * [python](https://www.python.org/) version 3.5 or greater
 * [uclogic-tools](https://github.com/DIGImend/uclogic-tools) ([read why][2])

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
 * [xdotool][7] (optional, for button shorcuts)
 * [notify-send][8] (optional, for desktop notifications)

[2]: https://github.com/benthor/HuionKamvasGT191LinuxDriver/issues/1#issuecomment-351207116
[7]: http://www.semicomplete.com/projects/xdotool/
[8]: https://wiki.archlinux.org/index.php/Desktop_notifications


Install packages in Archlinux:

```
$  pacman -S xorg-xinput xf86-input-evdev python-evdev python-pyusb xdotool libnotify
```

Install packages in Ubuntu:
```
$ sudo apt install xinput xserver-xorg-input-evdev python3-evdev python3-usb xdotool libnotify-bin
```

### Xorg Extra Code

You will likely also need to add some code to the Xorg server.
Create a new file in` /etc/X11/xorg.conf.d/evdev-tablet.conf` with the following content:

```
Section "InputClass"
	Identifier "evdev tablet catchall"
	MatchIsTablet "on"
	MatchDevicePath "/dev/input/event*"
	Driver "evdev"
EndSection
```

## Multi-Monitor

If you have a multi-monitor setup, edit your copy of `config.ini`
with the correct values for your particular setup. Like this:

```
# Multi Monitor Configuration

enable_multi_monitor = true
total_screen_width  = 2560 + 1920 + 1920
total_screen_height = 1440
tablet_offset_x     = 2560 + 1920
tablet_offset_y     = 0
```

[More information about multiple monitors in the wiki](https://github.com/joseluis/huion-linux-drivers/wiki/Multi-Monitor)


## Shortcuts

To customize the shortcuts associated with the buttons and the scrollbar,
edit the file `config.ini`, and use the xdotool syntax for the buttons actions.

First, assign the menu you're going to use as the starting menu.

### Example with a Single Buttons Menu

```
start_menu = [menu_simple]

[menu_simple]

# upper buttons
b0 = key Tab           # hide interface
b1 = key r             # rect select (gimp) & pick layer (krita)
b2 = key ctrl+x        # cut
b3 = key ctrl+c        # copy
b4 = key ctrl+v        # paste

# scrollbar
su = click 4           # mouse wheel up
sd = click 5           # mouse wheel down

# lower buttons
b5 = key ctrl+z        # undo
b6 = key ctrl+y        # redo (gimp)
b7 = key ctrl+shift+z  # redo (krita)
b8 = key 4             # turn left (krita)
b9 = key 6             # turn right (krita)
```

[See an example with multiple menus in the wiki](https://github.com/joseluis/huion-linux-drivers/wiki/Buttons-Shortcuts#12-example-with-multiple-menus)


## Supporting More Models

Current supported models are: `H950P`, `GT-191`, `GT-220 v2` and `GT-221 PRO`.

If you have access to a different Huion model, please open a new issue,
pasting the console output after executing the driver.

