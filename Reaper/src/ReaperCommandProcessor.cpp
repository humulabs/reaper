#include <Reaper.h>
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

    else if (strcmp(cmd, "rm") == 0) {
      _stream->print("rm ");
      _stream->println(strtok(NULL, ""));
    }

    else if (strcmp(cmd, "cp") == 0) {
      _reaper->sendFile(strtok(NULL, ""));
    }

    else if (strcmp(cmd, "ls") == 0) {
      _reaper->listFiles();
    }

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
