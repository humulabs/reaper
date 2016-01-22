import time
import serial
from serial.serialutil import SerialException

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

    def read(self, callback=None):
        """Read until EOF and return as bytes read, not including EOF"""
        data = []
        while True:
            ch = self.conn.read()[0]
            if ch == EOF:
                return data
            if callback is not None:
                callback(ch)
            data.append(ch)
