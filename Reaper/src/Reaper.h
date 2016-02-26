#ifndef Reaper_h
#define Reaper_h

#include "Arduino.h"
#include <SdFat.h>
#include <SPI.h>
#include "Xmodem.h"

#ifdef ARDUINO_ARCH_SAMD
#include <RTCZero.h>
#endif

class Reaper {
  public:
    Reaper();
    Reaper(Stream& stream, int chipSelect);
    void init();
    void listFiles();
	void listFile(char *filename);
    void sendFile(char *filename);
    void rm(char *filename);
    void info();
#ifdef ARDUINO_ARCH_SAMD
    void setDateTime(uint8_t year,    // 0 -> 2000
                     uint8_t month,
                     uint8_t day,
                     uint8_t hours,
                     uint8_t minutes,
                     uint8_t seconds);
    void setDateTime(uint8_t fields[6]);
    void getDateTime(uint8_t *fields);

#endif
  private:
	Xmodem _xmodem;
    Stream* _stream;
    int _chipSelect;
    SdFat _sd;
#ifdef ARDUINO_ARCH_SAMD
    RTCZero _rtc;
#endif
};

#endif
