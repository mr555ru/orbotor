#!/bin/sh
pylint orbotor.py ./orbotor --disable=all --enable=missing-docstring --reports=no > codestylers_logs/missing-docstrings.txt
flake8 . --statistics --count > codestylers_logs/flake8.txt