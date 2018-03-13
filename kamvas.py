#!/usr/bin/env python3

import usb.core
import usb.util
import sys, math
from evdev import UInput, ecodes, AbsInfo
from subprocess import run
import configparser


class main():
    settings = {}
    dev = None
    endpoint = None

    def run():
        read_config()
        setup_driver()
        main_loop()


def setup_driver():
    # pressure sensitive pen tablet area with 2 stylus buttons and no eraser
    cap_pen = {
        ecodes.EV_KEY: [ecodes.BTN_TOUCH, ecodes.BTN_TOOL_PEN, ecodes.BTN_STYLUS, ecodes.BTN_STYLUS2],
        ecodes.EV_ABS: [
            (ecodes.ABS_X, AbsInfo(0,0,main.settings['PEN_MAX_X'],0,0,main.settings['RESOLUTION'])), # value, min, max, fuzz, flat, resolution
            (ecodes.ABS_Y, AbsInfo(0,0,main.settings['PEN_MAX_Y'],0,0,main.settings['RESOLUTION'])),
            (ecodes.ABS_PRESSURE, AbsInfo(0,0,main.settings['PEN_MAX_Z'],0,0,0)),
        ]
    }

    main.dev = usb.core.find(idVendor=0x256c, idProduct=0x006e)
    if not main.dev:
        print("could not find device, maybe already opened?", file=sys.stderr)
        sys.exit(1)

    for cfg in main.dev:
        for i in cfg:
            for e in i:
                if not main.endpoint:
                    main.endpoint = e
            if main.dev.is_kernel_driver_active(i.index):
                main.dev.detach_kernel_driver(i.index)
                usb.util.claim_interface(main.dev, i.index)
                print("grabbed interface %d", i.index)

    main.endpoint = main.dev[0][(0,0)][0]
    vpen = UInput(events=cap_pen, name='PEN_DEVICE_NAME', version=0x3)

    print('Huion Kamvas GT-221 PRO driver should now be running')


# -----------------------------------------------------------------------------
def main_loop():
    SCROLL_VAL_PREV=0
    while True:
        try:
            data = main.dev.read(main.endpoint.bEndpointAddress, main.endpoint.wMaxPacketSize)
            # print(data) # DEBUG

            TOUCH = data[1] == 129
            PEN_BTN1 = data[1] == 130
            PEN_BTN2 = data[1] == 132
            SCROLLBAR = data[1] == 240
            BUTTONBAR = data[1] == 224

            if BUTTONBAR:
                # get the button value in power of two (1, 2, 4, 16, 32...)
                BUTTON_VAL = (data[5] << 8) + data[4]

                if BUTTON_VAL > 0: # 0 means release
                    # convert to the exponent (0, 1, 2, 3, 4...)
                    BUTTON_VAL = int(math.log(BUTTON_VAL, 2))

                    # SHORTCUTS TODO: read from config
                    BUTTON = {
                        0: "key Tab", # hide toolbars
                        1: "key b",   # brush tool
                        2: "key r",   # pick layer
                        3: "key w",   # wrap around mode
                        4: "key e",   # erase mode

                        5: "key control+z",    # Undo
                        6: "key ctrl+shift+z", # Redo
                        7: "key 4",  # rotate left
                        9: 'key 5',   # rotate right
                        8: "key 6",  # reset rotate
                    }

                    if BUTTON[BUTTON_VAL] != "":
                        # print("keypress(%s) == %s" % (BUTTON_VAL, BUTTON[BUTTON_VAL]))
                        keypress(BUTTON[BUTTON_VAL])


            elif SCROLLBAR:
                SCROLL_VAL = data[5]

                if SCROLL_VAL > 0: # 0 means release
                    if SCROLL_VAL_PREV == 0:
                        # print("Scrolling...")
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


# -----------------------------------------------------------------------------
def keypress(sequence):
    run("xdotool {}".format(sequence), shell=True, check=True)


# -----------------------------------------------------------------------------
def read_config():
    config = configparser.ConfigParser()
    config.read('config.ini')

    main.settings['PEN_DEVICE_NAME'] = config.get('config', 'PEN_DEVICE_NAME')
    main.settings['PEN_MAX_X'] = int(config.get('config', 'PEN_MAX_X'))
    main.settings['PEN_MAX_Y'] = int(config.get('config', 'PEN_MAX_Y'))
    main.settings['PEN_MAX_Z'] = int(config.get('config', 'PEN_MAX_Z'))
    main.settings['RESOLUTION'] = int(config.get('config', 'RESOLUTION'))

    


# -----------------------------------------------------------------------------
if __name__ == '__main__':
        main.run()
