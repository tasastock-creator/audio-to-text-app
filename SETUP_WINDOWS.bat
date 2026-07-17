@echo off
cd /d %~dp0
where py >nul 2>nul
if errorlevel 1 (
  echo Python is not installed. Install Python 3.11 or 3.12 from python.org, tick Add Python to PATH, then run this file again.
  pause
  exit /b 1
)
py -m venv .venv
call .venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
echo.
echo Setup complete. Now run START_WINDOWS.bat
pause
