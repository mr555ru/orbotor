#!/bin/sh
pylint orbotor.py ./orbotor --disable=all --enable=missing-docstring --reports=no > missing-docstrings.txt
flake8 . --statistics --count > flake8.txt