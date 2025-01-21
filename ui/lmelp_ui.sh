#!/bin/bash 
export GPG_TTY=$(tty)
source ~/miniforge3/etc/profile.d/conda.sh
source ~/miniforge3/etc/profile.d/mamba.sh
mamba activate whisper
pushd ~/git/lmelp
streamlit run ui/lmelp.py
popd