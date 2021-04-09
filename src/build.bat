@echo off
rd dist /s/q >nul 2>nul
rd build /s/q > nul 2>nul
rd eve_utils.egg-info > nul 2>nul

grep -o version setup.py

python setup.py sdist bdist_wheel
