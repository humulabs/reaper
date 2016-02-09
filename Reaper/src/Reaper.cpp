#include "Reaper.h"

/**
 * Construct a Reaper instance.
 * @param stream stream to use for command output
 * @param chipSelect chip select pin for SD card
 */
Reaper::Reaper(Stream& stream, int chipSelect) : _xmodem(stream) {
  _stream = &stream;
  _chipSelect = chipSelect;
}

/**
 * Connect to SD card.
 */
void Reaper::init() {
  if (!_sd.begin(_chipSelect, SPI_FULL_SPEED)) {
    if (!_sd.begin(_chipSelect, SPI_HALF_SPEED)) {
      Serial.println(F("Unable to talk to SD card"));
      return;
    }
    Serial.println(F("Connected to SD card at half speed"));
  }
  else {
    Serial.println(F("Connected to SD card at full speed"));
  }
}

/**
 * @internal
 *
 * Print file detail line to stream.
 *
 * @param stream     stream to use
 * @param file       file entry
 * @param path       full path to file
 */
void printFileDetails(Stream* stream, File file, String path) {
  stream->print(path);
  stream->print('\t');
  stream->print(file.fileSize(), DEC);
  stream->print('\t');
  file.printModifyDateTime(stream);
  stream->println();
}

/**
 * Print device information. Device information consists of
 * named fields printed one per line. Each line is of the form:
 *
 *    name '\t' value.
 *
 * Bytes are printed in hex, preceded by 0x.
 *
 * The following fields are available:
 *
 *   + **samd_id** - id of MCU if it is a SAMD chip,
 *                   see: http://tinyurl.com/atmel-samd-chip-id
 *
 * The following fields are from the SD CID register, see
 * https://www.sdcard.org/downloads/pls/index.html for details:
 *
 *   + **sd_mid** - Manufacturer id, one byte
 *   + **sd_oid** - OEM id, two bytes
 *   + **sd_pnm** - product name, 5 ASCII chars
 *   + **sd_prv** - product revision, 3 ASCII chars of form "N.M"
 *   + **sd_psn** - product serial number, 4 bytes
 *   + **sd_mdt** - manufacturing date, ASCII of form "m/yyyy" or "mm/yyyy"
 *   + **sd_size** - card capacity in 512 byte blocks, printed as decimal integer
 */
void Reaper::info() {
  char buf[33];

  // MCU chip id: http://tinyurl.com/atmel-samd-chip-id
  #ifdef ARDUINO_ARCH_SAMD
  volatile uint32_t val1, val2, val3, val4;
  volatile uint32_t *ptr1 = (volatile uint32_t *)0x0080A00C;
  val1 = *ptr1;
  volatile uint32_t *ptr = (volatile uint32_t *)0x0080A040;
  val2 = *ptr;
  ptr++;
  val3 = *ptr;
  ptr++;
  val4 = *ptr;

  _stream->print("samd_id\t0x");
  sprintf(buf, "%8x%8x%8x%8x", val1, val2, val3, val4);
  _stream->println(buf);
  #endif ARDUINO_ARCH_SAMD

  // SD info
  cid_t cid;
  if (!_sd.card()->readCID(&cid)) {
    return;
  }
  _stream->print(F("sd_mid\t0x"));
  sprintf(buf, "%02x", cid.mid);
  _stream->println(buf);

  _stream->print(F("sd_oid\t"));
  _stream->print(cid.oid[0]);
  _stream->println(cid.oid[1]);

  _stream->print(F("sd_pnm\t"));
  for (uint8_t i = 0; i < 5; i++) {
    _stream->print(cid.pnm[i]);
  }
  _stream->println();

  _stream->print(F("sd_prv\t"));
  _stream->print(int(cid.prv_n));
  _stream->print('.');
  _stream->println(int(cid.prv_m));

  _stream->print(F("sd_psn\t0x"));
  sprintf(buf, "%4x", cid.psn);
  _stream->println(buf);

  _stream->print(F("sd_mdt\t"));
  _stream->print(cid.mdt_month);
  _stream->print('/');
  _stream->println(2000 + cid.mdt_year_low + 10 * cid.mdt_year_high);

  _stream->print(F("sd_size\t"));
  _stream->println(_sd.card()->cardSize());
}

/**
 * @internal
 *
 * listFiles helper
 *
 * @param stream     stream to use
 * @param dir        directory entry to list
 * @param parentPath path of parent directory for printing
 */
void listDir(Stream* stream, File dir, String parentPath) {
  File entry = dir.openNextFile();
  while (entry) {
    char name[13];
    entry.getName(name, sizeof(name));
    String path = parentPath + "/" + name;

    if (entry.isDirectory()) {
      listDir(stream, entry, path);
    }
    else {
      printFileDetails(stream, entry, path);
    }

    entry.close();
    entry = dir.openNextFile();
  }
}

/**
 * List all files on SD card. All files in all directories on the card are
 * included in the listing. Directory entries themselves are not included.
 * The response includes a header line and one line for each file found
 * on the card. The fields in each line are separated by `\t` and the lines
 * are separated by `\r\n`.
 *
 * TODO: deal with large listings or deep directory structures which
 * currently exhaust memory
 */
void Reaper::listFiles() {
  File root;
  root.open("/");
  _stream->println("path\tsize\tlast_modified");
  listDir(_stream, root, String());
}

void Reaper::listFile(char *filename) {
  File file = _sd.open(filename);
  printFileDetails(_stream, file, String(filename));
  file.close();
}

/**
 * Send file using xmodem-1k protocol.
 *
 * @param filename name of file to send, can include directories
 */
void Reaper::sendFile(char *filename) {
  File file = _sd.open(filename);
  _xmodem.send(&file);
  file.close();
}
