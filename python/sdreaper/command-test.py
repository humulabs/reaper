#!/usr/bin/env python

"""
Usage: command-test [options] COUNT

Arguments:
  COUNT   number of echos to test [default: 10]

Options:
  -p PORT --port=PORT        serial port to use
  -b BAUD --baud=BAUD        baud rate
  -h --help                  show help
  --version                  show version
"""

import sys
from docopt import docopt
from sdreaper.reaper import Reaper

def main():
    args = docopt(__doc__, version='command-test 1.0.0')

    reaper = Reaper(port=args['--port'], baud=args['--baud'])
    reaper.connect()

    count = int(args['COUNT'])
    strings = [str(i) for i in range(count)]
    responses = []
    print('running {} echo commands'.format(count))
    for s in strings:
        print('.', end='', flush=True)
        responses.append(reaper.command('echo {}'.format(s), printChars=False))

    for i, res in enumerate(responses):
        assert bytes(res).decode('ascii') == '{}\r\n'.format(strings[i])
    print('\nassertions succeeded')
if __name__ == '__main__':
    sys.exit(main())
