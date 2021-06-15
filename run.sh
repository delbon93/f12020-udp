#!/bin/bash

MAIN=main
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

if [[ $# -gt 1 ]] ; then
    echo "Usage: $0 [app]"
    exit 1
fi

APP=$MAIN

if [[ $# == 1 ]] ; then
    APP=$1
fi

source ./venv/bin/activate

for APPPATH in `echo $PYTHONPATH | sed -e "s/:/ /g"` 
do
    TARGET=$APPPATH/$APP.py
    ls -s $TARGET >> /dev/null 2>&1
    if [[ $? == 0 ]] ; then
        echo "%> Running target '$TARGET'..."
        $PYTHON $TARGET
        exit
    fi
done

echo "%> Fatal: target '$APP' not found"
exit 2
