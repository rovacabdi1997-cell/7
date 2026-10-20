@echo off
cd /d "%~dp0"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0IKI-TV.ps1" -Action TV1
if errorlevel 1 pause
