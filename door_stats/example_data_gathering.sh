#!/bin/bash

cd ~/Tydirium/

source door-stats-venv/bin/activate

DATE=$(date +%Y-%m-%d)
HOST="localhost"
PORT=7216
OUTPUTPATH="./data"
nohup python run_data_gathering.py $DATE $HOST $PORT $OUTPUTPATH > /dev/null 2> door-stats.log &

