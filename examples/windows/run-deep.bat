@echo off
setlocal
cd /d "%~dp0..\.."
set "PYTHONPATH=%CD%\src"
set "VFS_PATH=%CD%\examples\vfs\deep.json"
set "SCRIPT_PATH=%CD%\examples\startup\error.script"

py -3 -m shell_emulator --vfs-path "%VFS_PATH%" --script-path "%SCRIPT_PATH%"

endlocal
