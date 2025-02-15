#!/bin/bash 
export GPG_TTY=$(tty)
cd /workspaces/lmelp
source .venv/bin/activate
pushd /workspaces/lmelp/scripts
ulimit -n 4096
python get_one_transcription.py
popd