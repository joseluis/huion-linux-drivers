from evdev import UInput, AbsInfo, ecodes as e

cap = {
    e.EV_KEY : [e.KEY_A, e.KEY_B],
    e.EV_ABS : [
        (e.ABS_X, AbsInfo(value=0, min=0, max=255, fuzz=0, flat=0, resolution=0)),
        (e.ABS_Y, AbsInfo(0, 0, 255, 0, 0, 0)),
        #(e.ABS_MT_POSITION_X, (0, 255, 128, 0)), 
    ],
    e.EV_MSC: [e.MSC_SCAN], #not sure why, but it appears to be needed
}

ui = UInput(events=cap, name='example-device-2', version=0x3)
print(ui)

print(ui.capabilities())

ui.write(e.EV_ABS, e.ABS_X, 20)
ui.write(e.EV_ABS, e.ABS_Y, 20)
ui.syn()
