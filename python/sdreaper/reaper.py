import time
import serial
from serial.serialutil import SerialException

# control codes
EOT = 0x04
SYN = 0x16

class Reaper(object):
    def __init__(self, port=None, baud=None, timeout=0.5):
        self.port = port
        self.baud = baud
        self.timeout = timeout
        self.conn = None

    def connect(self):
        """Connect to serial port, waiting until it is ready"""
        print('connecting to {} at {} baud...'.format(self.port, self.baud))

        while self.conn is None:
            try:
                self.conn = serial.Serial(port=self.port,
                                          baudrate=self.baud,
                                          bytesize=serial.EIGHTBITS,
                                          parity=serial.PARITY_NONE,
                                          stopbits=serial.STOPBITS_ONE,
                                          timeout=self.timeout)
            except SerialException as se:
                time.sleep(1.0)
                print('.', end='.', flush=True)

        print('\nconnected to {} at {} baud.'.format(self.port, self.baud))
        time.sleep(.1)

    def read(self, printChars=True, timeout=None):
        """
        Read until EOT and return as bytes read, not including EOT. If
        printChars is True then print each character as it is read.
        """
        data = []
        t1 = time.time()
        t2 = 0
        while True:
            bytesRead = self.conn.read(size=1)
            if not bytesRead or bytesRead[0] == EOT:
                return data
            t2 = time.time()
            if timeout is not None and t2 - t1 > timeout:
                return data
            if printChars:
                print(chr(bytesRead[0]), end='', flush=True)
            data.append(bytesRead[0])

    def sync(self):
        while True:
            self.conn.write([SYN])
            time.sleep(.01)
            # print('*', end='', flush=True)
            response = self.read(timeout=1)
            if response and response[0] == SYN:
                # print('SYN\n')
                return

    def commands(self, commands, printChars=True):
        self.read(timeout=3)
        results = []
        for cmd in commands:
            results.append(self.command(cmd))
        return results

    def command(self, command, printChars=True):
        # print('sending {}\n'.format(command))
        self.sync()
        time.sleep(.01)
        for c in command.rstrip('\n'):
            self.conn.write([ord(c)])
            time.sleep(.01)
        self.conn.write([ord('\n')])
        self.conn.flush()
        time.sleep(.01)
        return self.read(printChars=printChars)

    def receiveFile(self):
        def getc(size, timeout=1):
            data = self.conn.read(size)
            return data

        def putc(data, timeout=1):
            return self.conn.write(data)

        from xmodem import XMODEM1k
        xm = XMODEM1k(getc, putc)
        with open('foo.dat', 'wb+') as f:
            xm.recv(f)

