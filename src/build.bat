@echo off
copy ..\README.md /Y
rd dist /s/q >nul 2>nul
rd build /s/q > nul 2>nul
rd eve_utils.egg-info > nul 2>nul

grep version setup.py

python setup.py sdist bdist_wheel
del README.md >nul 2>nul
