SD_CARD ?= /Volumes/SD2

sample_data:
	cp -fr files/* $(SD_CARD)
	./clean-mac-dotfiles.sh $(SD_CARD)

.PHONY: sample_data
