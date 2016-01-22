#include "Reaper.h"

Reaper::Reaper() {
}

Reaper::Reaper(Stream& stream, int chipSelect) {
  _stream = &stream;
  _chipSelect = chipSelect;
}

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

void Reaper::listFiles() {
  File root;
  root.open("/");
  _stream->println("path\tsize\tlast_modified");
  listDir(_stream, root, String());
}
