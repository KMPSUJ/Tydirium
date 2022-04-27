#!/bin/bash

cd ~/Tydirium/

source door-stats-venv/bin/activate

HOST="localhost"
PORT=7216
OUTPUTPATH="./data"
python upload_predictions.py $HOST $PORT $OUTPUTPATH > /dev/null 2> door-stats.log
