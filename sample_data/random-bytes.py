#!/usr/bin/env python

"""
Usage: random-bytes [-t | --text] <count>

Options:
  -t --text  only include printable characters

Generate <count> pseudo-random bytes to standard out.
"""

from docopt import docopt
import sys
from random import randint

if __name__ == '__main__':
    args = docopt(__doc__)

    try:
        count = int(args['<count>'])
    except ValueError:
        print("count must be an integer")
        sys.exit(1)

    if args['--text']:
        start = 0x20
        end = 0x7e
    else:
        start = 0
        end = 0xff

# not optimized
for _ in range(count):
    val = randint(start, end)
    sys.stdout.buffer.write(bytes([val]))

