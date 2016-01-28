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
      _stream->println(F("Unable to talk to SD card"));
      return;
    }
    _stream->println(F("Connected to SD card at half speed"));
  }
  else {
    _stream->println(F("Connected to SD card at full speed"));
  }
}

/**
 * @internal
 *
 * listFiles helper.

 * @param stream     [description]
 * @param dir        [description]
 * @param parentPath [description]
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
      stream->print(path);
      stream->print('\t');
      stream->print(entry.fileSize(), DEC);
      stream->print('\t');
      entry.printModifyDateTime(stream);
      stream->println();
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
 */
void Reaper::listFiles() {
  File root;
  root.open("/");
  _stream->println("path\tsize\tlast_modified");
  listDir(_stream, root, String());
}

/**
 * Send file using xmodem-1k protocol.
 *
 * @param filename name of file to send, can include directories
 */
void Reaper::sendFile(char *filename) {
  File file = _sd.open(filename);
  _xmodem.send(&file);
}
