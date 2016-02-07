#!/usr/bin/env python

"""
Usage: sdreaper [options] [<command>...]
       sdreaper -h | --help | --version

Examples:
    # run interactively
    sdreaper -p /dev/tty.usbmodem1421

    # connect and print serial output
    sdreaper -p /dev/tty.usbmodem1421 --monitor

    # run a single command
    sdreaper -p /dev/tty.usbmodem1421 ls

    # run multiple commands
    sdreaper -p /dev/tty.usbmodem1421 ls ls

Options:
  -p PORT --port=PORT        serial port to use
  -b BAUD --baud=BAUD        baud rate, ignored if port is SerialUSB on
                             Arduino [default: 9600]
  --monitor                  monitor and print serial output
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
from sdreaper.app import App
import logging

logging.basicConfig(format='%(levelname)-5s %(message)s',
                    filename='sdreaper.log',
                    level=logging.INFO)


def main():
    args = docopt(__doc__, version='sdreaper 1.0.1')

    reaper = Reaper(port=args['--port'], baud=args['--baud'])
    reaper.connect()

    commands = args['<command>']
    if args['--monitor']:
        while True:
          reaper.read()
    elif commands:
        reaper.commands(commands)
    else:
        reaper.echo = False
        App(reaper)

if __name__ == '__main__':
    sys.exit(main())
