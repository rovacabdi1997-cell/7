# WinCC arşiv envanteri — `sql cart curt.rar`

Durum: 2026-10-18, dosya düzeyinde inceleme. MDF içerikleri henüz okunmadı.
Kaynak: `D:\turkmen gips\sql cart curt.rar` (253 MB sıkıştırılmış, 641 MB açık, 898 dosya, 164 klasör).
Açılmış kopya: `D:\turkmen gips\sql cart curt\`.

## Sistem

| Bilgi | Değer | Kaynak |
|---|---|---|
| SCADA | SIMATIC WinCC V7.3 | Saha fotoğrafları |
| Veritabanı | SQL Server 2008 R2, instance `WINCC` | Saha fotoğrafları |
| Proje adı | `chengxing` (成型, şekillendirme hattı) | `*.MCP` |
| Bilgisayar adları | `IOP`, `CPI` | Alarm arşivi dosya adları |
| Runtime veritabanı | `CC_chengxin_23_04_09_13_06_06R` @ `IOP\WINCC` | `chengxing/UA/UALogFile.txt:6` |
| Proje oluşturma | 2023-04-09 | Runtime DB adı, klasör tarihleri |
| OPC UA sunucu | `opc.tcp://[HostName]:4862` | `chengxing/OPC/UAServer/OpcUaServerWinCC.xml:6` |
| Redundancy | Kapalı | `UALogFile.txt:1-3` |

## Proje kopyaları

| Klasör | Dosya | Boyut | Not |
|---|---|---|---|
| `二横wincc/chengxing` | 297 | 138 MB | `ProjectOpened.lck` var. Kopyalandığı anda WinCC'de açık olan proje bu. "二横" = ikinci hat. |
| `chengxing` | 298 | 140 MB | `IOP` bilgisayarının kopyası, `二横wincc` ile büyük ölçüde aynı. |
| `chengxing 2/chengxing` | 289 | 115 MB | `CPI` bilgisayarının kopyası, ek ekran `NewPdl1.Pdl` var. |
| `adada` | 13 | 37 MB | Yalnız veritabanı dosyaları ve proje dosyası. |
| `11111` | 1 | 195 MB | `QQ_9.9.12_240729_x64_01.exe`. WinCC ile ilgisi yok. Çalıştırılmamalı. |

## Veritabanı dosyaları

| Dosya | Görev | Durum |
|---|---|---|
| `chengxing.mdf` | Yapılandırma: tag, bağlantı, alarm tanımı | Okunmadı |
| `chengxingRT.mdf` | Runtime veritabanı | Okunmadı |
| `CHENGXINGAlg.mdf` | Alarm yapılandırması | Okunmadı |
| `ArchiveManager/AlarmLogging/IOP_*_ALG_*.mdf` | Alarm geçmişi, 2023-06-29 04:03–09:27 | Okunmadı |
| `ArchiveManager/AlarmLogging/CPI_*_ALG_*.mdf` | Alarm geçmişi, 2023-06-26 14:27 – 2023-07-06 05:17 | Okunmadı |

Dosyalar WinCC çalışırken kopyalandı. SQL Server'a attach edilirse tutarsızlık hatası verebilir.

## Önemli bulgular

1. **Tag Logging arşivi yok.** `ArchiveManager` altında yalnız `AlarmLogging` var. `TagLoggingFast` veya `TagLoggingSlow` klasörü bulunmuyor. Geçmiş proses değerleri bu kopyada yok.
2. **Alarm geçmişi kısa ve eski.** Yalnız 2023 Haziran–Temmuz devreye alma dönemini kapsıyor.
3. **Tag Logging yapılandırması var.** `CCConfigStudio.ini` içinde `TlgPVARCHIVES`, `TlgCARCHIVES`, `TlgTIMESERIES` editör ayarları duruyor. Hangi tag'lerin arşivlendiği `chengxing.mdf` içinde.
4. **Ekranlar:** `GraCS/NewPdl0.Pdl` ana ekran, `NewPdl1.Pdl` yalnız `CPI` kopyasında.

## Güvenlik notları

- OPC UA sunucusunda `SecurityPolicy#None` ve `Anonymous` kullanıcı açık. Ağdaki herkes şifresiz bağlanabilir. Fabrikaya bildirilmeli.
- `chengxing/PASS/UserAdmin.ini` kullanıcı yönetimine ait. İçeriği belgelere ve koda alınmayacak.
- QQ kurulum dosyası arşivden silinmeli veya ayrı tutulmalı.

## Sonraki adım

MDF içeriklerini salt-okunur okumak. Bu oturumda izin sistemi engelliyor.
Okuma scripti: oturum scratchpad'inde `tools/mdf_strings.py`.
