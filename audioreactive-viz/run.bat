@echo off
REM ─── Audioreactive Visualizer — Launch Script (Windows) ───

cd /d "%~dp0"

set VENV_DIR=.venv

REM Create venv if missing
if not exist "%VENV_DIR%\Scripts\activate.bat" (
    echo [Setup] Creating virtual environment...
    python -m venv %VENV_DIR%
)

REM Activate
call %VENV_DIR%\Scripts\activate.bat

REM Install / update deps
echo [Setup] Installing dependencies...
pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt

REM Optional: install SpoutGL on Windows
pip install --quiet SpoutGL 2>nul

REM Launch
echo [Launch] Starting visualizer...
python main.py %*
