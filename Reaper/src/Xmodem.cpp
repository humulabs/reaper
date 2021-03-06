#include "Xmodem.h"

/**
 * Construct an Xmodem instance.
 *
 * @param serial port to use
 */
Xmodem::Xmodem(Stream& serial, int led) {
#ifdef ARDUINO
  _serial = &serial;
  _led = led;
  if (_led > -1) {
    pinMode(_led, OUTPUT);
  }
#else
  _serial = *serial;
#endif // ifdef ARDUINO
}

/**
 * Send a file over the serial port.
 * @param file file to send
 */
int Xmodem::send(File* file) {
  _file = file;
  _packetNumber = 1;
  beginLed();

  while (true) {
    int c = serialRead();
    if (c != -1) {
      resetTimer();
      break;
    }
    delay(100);
  }

  int status = 0;
  while (true) {
    size_t bytesRead = readPacket();
    resetTimer();
    if (bytesRead > 0) {
      status = sendPacket();
      if (_packetNumber % 20 == 0) {
        toggleLed();
      }
      if (status < 0) {
        break;
      }
    }
    if (bytesRead < PACKET_SIZE) {
      break;
    }
  }
  serialWrite(EOT);
  while (serialRead() == -1);
  endLed();
  return status;
}

/**
 * @internal
 *
 * Send the current packet over the serial port and handle response.
 *
 *  + NAK - resend packet
 *  + ACK - advance packet counter and return
 *  + CAN - return
 *
 * @return 0 if ACK-ed or NAK-ed, -1 if CAN-ed, -2 if timed out
 */
int Xmodem::sendPacket() {
  serialWrite(STX);
  serialWrite(_packetNumber);
  serialWrite(255 - _packetNumber);
  serialWrite(_packet, PACKET_SIZE);
  serialWrite((_crc >> 8) & 0xff);
  serialWrite(_crc & 0xff);

  int c;
  while (true) {
    c = serialRead();
    if (c == NAK) {
      delay(5);
      return 0;
    }
    else if (c == ACK) {
      _packetNumber++;
      return 0;
    }
    else if (c == CAN) {
      return -1;
    }
    else if (millis() - _timer > SEND_TIMEOUT) {
      Serial.println("receiver timed out");
      return -2;
    }
  }
}

/**
 * Read current packet from current file. Pad the packet with PAD_CHAR if the
 * file has less than PACKET_SIZE bytes left to read.
 *
 * @return the number of bytes read from the file
 */
size_t Xmodem::readPacket() {
  size_t bytesRead = fileRead(_packet, PACKET_SIZE);
  for (size_t i = bytesRead; i < PACKET_SIZE; i++) {
    _packet[i] = PAD_CHAR;
  }

  _crc = crc_init();
  _crc = crc_update(_crc, _packet, PACKET_SIZE);
  _crc = crc_finalize(_crc);

  return bytesRead;
}

/**
 * @internal
 *
 * Read a block from a file.
 *
 * @param  buffer  buffer to hold data read from file
 * @param  count   number of bytes to read from file
 * @return         number of bytes actually read
 */
size_t Xmodem::fileRead(uint8_t *buffer, size_t count) {
#ifdef ARDUINO
  int n = _file->read(buffer, count);
  return n < 0 ? 0 : (size_t)n;
#else
  return fread(buffer, 1, count, _file);
#endif // ifdef ARDUINO
}

/**
 * @internal
 *
 * Write a block of data to the serial port.
 *
 * @param  buffer data to write
 * @param  count  number of bytes to write
 * @return        number of bytes actually written
 */
size_t Xmodem::serialWrite(uint8_t *buffer, size_t count) {
#ifdef ARDUINO
  uint8_t *current = buffer;
  int remaining = count;
  int batchSize = 128;
  size_t written = 0;
  while (remaining > 0) {
    int currentBatchSize = min(batchSize, remaining);
    written += _serial->write(current, currentBatchSize);
    current += currentBatchSize;
    remaining -= currentBatchSize;
  }
  return written;

#else
  return write(_serial, buffer, count);
#endif // ifdef ARDUINO
}

/**
 * @internal
 *
 * Write a byte to the serial port.
 *
 * @param  c byte to write
 * @return c if byte written, or -1 if error
 */
int Xmodem::serialWrite(uint8_t c) {
#ifdef ARDUINO
  return _serial->write(c);
#else
  return write(_serial, &c, 1);
#endif // ifdef ARDUINO
}

/**
 * @internal
 *
 * Read a byte from the serial port.
 *
 * @return byte read, or -1 no data is available to read
 */
int Xmodem::serialRead() {
#ifdef ARDUINO
  return _serial->read();
#else
  uint8_t c;
  size_t bytesRead = read(_serial, &c, 1);
  if (bytesRead == 0) {
    return -1;
  }
  else {
    return (int)c;
  }
#endif // ifdef ARDUINO
}
