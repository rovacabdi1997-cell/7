@echo off
chcp 65001 >nul
cd /d "%~dp0"
start "Onumcilik gozegciligi - serwer" "%~dp0runtime\node.exe" "%~dp0server.js"
timeout /t 2 /nobreak >nul
start "" "http://localhost:3010/"
