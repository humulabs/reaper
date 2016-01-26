import serial
try:
    from StringIO import StringIO
except:
    from io import StringIO
from xmodem import XMODEM1k
from time import sleep
import logging
import sys

logging.basicConfig(format='%(levelname)-5s %(message)s',
                    level=logging.DEBUG)

port = serial.Serial(port=sys.argv[1],
                     parity=serial.PARITY_NONE,
                     bytesize=serial.EIGHTBITS,
                     stopbits=serial.STOPBITS_ONE,
                     timeout=None,
                     xonxoff=0,
                     rtscts=0,
                     dsrdtr=0,
                     baudrate=9600)

def readUntil(char = None):
    def serialPortReader():
        while True:
            tmp = port.read(1)
            if not tmp or (char and char == tmp):
                break
            yield tmp
    return ''.join(serialPortReader())

def getc(size, timeout=1):
    port.timeout = timeout
    data = port.read(size)
    # if len(data) == 0:
    #     data = None
    return data

def putc(data, timeout=None):
    return port.write(data)


f = open('file-received', 'wb+')

xm = XMODEM1k(getc, putc)
len = xm.recv(f)
f.close()
