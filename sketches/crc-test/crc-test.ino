#include "crc.h"

/**
 * Test CRC lib. CRC lib generated by https://pycrc.org
 * and tweaked for Arduino.
 */

void setup()
{
  SerialUSB.begin(9600);
  while (!SerialUSB);

  const char* str = "HELLO";
  crc_t crc = crc_init();
  crc = crc_update(crc, (void *)str, strlen(str));
  crc = crc_finalize(crc);

  SerialUSB.println(crc, HEX);
}

void loop()
{
}