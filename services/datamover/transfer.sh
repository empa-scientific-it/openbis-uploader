#!/bin/sh

event="$1"
directory="$2"
file="$3"
case "$event" in
  w) echo "Incoming file ${directory}/${file}" && rsync -avz "$directory/$file" ${DEST};;
  *) echo "Event: ${event}: events other than write are ignored";;
esac

