#!/bin/bash
source venv/bin/activate # source the virtualenv to set new $PATH

RUNFILE=polygon-price-history.py
echo "Running: $RUNFILE"
python3 $RUNFILE