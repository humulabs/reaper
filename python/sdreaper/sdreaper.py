#!/usr/bin/env python

"""
Usage: sdreaper -p PORT -b BAUD
       sdreaper -h | --help | --version

Options:
  -p PORT --port=PORT        serial port to use
  -b BAUD --baud=BAUD        baud rate
  -h --help      show help
  --version      show version

Connect to Arduino Reaper on serial port. It is okay to start sdreaper
before the Arduino is connected: sdreaper will wait until serial port is ready.
"""

import sys
import time

import serial
from serial.serialutil import SerialException
from docopt import docopt

# Arduino Reaper EOF
EOF = 0xff


class Reaper(object):
    def __init__(self, port=None, baud=None):
        self.port = port
        self.baud = baud
        self.conn = None

    def connect(self):
        """Connect to serial port, waiting until it is ready"""
        print('connecting to {} at {} baud...'.format(self.port, self.baud))

        while self.conn is None:
            try:
                self.conn = serial.Serial(self.port, self.baud)
            except SerialException as se:
                time.sleep(1.0)
                print('.', end='.', flush=True)

        print('\nconnected to {} at {} baud.'.format(self.port, self.baud))


    def read(self):
        """Read and print data until EOF"""
        while True:
            ch = self.conn.read()
            if ch[0] == EOF:
                return
            print(ch.decode(), end='', flush=True)


def main():
    args = docopt(__doc__, version='sdreaper 1.0.1')
    reaper = Reaper(port=args['--port'], baud=args['--baud'])
    reaper.connect()
    reaper.read()


if __name__ == '__main__':
    sys.exit(main())
