#!/usr/bin/env bash
# shellcheck disable=SC2086

PEN_DEVICE_NAME="Tablet Monitor Pen"
TABLET_WIDTH=1920
TABLET_HEIGHT=1080

# Current screen setup assumes 3 monitors, with the tablet being the rightmost:
#
#   [Left:2560x1440] - [Middle:1920x1080] - [Right:1920x1080](TABLET)
#
# Edit these to match your setup:

TOTAL_SCREEN_WIDTH=$((2560 + 1920 + TABLET_WIDTH)) # 6400
TOTAL_SCREEN_HEIGHT=1440

TABLET_OFFSET_X=$((2560 + 1920)) # 4480
TABLET_OFFSET_Y=0


# DEBUG
# echo "TABLET_WIDTH=1920, TABLET_HEIGHT=1080"
# echo "TOTAL_SCREEN_WIDTH=$TOTAL_SCREEN_WIDTH, TOTAL_SCREEN_HEIGHT=$TOTAL_SCREEN_HEIGHT"
# echo "TABLET_OFFSET_X=$TABLET_OFFSET_X, TABLET_OFFSET_Y=$TABLET_OFFSET_Y"


# #############################################################################


C0=$(echo "scale=8;$TABLET_WIDTH / $TOTAL_SCREEN_WIDTH" | bc)
C1=$(echo "scale=8;$TABLET_OFFSET_X/$TOTAL_SCREEN_WIDTH" | bc)
C2=$(echo "scale=8;$TABLET_HEIGHT/$TOTAL_SCREEN_HEIGHT" | bc)
C3=$(echo "scale=8;$TABLET_OFFSET_Y/$TOTAL_SCREEN_HEIGHT" | bc)


# DEBUG
# echo "C0 = touch_area_width / total_width = $TABLET_WIDTH / $TOTAL_SCREEN_WIDTH = $C0"
# echo "C2 = touch_area_height / total_height = $TABLET_HEIGHT/$TOTAL_SCREEN_HEIGHT = $C2"
# echo "C1 = touch_area_x_offset / total_width = $TABLET_OFFSET_X/$TOTAL_SCREEN_WIDTH = $C1"
# echo "C3 = touch_area_y_offset / total_height = $TABLET_OFFSET_Y/$TOTAL_SCREEN_HEIGHT = $C3"
# echo "xinput set-prop \"$PEN_DEVICE_NAME=\" --type=float \"Coordinate Transformation Matrix\" $C0 0 $C1 0 $C2 $C3 0 0 1"
#
# The matrix is:
# [ C0   0  C1 ]
# [  0  C2  C3 ]
# [  0   0   1 ]

xinput set-prop "$PEN_DEVICE_NAME" --type=float "Coordinate Transformation Matrix" $C0 0 $C1 0 $C2 $C3 0 0 1

echo Mapped tablet area to \'"$TABLET_WIDTH"x"$TABLET_HEIGHT"+"$TABLET_OFFSET_X"+"$TABLET_OFFSET_Y"\'
