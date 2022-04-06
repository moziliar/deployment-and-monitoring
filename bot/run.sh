#!/bin/bash

cd /home/mzr/CS3210-AY2122-S1/bot
source ./venv/bin/activate
pip3 install -r ./requirement.txt
python3 ./src/bot.py
