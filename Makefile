# arduino.cc
# ARDUINO=/Applications/Arduino-1.6.6.app/Contents/MacOS/Arduino -v
# BOARD ?= arduino:samd:arduino_zero_edbg

# arduino.org
ARDUINO=/Applications/Arduino.org.app/Contents/MacOS/Arduino

# DBG port .org
# BOARD ?= arduino:samd:arduino_zero_pro_bl_dbg
# PORT ?= /dev/tty.usbmodem1422

# USB port .org
BOARD ?= arduino:samd:arduino_zero_pro_bl
PORT ?= /dev/tty.usbmodem1421

BAUD ?= 9600
SKETCH ?= ListFiles

go: upload run

compile:
	@mkdir -p build
	$(ARDUINO) --board $(BOARD) \
	           --verify $(realpath sketches/$(SKETCH)/$(SKETCH).ino)

upload:
	@mkdir -p build
	$(ARDUINO) --board $(BOARD) \
	           --port $(PORT) \
	           --upload $(realpath sketches/$(SKETCH)/$(SKETCH).ino)

run:
	python serial-test.py $(PORT) $(BAUD)

.PHONY: go compile upload run
