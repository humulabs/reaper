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
 * List all files and directories on the SD card. Each file or directory is
 * printed on a single line of the form:
 *
 *     <indent>DATE<sp>TIME<sp>SIZE<sp>NAME
 *
 * where:
 *   - <indent> 2 spaces * the current directory level
 *   - <sp> 1 or more spaces
 *   - DATE: file last modified date
 *   - TIME: file last modified time
 *   - SIZE: file size
 *   - NAME: file name (not including parent dirs), if NAME is
 *           a directory it ends with a slash "/"
 *
 * For example the listing:
 *
 *     2016-02-09 13:43:42        513 small.dat
 *     2016-01-28 14:41:24          0 x/
 *       2016-02-09 13:43:42         42 z.dat
 *
 *  Contains two files `small.data` and `x/z.dat` and one directory `x`.
 */
void Reaper::listFiles() {
  _sd.ls(_stream, "/", LS_A | LS_DATE | LS_SIZE | LS_R);
}

/**
 * List details for a file. Output is a single line of the form:
 *
 *     DATE<sp>TIME<sp>SIZE<sp>filename
 *
 * where:
 *   - <sp> 1 or more spaces
 *   - DATE: file last modified date
 *   - TIME: file last modified time
 *   - SIZE: file size
 *   - NAME: full filename including any parent dirs
 *
 * @param filename full path to file, using slashes "/" to separate directories
 */
void Reaper::listFile(char *filename) {
  File file = _sd.open(filename);

  file.printModifyDateTime(_stream);
  _stream->write(' ');
  file.printFileSize(_stream);
  _stream->write(' ');
  _stream->println(filename);

  file.close();
}

/**
 * Remove file.
 * @param filename full path to file, using slashes "/" to separate directories
 */
void Reaper::rm(char *filename) {
  _sd.remove(filename);
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
