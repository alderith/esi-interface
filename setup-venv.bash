#!/bin/bash
#Setup VENV
#You will need to install virtualenv:
# 1. sudo apt-get install python-virtualenv

mkdir virtualenv-esi
#virtualenv virtualenv-esi
python3 -m venv virtualenv-esi
source virtualenv-esi/bin/activate
pip install -r requirements.txt
