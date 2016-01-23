#ifndef ReaperCommandProcessor_h
#define ReaperCommandProcessor_h

#include <Reaper.h>

#define COMMAND_BUFFER_SIZE 128

#define EOT 0x04
#define SYN 0x16

class ReaperCommandProcessor {
  public:
    ReaperCommandProcessor(Stream& stream, Reaper& reaper);
    void processCommands();

  private:
    Stream* _stream;
    Reaper* _reaper;

    char _commandBuffer[COMMAND_BUFFER_SIZE];
    byte _commandBufferIndex;

	void processChar(const int c);
	boolean processCommandLine();
};

#endif
