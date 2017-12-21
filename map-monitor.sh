#!/bin/bash
# Edit these to match your setup:

XSCREEN_WIDTH=6400
XSCREEN_HEIGHT=1440

TABLET_WIDTH=1920
TABLET_HEIGHT=1080

TABLET_OFFSET_X=4480
TABLET_OFFSET_Y=0

############## Don't Edit this! ##############
C0=`echo "scale=8;$TABLET_WIDTH / $XSCREEN_WIDTH" | bc`
C1=`echo "scale=8;$TABLET_OFFSET_X/$XSCREEN_WIDTH" | bc`
C2=`echo "scale=8;$TABLET_HEIGHT/$XSCREEN_HEIGHT" | bc`
C3=`echo "scale=8;$TABLET_OFFSET_Y/$XSCREEN_HEIGHT" | bc`
xinput set-prop "kamvas-pen" --type=float "Coordinate Transformation Matrix" $C0 0 $C1 0 $C2 $C3 0 0 1
echo Mapped tablet area to \'"$TABLET_WIDTH"x"$TABLET_HEIGHT"+"$TABLET_OFFSET_X"+"$TABLET_OFFSET_Y"\'
