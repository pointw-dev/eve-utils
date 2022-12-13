@echo off
setlocal
grep version setup.py
dir dist /b
echo.

if "x%1"=="x" goto real
if "x%1"=="xtest" goto test
if "x%1"=="xTEST" goto test
if not exist \Envs\%1\Lib\site-packages\eve_utils\nul goto usage

:dev
echo publishing to %1 virtual environment
rd \Envs\%1\Lib\site-packages\eve_utils /s/q >nul
md \Envs\%1\Lib\site-packages\eve_utils >nul
xcopy %~dp0\bin\* \envs\%1\scripts /s/Y >nul
xcopy %~dp0\eve_utils\* \Envs\%1\Lib\site-packages\eve_utils /s/Y >nul

goto :end


:test
echo publishing to TEST PyPi
if not exist dist\nul call build.bat
twine upload --repository-url https://test.pypi.org/legacy/ dist/*
echo install with:
echo pip install libcst
echo pip install inflect
echo pip install --index-url https://test.pypi.org/simple/ eve-utils

goto :end


:real
echo publishing to PROD PyPi
if not exist dist\nul call build.bat
twine upload dist/*
echo install with:
echo pip install eve-utils
echo upgrade with:
echo pip install --upgrade eve-utils

goto :end


:usage
echo USAGE: publish [test^|vir_folder]
echo e.g. publish         (publishes to PyPi)
echo      publish test    (publishes to TEST PyPi)
echo      publish my-api  (copies files to that python virtual environment
echo                       must have eve-utils already installed)
goto :end


:end
endlocal
