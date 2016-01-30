#ifndef Xmodem_h
#define Xmodem_h

#include <stdio.h>
#include "crc.h"

#ifdef ARDUINO
#include <Arduino.h>
#include <SdFat.h>

#else

#include <unistd.h>
#include <fcntl.h>
#define File FILE
#define Stream int

#endif // ifdef ARDUINO

#define STX 0x02
#define EOT 0x04
#define ACK 0x06
#define NAK 0x15
#define CAN 0x18

#define PAD_CHAR 0x00

class Xmodem {
  public:
    Xmodem(Stream& serial, int led=13);
    int send(File* file);

  private:
    static const size_t PACKET_SIZE = 1024;
    static const unsigned long SEND_TIMEOUT = 3000;

    Stream *_serial;
    File *_file;
    uint8_t _packetNumber;
    uint8_t _packet[PACKET_SIZE];
    crc_t _crc;
    unsigned long _timer;
    int _led;
    int _ledState;

    size_t readPacket();
    int sendPacket();
    int serialWrite(uint8_t c);
    size_t serialWrite(uint8_t *buffer, size_t count);
    int serialRead();
    size_t fileRead(uint8_t *buffer, size_t count);

    inline void resetTimer() {
      _timer = millis();
    }

    inline void setLed(int state) {
      if (_led > -1) {
        _ledState = state;
        digitalWrite(_led, _ledState);
      }
    }

    inline void toggleLed() {
      _ledState = !_ledState;
      digitalWrite(_led, _ledState);
    }

    inline void blink(unsigned long interval) {
      if (_led > -1) {
        setLed(HIGH);
        delay(interval);
        setLed(LOW);
        delay(interval);
      }
    }

    inline void beginLed() {
      if (_led > -1) {
        for (uint8_t i = 0; i < 3; i++) {
          blink(100);
        }
        setLed(HIGH);
      }
    }

    inline void endLed() {
      if (_led > -1) {
        setLed(LOW);
      }
    }
};

#ifndef ARDUINO
inline void delay(unsigned long ms) {
  usleep(ms * 1000);
}
#endif // ifndef ARDUINO

#endif // ifndef Xmodem_h
