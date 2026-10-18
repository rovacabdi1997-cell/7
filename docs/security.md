# Güvenlik

## Uygulanan kontroller

| Kontrol | Yer |
|---|---|
| API yalnız `GET` kabul eder | `backend/app/main.py`, test: `test_only_get_is_allowed` |
| Yazma ve yönetim komutları reddedilir | `backend/adapters/readonly_guard.py`, 13 test |
| Her sorgu guard'dan geçer, atlanamaz | `GuardedExecutor` |
| ADO bağlantısı `adModeRead`, recordset `adLockReadOnly` | `AdoExecutor` |
| Bağlantı bilgisi yalnız ortam değişkeninde | `WINCC_CONNECTION_STRING` |
| Hata mesajlarında bağlantı ayrıntısı yok | Yalnız hata türü yazılır |
| Doğrulanmamış veri gerçek gibi gösterilmez | `mode` alanı, `test_unverified_mapping_returns_empty_not_demo` |

## Bilinen riskler

1. **Next.js 15.5.2 güvenlik açığı (CVE-2025-66478).** Bu bilgisayarda internet olmadığı için önbellekteki sürüm kullanıldı. İnternet olan ilk fırsatta yükseltilmeli:
   ```bash
   npm --prefix frontend install next@15 --save-exact
   npm --prefix frontend audit
   ```
   15.5.7 bu açığı kapatır. Sonraki yamaları da almak için 15.x'in en son sürümü kurulmalı ve `npm audit` temiz çıkmalı.
   Fabrika ağına kurmadan önce zorunlu.
2. **WinCC OPC UA sunucusu güvenliksiz.** `OpcUaServerWinCC.xml` içinde `SecurityPolicy#None` ve `Anonymous` açık. Fabrikaya bildirilmeli. Bizim sistem bu yolu kullanırsa şifreli politika ve ayrı kullanıcı istenmeli.
3. **`PASS/UserAdmin.ini`** arşivde var. İçeriği hiçbir belgeye veya koda alınmadı.
4. **QQ kurulum dosyası** (`11111/QQ_9.9.12_240729_x64_01.exe`) arşivde var. WinCC ile ilgisi yok, çalıştırılmamalı.

## Ağ

- API `0.0.0.0:8010`, arayüz `:3010`. Yalnız fabrika iç ağında açılmalı, internete açılmamalı.
- CORS izinli kaynakları `CORS_ORIGINS` ile sınırlandır.
