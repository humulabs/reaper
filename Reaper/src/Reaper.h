#ifndef Reaper_h
#define Reaper_h

#include "Arduino.h"
#include <SdFat.h>
#include <SPI.h>

class Reaper {
  public:
    Reaper();
    Reaper(Stream& stream, int chipSelect);
    void init();
    void listFiles();

  private:
    Stream* _stream;
    int _chipSelect;
    SdFat _sd;
};

#endif
