#!/usr/bin/env python

"""
Usage: sdreaper [options] [<command>...]
       sdreaper -h | --help | --version

Examples:
    # connect and print serial output
    sdreaper -p /dev/tty.usbmodem1421 -b 9600

    # run a single command
    sdreaper -p /dev/tty.usbmodem1421 -b 9600 list

    # run a list of commands
    sdreaper -p /dev/tty.usbmodem1421 -b 9600 list list exit

Options:
  -p PORT --port=PORT        serial port to use
  -b BAUD --baud=BAUD        baud rate
  -h --help                  show help
  --version                  show version

Connect to Arduino Reaper on serial port, send the specified commands and
print the results. If no commands are given then run as a read-only serial
monitor. It is okay to run sdreaper before the Arduino is connected: sdreaper
will wait until the serial port is ready.
"""

import sys
from docopt import docopt
from sdreaper.reaper import Reaper


def main():
    args = docopt(__doc__, version='sdreaper 1.0.1')

    reaper = Reaper(port=args['--port'], baud=args['--baud'])
    reaper.connect()

    commands = args['<command>']
    if not commands:
        while True:
            reaper.read()
    else:
        reaper.commands(commands)

if __name__ == '__main__':
    sys.exit(main())
