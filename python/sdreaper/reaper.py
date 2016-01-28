import time
import os
import serial
from serial.serialutil import SerialException
from xmodem import XMODEM1k


# ASCII Control Codes
# -------------------

# terminates command output send from board
EOT = 0x04

# used to sync communication, board replies with SYN when it receives one
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

    def read(self, printChars=True, timeout=None, stringify=False):
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
                break
            t2 = time.time()
            if timeout is not None and t2 - t1 > timeout:
                break
            if printChars:
                print(chr(bytesRead[0]), end='', flush=True)
            data.append(bytesRead[0])

        if stringify:
            return ''.join([chr(b) for b in data])
        else:
            return data

    def sync(self):
        while True:
            self.conn.write([SYN])
            time.sleep(.01)
            response = self.read(timeout=1)
            if response and response[0] == SYN:
                return
            elif response:
                print(response, flush=True)

    def commands(self, commands):
        self.read(timeout=3)
        results = []
        for cmd in commands:
            results.append(self.command(cmd))
        return results

    def command(self, command):
        parts = command.split()
        verb = parts[0]
        if verb == 'cp':

            # get file size
            filename = parts[1]
            self.send_command('ls {}'.format(filename))
            file_info = self.read(stringify=True, printChars=False)
            size = int(file_info.split('\t')[1])

            # receive file
            path = filename.split('/')
            local_filename = os.path.join('.', *path)
            self.send_command(command)
            self.receiveFile(local_filename, size)

            print('received {}, size={}'.format(filename, size))

        else:
            self.send_command(command)
            return self.command_response()

    def send_command(self, command):
        self.sync()
        time.sleep(.01)
        for c in command.rstrip('\n'):
            self.conn.write([ord(c)])
            time.sleep(.01)
        self.conn.write([ord('\n')])
        self.conn.flush()
        time.sleep(.01)

    def command_response(self):
        return self.read(printChars=True)

    def receiveFile(self, filename, size):
        def getc(size, timeout=1):
            self.conn.timeout = timeout
            data = self.conn.read(size)
            if len(data) == 0:
                data = None
            return data

        def putc(data, timeout=1):
            return self.conn.write(data)

        xm = XMODEM1k(getc, putc)
        with open(filename, 'wb+') as f:
            xm.recv(f)
            f.truncate(size)
            self.conn.timeout = self.timeout
