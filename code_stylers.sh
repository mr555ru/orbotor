#!/bin/sh
if ! type "pep257" > /dev/null; then
  echo "pep257 is not installed. pip install pep257";
  exit;
fi
if ! type "flake8" > /dev/null; then
  echo "flake8 is not installed. pip install flake8";
  exit;
fi
pep257 . 2> codestylers_logs/docstrings.txt
flake8 . --statistics --count > codestylers_logs/flake8.txt
flake8 . --max-complexity 10 | grep C > codestylers_logs/complexity.txt