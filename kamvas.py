#!/usr/bin/env python3

import usb.core, usb.util
import sys
from evdev import UInput, ecodes, AbsInfo
from subprocess import run, PIPE
import math, ast
from configparser import ConfigParser, ExtendedInterpolation
from time import gmtime, strftime

MENU = {}


# -----------------------------------------------------------------------------
class main():
    settings = {'pen_device_name':'Tablet Monitor Pen'
        + strftime(" %H%M%S", gmtime())}
    dev = None
    endpoint = None
    vpen = None
    current_menu = None

    def run():
        find_usb_device()
        read_config()
        prepare_driver()
        setup_driver()
        multi_monitor()
        main_loop()


# -----------------------------------------------------------------------------
def find_usb_device():
    sys.stdout.write("Finding USB device . . . ")

    main.dev = usb.core.find(idVendor=0x256c, idProduct=0x006e)

    if not main.dev:
        print("Could not find device, maybe already opened?", file=sys.stderr)
        sys.exit(1)
    else:
        print("Done!")

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


# -----------------------------------------------------------------------------
def prepare_driver():
    """
    This is necessary for now.
    See https://github.com/benthor/HuionKamvasGT191LinuxDriver/issues/1#issuecomment-351207116
    """

    sys.stdout.write("Preparing driver . . . ")

    module_old   = "hid_uclogic"
    module_new   = "uinput"

    module_found = run('lsmod | grep "^{}"'.format(module_old), shell=True)

    if module_found.returncode == 0:
        run('rmmod "{}"'.format(module_old), shell=True)
    elif module_found.returncode == 2:
        print('Grep error 2')
        exit()

    run('modprobe "{}"'.format(module_new), shell=True)

    uclogic_str = run('"{}/uclogic-probe" "{}" "{}" | "{}/uclogic-decode"'.format(
        main.settings['uclogic_bins'], main.dev.bus, main.dev.address,
        main.settings['uclogic_bins']), shell=True,
        stdout=PIPE)

    #print('-' * 80 + '\n' + uclogic_str.stdout.decode("utf-8") + '-' * 80) # DEBUG

    if uclogic_str.returncode:
        print("ERROR")
        sys.exit(1)

    print("Done!")


# -----------------------------------------------------------------------------
def setup_driver():

    sys.stdout.write("Setting up driver . . . ")

    # pressure sensitive pen tablet area with 2 stylus buttons and no eraser
    cap_pen = {
        ecodes.EV_KEY: [ecodes.BTN_TOUCH, ecodes.BTN_TOOL_PEN, ecodes.BTN_STYLUS, ecodes.BTN_STYLUS2],
        ecodes.EV_ABS: [
            (ecodes.ABS_X, AbsInfo(0,0,main.settings['pen_max_x'],0,0,main.settings['resolution'])), # value, min, max, fuzz, flat, resolution
            (ecodes.ABS_Y, AbsInfo(0,0,main.settings['pen_max_y'],0,0,main.settings['resolution'])),
            (ecodes.ABS_PRESSURE, AbsInfo(0,0,main.settings['pen_max_z'],0,0,0)),
        ]
    }

    main.vpen = UInput(events=cap_pen, name=main.settings['pen_device_name'], version=0x3)

    print("Done!")

    # INFO ---------------------

    if main.settings['enable_buttons'] and main.settings['buttons'] > 0 :
        print("\tbuttons enabled ({})".format(main.settings['buttons']))
    else:
        print("\tbuttons disabled ({})".format(main.settings['buttons']))

    if main.settings['enable_scrollbar'] and main.settings['scrollbar'] > 0 :
        print("\tscrollbar enabled ({})".format(main.settings['scrollbar']))
    else:
        print("\tscrollbar disabled ({})".format(main.settings['scrollbar']))

    print('Huion Kamvas {} driver should now be running'.format(main.settings['tablet_name']))


# -----------------------------------------------------------------------------
def multi_monitor():
    sys.stdout.write("Setting up multiple monitors . . . ")

    # try:
    #     data = main.dev.read(main.endpoint.bEndpointAddress, main.endpoint.wMaxPacketSize)
    # except usb.core.USBError as e:
    #     data = None
    #     if e.args == ('Operation timed out',):
    #         print(e, file=sys.stderr)
    #

    C0=(main.settings["tablet_width"] / main.settings["total_screen_width"])
    C1=(main.settings["tablet_offset_x"] / main.settings["total_screen_width"])
    C2=(main.settings["tablet_height"] / main.settings["total_screen_height"])
    C3=(main.settings["tablet_offset_y"] / main.settings["total_screen_height"])

    # print('xinput set-prop "{}" --type=float "Coordinate Transformation Matrix" {} 0 {} 0 {} {} 0 0 1'.format(
    #     main.settings['pen_device_name'], C0, C1, C2, C3))

    run('xinput set-prop "{}" --type=float "Coordinate Transformation Matrix" {} 0 {} 0 {} {} 0 0 1'.format(
        main.settings['pen_device_name'], C0, C1, C2, C3),
        shell=True, check=True)

    print('Mapped tablet area to "{}"x"{}"+"{}"+"{}"'.format(
        main.settings["tablet_width"], main.settings["tablet_height"],
        main.settings["tablet_offset_x"], main.settings["tablet_offset_y"]))


