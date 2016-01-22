import serial
from serial.serialutil import SerialException

import sys
import time

EOF = 0xff

def readResponse(s):
    while True:
        ch = s.read()

        if ch[0] == EOF:
            return

        print(ch.decode(), end='', flush=True)

if __name__ == '__main__':
    port = sys.argv[1]
    baud = int(sys.argv[2])

    s = None

    print('connecting to {} at {} baud...'.format(port, baud))

    while s is None:
        try:
            s = serial.Serial(port, baud)
        except SerialException as se:
            time.sleep(1.0)
            print('.', end='.', flush=True)

    print('\n+connected+\n')
    readResponse(s)
