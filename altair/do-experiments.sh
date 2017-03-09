#!/bin/bash

if test "$#" -ne 1
then
    echo "Usage: do-experiments.sh CONFIG_DIR"
    echo "    CONFIG_FILE - Text file of experiment configurations as command line arguments"
    exit 1
fi

while read line
do
    echo python altair/experiments.py $line
    python altair/experiments.py $line
done < $1
