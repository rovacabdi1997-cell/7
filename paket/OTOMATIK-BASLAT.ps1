# Bu bilgisayar açıldığında (kullanıcı oturum açınca) ilgili ekranı kendiliğinden başlatır.
#   -Ekran merkez | tv1 | tv2      -Kaldir : görevi siler
# Yönetici yetkisi gerekmez; görev yalnız bu kullanıcı için kurulur.
param([ValidateSet('merkez','tv1','tv2')][string]$Ekran, [switch]$Kaldir)
$ErrorActionPreference = 'Stop'
$paket = Split-Path -Parent $MyInvocation.MyCommand.Path
$ad = "TurkmenGips-$Ekran"
if ($Kaldir) {
  Unregister-ScheduledTask -TaskName $ad -Confirm:$false -ErrorAction SilentlyContinue
  Write-Host "Kaldirildi: $ad"; return
}
$islem = New-ScheduledTaskAction -Execute 'powershell.exe' -Argument "-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$paket\BASLAT.ps1`" -Ekran $Ekran" -WorkingDirectory $paket
$tetik = New-ScheduledTaskTrigger -AtLogOn -User $env:USERNAME
# Ağ ve masaüstü hazır olsun diye 30 sn gecikme.
$tetik.Delay = 'PT30S'
Register-ScheduledTask -TaskName $ad -Action $islem -Trigger $tetik -Description 'Turkmen Gips ekran baslatici' -Force | Out-Null
Write-Host "Kuruldu: $ad (oturum acilinca 30 sn sonra baslar). Kaldirmak icin: OTOMATIK-BASLAT.ps1 -Ekran $Ekran -Kaldir"
