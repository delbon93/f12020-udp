#!/bin/bash

MAIN=./src/main.py
PYTHON=./venv/bin/python

add_to_path() {
    PYTHONPATH="$PYTHONPATH:$1"
    for FILE in $1/*
    do
        if [[ -d $FILE && `basename $FILE` != "__pycache__" ]] ; then
            add_to_path $FILE
        fi
    done
}

add_to_path "./src"
export PYTHONPATH

source ./venv/bin/activate
$PYTHON $MAIN