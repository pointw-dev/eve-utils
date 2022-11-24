#!/usr/bin/env bash

grep version setup.py
echo Removing build artifiacts

rm -rf dist
rm -rf build
rm -rf eve_utils.egg-info
rm README.md 2> /dev/null
