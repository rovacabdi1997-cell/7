@echo off
chcp 65001 >nul
cd /d "%~dp0"
start "Onumcilik gozegciligi - serwer" "%~dp0runtime\node.exe" "%~dp0server.js"
timeout /t 2 /nobreak >nul
rem Iki TV ekrany: TV 1 Gipsokarton, TV 2 Gury garyndy. Ayri pencerelerde acilir.
rem Pencereyi diger ekrana tasimak: Win+Shift+Sol/Sag ok. Tam ekran: F11.
start "" msedge --new-window --app=http://localhost:3010/tv/1/ --window-size=1280,720 --no-first-run --user-data-dir="%LOCALAPPDATA%\TurkmenGips\Pencere1"
start "" msedge --new-window --app=http://localhost:3010/tv/2/ --window-size=1280,720 --no-first-run --user-data-dir="%LOCALAPPDATA%\TurkmenGips\Pencere2"
