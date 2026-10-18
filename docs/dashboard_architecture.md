# Mimari

```text
WinCC / SQL Server / OPC UA
        │  salt-okunur
        ▼
backend/adapters   ── demo.py (SIMULÝASIÝA) | wincc_sql.py (HAKYKY)
        │  tek Snapshot modeli
        ▼
backend/api        ── FastAPI, yalnız GET + SSE
        │  /api/stream (5 sn)
        ▼
frontend           ── Next.js, Türkmence arayüz
        │
        ▼
Yönetim PC'leri, fabrika TV'leri (kiosk)
```

## İlkeler

1. **Tek model.** Her adaptör aynı `Snapshot` yapısını döner. Ekranlar hangi adaptörün çalıştığını bilmez.
2. **Karışma yok.** `DATA_SOURCE=wincc` iken doğrulanmamış alan boş gelir, demo değerine düşmez. Her değer `mode` alanı taşır: `SIMULÝASIÝA`, `HAKYKY` veya `ÝOK`.
3. **Yazma yok.** API yalnız `GET` kabul eder. Her sorgu `readonly_guard.py` kontrolünden geçer.
4. **İnternetsiz.** Web fontu, CDN veya grafik kütüphanesi yok. Grafikler düz SVG.
5. **Deterministik demo.** Aynı saat aynı değeri verir. Sunumda sürpriz olmaz.

## Ekranlar

| Yol | Ekran |
|---|---|
| `/` | Baş dolandyryş paneli |
| `/gipsokarton` | Gipsokarton önümçiligi |
| `/gury-garyndy` | Gury garyndy önümçiligi |
| `/duyduryslar` | Duýduryşlar we durmalar |
| `/calsyk` | Çalşyk we işgärler |
| `/tv` | Büyük TV görünümü, 15 sn'de bir slayt değişir |

TV parametreleri: `?slide=0..3` sabit slayt, `?interval=20` saniye.

## API

| Uç | Açıklama |
|---|---|
| `GET /api/health` | Durum, adaptör, veri modu |
| `GET /api/snapshot` | Tam anlık görüntü |
| `GET /api/overview` | Baş panel özeti |
| `GET /api/lines/{id}` | `gipsokarton` veya `gury-garyndy` |
| `GET /api/alarms?state=open\|all&line=` | Alarmlar |
| `GET /api/shift` | Vardiya |
| `GET /api/mapping` | Veri eşleme tablosu |
| `GET /api/stream` | SSE, her `REFRESH_SECONDS` saniyede bir snapshot |

OpenAPI belgesi: `http://<sunucu>:8010/docs`.
