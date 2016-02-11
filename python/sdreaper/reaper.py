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
    def __init__(self, port=None, data_dir='data', timeout=0.5, echo=True):
        self.port = port
        self.data_dir = data_dir
        self.timeout = timeout
        self.conn = None
        self.echo = echo
        self._devices_by_id = None
        self._devices_by_name = {}

        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)

    def pr(self, s, end='\n', flush=False):
        if self.echo:
            print(s, end=end, flush=flush)

    def connect(self):
        """Connect to serial port, waiting until it is ready"""
        self.pr('connecting to {} ...'.format(self.port))

        while self.conn is None:
            try:
                self.conn = serial.Serial(port=self.port, timeout=self.timeout)
            except SerialException as se:
                time.sleep(1.0)
                self.pr('.', end='.', flush=True)

        self.pr('\nconnected to {}'.format(self.port))
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
            size = int(file_info.split()[2])

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

    def info(self):
        self.send_command('info')
        fields = {}
        for line in self.read(stringify=True).splitlines():
            name, value = line.split('\t')
            fields[name] = value
        return fields

    def cp(self, sd_filename, local_filename, size, progress_fun=None):
        self.send_command('cp {}'.format(sd_filename))
        self.receiveFile(local_filename, size, progress_fun)

    def ls(self):
        """Get list of files"""
        self.send_command('ls')
        result = []
        listing = self.read(stringify=True)

        current_dir = []
        prev_level = 0
        for line in listing.splitlines()[1:]:
            level = int((len(line) - len(line.lstrip())) / 2)
            date, time, size, name = line.split()

            if name.endswith('/'):
                current_dir[level:] = [name]
            else:
                current_dir = current_dir[0:level]
                result.append(dict(
                    name=''.join(current_dir + [name]),
                    size=int(size),
                    last_modified=' '.join([date, time])))

            name = current_dir
            prev_level = level
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

    def set_device_name(self, name, device_id):
        if self._devices_by_id is None:
            self._read_devices()
        if self._devices_by_name.get(name):
            return False

        self._devices_by_id[device_id] = name
        self._devices_by_name[name] = device_id
        self._write_devices()
        return True

    def get_device_name(self, device_id):
        if self._devices_by_id is None:
            self._read_devices()
        return self._devices_by_id.get(device_id)

    def get_device_id(self, name):
        if self._devices_by_id is None:
            self._read_devices()
        return self._devices_by_name.get(name)

    @property
    def device_file(self):
        return os.path.join(self.data_dir, 'devices.txt')

    def _read_devices(self):
        self._devices_by_name = {}
        pat = '^(?!#)(.+)=\\s(.+)'
        try:
            with open(self.device_file, 'r') as f:
                for line in f:
                    if not line.startswith('#'):
                        try:
                            name, code = line.rsplit('=', 1)
                            self._devices_by_name[name.strip()] = code.strip()

                        except Exception as e:
                            pass
            self._devices_by_id = {
                code: name for name, code in self._devices_by_name.items()
            }

        except:
            self._devices_by_id = {}

    def _write_devices(self):
        header = '\n'.join([
            '# Names for devices based on their device ids, format:',
            '#',
            '#  name = code',
            '#',
            '# name is space trimmed, but can contain spaces',
            '# Blank lines are ignored. Codes and names should be unique.',
            '',
        ])

        with open(self.device_file, 'w+') as f:
            print(header, file=f)
            for code, name in self._devices_by_id.items():
                print('{0:20s} = {1}'.format(name, code), file=f)


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
        rate = round(float(self._bytes_written) / 1000 / elapsed, 1)
        return 'received {} bytes in {} seconds, rate: {} KB/s'.format(
            self._bytes_written, round(elapsed, 2), rate)
