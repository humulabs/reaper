#include <SPI.h>
#include <SdFat.h>
#include "Xmodem.h"

const int chipSelect = 10;

SdFat sd;
File file;
Xmodem xm(SerialUSB);

void setup()
{
  SerialUSB.begin(9600, SERIAL_8N1);
  while (!SerialUSB);

  Serial.begin(9600);
  Serial.println("\n++ Init Card ++ ");
  if (!sd.begin(chipSelect, SPI_HALF_SPEED)) {
  	Serial.println("unable to init SD card");
  }
  Serial.println("OK");

  file = sd.open("booyah.txt");
  Serial.println("opened file");
  xm.send(&file);
  file.close();
  Serial.println("--done--");
}

void loop(void) {
}
