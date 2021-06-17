#!/bin/bash

MAIN=main
PYTHON=./venv/bin/python

if [[ $# -gt 1 ]] ; then
    echo "Usage: $0 [app]"
    exit 1
fi

APP=$MAIN

if [[ $# == 1 ]] ; then
    APP=$1
fi

source ./venv/bin/activate


TARGET=./$APP.py
ls -s $TARGET >> /dev/null 2>&1
if [[ $? == 0 ]] ; then
    echo "%> Running target '$TARGET'..."
    $PYTHON $TARGET
    exit
fi

echo "%> Fatal: target '$APP' not found"
exit 2
