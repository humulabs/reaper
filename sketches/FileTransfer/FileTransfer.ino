#include <SPI.h>
#include <SdFat.h>
#include "Xmodem.h"

const int chipSelect = 10;

SdFat sd;
File file;
Xmodem xm(SerialUSB);

void setup()
{
  SerialUSB.begin(12582912, SERIAL_8N1);
  while (!SerialUSB);

  Serial.begin(9600);
  Serial.println("\n++ Init Card ++ ");
  if (!sd.begin(chipSelect, SPI_HALF_SPEED)) {
  	Serial.println("unable to init SD card");
  }
  Serial.println("OK");

  unsigned long t1 = millis();
  file = sd.open("file-10MB");
  // file = sd.open("booyah.txt");
  Serial.println("opened file");
  xm.send(&file);
  unsigned long t2 = millis();
  float durationSeconds = (float)(t2 - t1) / 1000;

  Serial.print("duration seconds: ");
  Serial.println(durationSeconds);

  Serial.print("file size: ");
  Serial.println(file.size());

  Serial.print("transfer rate: ");
  Serial.print((float)file.size() / durationSeconds);
  Serial.println(" bytes/second");
  file.close();
}

void loop(void) {
}
