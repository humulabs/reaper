import serial
import sys
import timeit

EOT = 0x04

port = serial.Serial(port=sys.argv[1],
                     parity=serial.PARITY_NONE,
                     bytesize=serial.EIGHTBITS,
                     stopbits=serial.STOPBITS_ONE,
                     timeout=1,
                     baudrate=sys.argv[2])

data = []

dot = 10 * 1024
print('reading data, printing a dot "." every {} bytes'.format(dot))
start_time = timeit.default_timer()
while True:
    if port.inWaiting() > 0:
        inData = port.read(size=1)
        if inData[0] == EOT:
            break
        if len(data) % dot == 0:
            print('.', end='', flush=True)
        data += inData

elapsed = timeit.default_timer() - start_time

print('\nread {} bytes in {} seconds'.format(len(data), elapsed))
print('rate = {}'.format(float(len(data)) / elapsed))
