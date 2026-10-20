@echo off
setlocal
cd /d "%~dp0"
if not exist "SQL-AYARLARI.bat" (
  echo SQL-AYARLARI-ORNEK.bat dosyasini SQL-AYARLARI.bat olarak kopyalayip doldurun.
  pause
  exit /b 1
)
call "SQL-AYARLARI.bat"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0IKI-TV.ps1" -Action LiveServer
pause
endlocal
