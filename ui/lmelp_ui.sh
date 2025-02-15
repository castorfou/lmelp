#!/bin/bash 
export GPG_TTY=$(tty)
pushd /workspaces/lmelp/
streamlit run ui/lmelp.py
popd