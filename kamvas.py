import usb.core
import usb.util
import sys, math
from evdev import UInput, ecodes, AbsInfo
from subprocess import run

# Make sure the device name for the pen is right for your system.
# You can run this command to check it out:
#
#   xinput list
#
PEN_DEVICE_NAME="Tablet Monitor Pen"

PEN_MAX_X = 95352
PEN_MAX_Y = 53645
PEN_MAX_Z = 8191
RESOLUTION = 5080

# pressure sensitive pen tablet area with 2 stylus buttons and no eraser
cap_pen = {
    ecodes.EV_KEY: [ecodes.BTN_TOUCH, ecodes.BTN_TOOL_PEN, ecodes.BTN_STYLUS, ecodes.BTN_STYLUS2],
    ecodes.EV_ABS: [
        (ecodes.ABS_X, AbsInfo(0,0,PEN_MAX_X,0,0,RESOLUTION)), #value, min, max, fuzz, flat, resolution
        (ecodes.ABS_Y, AbsInfo(0,0,PEN_MAX_Y,0,0,RESOLUTION)),
        (ecodes.ABS_PRESSURE, AbsInfo(0,0,PEN_MAX_Z,0,0,0)),
    ]
}

dev = usb.core.find(idVendor=0x256c, idProduct=0x006e)
if not dev:
    print("could not find device, maybe already opened?", file=sys.stderr)
    sys.exit(1)

endpoint = None
for cfg in dev:
    for i in cfg:
        for e in i:
            # print("endpoint", e) # DEBUG
            if not endpoint:
                endpoint = e
        if dev.is_kernel_driver_active(i.index):
            dev.detach_kernel_driver(i.index)
            usb.util.claim_interface(dev, i.index)
            print("grabbed interface %d", i.index)

endpoint = dev[0][(0,0)][0]
vpen = UInput(events=cap_pen, name=PEN_DEVICE_NAME, version=0x3)

def keypress(sequence):
    #p = Popen(['xdotool'], stdin=PIPE)
    #p = Popen(['echo'], stdin=PIPE)
    #p.communicate(input=sequence)
    run("xdotool {}".format(sequence), shell=True, check=True)



print('Huion Kamvas GT-221 PRO driver should now be running')


SCROLL_VAL_PREV=0

while True:
    try:
        data = dev.read(endpoint.bEndpointAddress,endpoint.wMaxPacketSize)
        # print(data) # DEBUG

        TOUCH = data[1] == 129
        PEN_BTN1 = data[1] == 130
        PEN_BTN2 = data[1] == 132
        SCROLLBAR = data[1] == 240
        BUTTONBAR = data[1] == 224

        if BUTTONBAR:
            # get the button value in power of two (1, 2, 4, 16, 32...)
            BUTTON_VAL = (data[5] << 8) + data[4]
            # print("BUTTON_VAL == %s" % BUTTON_VAL) # DEBUG

            if BUTTON_VAL > 0: # 0 means release
                # convert to the exponent (0, 1, 2, 3, 4...)
                BUTTON_VAL = int(math.log(BUTTON_VAL, 2))
                # print("PRESS BUTTON %s" % BUTTON_VAL) # DEBUG


                # SHORTCUTS
                #
                # Use xdotool syntax. E.g.: "key ctrl+shift+f1"

                # Krita keybindings
                BUTTON = {
                    0: "key Tab", # hide toolbars
                    1: "key b",   # brush tool
                    2: "key r",   # pick layer
                    3: "key w",   # wrap around mode
                    4: "key e",   # erase mode

                    5: "key control+z",    # Undo
                    6: "key ctrl+shift+z", # Redo
                    7: "key 4",  # rotate left
                    8: "key 5",  # reset rotate
                    9: 'key 6'   # rotate right
                }

                if BUTTON[BUTTON_VAL] != "":
                    # print("keypress(%s) == %s" % (BUTTON_VAL, BUTTON[BUTTON_VAL])) # DEBUG
                    keypress(BUTTON[BUTTON_VAL])


        elif SCROLLBAR:
            SCROLL_VAL = data[5]
            # print("scrolling VALUE %s" % SCROLL_VAL) # DEBUG

            if SCROLL_VAL > 0: # 0 means release
                if SCROLL_VAL_PREV == 0:
                    SCROLL_VAL_PREV=SCROLL_VAL

                if SCROLL_VAL > SCROLL_VAL_PREV:
                    # keypress("click 4") # mouse wheel up
                    keypress("key ctrl+minus") # zoom out

                elif SCROLL_VAL < SCROLL_VAL_PREV:
                    # keypress("click 5") # mouse wheel down
                    keypress("key ctrl+plus") # zoom in


            SCROLL_VAL_PREV = SCROLL_VAL

        else:
            X = (data[8] << 16) + (data[3] << 8) + data[2]
            Y = (data[5] << 8) + data[4]
            PRESS = (data[7] << 8) + data[6]
            # print("X %6d Y%6d PRESS %4d (%s %s %s))" % (X, Y, PRESS, TOUCH, PEN_BTN1, PEN_BTN2)) # DEBUG

            vpen.write(ecodes.EV_ABS, ecodes.ABS_X, X)
            vpen.write(ecodes.EV_ABS, ecodes.ABS_Y, Y)
            vpen.write(ecodes.EV_ABS, ecodes.ABS_PRESSURE, PRESS)
            vpen.write(ecodes.EV_KEY, ecodes.BTN_TOUCH, TOUCH and 1 or 0)
            vpen.write(ecodes.EV_KEY, ecodes.BTN_STYLUS, PEN_BTN1 and 1 or 0)
            vpen.write(ecodes.EV_KEY, ecodes.BTN_STYLUS2, PEN_BTN2 and 1 or 0)
            vpen.syn()

    except usb.core.USBError as e:
        data = None
        if e.args == ('Operation timed out',):
            print(e, file=sys.stderr)
            continue

