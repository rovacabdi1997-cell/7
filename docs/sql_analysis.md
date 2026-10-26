# SQL Server analizi

Durum: 2026-10-26. Yapılandırma veritabanlarından tag listesi metin çıkarma ile okundu.

## Güncelleme 26.10.2026

- `chengxing.mdf` kopyalarından 417 tag adı ve PLC adresi çıkarıldı: CPI 329, IOP 115 ham kayıt.
- Liste: `docs/wincc/wincc-tag-listesi-2026-10-26.csv`.
- Bağlantı `chengxingPLC`, kanal SIMATIC S7-1200/S7-1500, PLC adresi adayı `192.168.10.6`.
- Üç canlı tag ve okuma yolu: `docs/handoff/HANDOFF-2026-10-26-002-UC-TAG.md`.
- SQL Server yine kurulmadı. Tablo yapısı ve canlı değer okunmadı. Aşağıdaki 2026-10-18 notları geçerli.

## Bilinenler

| Bilgi | Değer | Kaynak |
|---|---|---|
| Sürüm | SQL Server 2008 R2 | Saha fotoğrafları |
| Instance | `WINCC` (ör. `IOP\WINCC`) | Saha fotoğrafları, `UALogFile.txt:6` |
| Runtime DB | `CC_chengxin_23_04_09_13_06_06R` | `chengxing/UA/UALogFile.txt:6` |
| Yapılandırma DB kopyası | `chengxing.mdf` (10 MB) | Arşiv |
| Runtime DB kopyası | `chengxingRT.mdf` (10 MB) | Arşiv |
| Alarm yapılandırması | `CHENGXINGAlg.mdf` (10 MB) | Arşiv |
| Alarm arşivi segmentleri | `ArchiveManager/AlarmLogging/*_ALG_*.mdf` | Arşiv |
| Tag Logging arşivi | **Yok** | `ArchiveManager` altında yalnız `AlarmLogging` var |

## Neden okunamadı

1. Bu oturumda salt-okunur string çıkarma scripti izin sistemi tarafından beş kez engellendi.
2. Bu bilgisayarda SQL Server kurulu değil. PostgreSQL 16 var, `.mdf` okuyamaz.
3. İnternet erişimi yok. SQL Server Express veya Docker imajı indirilemiyor.
4. Dosyalar WinCC çalışırken kopyalandı. Attach denemesi tutarsızlık hatası verebilir.

## Okuma yöntemleri (öncelik sırasıyla)

| Yöntem | Ne verir | Gereken |
|---|---|---|
| String çıkarma (`mdf_strings.py`) | Tag adları, alarm metinleri, bağlantı adları | Yalnız izin |
| Ayrı makinede SQL Server'a kopya attach | Tablo/kolon yapısı, tam tag listesi | SQL Server 2008 R2+ kurulu, internetsiz olmayan makine |
| Fabrikada WinCC Explorer'dan export | Resmî tag listesi (CSV) | Fabrika yetkilisi, üretim durunca |
| WinCC OLE DB ile canlı okuma | Gerçek alarm ve arşiv değerleri | Connectivity Pack lisansı |

Kopyaları attach etmek fabrikadaki canlı sisteme dokunmaz. Yine de yalnız kopya üzerinde ve `READ_ONLY` modunda yapılmalı.

## Beklenen içerik

WinCC V7 yapılandırma veritabanında tag tanımları, bağlantılar ve alarm metinleri bulunur. Kesin tablo adları okununca bu belgeye eklenecek. Doğrulanmamış tablo adı yazılmadı.
