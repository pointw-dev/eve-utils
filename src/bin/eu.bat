@echo off
setlocal
if "x%1" == "xrun" goto run

python %~dp0eve-utils %*
goto end

:run
start "eve-utils run" python %~dp0eve-utils %*

:end
endlocal
