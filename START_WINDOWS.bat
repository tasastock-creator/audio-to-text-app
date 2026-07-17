@echo off
cd /d %~dp0
if not exist .venv\Scripts\python.exe (
  echo Please run SETUP_WINDOWS.bat first.
  pause
  exit /b 1
)
start "" http://localhost:8787
.venv\Scripts\python.exe server.py
pause
