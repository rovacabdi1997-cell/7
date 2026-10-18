@echo off
chcp 65001 >nul
cd /d "%~dp0"
start "Onumcilik gozegciligi - serwer" "%~dp0runtime\node.exe" "%~dp0server.js"
timeout /t 2 /nobreak >nul
rem Full-screen kiosk. Close with Alt+F4.
start "" msedge --kiosk "http://localhost:3010/tv/" --edge-kiosk-type=fullscreen --no-first-run
