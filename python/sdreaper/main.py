#!/usr/bin/env python

"""
Usage: sdreaper [options] <command>
       sdreaper -h | --help | --version

Examples:
    # connect and print serial output
    sdreaper -p /dev/tty.usbmodem1421 -b 9600 print

Options:
  -p PORT --port=PORT        serial port to use
  -b BAUD --baud=BAUD        baud rate
  -h --help                  show help
  --version                  show version

Commands:
   print    read and print serial port output until EOF

Connect to Arduino Reaper on serial port and perform the specified actions.
It is okay to run sdreaper before the Arduino is connected: sdreaper will wait
until the serial port is ready.
"""

import sys
from docopt import docopt
from sdreaper.reaper import Reaper


def main():
    args = docopt(__doc__, version='sdreaper 1.0.1')

    # connect and read once
    cmd = args['<command>']
    if cmd == 'print':
        reaper = Reaper(port=args['--port'], baud=args['--baud'])
        reaper.connect()

        def printer(ch):
            print(chr(ch), end='', flush=True)

        reaper.read(callback=printer)
    else:
        exit('"{}"" is not a valid command. See "sdreaper -h".'.format(cmd))

if __name__ == '__main__':
    sys.exit(main())
