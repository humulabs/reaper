#!/usr/bin/env python

"""
Usage: sdreaper [options] [<command>...]

Examples:
    sdreaper
    sdreaper -d c:\\tag-data

Options:
  -r --run                 begin download automatically
  -d DATA --data=DATA      data directory to use [default: data]

Advanced Options:
  -p PORT --port=PORT      Port to use. By default the port is auto detected.
  --monitor                monitor and print serial output
  --get-time               get device time, assumed to be UTC
  --set-time               set device time to current system time, in UTC
  --find-devices           list connected Arduino Reaper boards
  --no-rm                  do not remove files after download, by default
                           files are removed after they are downloaded
  -h --help                show help
  --version                show version
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

    if args['--find-devices']:
        print('Finding devices...\n')
        for p in Reaper.find():
            print(p)
        return

    port = args.get('--port')
    if not port:
        try:
            port = Reaper.find()[0]
        except IndexError:
            print('Unable to auto-detect device. Please check connection.\n'
                  'If device is connected you may need to specify port'
                  ' with -p')
            return 1

    reaper = Reaper(port=port, data_dir=args['--data'])
    reaper.connect()

    if args['--monitor']:
        while True:
            reaper.read()
    elif args['--get-time']:
        reaper.echo = False
        print(reaper.get_time())
    elif args['--set-time']:
        reaper.echo = False
        print(reaper.set_time())
    elif args['<command>']:
        reaper.commands(args['<command>'])
    else:
        reaper.echo = False
        App(reaper, not args['--no-rm'], args['--run'])

    reaper.disconnect()

if __name__ == '__main__':
    sys.exit(main())
