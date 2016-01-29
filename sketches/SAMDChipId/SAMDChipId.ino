/**
 * Print SAMD chip serial number.
 *
 * http://atmel.force.com/support/articles/en_US/FAQ/Reading-unique-serial-number-on-SAM-D20-SAM-D21-SAM-R21-devices
 */
void setup() {
  Serial.begin(9600);
  delay(1000);
}

void loop() {
  printChipId();
  delay(3000);
}

void printChipId() {
  volatile uint32_t val1, val2, val3, val4;
  volatile uint32_t *ptr1 = (volatile uint32_t *)0x0080A00C;
  val1 = *ptr1;
  volatile uint32_t *ptr = (volatile uint32_t *)0x0080A040;
  val2 = *ptr;
  ptr++;
  val3 = *ptr;
  ptr++;
  val4 = *ptr;

  Serial.print("chip id: 0x");
  char buf[33];
  sprintf(buf, "%8x%8x%8x%8x", val1, val2, val3, val4);
  Serial.println(buf);
}
