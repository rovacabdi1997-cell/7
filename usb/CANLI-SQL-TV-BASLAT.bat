@echo off
setlocal
cd /d "%~dp0"

if not exist "SQL-AYARLARI.bat" (
  echo.
  echo SQL ayarlari bulunamadi.
  echo SQL-AYARLARI-ORNEK.bat dosyasini SQL-AYARLARI.bat olarak kopyalayin,
  echo sonra WinCC baglanti bilgisini yetkili saha personeliyle doldurun.
  echo.
  pause
  exit /b 1
)

call "SQL-AYARLARI.bat"
set "SITE_DIR=site-live"
set "PORT=3010"

where py >nul 2>nul
if errorlevel 1 (
  echo Python bulunamadi. Canli SQL modu icin Python 3.11 veya uzeri gerekir.
  pause
  exit /b 1
)

py -c "import uvicorn, fastapi" >nul 2>nul
if errorlevel 1 (
  echo Canli SQL modu icin Python paketleri eksik.
  echo Bir kez su komutu calistirin:
  echo py -m pip install -r KAYNAK-KOD\backend\requirements.txt
  pause
  exit /b 1
)

start "Turkmen Gips SQL API" /min cmd /c "py -m uvicorn app.main:app --app-dir KAYNAK-KOD\backend --host 0.0.0.0 --port 8010"
start "Turkmen Gips TV Sunucusu" /min cmd /c "set SITE_DIR=site-live&&set PORT=3010&&runtime\node.exe server.js"
timeout /t 4 /nobreak >nul

start "" msedge --kiosk "http://localhost:3010/tv/" --edge-kiosk-type=fullscreen --no-first-run
endlocal
