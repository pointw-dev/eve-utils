@echo off
if not exist dist\nul call build.bat

if "x%1"=="x" goto real

:test
echo publishing to TEST PyPi
twine upload --repository-url https://test.pypi.org/legacy/ dist/*
echo install with:
echo pip install libcst
echo pip install inflect
echo pip install --index-url https://test.pypi.org/simple/ eve-utils


goto :end


:real
echo publishing to PROD PyPi
twine upload dist/*
echo install with:
echo pip install eve-utils
echo upgrade with:
echo pip install --upgrade eve-utils

:end

