#!/usr/bin/env python

"""
Usage: sdreaper [options] [<command>...]
       sdreaper -h | --help | --version

Examples:
    # launch UI using default USB port
    sdreaper

    # launch UI with specified USB port
    sdreaper -p COM6

Options:
  -p PORT --port=PORT      USB port to use [default: /dev/tty.usbmodem1421]
  -d DATA --data=DATA      data directory to use [default: data]
  -r --run                 begin download automatically
  --monitor                monitor and print serial output (diagnostic use)
  --get-time               get device time, assumed to be UTC
  --set-time               set device time to current system time, in UTC
  --no-rm                  do not remove files after download, by default
                           files are removed after they are downloaded
  -h --help                show help
  --version                show version

Interactive utility app to work with board running Arduino Reaper library.
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

    reaper = Reaper(port=args['--port'], data_dir=args['--data'])
    reaper.connect()

    commands = args['<command>']
    if args['--monitor']:
        while True:
            reaper.read()
    elif args['--get-time']:
        reaper.echo = False
        print(reaper.get_time())
    elif args['--set-time']:
        reaper.echo = False
        print(reaper.set_time())
    elif commands:
        reaper.commands(commands)
    else:
        reaper.echo = False
        App(reaper, not args['--no-rm'], args['--run'])

if __name__ == '__main__':
    sys.exit(main())
