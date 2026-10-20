@echo off
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0BASLAT.ps1" -Ekran tv2
if errorlevel 1 pause
