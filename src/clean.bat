@echo off

grep version setup.py
echo Removing build artifacts

rd dist /s/q >nul 2>nul
rd build /s/q > nul 2>nul
rd eve_utils.egg-info > nul 2>nul
del README.md >nul 2>nul
