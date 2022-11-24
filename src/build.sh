#!/usr/bin/env bash

cp ../README.md .
rm -rf dist
rm -rf build
rm -rf eve_utils.egg-info

grep version setup.py

## WHY DOES THIS NOT WORK? IS IT EVEN NEEDED?  python setup.py sdist bdist_wheel
python setup.py bdist_wheel
rm README.md

