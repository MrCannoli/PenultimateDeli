#!/bin/bash
#set -euo 
# Simple script to automate generating and moving input data for a specified number of days
# Note using this requires that the folder pointers used in the scripts all point to the correct location
# $1 is the number of days' data you want the scripts to generate data for
# $2 is the directory base folder name in the cutting board
# $3 is a seed for rand. If not provided, a random seed is used.
# $4 is a boolean denoting whether to strip transactions or not
# All inputs past the 4th is a list of percentage values to use as binary setpoints
# Example use call:
# ./prep_cutting_board.sh 2 "all_data_6_10" 12345 1 0.015
# ./prep_cutting_board.sh 2 "all_data_6_11_to_8_19" 12345 1 0.015
echo "Configuring data for " $1 " days' worth from ../CuttingBoard/$2" 
DIR_NAME="$2"

# Configure the raw data for the specified number of days
if [ $4 = 1 ]
then
python3 StripNumTransactions.py -d $2  # This step may not be necessary?
DIR_NAME="$2_stripped"
echo "Using stripped files in $DIR_NAME"
else
echo "Using raw files for data"
fi

if [ -z "$5" ]
then
    python3 GenerateInputMap.py -n $1 -d $DIR_NAME
else
    # Use setpoints from input 5 onwards
    python3 GenerateInputMap.py -n $1 -d $DIR_NAME -s $5
fi

# Check if a seed was provided
if [ -z "$3" ]
then
    echo "Using randomized list"
    python3 RandomSelectTestTrain.py -n $1 -d $DIR_NAME
else
    echo "Selecting with random seed $3"
    python3 RandomSelectTestTrain.py -n $1 -s $3 -d $DIR_NAME 
fi

echo "Creating combined test and train files"
python3 CombineCSVs.py -n $1 -d $DIR_NAME
