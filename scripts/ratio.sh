#!/bin/bash
# watch -n60 "./ratio.sh"

pushd ~/git/lmelp/audios > /dev/null
# Count the number of .txt files
txt_count=$(find . -type f -name "*.txt" | wc -l)

# Count the number of .mp3 and .m4a files
audio_count=$(find . -type f \( -name "*.mp3" -o -name "*.m4a" \) | wc -l)

# Calculate the ratio and express it as a percentage
if [ $audio_count -ne 0 ]; then
  ratio=$(echo "scale=2; ($txt_count / $audio_count) * 100" | bc)
  echo "Ratio: $ratio%"
else
  echo "No audio files found."
fi
popd > /dev/null