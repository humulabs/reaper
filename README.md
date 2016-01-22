# Reaper

Arduino library and command line utility to download and delete SD card files.
Currently tested on Arduino SAMD boards.

## Running

1. install SdFat-beta Arduino library
1. install Reaper Arduino library
1. pip install pyserial
1. adjust port and paths to Arduino in Makefile

```bash
make
```

The `SKETCH_DIR` and `SKETCH` env vars tell make where to find sketches and what
sketch to use. For example to build a sketch in the sketches dir:

```
SKETCH_DIR=sketches SKETCH=bench make compile
```

## serial-test.py

Run it with `make run`. It will wait for serial port to be available so you can
run `serial-test` before resetting the Arduino.

## sketches

Misc Programs used for development of Reaper. Some may become Reaper examples, some
will get tossed.


## 3rd Party

- [SdFat-beta](https://github.com/greiman/SdFat-beta) - SD card access
- [pycrc](https://github.com/tpircher/pycrc) - generated CRC function C source code
- [pyserial]() - Python serial communication

## License
[![MIT License](http://img.shields.io/badge/license-MIT-blue.svg?style=flat)](LICENSE)
