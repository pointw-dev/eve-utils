@echo off
setlocal
if "x%i" == "xrun" goto run

python %~dp0eve-utils %*
goto end

:run
start "eve-utils" python %~dp0eve-utils %*

:end
endlocal
