#!/bin/bash 
export GPG_TTY=$(tty)
pushd /workspaces/lmelp/scripts
ulimit -n 4096
python get_one_transcription.py
popd