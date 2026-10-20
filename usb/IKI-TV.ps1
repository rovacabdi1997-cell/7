param(
  [ValidateSet('DemoServer', 'LiveServer', 'TV1', 'TV2')]
  [string]$Action
)

$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot

try {
  $settings = Get-Content -LiteralPath (Join-Path $PSScriptRoot 'IKI-TV-AYARLARI.json') -Raw | ConvertFrom-Json
  $serverUri = [uri]$settings.serverUrl
  if (-not $serverUri.IsAbsoluteUri -or $serverUri.Scheme -notin @('http', 'https') -or $serverUri.AbsolutePath -ne '/' -or $serverUri.Query -or $serverUri.Fragment -or $serverUri.UserInfo) {
    throw 'IKI-TV-AYARLARI.json: serverUrl http://SUNUCU-IP:3010 biciminde olmali.'
  }
  $baseUrl = $serverUri.GetLeftPart([System.UriPartial]::Authority)

  if ($Action -in @('TV1', 'TV2')) {
    $tvNo = if ($Action -eq 'TV1') { 1 } else { 2 }
    $url = "$baseUrl/tv/$tvNo/"
    # Optional: apiUrl in IKI-TV-AYARLARI.json points the TV at the central API (live mode).
    if ($settings.PSObject.Properties.Name -contains 'apiUrl' -and $settings.apiUrl) { $url = "$url" + "?api=" + $settings.apiUrl }
    $null = Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 8
    $edgeCandidates = @(
      (Join-Path ${env:ProgramFiles(x86)} 'Microsoft\Edge\Application\msedge.exe'),
      (Join-Path $env:ProgramFiles 'Microsoft\Edge\Application\msedge.exe'),
      (Join-Path $env:LOCALAPPDATA 'Microsoft\Edge\Application\msedge.exe')
    )
    $edge = $edgeCandidates | Where-Object { Test-Path -LiteralPath $_ } | Select-Object -First 1
    if (-not $edge) { throw 'Microsoft Edge bulunamadi. Edge kurun veya rehberdeki TV adresini tarayicida acin.' }
    $profilePath = Join-Path $env:LOCALAPPDATA "TurkmenGips\$Action"
    Start-Process -FilePath $edge -ArgumentList @('--kiosk', $url, '--edge-kiosk-type=fullscreen', '--no-first-run', "--user-data-dir=`"$profilePath`"")
    exit 0
  }

  if ($Action -notin @('DemoServer', 'LiveServer')) { throw 'Gecerli bir baslatma dosyasi kullanin.' }
  $ports = if ($Action -eq 'LiveServer') { @(3010, 8010) } else { @(3010) }
  foreach ($port in $ports) {
    if (Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue) {
      throw "$port portu kullanimda. Calisan sunucuyu kontrol edin; ikinci kez baslatmayin. TV dosyalari mevcut sunucuya baglanabilir."
    }
  }

  $logDir = Join-Path $PSScriptRoot 'CALISMA-KAYITLARI'
  $null = New-Item -ItemType Directory -Force -Path $logDir
  $stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
  if ($Action -eq 'LiveServer') {
    if (-not $env:WINCC_CONNECTION_STRING) { throw 'SQL-AYARLARI.bat icinde gercek WinCC baglanti bilgisi gerekli.' }
    $env:DATA_SOURCE = 'wincc'
    $py = (Get-Command py -ErrorAction Stop).Source
    & $py -c 'import uvicorn, fastapi, win32com.client'
    if ($LASTEXITCODE -ne 0) { throw 'Python paketleri eksik: py -m pip install -r KAYNAK-KOD\backend\requirements.txt pywin32' }
    # Browsers on both TV PCs use the central web origin, not their own IPs.
    $origins = @('http://localhost:3010', 'http://127.0.0.1:3010', $baseUrl)
    if ($env:CORS_ORIGINS) { $origins += $env:CORS_ORIGINS.Split(',') }
    $env:CORS_ORIGINS = ($origins | Select-Object -Unique) -join ','
    $apiProcess = Start-Process -FilePath $py -ArgumentList @('-m', 'uvicorn', 'app.main:app', '--app-dir', 'KAYNAK-KOD\backend', '--host', '0.0.0.0', '--port', '8010') -WorkingDirectory $PSScriptRoot -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $logDir "$stamp-api.log") -RedirectStandardError (Join-Path $logDir "$stamp-api-error.log")
    $env:SITE_DIR = 'site-live'
  } else {
    $env:SITE_DIR = 'site'
  }
  $env:PORT = '3010'
  $nodeProcess = Start-Process -FilePath (Join-Path $PSScriptRoot 'runtime\node.exe') -ArgumentList 'server.js' -WorkingDirectory $PSScriptRoot -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $logDir "$stamp-web.log") -RedirectStandardError (Join-Path $logDir "$stamp-web-error.log")
  $ready = $false
  for ($attempt = 0; $attempt -lt 15; $attempt++) {
    try {
      $null = Invoke-WebRequest -Uri 'http://127.0.0.1:3010/tv/' -UseBasicParsing -TimeoutSec 2
      if ($Action -eq 'LiveServer') { $null = Invoke-WebRequest -Uri 'http://127.0.0.1:8010/api/health' -UseBasicParsing -TimeoutSec 2 }
      $ready = $true
      break
    } catch { Start-Sleep -Milliseconds 500 }
  }
  if (-not $ready) {
    if ($nodeProcess -and -not $nodeProcess.HasExited) { Stop-Process -Id $nodeProcess.Id -ErrorAction SilentlyContinue }
    if ($apiProcess -and -not $apiProcess.HasExited) { Stop-Process -Id $apiProcess.Id -ErrorAction SilentlyContinue }
    throw 'Sunucu baslatilamadi. CALISMA-KAYITLARI klasorundeki hata kayitlarini kontrol edin.'
  }
  Write-Host "Sunucu hazir: $baseUrl"
  Write-Host "TV 1: $baseUrl/tv/1/"
  Write-Host "TV 2: $baseUrl/tv/2/"
  Write-Host 'TV bilgisayarlarinda ilgili TV baslatma dosyasini acin.'
  Write-Host 'Bu bilgi penceresi kapaninca sunucu arka planda calismaya devam eder.'
  exit 0
} catch {
  Write-Host "Baslatilamadi: $($_.Exception.Message)" -ForegroundColor Red
  exit 1
}
