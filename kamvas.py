import usb.core
import usb.util
import sys
from evdev import UInput, ecodes, AbsInfo

PEN_MAX_X = 86970
PEN_MAX_Y = 47752
PEN_MAX_Z = 8191
RESOLUTION = 5080

#pressure sensitive pen tablet area with 2 stylus buttons and no eraser
cap_pen = {
    ecodes.EV_KEY: [ecodes.BTN_TOUCH, ecodes.BTN_TOOL_PEN, ecodes.BTN_STYLUS, ecodes.BTN_STYLUS2],
    ecodes.EV_ABS: [
        (ecodes.ABS_X, AbsInfo(0,0,PEN_MAX_X,0,0,RESOLUTION)), #value, min, max, fuzz, flat, resolution
        (ecodes.ABS_Y, AbsInfo(0,0,PEN_MAX_Y,0,0,RESOLUTION)),
        (ecodes.ABS_PRESSURE, AbsInfo(0,0,PEN_MAX_Z,0,0,0)),
    ],
    #ecodes.EV_MSC: [ecodes.MSC_SCAN], #not sure why, but it appears to be needed
}

dev = usb.core.find(idVendor=0x256c, idProduct=0x006e)
if not dev:
    print("could not find device, maybe already opened?", file=sys.stderr)
    sys.exit(1)

endpoint = None
for cfg in dev:
    for i in cfg:
        for e in i:
            #print("endpoint", e)
            if not endpoint:
                endpoint = e
        if dev.is_kernel_driver_active(i.index):
            dev.detach_kernel_driver(i.index)
            usb.util.claim_interface(dev, i.index)
            print("grabbed interface %d", i.index)

endpoint = dev[0][(0,0)][0]
vpen = UInput(events=cap_pen, name="kamvas-pen", version=0x3)
print('huion kamvas GT191 driver should now be running')
while True:
    try:
        data = dev.read(endpoint.bEndpointAddress,endpoint.wMaxPacketSize)
        X = (data[8] << 16) + (data[3] << 8) + data[2]
        Y = (data[5] << 8) + data[4]
        PRESS = (data[7] << 8) + data[6]
        TOUCH = data[1] == 129
        BTN1 = data[1] == 130
        BTN2 = data[1] == 132
        #print(data)
        #print("X %6d Y%6d PRESS %4d (%s %s %s))" % (X, Y, PRESS, TOUCH, BTN1, BTN2))
        vpen.write(ecodes.EV_ABS, ecodes.ABS_X, X)
        vpen.write(ecodes.EV_ABS, ecodes.ABS_Y, Y)
        vpen.write(ecodes.EV_ABS, ecodes.ABS_PRESSURE, PRESS)
        vpen.write(ecodes.EV_KEY, ecodes.BTN_TOUCH, TOUCH and 1 or 0)
        vpen.write(ecodes.EV_KEY, ecodes.BTN_STYLUS, BTN1 and 1 or 0)
        vpen.write(ecodes.EV_KEY, ecodes.BTN_STYLUS2, BTN2 and 1 or 0)
        vpen.syn()
    except usb.core.USBError as e:
        data = None
        if e.args == ('Operation timed out',):
            print(e, file=sys.stderr)
            continue
