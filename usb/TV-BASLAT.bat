@echo off
chcp 65001 >nul
cd /d "%~dp0"
start "Onumcilik gozegciligi - serwer" "%~dp0runtime\node.exe" "%~dp0server.js"
timeout /t 2 /nobreak >nul
rem Tam ekran (kiosk). Iki TV ayri pencerede; diger ekrana tasimak: Win+Shift+Sol/Sag ok. Cikis: Alt+F4.
start "" msedge --kiosk "http://localhost:3010/tv/1/" --edge-kiosk-type=fullscreen --no-first-run --user-data-dir="%LOCALAPPDATA%\TurkmenGips\Kiosk1"
start "" msedge --kiosk "http://localhost:3010/tv/2/" --edge-kiosk-type=fullscreen --no-first-run --user-data-dir="%LOCALAPPDATA%\TurkmenGips\Kiosk2"
