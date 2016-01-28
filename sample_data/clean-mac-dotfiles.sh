#!/bin/bash

# Usage: ./clean-mac-dotfiles /Volumes/YOUR-SD-CARD
#
# Removes dot junk OS puts on root of mounted filesystems.
# Only removes these files and dirs if fs is of type msdos.

fs=$1

df -T msdos $fs > /dev/null && \
  rm -frv $fs/.Spotlight* \
          $fs/.Trash* \
          $fs/.fseventsd \
          $fs/._.*