# -----------------------------------------------------------------------------
def main_loop():
    SCROLL_VAL_PREV=0
    while True:
        try:
            data = main.dev.read(main.endpoint.bEndpointAddress, main.endpoint.wMaxPacketSize)

            is_touch = data[1] == 129
            is_pen_btn1 = data[1] == 130
            is_pen_btn2 = data[1] == 132
            is_scrollbar = data[1] == 240
            is_buttonbar = data[1] == 224

            if is_buttonbar and main.settings['enable_buttons']:

                # get the button value in power of two (1, 2, 4, 16, 32...)
                BUTTON_VAL = (data[5] << 8) + data[4]

                if BUTTON_VAL > 0: # 0 means release

                    # convert to the exponent (0, 1, 2, 3, 4...)
                    BUTTON_VAL = int(math.log(BUTTON_VAL, 2))

                    # TODO: read from config
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
                        # print("keypress(%s) == %s" % (BUTTON_VAL, BUTTON[BUTTON_VAL])) # DEBUG
                        keypress(BUTTON[BUTTON_VAL])


            elif is_scrollbar and main.settings['enable_scrollbar']:
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

                main.vpen.write(ecodes.EV_ABS, ecodes.ABS_X, X)
                main.vpen.write(ecodes.EV_ABS, ecodes.ABS_Y, Y)
                main.vpen.write(ecodes.EV_ABS, ecodes.ABS_PRESSURE, PRESS)
                main.vpen.write(ecodes.EV_KEY, ecodes.BTN_TOUCH, is_touch and 1 or 0)
                main.vpen.write(ecodes.EV_KEY, ecodes.BTN_STYLUS, is_pen_btn1 and 1 or 0)
                main.vpen.write(ecodes.EV_KEY, ecodes.BTN_STYLUS2, is_pen_btn2 and 1 or 0)
                main.vpen.syn()

        except usb.core.USBError as e:
            data = None
            if e.args == ('Operation timed out',):
                print(e, file=sys.stderr)
                continue


# -----------------------------------------------------------------------------
def keypress(sequence):
    if main.settings['enable_notifications']:
        run('notify-send {}'.format(sequence.upper()), shell=True, check=True)

    run("xdotool {}".format(sequence), shell=True, check=True)


# -----------------------------------------------------------------------------
def read_config():

    sys.stdout.write("Reading config.ini . . . ")

    config = ConfigParser(interpolation=ExtendedInterpolation())

    # TODO manage errors
    config.read('config.ini')

    main.settings['uclogic_bins'] = config.get('config', 'uclogic_bins')

    main.settings['tablet_name'] = config.get('config', 'tablet_name')
    main.settings['pen_max_x'] = ast.literal_eval(config.get('config', 'pen_max_x'))
    main.settings['pen_max_y'] = ast.literal_eval(config.get('config', 'pen_max_y'))
    main.settings['pen_max_z'] = ast.literal_eval(config.get('config', 'pen_max_z'))
    main.settings['resolution'] = ast.literal_eval(config.get('config', 'resolution'))
    main.settings['buttons'] = ast.literal_eval(config.get('config', 'buttons'))
    main.settings['scrollbar'] = ast.literal_eval(config.get('config', 'scrollbar'))
    main.settings['tablet_width'] = ast.literal_eval(config.get('config', 'tablet_width'))
    main.settings['tablet_height'] = ast.literal_eval(config.get('config', 'tablet_height'))

    main.settings['total_screen_width'] = ast.literal_eval(config.get('config', 'total_screen_width'))
    main.settings['total_screen_height'] = ast.literal_eval(config.get('config', 'total_screen_height'))
    main.settings['tablet_offset_x'] = ast.literal_eval(config.get('config', 'tablet_offset_x'))
    main.settings['tablet_offset_y'] = ast.literal_eval(config.get('config', 'tablet_offset_y'))

    main.settings['enable_multi_monitor'] = config.getboolean('config', 'enable_multi_monitor') # TODO do something with this
    main.settings['enable_notifications'] = config.getboolean('config', 'enable_notifications')
    main.settings['enable_buttons'] = config.getboolean('config', 'enable_buttons')
    main.settings['enable_scrollbar'] = config.getboolean('config', 'enable_scrollbar')

    main.settings['start_menu'] = config.get('config', 'start_menu')

    for section in config.sections():
        if section.startswith('menu_'):
            MENU[section] = {}

            # pretty title
            if config.has_option(section, 'title'):
                MENU[section]['title'] = config.get(section, 'title')
            else:
                MENU[section]['title'] = "[{}]".format(section)

            # print("\n{}".format(MENU[section]['title'])) # DEBUG

            # buttons
            for n in range(0, main.settings['buttons']):
                btn = 'b' + str(n)
                if config.has_option(section, btn):
                    MENU[section][n] = config.get(section, btn)
                else:
                    MENU[section][n] = ""

                # print("button {} = {}".format(n, MENU[section][n])) # DEBUG


    main.current_menu = main.settings['start_menu']

    print("Done!")


# -----------------------------------------------------------------------------
if __name__ == '__main__':
        main.run()
