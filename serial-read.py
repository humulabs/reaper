import serial
import sys

EOT = 0x04

port = serial.Serial(port=sys.argv[1],
                     parity=serial.PARITY_NONE,
                     bytesize=serial.EIGHTBITS,
                     stopbits=serial.STOPBITS_ONE,
                     timeout=1,
                     baudrate=sys.argv[2])

data = []
while True:
    bytesRead = port.read(size=1)
    if bytesRead and bytesRead[0] == EOT:
        break
    data.append(bytesRead)

print('read {} bytes'.format(len(data)))
