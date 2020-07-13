@echo off
rd dist /s/q >nul 2>nul

grep -o version setup.py

python setup.py sdist bdist_wheel

echo About to upload to pypi (Ctrl+C to cancel)
pause
twine upload dist/*
