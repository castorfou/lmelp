#!/bin/bash 
export GPG_TTY=$(tty)
source ~/miniforge3/etc/profile.d/conda.sh
source ~/miniforge3/etc/profile.d/mamba.sh
mamba activate whisper
pushd ~/git/lmelp/scripts
python store_all_auteurs_from_all_episodes.py  "$@"
popd
