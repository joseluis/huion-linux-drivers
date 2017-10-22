# Quick and Dirty Linux support for Huion Kamvas GT-191
This is a very quick and dirty but working user space evdev driver for Huion Kamvas GT-191 for Linux.

Cobbled together in Python as a workaround while waiting for DIGImend/digimend-kernel-drivers#78 to be closed. 50% of the code is borrowed from [dannytaylor's driver](dannytaylor/pinspiroy) for the Huion Inspiroy G10T. Consequently, this code inherits the former's (MIT) License.

## Requirements

 * pyusb (pip install pyusb)
 * python-evdev (pip install evdev)
 * xf86-input-evdev


## Usage

Not necessary to install this driver, just execute with superuser privileges (i.e., as root)

## 

## Known Bugs & Troubleshooting

- Sometimes when replugging the display, the driver stops working until the next reboot

- 

