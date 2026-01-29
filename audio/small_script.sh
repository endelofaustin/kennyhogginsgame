#!/usr/bin/env bash
set -e

AUDIO_DIR="audio"
DISABLED_DIR="$AUDIO_DIR/mp3_disabled"

mkdir -p "$DISABLED_DIR"

for mp3 in "$AUDIO_DIR"/*.mp3; do
  [ -e "$mp3" ] || continue

  wav="${mp3%.mp3}.wav"

  echo "Converting: $mp3 -> $wav"
  ffmpeg -y -v error -i "$mp3" "$wav"

  echo "Disabling original: $mp3"
  mv "$mp3" "$DISABLED_DIR/"
done

echo "Done. All MP3s converted to WAV and moved to $DISABLED_DIR/"
