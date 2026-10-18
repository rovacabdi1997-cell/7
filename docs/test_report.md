# Test raporu — 2026-10-18

## Otomatik testler

| Test | Sonuç |
|---|---|
| Backend `pytest` | **44 geçti, 0 başarısız** |
| Frontend `tsc --noEmit` | Hata yok |
| Frontend `next build` | Başarılı, 9 sayfa |
| Türkmence harf kontrolü (`check:tk`) | Geçti |
| 6 sayfa + API sağlık HTTP kontrolü | Hepsi 200 |

Backend test kapsamı:

- Demo adaptör: deterministik çıktı, her değerde `SIMULÝASIÝA`, yalnız iki hat, arıza ve planlı duruş, gün başlangıcı 08:00, gece saatleri, torba hesabı, alarm durumları, ay toplamı.
- Vardiya: sabah, gece yarısı geçişi, mola.
- Salt-okunur koruma: 4 izinli, 9 reddedilen sorgu.
- WinCC adaptör: doğrulanmamış alan sorgulanmaz, doğrulanmış alan `HAKYKY` okunur, kaynak hatasında değer uydurulmaz, eşlemedeki yazma sorgusu engellenir, alarm satırları eşlenir.
- API: tüm uçlar, filtreler, 404, SSE akışı, `POST` reddi.

## Tarayıcı testleri

| Senaryo | Sonuç |
|---|---|
| Baş panel, gipsokarton, gury garyndy, alarmlar, vardiya | Veriler görünüyor, konsol hatası yok |
| TV 1920×1080, 4 slayt | Taşma yok |
| TV 3840×2160 | Taşma yok, taban yazı 44 px |
| Mobil 375 px | Yatay kaydırma yok, tablo kendi içinde kayar |
| Alarm filtresi "Hemmesi" | 3 kapanmış alarm listelendi |
| API kapatıldı | "Serwer bilen aragatnaşyk ýok" uyarısı, sahte veri yok |
| API yeniden açıldı | Otomatik yeniden bağlandı, uyarı kalktı |

## Test edilemeyenler

| Konu | Neden |
|---|---|
| Gerçek WinCC bağlantısı | Fabrika sistemine erişim yok; doğrulanmış alan 0 |
| `AdoExecutor` gerçek çalışması | pywin32 ve WinCC Connectivity Pack bu makinede yok; yalnız sahte executor ile test edildi |
| MDF içeriği | İzin sistemi engelledi |
| Gerçek TV donanımı | Yalnız tarayıcı çözünürlük emülasyonu |
| Türkmence dil doğruluğu | Otomatik kontrol yalnız Türkçeye özgü harfleri yakalar; anadili Türkmence biri metinleri gözden geçirmeli |
| `npm audit` | İnternet yok |

## Bilinen sorun

Next.js 15.5.2 güvenlik açığı taşıyor. Ayrıntı: `security.md`.
