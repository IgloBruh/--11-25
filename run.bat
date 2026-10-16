@echo off
setlocal
cd /d "%~dp0"
set "PYTHONPATH=%~dp0src"

where py >nul 2>&1
if not errorlevel 1 (
    py -3 -m shell_emulator
) else (
    python -m shell_emulator
)

endlocal
