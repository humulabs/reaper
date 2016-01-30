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
