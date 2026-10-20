# Türkmen Gips — tek başlatıcı. Bütün ayarlar SAHA-AYARLARI.json içindedir.
#   -Ekran sunum | tv1 | tv2 | merkez | api | kontrol
# merkez  : yalnız sunucuyu başlatır (merkez bilgisayar).
# tv1/tv2 : TV bilgisayarında tam ekran açar; sunucu merkezdeyse yeniden başlatmaz.
# api     : canlı veri sunucusunu (Python) başlatır; veriKaynagy = "api" iken gerekir.
# kontrol : merkez sunucuya ve API'ye erişimi denetler.
param([ValidateSet('sunum','tv1','tv2','merkez','api','kontrol')][string]$Ekran = 'sunum')
$ErrorActionPreference = 'Stop'
$paket = Split-Path -Parent $MyInvocation.MyCommand.Path

function Ayarlar {
  $yol = Join-Path $paket 'SAHA-AYARLARI.json'
  $a = Get-Content -LiteralPath $yol -Raw -Encoding UTF8 | ConvertFrom-Json
  if ($a.merkezIp -notmatch '^(\d{1,3}\.){3}\d{1,3}$') { throw "SAHA-AYARLARI.json: merkezIp IPv4 olmali (ornek 192.168.1.50)." }
  if ($a.veriKaynagy -notin @('kayit','api')) { throw "SAHA-AYARLARI.json: veriKaynagy 'kayit' veya 'api' olmali." }
  if ($a.tema -notin @('acik','koyu')) { throw "SAHA-AYARLARI.json: tema 'acik' veya 'koyu' olmali." }
  return $a
}

function BuMerkezMi($ip) {
  if ($ip -eq '127.0.0.1') { return $true }
  $yerel = Get-NetIPAddress -AddressFamily IPv4 -ErrorAction SilentlyContinue | Select-Object -ExpandProperty IPAddress
  return $yerel -contains $ip
}

function Acik($url) {
  try { $null = Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 2; return $true } catch { return $false }
}

