#!/bin/bash
if ! command -v python3 &> /dev/null # check if python3 exists in the current $PATH
then
    echo "python3 could not be found"
    exit
fi

echo "Setting up python virtual environment: venv"
python3 -m venv venv # setup new virtual env called venv

echo "Installing code dependencies"
source venv/bin/activate # source the virtualenv to set new $PATH
pip install -r requirements.txt # install all python deps