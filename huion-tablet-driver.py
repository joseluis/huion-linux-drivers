#!/usr/bin/env python3

import usb.core, usb.util
import sys
import os.path
import platform
from evdev import UInput, ecodes, AbsInfo, InputDevice, list_devices
import subprocess as sp
import math
import numexpr
from configparser import ConfigParser, ExtendedInterpolation
from time import gmtime, strftime, sleep

MENU = {}


# -----------------------------------------------------------------------------
class main():
    """
    """
    settings = {'pen_device_name':'Tablet Monitor Pen' # must be defined here
                + strftime(" %H%M%S", gmtime())}       # for pressure to work
    dev = None
    endpoint = None
    vpen = None
    current_menu = None

    def run():
        find_usb_device()
        read_config()
        #prepare_driver()
        setup_driver()
        calibrate()
        multi_monitor()
        main_loop()


# -----------------------------------------------------------------------------
def find_usb_device():
    """
    """
    sys.stdout.write("Finding USB device. . . ")

    device_ids = [(0x256c, 0x006d), (0x256c, 0x006e)]
    for cur_dev_id in device_ids:
        main.dev = usb.core.find(idVendor=cur_dev_id[0], idProduct=cur_dev_id[1])
        if main.dev: break

    if not main.dev:
        print("Error, Could not find device, maybe already opened?",
            file=sys.stderr)
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
    See https://github.com/benthor/HuionKamvasGT191LinuxDriver/issues/1
    """

    sys.stdout.write("Preparing driver. . . ")

    module_old   = "hid_uclogic"
    module_new   = "uinput"

    module_found = sp.run('lsmod | grep "^{}"'.format(module_old), shell=True)

    if module_found.returncode == 0:
        sp.run('rmmod "{}"'.format(module_old), shell=True)
    elif module_found.returncode == 2:
        print('Grep error 2')
        exit()

    sp.run('modprobe "{}"'.format(module_new), shell=True)

    cmd='"{}/uclogic-probe" "{}" "{}" | "{}/uclogic-decode"'.format(
        main.settings['uclogic_bins'], main.dev.bus, main.dev.address,
        main.settings['uclogic_bins'])
    try:
        uc_str = sp.run(cmd, shell=True, check=True, stdout=sp.PIPE)
    except sp.CalledProcessError as e:
        run_error(e, cmd)

    print("Done!")

    if main.settings['debug_mode']:
        print('-'*80+'\n'+ uc_str.stdout.decode("utf-8") +'-'*80)


# -----------------------------------------------------------------------------
def setup_driver():
    """
    """

    sys.stdout.write("Setting up driver. . . ")

    # pressure sensitive pen tablet area with: 2 stylus buttons, no eraser, tilt
    cap_pen = {
        ecodes.EV_KEY: [ecodes.BTN_TOUCH, ecodes.BTN_TOOL_PEN,ecodes.BTN_STYLUS, ecodes.BTN_STYLUS2],
        ecodes.EV_ABS: [
            # value,min,max,fuzz,flat,resolution
            (ecodes.ABS_X,AbsInfo(0,0,main.settings['pen_max_x'],0,0,main.settings['resolution'])),
            (ecodes.ABS_Y,AbsInfo(0,0,main.settings['pen_max_y'],0,0,main.settings['resolution'])),
            (ecodes.ABS_PRESSURE, AbsInfo(0,0,main.settings['pen_max_z'],0,0,0)),
            (ecodes.ABS_TILT_X, AbsInfo(0,main.settings['pen_min_tilt'],main.settings['pen_max_tilt'],0,0,0)),
            (ecodes.ABS_TILT_Y, AbsInfo(0,main.settings['pen_min_tilt'],main.settings['pen_max_tilt'],0,0,0)),
        ]
    }
    main.vpen = UInput(events=cap_pen, name=main.settings['pen_device_name'], version=0x3)

    print("Done!")

    # INFO ---------------------

    print("\tTablet model name         {}".format(main.settings['model_name']))

    if main.settings['enable_buttons'] and main.settings['buttons'] > 0 :
        print("\tButtons                   ENABLED ({})".format(
            main.settings['buttons']))
    else:
        print("\tButtons                   disabled ({})".format(
            main.settings['buttons']))

    # scrollbar
    if main.settings['enable_scrollbar']:
        print("\tScrollbar                 ENABLED ({})".format(
            main.settings['scrollbar']))

        if main.settings['scrollbar_reverse']:
            print("\t\tReversed:         {}".format(
            main.settings['scrollbar_reverse']))
    else:
        print("\tScrollbar                 disabled ({})".format(
           main.settings['scrollbar']))

    # notifications
    if main.settings['enable_notifications']:
        print("\tNotifications:            ENABLED")
        if main.settings['buttons_notifications']:
            print("\t\tfor buttons       ENABLED")
        else:
            print("\t\tfor buttons       disabled")
        if main.settings['scrollbar_notifications']:
            print("\t\tfor scrollbar     ENABLED")
        else:
            print("\t\tfor scrollbar     disabled")
    else:
        print("\tNotifications             disabled")

    if main.settings['screen']:
        print("\tScreen                    Enabled ({}x{})".format(
            main.settings['screen_width'], main.settings['screen_height']))
        print("\tCurrent Monitor Setup     {}".format(
            main.settings['monitor_setup']))
        if main.settings['enable_multi_monitor']:
            print("\tMulti Monitor Setup       ENABLED")
        else:
            print("\tMulti Monitor Setup       disabled")

        if main.settings['enable_xrandr']:
            print("\tCalling xrandr            ENABLED")
        else:
            print("\tCalling xrandr            disabled")

    else:
        print("\tScreen                    disabled")

    if main.settings['debug_mode']:
        print("\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        print("\t\t\t< DEBUG MODE ENABLED >")
        print("Enabled by default. You can disable it by setting debug_mode = false")
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")

        pf = platform.uname()
        print("\nSYSTEM: {} {} ({} {})".format(
            pf.system, pf.release, pf.machine, pf.processor))
        print("{}".format(pf.version))

        devices = [InputDevice(path) for path in list_devices()]
        for device in devices:
            if device.name == main.settings['pen_device_name']:
                try:
                    path = device.path
                except:
                    path = device.fn
                print("\nDEVICE: {} ({})".format(path, device.phys))
                print("{}".format(device.info))

                print("\n{}".format(main.endpoint)) # DEBUG

                print("\nTABLET CAPABILITIES:")

                caps = device.capabilities(verbose=True)
                for cap in caps:
                    print(caps[cap])
        print("\nVPEN:")
        print(main.vpen)

        print("\nXINPUT:")
        cmd='xinput list --short | grep "Tablet Monitor Pen"'
        try:
            sp.run(cmd, shell=True, check=True)
        except sp.CalledProcessError as e:
            run_error(e, cmd)


# -----------------------------------------------------------------------------
def multi_monitor():
    """
    """

    if not (main.settings['enable_multi_monitor'] and main.settings['screen']):
        return

    print("\nSetting up multiple monitors. . . ")

    if main.settings['enable_xrandr']:
        print("Running xrandr. . . ")
        cmd='xrandr {}'.format(main.settings['xrandr_args'])
        if main.settings['debug_mode']:
            print('» {}'.format(cmd))
        try:
            sp.run(cmd, shell=True, check=True)
        except sp.CalledProcessError as e:
            run_error(e, cmd)

    C0=(main.settings['screen_width'] / main.settings['total_screen_width'])
    C1=(main.settings['tablet_offset_x'] / main.settings['total_screen_width'])
    C2=(main.settings['screen_height'] / main.settings['total_screen_height'])
    C3=(main.settings['tablet_offset_y'] / main.settings['total_screen_height'])

    cmd='xinput set-prop "{}" --type=float "{}" {} 0 {} 0 {} {} 0 0 1'.format(
        main.settings['pen_device_name'], "Coordinate Transformation Matrix",
        C0, C1, C2, C3)
    try:
        print("Running xinput. . . ")
        if main.settings['debug_mode']:
            print('» {}'.format(cmd))
        sp.run(cmd, shell=True, check=True)
    except sp.CalledProcessError as e:
        run_error(e, cmd)

    print('Mapped tablet area to "{}x{} + {}x{}"'.format(
        main.settings['screen_width'], main.settings['screen_height'],
        main.settings['tablet_offset_x'], main.settings['tablet_offset_y']))

# -----------------------------------------------------------------------------
def calibrate():

    if not main.settings['enable_calibration']:
        return

    sys.stdout.write("Calibrating. . . ")

    cmd='xinput set-int-prop "{}" "Evdev Axis Calibration" 32 {} {} {} {}'.format(
            main.settings['pen_device_name'],
            main.settings['calibrate_min_x'], main.settings['calibrate_max_x'],
            main.settings['calibrate_min_y'], main.settings['calibrate_max_y'])
    try:
        sp.run(cmd, shell=True, check=True)
    except sp.CalledProcessError as e:
        run_error(e, cmd)

    cmd='xinput set-int-prop "{}" "Evdev Axes Swap" 8 0'.format(
        main.settings['pen_device_name'])
    try:
        sp.run(cmd, shell=True, check=True)
    except sp.CalledProcessError as e:
        run_error(e, cmd)

    print('Done!')


# -----------------------------------------------------------------------------
def main_loop():
    """
    """

    print('\nHuion Kamvas driver should now be running. . .')

    if main.settings['debug_mode']:
        if main.settings['tablet_debug_only']:
            print("\n(Input from the tablet will ONLY be used to print it out)")
        else:
            print("\n(Input from the tablet will be printed out)")
    print()

    if main.current_menu:
        switch_menu(main.current_menu)

    SCROLL_VAL_PREV=0

    if main.settings['debug_mode']:
        HOVER_PREV = False

    while not sleep(main.settings['refresh_rate_fps']):
        try:
            data = main.dev.read(main.endpoint.bEndpointAddress, main.endpoint.wMaxPacketSize)

            # DATA INTERPRETATION:
            # source: https://github.com/andresm/digimend-kernel-drivers/commit/b7c8b33c0392e2a5e4e448f901e3dfc206d346a6

            # 00 01 02 03 04 05 06 07 08 09 10 11
            # ^  ^  ^  ^  ^  ^  ^  ^  ^  ^  ^  ^
            # |  |  |  |  |  |  |  |  |  |  |  |
            # |  |  |  |  |  |  |  |  |  |  |  Y Tilt
            # |  |  |  |  |  |  |  |  |  |  X Tilt
            # |  |  |  |  |  |  |  |  |  Y HH
            # |  |  |  |  |  |  |  |  X HH
            # |  |  |  |  |  |  |  Pressure H
            # |  |  |  |  |  |  Pressure L
            # |  |  |  |  |  Y H
            # |  |  |  |  Y L
            # |  |  |  X H
            # |  |  X L
            # |  Pen buttons
            # Report ID - 0x08

            is_hover     = data[1] == 128
            is_touch     = data[1] == 129
            is_buttonbar = data[1] == 224
            is_scrollbar = data[1] == 240
            if main.settings['pen_buttons_reverse']:
                is_pen_btn1  = data[1] == 132 # right
                is_pen_btn2  = data[1] == 130 # middle
            else:
                is_pen_btn1  = data[1] == 130 # middle
                is_pen_btn2  = data[1] == 132 # right


            # DEBUG

            if main.settings['debug_mode']:
                if is_hover:
                    if not HOVER_PREV:
                        print("...")
                        HOVER_PREV = True
                else:
                    HOVER_PREV = False

                    data_str = ""
                    for e in data:
                        data_str += "{:02x} ".format(e)
                    try:
                        data_str2 = "| X:{:05d} Y:{:05d} PRES:{:04d} TILT_X:{:03d} TILT_Y:{:03d}".format(
                            (data[8]<<16) + (data[3]<<8) + data[2],
                            (data[9]<<16) + (data[5]<<8) + data[4],
                            (data[7]<<8) + data[6],
                            data[10] >= 128 and (data[10]-256) or data[10],
                            0 - (data[11] >= 128 and (data[11]-256) or data[11]),
                        )
                        #   ^ tilt calculation source: https://github.com/Mantaseus/Huion_Kamvas_Linux/blob/master/driver/kamvas_driver.py#L222
                    except:
                        data_str2 = ""

                    data_str += data_str2
                    print("{}".format(data_str))

            if main.settings['tablet_debug_only']:
                continue


            # BUTTON EVENT

            if is_buttonbar and main.settings['enable_buttons']:
                # get the button value in power of two (1, 2, 4, 16, 32...)
                BUTTON_VAL = (data[5] << 8) + data[4]

                if BUTTON_VAL > 0: # 0 means release
                    # convert to the exponent (0, 1, 2, 3, 4...)
                    BUTTON_VAL = int(math.log(BUTTON_VAL, 2))
                    if main.current_menu:
                        do_shortcut("button", MENU[main.current_menu][BUTTON_VAL])

            # SCROLLBAR EVENT

            elif is_scrollbar and main.settings['enable_scrollbar']:
                SCROLL_VAL = data[5]

                if SCROLL_VAL > 0: # 0 means release
                    if SCROLL_VAL_PREV == 0:
                        SCROLL_VAL_PREV=SCROLL_VAL

                    if main.current_menu:
                        if main.settings['scrollbar_reverse']:
                            if SCROLL_VAL > SCROLL_VAL_PREV:
                                do_shortcut("scrollbar", MENU[main.current_menu]['scroll_up'])
                            elif SCROLL_VAL < SCROLL_VAL_PREV:
                                do_shortcut("scrollbar", MENU[main.current_menu]['scroll_down'])
                        else:
                            if SCROLL_VAL < SCROLL_VAL_PREV:
                                do_shortcut("scrollbar", MENU[main.current_menu]['scroll_up'])
                            elif SCROLL_VAL > SCROLL_VAL_PREV:
                                do_shortcut("scrollbar", MENU[main.current_menu]['scroll_down'])

                SCROLL_VAL_PREV = SCROLL_VAL

            # TOUCH EVENT

            else:
                # bitwise operations: n<<16 == n*65536 and n<<8 == n*256
                try:
                    X = (data[8]<<16) + (data[3]<<8) + data[2]
                except:
                    try:
                        X = (data[3]<<8) + data[2]
                    except:
                        X = 0
                try:
                    Y = (data[9]<<16) + (data[5]<<8) + data[4]
                except:
                    try:
                        Y = (data[9]<<16) + (data[5]<<8) + data[4]
                    except:
                        Y = 0
                try:
                    PRESS = (data[7]<<8) + data[6]
                except:
                    PRESS = main.settings['pen_max_z']

                # tilt calculation source: https://github.com/Mantaseus/Huion_Kamvas_Linux/blob/master/driver/kamvas_driver.py#L222
                try:
                    TILT_X = data[10] >= 128 and (data[10]-256) or data[10]
                except:
                    TILT_X = 0
                try:
                    TILT_Y = 0 - (data[11] >= 128 and (data[11]-256) or data[11]) # invert Y tilt axis
                except:
                    TILT_Y = 0

                main.vpen.write(ecodes.EV_ABS, ecodes.ABS_X, X)
                main.vpen.write(ecodes.EV_ABS, ecodes.ABS_Y, Y)
                main.vpen.write(ecodes.EV_ABS, ecodes.ABS_PRESSURE, PRESS)
                main.vpen.write(ecodes.EV_KEY, ecodes.BTN_TOUCH,
                    is_touch and 1 or 0)
                # Tilt wont probably work so easily. The value may need to be converted to degrees
                main.vpen.write(ecodes.EV_ABS, ecodes.ABS_TILT_X, TILT_X)
                main.vpen.write(ecodes.EV_ABS, ecodes.ABS_TILT_Y, TILT_Y)
                main.vpen.write(ecodes.EV_KEY, ecodes.BTN_STYLUS, is_pen_btn1 and 1 or 0)
                main.vpen.write(ecodes.EV_KEY, ecodes.BTN_STYLUS2, is_pen_btn2 and 1 or 0)
                main.vpen.syn()

        except usb.core.USBError as e:
            data = None
            if e.args == (19,'No such device (it may have been disconnected)'):
                print(e, file=sys.stderr)
                sys.exit()


# -----------------------------------------------------------------------------
def do_shortcut(title, sequence):
    """ Interprets whether the shortcut is a keypress or a menu link
        and triggers the appropiate action in either case.
    """
    # empty shortcut
    if sequence == "":
        pass

    # is a menu link
    elif sequence.startswith('[') and sequence.endswith(']'):
        switch_menu(sequence.strip('[]'))

    # is a keyboard shortcut
    else:
        keypress(title, sequence)


# -----------------------------------------------------------------------------
def keypress(title, sequence):
    """
    """
    if main.settings['enable_notifications']:
        if (title == 'scrollbar' and main.settings['scrollbar_notifications']) \
            or (title != 'scrollbar' and main.settings['buttons_notifications']):

            cmd='notify-send "{}" "{}"'.format(title, sequence)
            try:
                sp.run(cmd, shell=True, check=True)
            except sp.CalledProcessError as e:
                run_error(e, cmd)

    cmd="xdotool {}".format(sequence)
    try:
        sp.run(cmd, shell=True, check=True)
    except sp.CalledProcessError as e:
        run_error(e, cmd)


# -----------------------------------------------------------------------------
def switch_menu(new_menu):
    """
    """
    if not main.settings['enable_buttons'] or main.settings['buttons'] == 0:
        return

    main.current_menu = new_menu

    # print the menu
    menu_title = MENU[new_menu]['title']
    menu_text = ""
    for n in range(0, main.settings['buttons']):
        menu_text += "\nbutton {} = {}".format(n, MENU[main.current_menu][n])

    print(menu_title + menu_text)

    if main.settings['enable_notifications']:
        cmd='notify-send "{}" "{}"'.format(menu_title, menu_text)
        try:
            sp.run(cmd, shell=True, check=True)
        except sp.CalledProcessError as e:
            run_error(e, cmd)


# -----------------------------------------------------------------------------
def run_error(error, command, exit=True):
    """
    """
    print("ERROR running the following comand:")
    print("\t{}".format(command))
    print("RETURN CODE: {}".format(error.returncode))
    if exit:
        sys.exit(1)


# -----------------------------------------------------------------------------
def read_config():
    """
    """

    sys.stdout.write("Reading configuration. . . ")

    if os.path.exists('config.ini'):
        config = ConfigParser(interpolation=ExtendedInterpolation())
        config.read('config.ini')
    else:
        print("ERROR: Couldn't locate config.ini")
        sys.exit(2)


    # tablet info

    current_tablet = config.get('config', 'current_tablet').split("#",1)[0].strip('[]').strip()

    try:
        main.settings['model_name'] = config.get(current_tablet, 'model_name')
    except:
        main.settings['model_name'] = "Unnamed Tablet"

    try:
        main.settings['pen_max_x'] = numexpr.evaluate(config.get(current_tablet, 'pen_max_x'))
    except:
        main.settings['pen_max_x'] = 0
    try:
        main.settings['pen_max_y'] = numexpr.evaluate(config.get(current_tablet, 'pen_max_y'))
    except:
        main.settings['pen_max_y'] = 0
    try:
        main.settings['pen_max_z'] = numexpr.evaluate(config.get(current_tablet, 'pen_max_z'))
    except:
        main.settings['pen_max_z'] = 0
    try:
        main.settings['pen_min_tilt'] = numexpr.evaluate(config.get(current_tablet, 'pen_min_tilt'))
    except:
        main.settings['pen_min_tilt'] = 0
    try:
        main.settings['pen_max_tilt'] = numexpr.evaluate(config.get(current_tablet, 'pen_max_tilt'))
    except:
        main.settings['pen_max_tilt'] = 0
    try:
        main.settings['resolution'] = numexpr.evaluate(config.get(current_tablet, 'resolution'))
    except:
        main.settings['resolution'] = 0
    # number of buttons in tablet
    try:
        main.settings['buttons'] = numexpr.evaluate(config.get(current_tablet, 'buttons'))
    except:
        main.settings['buttons'] = 0
    # number of scrollbars
    try:
        main.settings['scrollbar'] = numexpr.evaluate(config.get(current_tablet, 'scrollbar'))
    except:
        main.settings['scrollbar'] = 0
    try:
        main.settings['screen'] = config.getboolean(current_tablet, 'screen')
        try:
            main.settings['screen_width'] = numexpr.evaluate(config.get(current_tablet, 'screen_width'))
            main.settings['screen_height'] = numexpr.evaluate(config.get(current_tablet, 'screen_height'))
        except:
            main.settings['screen_width'] = 1920
            main.settings['screen_height'] = 1080
    except:
        main.settings['screen'] = False


    # DEBUG mode
    try:
        main.settings['debug_mode'] = config.getboolean('config', 'debug_mode')
    except:
        main.settings['debug_mode'] = False

    # [tablet_debug]
    try:
        main.settings['tablet_debug_only'] = config.getboolean(current_tablet, 'debug_only')
        # also enables debug_mode
        if main.settings['tablet_debug_only']:
            main.settings['debug_mode'] = True
    except:
        main.settings['tablet_debug_only'] = False


    # features

    # tablet buttons
    try:
        main.settings['enable_buttons'] = config.getboolean('config', 'enable_buttons')
        if main.settings['buttons'] == 0:
            main.settings['enable_buttons'] = False
    except:
        main.settings['enable_buttons'] = False

    # pen buttons
    try:
        main.settings['pen_buttons_reverse'] = config.getboolean('config', 'pen_buttons_reverse')
    except:
        main.settings['pen_buttons_reverse'] = False

    try:
        main.settings['buttons_notifications'] = config.getboolean('config', 'buttons_notifications')
    except:
        main.settings['buttons_notifications'] = True

    # scrollbar
    try:
        main.settings['enable_scrollbar'] = config.getboolean('config', 'enable_scrollbar')
        if main.settings['scrollbar'] == 0:
            main.settings['enable_scrollbar'] = False
    except:
        main.settings['enable_scrollbar'] = False

    # scrollbar reverse
    try:
        main.settings['scrollbar_reverse'] = config.getboolean('config', 'scrollbar_reverse')
    except:
        main.settings['scrollbar_reverse'] = False

    # scrollbar notifications
    try:
        main.settings['scrollbar_notifications'] = config.getboolean('config', 'scrollbar_notifications')
    except:
        main.settings['scrollbar_notifications'] = False


    # multi-monitor setup

    try:
        main.settings['enable_multi_monitor'] = config.getboolean('config', 'enable_multi_monitor')
    except:
        main.settings['enable_multi_monitor'] = False

    try:
        main.settings['enable_xrandr'] = config.getboolean('config', 'enable_xrandr')
    except:
        main.settings['enable_xrandr'] = False

    try:
        main.settings['monitor_setup'] = config.get('config', 'current_monitor_setup')
        current_monitor_setup =  main.settings['monitor_setup'].split("#",1)[0].strip('[]').strip()
        main.settings['total_screen_width'] = numexpr.evaluate(config.get(current_monitor_setup,
            'total_screen_width').split("#",1)[0].strip())
        main.settings['total_screen_height'] = numexpr.evaluate(config.get(current_monitor_setup,
            'total_screen_height').split("#",1)[0].strip())
        main.settings['tablet_offset_x'] = numexpr.evaluate(config.get(current_monitor_setup,
            'tablet_offset_x').split("#",1)[0].strip())
        main.settings['tablet_offset_y'] = numexpr.evaluate(config.get(current_monitor_setup,
            'tablet_offset_y').split("#",1)[0].strip())

        main.settings['xrandr_args'] = config.get(current_monitor_setup,
            'xrandr_args').split("#",1)[0].strip()
    except:
        current_monitor_setup = "none"

    # tablet calibration

    try:
        main.settings['enable_calibration'] = config.getboolean('config', 'enable_calibration')
        main.settings['calibrate_min_x'] = numexpr.evaluate(config.get('config',
            'calibrate_min_x').split("#",1)[0].strip())
        main.settings['calibrate_max_x'] = numexpr.evaluate(config.get('config',
            'calibrate_max_x').split("#",1)[0].strip())
        main.settings['calibrate_min_y'] = numexpr.evaluate(config.get('config',
            'calibrate_min_y').split("#",1)[0].strip())
        main.settings['calibrate_max_y'] = config.get('config',
            'calibrate_max_y').split("#",1)[0].strip()
    except:
        main.settings['enable_calibration'] = False

    # miscellaneus

    main.settings['uclogic_bins'] = config.get('config', 'uclogic_bins')
    try:
        main.settings['enable_notifications'] = config.getboolean('config', 'enable_notifications')
    except:
        main.settings['enable_notifications'] = True
    try:
        main.settings['refresh_rate_fps'] = 1 / numexpr.evaluate(config.get('config', 'refresh_rate_fps').split("#",1)[0].strip())
    except:
        main.settings['refresh_rate_fps'] = 1 / 100
    try:
        main.settings['start_menu'] = config.get('config', 'start_menu').strip('[]')
    except:
        main.settings['start_menu'] = ''


    for section in config.sections():
        if section.startswith('menu_'):
            MENU[section] = {}

            # pretty title
            if config.has_option(section, 'title'):
                MENU[section]['title'] = config.get(section, 'title')
            else:
                MENU[section]['title'] = "[{}]".format(section)

            # buttons
            for n in range(0, main.settings['buttons']):
                btn = 'b' + str(n)
                if config.has_option(section, btn):
                    MENU[section][n] = config.get(
                        section, btn).strip()
                else:
                    MENU[section][n] = ""

            # scrollbar
            if main.settings['scrollbar']:
                try:
                    MENU[section]['scroll_up'] = config.get(section, 'su').strip()
                except:
                    MENU[section]['scroll_up'] = ""
                try:
                    MENU[section]['scroll_down'] = config.get(section, 'sd').strip()
                except:
                    MENU[section]['scroll_down'] = ""

    main.current_menu = main.settings['start_menu']

    print("Done!")


# -----------------------------------------------------------------------------
if __name__ == '__main__':
    main.run()
