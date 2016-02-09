#ifndef Reaper_h
#define Reaper_h

#include "Arduino.h"
#include <SdFat.h>
#include <SPI.h>
#include "Xmodem.h"

class Reaper {
  public:
    Reaper();
    Reaper(Stream& stream, int chipSelect);
    void init();
    void listFiles();
	void listFile(char *filename);
    void sendFile(char *filename);
    void info();

  private:
	Xmodem _xmodem;
    Stream* _stream;
    int _chipSelect;
    SdFat _sd;
};

#endif