function SunucuyuBaslat($a) {
  $adres = "http://127.0.0.1:$($a.sunumPort)/sunum/TURKMEN-GIPS-BAKANLIK-SUNUMU.html"
  if (Acik $adres) { return }
  $tutan = Get-NetTCPConnection -LocalPort $a.sunumPort -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1
  if ($tutan) {
    $islem = Get-Process -Id $tutan.OwningProcess -ErrorAction SilentlyContinue
    throw "$($a.sunumPort) portunu baska bir program tutuyor: $($islem.ProcessName) (PID $($tutan.OwningProcess)). Kapatin veya SAHA-AYARLARI.json'da sunumPort'u degistirin."
  }
  $env:PORT = "$($a.sunumPort)"
  $kayit = Join-Path $paket 'KAYITLAR'; $null = New-Item -ItemType Directory -Force $kayit
  Start-Process -FilePath (Join-Path $paket 'runtime\node.exe') -ArgumentList 'server.cjs' -WorkingDirectory $paket -WindowStyle Hidden `
    -RedirectStandardOutput (Join-Path $kayit 'sunucu.log') -RedirectStandardError (Join-Path $kayit 'sunucu-hata.log') | Out-Null
  for ($i = 0; $i -lt 25; $i++) { Start-Sleep -Milliseconds 200; if (Acik $adres) { return } }
  throw "Sunucu acilamadi. KAYITLAR\sunucu-hata.log dosyasina bakin."
}

function Adres($a, $yol) {
  $host_ = if (BuMerkezMi $a.merkezIp) { 'localhost' } else { $a.merkezIp }
  $url = "http://$($host_):$($a.sunumPort)$yol"
  $ek = "tema=$($a.tema)"
  if ($a.veriKaynagy -eq 'api') { $ek += '&api=' + [uri]::EscapeDataString("http://$($a.merkezIp):$($a.apiPort)") }
  if ($url.Contains('?')) { return "$url&$ek" } else { return "$url?$ek" }
}

function Edge {
  $adaylar = @("${env:ProgramFiles(x86)}\Microsoft\Edge\Application\msedge.exe", "$env:ProgramFiles\Microsoft\Edge\Application\msedge.exe")
  $e = $adaylar | Where-Object { Test-Path -LiteralPath $_ } | Select-Object -First 1
  if (-not $e) { throw 'Microsoft Edge bulunamadi.' }
  return $e
}

$a = Ayarlar
switch ($Ekran) {
  'merkez' { SunucuyuBaslat $a; Write-Host "Sunucu hazir: http://$($a.merkezIp):$($a.sunumPort)/" }
  'sunum'  { if (BuMerkezMi $a.merkezIp) { SunucuyuBaslat $a }; Start-Process (Adres $a '/sunum/TURKMEN-GIPS-BAKANLIK-SUNUMU.html') }
  { $_ -in 'tv1','tv2' } {
    if (BuMerkezMi $a.merkezIp) { SunucuyuBaslat $a }
    $no = if ($Ekran -eq 'tv1') { 1 } else { 2 }
    $profil = Join-Path $env:LOCALAPPDATA "TurkmenGips\TV$no"
    Start-Process -FilePath (Edge) -ArgumentList @('--kiosk', (Adres $a "/tv/$no/"), '--edge-kiosk-type=fullscreen', '--no-first-run', "--user-data-dir=`"$profil`"")
  }
  'api' {
    $py = (Get-Command py -ErrorAction SilentlyContinue).Source
    if (-not $py) { $py = (Get-Command python -ErrorAction Stop).Source }
    $env:DATA_SOURCE = if ($env:WINCC_CONNECTION_STRING) { 'wincc' } else { 'demo' }
    $env:CORS_ORIGINS = "http://localhost:$($a.sunumPort),http://127.0.0.1:$($a.sunumPort),http://$($a.merkezIp):$($a.sunumPort)"
    $kayit = Join-Path $paket 'KAYITLAR'; $null = New-Item -ItemType Directory -Force $kayit
    Start-Process -FilePath $py -ArgumentList @('-m','uvicorn','app.main:app','--app-dir',(Join-Path $paket 'KAYNAK-KOD\backend'),'--host','0.0.0.0','--port',"$($a.apiPort)") `
      -WorkingDirectory $paket -WindowStyle Hidden -RedirectStandardOutput (Join-Path $kayit 'api.log') -RedirectStandardError (Join-Path $kayit 'api-hata.log') | Out-Null
    for ($i = 0; $i -lt 30; $i++) { Start-Sleep -Milliseconds 300; if (Acik "http://127.0.0.1:$($a.apiPort)/api/health") { Write-Host "API hazir ($env:DATA_SOURCE): http://$($a.merkezIp):$($a.apiPort)/api/health"; return } }
    throw "API acilamadi. Python paketleri: py -m pip install -r KAYNAK-KOD\backend\requirements.txt ; hata: KAYITLAR\api-hata.log"
  }
  'kontrol' {
    $s = Acik "http://$($a.merkezIp):$($a.sunumPort)/sunum/TURKMEN-GIPS-BAKANLIK-SUNUMU.html"
    Write-Host ("Sunum sunucusu  {0}:{1}  -> {2}" -f $a.merkezIp, $a.sunumPort, $(if ($s) { 'ACIK' } else { 'ULASILAMIYOR' }))
    if ($a.veriKaynagy -eq 'api') {
      $p = Acik "http://$($a.merkezIp):$($a.apiPort)/api/health"
      Write-Host ("Canli veri API  {0}:{1}  -> {2}" -f $a.merkezIp, $a.apiPort, $(if ($p) { 'ACIK' } else { 'ULASILAMIYOR' }))
    } else { Write-Host 'Veri kaynagi: kayitli sunum dongusu (API gerekmez)' }
  }
}
