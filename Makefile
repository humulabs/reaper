# arduino.cc
ARDUINO=/Applications/Arduino-1.6.7.app/Contents/MacOS/Arduino
BOARD ?= arduino:samd:arduino_zero_edbg

# arduino.org
#ARDUINO=/Applications/Arduino.org.app/Contents/MacOS/Arduino

# DBG port .org
#BOARD ?= arduino:samd:arduino_zero_pro_bl_dbg
PORT ?= /dev/tty.usbmodem1412

# USB port .org
# BOARD ?= arduino:samd:arduino_zero_pro_bl
# PORT ?= /dev/tty.usbmodem1421

SKETCH_DIR ?= Reaper/examples
SKETCH ?= CommandLoop

DOXYGEN ?= /Applications/Doxygen.app/Contents/Resources/doxygen

go: upload run

build_dir:
	@mkdir -p build

install:
	$(MAKE) -C python clean uninstall install

clean:
	rm -fr build

doc: build_dir
	doxygen Reaper/.doxygen.conf

compile: build_dir
	$(ARDUINO) --board $(BOARD) \
	           --verify $(realpath $(SKETCH_DIR)/$(SKETCH)/$(SKETCH).ino)

upload: build_dir
	$(ARDUINO) --board $(BOARD) \
	           --port $(PORT) \
	           --upload $(realpath $(SKETCH_DIR)/$(SKETCH)/$(SKETCH).ino)

run:
	python python/sdreaper/main.py -p $(PORT) --monitor

.PHONY: go compile upload run doc build_dir install
