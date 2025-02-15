#!/bin/bash
sudo apt update
sudo apt install -y libdbus-1-dev libdbus-glib-1-dev cmake 
sudo apt install -y locales
sudo sed -i 's/^# *\(fr_FR.UTF-8\)/\1/' /etc/locale.gen
sudo dpkg-reconfigure locales -f noninteractive
pip install --upgrade pip
pip install -r .devcontainer/requirements.txt
pre-commit install
sudo git config --system --add safe.directory '*'