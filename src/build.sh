#!/usr/bin/env bash

cp ../README.md .
rm -rf dist
rm -rf build
rm eve_utils.egg-info

grep version setup.py

python setup.py sdist bdist_wheel
rm README.md

