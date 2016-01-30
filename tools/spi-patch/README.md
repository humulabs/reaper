# SPI patch

Using SdFat-beta and Arduino.cc libs the patch improves card read speed
from 109KB/s to 129KB/s.

Source:

  https://forum.arduino.cc/index.php?topic=358160.30

I copied the SERCOM and SPI files over the originals that are part of the
SAMD board library. To find the originals:

find ~/Library/Arduino15 -name SERCOM.cpp
find ~/Library/Arduino15 -name SPI.cpp

If you break things, use the Arduino.cc IDE board manager to uninstall
the Arduino Zero then install it again.

I did not try the Sd2Card patches as those are for the 2009 version of SdFat
that is wrapped by the Arduino SD library. May try them at some point.
