#!/bin/bash
#set -euo 

# Simple script to automate generating and moving input data for a specified number of days
# Note using this requires that the folder pointers used in the scripts all point to the correct location

# First input is the number of days' data you want the scripts to generate data for
echo "Configuring data for " $1 " days' worth"

# Configure the raw data for the specified number of days
python3 GenerateInputMap.py -n $1
python3 RandomSelectTestTrain.py -n $1
python3 CombineCSVs.py -n $1