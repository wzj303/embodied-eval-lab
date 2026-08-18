@echo off
setlocal

set "NODE_DIR=C:\Program Files\nodejs"

if not exist "%NODE_DIR%\node.exe" (
    echo Node.js is not installed at %NODE_DIR% 1>&2
    exit /b 1
)

set "PATH=%NODE_DIR%;%PATH%"

if "%~1"=="" (
    endlocal
    exit /b 0
)

call %*
exit /b %ERRORLEVEL%
