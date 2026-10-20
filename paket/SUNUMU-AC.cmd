@echo off
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0BASLAT.ps1" -Ekran sunum
if errorlevel 1 pause
