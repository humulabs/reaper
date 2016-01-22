#include <SPI.h>
#include <SdFat.h>
#include <Reaper.h>

const int chipSelect = 10;

Reaper reaper = Reaper(SerialUSB, chipSelect);

void setup()
{
  SerialUSB.begin(9600);
  while (!SerialUSB);

  SerialUSB.println("\n++ Init Card ++ ");
  reaper.init();

  SerialUSB.println("\n++ List Files ++ ");
  reaper.listFiles();
  SerialUSB.write(EOF);
}

void loop(void) {
}
