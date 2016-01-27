const uint8_t EOT = 0x04;
const uint8_t CHAR = 'x';

const unsigned long SIZE    = 1024 * 10 * 10;

// I think SerialUSB may ignore baud:
// https://www.pjrc.com/teensy/td_serial.html
const unsigned long BAUD    = 115200;


// arduino/samd/cores/arduino/USB/samd21_device.c indicated 128 is the largest
// buffer we can use safely.
// https://forum.arduino.cc/index.php?topic=340897.0
// I do get a port connect/detach then error if I try sizes like 768 or 1024
const size_t BATCH_SIZE     = 128;

char BUFFER[BATCH_SIZE];

void setup()
{
  Serial.begin(9600);
  SerialUSB.begin(BAUD);
  while(!SerialUSB);

  usbInfo();
  setFullSpeed();
  usbInfo();

  Serial.print("SIZE=");
  Serial.println(SIZE);

  Serial.print("BAUD=");
  Serial.println(BAUD);

  Serial.print("BATCH_SIZE=");
  Serial.println(BATCH_SIZE);


  for (int i = 0; i < BATCH_SIZE; i++) {
    BUFFER[i] = CHAR;
  }
  unsigned long t1 = millis();

  sendBytes(SIZE);

  SerialUSB.write(EOT);
  SerialUSB.end();
  unsigned long t2 = millis();

  float durationSeconds = (float)(t2 - t1) / 1000;
  Serial.print("duration seconds: ");
  Serial.println(durationSeconds);
  Serial.print("rate: ");
  Serial.print((float)SIZE / durationSeconds);
  Serial.println(" bytes/second");
}

void usbInfo() {
  Serial.print("REG_USB_DEVICE_STATUS: ");
  Serial.println(REG_USB_DEVICE_STATUS, HEX);

  Serial.print("USB->DEVICE.STATUS.reg: ");
  Serial.println(USB->DEVICE.STATUS.reg, HEX);

  Serial.print("USB->DEVICE.STATUS.bit.SPEED: ");
  Serial.println(USB->DEVICE.STATUS.bit.SPEED, HEX);
}

void sendBytes(unsigned long count) {
  int numBatches = count / BATCH_SIZE;

  int lastPct = -1;
  for (int i = 0; i < numBatches; i++) {
    SerialUSB.write(BUFFER, BATCH_SIZE);
    int pct = (i * 100) / numBatches;
    if (pct % 5 == 0 && pct != lastPct) {
      Serial.print(pct);
      Serial.print("..");
      lastPct = pct;
    }
  }

  for (int i = 0; i < count - BATCH_SIZE * numBatches; i++) {
    SerialUSB.write(CHAR);
  }
  Serial.println();
}

void setFullSpeed() {
  // is this right? i think we're already at full speed
  // from CMSIS/Device/ATMEL/samd21/include/component/usb.h
  // USB->DEVICE.CTRLB.bit.SPDCONF = USB_DEVICE_CTRLB_SPDCONF_0;
}

void loop(void) {
}
