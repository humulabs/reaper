import serial
import sys
import timeit
import time

EOT = 0x04

port = None

while port is None:
    try:
        port = serial.Serial(port=sys.argv[1],
                             parity=serial.PARITY_NONE,
                             bytesize=serial.EIGHTBITS,
                             stopbits=serial.STOPBITS_ONE,
                             timeout=None,
                             baudrate=9600)
    except:
        print('.', end='', flush=True)
        time.sleep(1)

print('connected\n')
data = []

dot = 100 * 1024
print('reading data, printing a dot "." every {} bytes'.format(dot))
start_time = timeit.default_timer()

elapsed = None
while True:
    try:
        inData = port.read(size=16384)
        elapsed = timeit.default_timer() - start_time
        data += inData
        if len(data) % 10 * 1024 == 0:
            print('.', end='', flush=True)

    except KeyboardInterrupt as e:
        break

print('\nread {} bytes in {} seconds'.format(len(data), elapsed))
print('rate = {}'.format(float(len(data)) / elapsed))

with open(sys.argv[2], 'wb') as f:
    f.write(bytearray(data))
