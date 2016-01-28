# Reaper

Arduino library and python utility to transfer files off an SD card using a
Serial port. The main use case is recovering sensor data from a sealed data
logger that does not have wifi or easy access  to the SD card itself.

## Install
1. install Arduino DIDE 1.6.7
1. install SdFat-beta Arduino library
1. install Reaper Arduino library
1. make install

## Loading Firmwmare

1. adjust port and paths to Arduino in Makefile
1. run make

```bash
make compile
```

The `SKETCH_DIR` and `SKETCH` env vars tell make where to find sketches and what
sketch to use. For example to build a sketch in the sketches dir:

```
SKETCH_DIR=sketches SKETCH=bench make compile
```

# Running

### list files on SD card
sdreaper -p /dev/tty.usbmodem1421 'ls'

### copy file from SD card
sdreaper -p /dev/tty.usbmodem1421 'cp small.dat'


# Sample test data

Mount SD card on Mac to copy sample files.

```
cd sample_data
SD_CARD=/Volumes/YOUR-CARD make
```

Empty Mac Trash and eject from finder. Not strictly necessary but if without
these steps the annoying .Spotlightxxx files may not get removed from SD card.

## sketches

Misc Programs used for development of Reaper. Some may become Reaper examples, some
will get tossed.


## 3rd Party

- [SdFat-beta](https://github.com/greiman/SdFat-beta) - SD card access
- [pycrc](https://github.com/tpircher/pycrc) - generated CRC function C source code
- [pyserial]() - Python serial communication

## License
[![MIT License](http://img.shields.io/badge/license-MIT-blue.svg?style=flat)](LICENSE)
