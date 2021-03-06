#include <ReaperCommandProcessor.h>

/**
 * Construct a ReaperCommandProcessor.
 *
 * @param stream stream to use for command output
 * @param reaper to use to execute commands
 */
ReaperCommandProcessor::ReaperCommandProcessor(Stream& stream, Reaper& reaper)
{
  _stream = &stream;
  _reaper = &reaper;
  _commandBufferIndex = 0;
}

/**
 * @internal
 *
 * Process a single command line. Process the command found in
 * _commandBuffer which is assumed to contain a string. No action is
 * taken if the command is not recognized.
 *
 * @return true if the command was not "exit"
 */
boolean ReaperCommandProcessor::processCommandLine() {
  Serial.print("processCommandLine: ");
  Serial.println(_commandBuffer);

  char* cmd = strtok(_commandBuffer, " ");

  if (cmd != NULL) {
    if (strcmp(cmd, "exit") == 0) {
      _stream->println("exiting");
      _stream->write(EOT);
      return false;
    }

    else if (strcmp(cmd, "info") == 0) {
      _reaper->info();
    }

    else if (strcmp(cmd, "rm") == 0) {
      _reaper->rm(strtok(NULL, ""));
    }

    else if (strcmp(cmd, "cp") == 0) {
      _reaper->sendFile(strtok(NULL, ""));
    }

    else if (strcmp(cmd, "ls") == 0) {
      char *filename = strtok(NULL, "");
      if (filename != NULL) {
        _reaper->listFile(filename);
      }
      else {
        _reaper->listFiles();
      }
    }

#ifdef ARDUINO_ARCH_SAMD
    else if (strcmp(cmd, "get_time") == 0) {
      uint8_t timeBuf[6];
      char buf[4];
      _reaper->getDateTime(timeBuf);
      for (uint8_t i = 0; i < sizeof(timeBuf); i++) {
        _stream->print(itoa(timeBuf[i], buf, 10));
        _stream->print(' ');
      }
    }

    else if (strcmp(cmd, "set_time") == 0) {
      uint8_t timeBuf[6] = {0, 0, 0, 0, 0, 0};
      for (uint8_t i = 0; i < sizeof(timeBuf); i++) {
        char *tok = strtok(NULL, " ");
        if (tok == NULL) {
          break;
        }
        timeBuf[i] = atoi(tok);
      }
      _reaper->setDateTime(timeBuf);
    }
#endif

    else if (strcmp(cmd, "echo") == 0) {
      _stream->println(strtok(NULL, ""));
    }

    _stream->write(EOT);
  }

  return true;
}

void ReaperCommandProcessor::processChar(int c) {
  Serial.print((char)c);
  switch (c) {
    case '\r':
      break;

    case '\n':
      _commandBuffer[_commandBufferIndex] = '\0';
      processCommandLine();
      _commandBufferIndex = 0;
      break;

    default:
      if (_commandBufferIndex < COMMAND_BUFFER_SIZE - 1) {
        _commandBuffer[_commandBufferIndex++] = c;
      }
      break;
  }
}

/**
 * Read and process commands. This method reads data from the input stream
 * and processes each command it finds. It returns when there are no bytes
 * available to read from the input stream and all fully read commands have
 * been executed.
 */
void ReaperCommandProcessor::processCommands() {
  while (_stream->available() > 0) {
    int c = _stream->read();
    Serial.print(c);
    if (c == -1) {
      Serial.println("-1");
    }
    else if (c == SYN) {
      _stream->write(SYN);
      _stream->flush();
      Serial.println("SYN");
    }
    else {
      processChar(c);
    }
  }
}
