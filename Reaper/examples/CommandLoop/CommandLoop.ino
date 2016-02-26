#include <SPI.h>
#include <SdFat.h>
#include <Reaper.h>

#include <ReaperCommandProcessor.h>

const int chipSelect = 10;

Reaper reaper = Reaper(SerialUSB, chipSelect);
ReaperCommandProcessor proc(SerialUSB, reaper);

void setup()
{
  pinMode(13, OUTPUT);
  digitalWrite(13, LOW);

  SerialUSB.begin(9600);
  Serial.begin(9600, SERIAL_8N1);
  while (!SerialUSB);

  SerialUSB.println("\n++ Init Card ++ ");
  reaper.init();
  SerialUSB.println("OK");
  Serial.println("Ready");
  digitalWrite(13, LOW);
}

void loop(void) {
  proc.processCommands();
}
