import time
import timeit
import os
import io
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
    def __init__(self, port=None, baud=None, timeout=0.5, echo=True):
        self.port = port
        self.baud = baud
        self.timeout = timeout
        self.conn = None
        self.echo = echo

    def pr(self, s, end='\n', flush=False):
        if self.echo:
            print(s, end=end, flush=flush)

    def connect(self):
        """Connect to serial port, waiting until it is ready"""
        self.pr('connecting to {} at {} baud...'.format(self.port, self.baud))

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
                self.pr('.', end='.', flush=True)

        self.pr('\nconnected to {} at {} baud.'.format(self.port, self.baud))
        time.sleep(.1)

    def read(self, timeout=None, stringify=False):
        """Read until EOT and return data read, not including EOT

        :param timeout: how long to wait for response to complete
        :param stringify: if True return a string from ASCII bytes, else
            return the bytes as is
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
            self.pr(chr(bytesRead[0]), end='', flush=True)
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
                self.pr(response, flush=True)

    def commands(self, commands):
        """Run a list of commands and return results"""
        self.read(timeout=3)
        results = []
        for cmd in commands:
            results.append(self.command(cmd))
        return results

    def command(self, command):
        """Run a single command and return results"""
        parts = command.split()
        verb = parts[0]
        if verb == 'cp':
            # get file size
            filename = parts[1]
            self.send_command('ls {}'.format(filename))
            file_info = self.read(stringify=True)
            size = int(file_info.split('\t')[1])

            # receive file
            path = filename.split('/')
            local_filename = os.path.join('.', *path)
            self.send_command(command)

            def progress_fun(num_bytes, w):
                print('.', end='', flush=True)

            self.echo = False
            self.receiveFile(local_filename, size, progress_fun)
            self.echo = True

            print('received {}, size={}'.format(filename, size))
        elif verb == 'info':
            self.send_command(command)
            return self.read()
        else:
            self.send_command(command)
            return self.read()

    def cp(self, sd_filename, local_filename, size, progress_fun=None):
        self.send_command('cp {}'.format(sd_filename))
        self.receiveFile(local_filename, size, progress_fun)

    def ls(self):
        """Get list of files"""
        self.send_command('ls')
        result = []
        listing = self.read(stringify=True)
        for entry in listing.splitlines()[1:]:
            fields = entry.split('\t')
            result.append(dict(
                name=fields[0],
                size=int(fields[1]),
                last_modified=fields[2]))
        return result

    def send_command(self, command):
        self.sync()
        time.sleep(.01)
        for c in command.rstrip('\n'):
            self.conn.write([ord(c)])
            time.sleep(.01)
        self.conn.write([ord('\n')])
        self.conn.flush()
        time.sleep(.01)

    def receiveFile(self, filename, size, progress_fun):
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
            stream = StreamWriter(f, progress_fun)
            xm.recv(stream)
            report = stream.report()
            f.truncate(size)
            self.conn.timeout = self.timeout
        return report

class StreamWriter(object):
    def __init__(self, writer, progress_fun=None):
        self._w = writer
        self._bytes_written = 0
        self._start_time = timeit.default_timer()
        self._latest_time = self._start_time
        self._progress_fun = progress_fun

    @property
    def bytes_written(self):
        return self._bytes_written

    def write(self, b):
        count = self._w.write(b)
        self._latest_time = timeit.default_timer()
        self._bytes_written += count
        if self._progress_fun:
            self._progress_fun(count, self)
        return count

    def report(self):
        elapsed = self._latest_time - self._start_time
        rate =  round(float(self._bytes_written) / 1000 / elapsed, 1)
        return 'received {} bytes in {} seconds, rate: {} KB/s'.format(
              self._bytes_written, round(elapsed, 2), rate)
