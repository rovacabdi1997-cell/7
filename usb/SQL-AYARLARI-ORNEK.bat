@echo off
rem Bu dosyanin kopyasini SQL-AYARLARI.bat adi ile kaydedin.
rem Degeri sahadaki WinCC Connectivity Pack / SQL bilgisine gore doldurun.
set "DATA_SOURCE=wincc"
set "REFRESH_SECONDS=5"
set "WINCC_CONNECTION_STRING=Provider=WinCCOLEDBProvider.1;Catalog=CC_PROJE_R;Data Source=.\WINCC"
set "CORS_ORIGINS=http://localhost:3010,http://127.0.0.1:3010"
