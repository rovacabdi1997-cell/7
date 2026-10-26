# v9 Talimat A — backend boşluk raporu (26.10.2026)

Kaynak: `docs/TAM-PLAN-v9.md` Bölüm 24, 26, 29. İnceleme yalnız okuma; backend kodu değiştirilmedi.
Taban: depo `turkmen-gips-monitoring`, commit `d11717d`, çalışma ağacı kirli. Testler: 75/75 geçti.

## Görev karşılaştırması

| Görev | Bugünkü durum | Boşluk |
|---|---|---|
| G1 Sözleşme kilidi | `docs/api/` yok. Pydantic modeli var, alan başına birim/kaynak/mod var | `openapi.json`, `examples/`, `API-SOZLESMESI.md` yok. Bayatlık eşiği alan başına değil, tek global `STALE_AFTER_SECONDS=15` |
| G2 Zorunlu alanlar | Hat durumu ayrı, makine id'li, saatlik seri, alarm önemi ve zamanı var | Eksik: vardiya üretimi ve vardiya hedefi, kalınlık ve levha tipi, kapasite kullanımı, enerji kW ve kWh, güncel duruş nedeni ve süresi, bağlantı durumu ve son başarılı veri zamanı |
| G3 Veri modu | `SIMULÝASIÝA`, `HAKYKY`, `ÝOK` | `KÖNE` yok. Değer adları planla farklı. Alan başına kaynak zaman damgası yok |
| G4 Akış | `/api/stream`, `event: snapshot`, `retry: 3000`, CORS listesi var | Kopma sonrası KÖNE işareti istemcide; sunucu tarafı yaş alanı eklenecek |
| G5 Üç tag | `tag_mapping.json` içinde hız ve üretim `CANDIDATE`, tag adı okunmadı | Hat çalışıyor/duruyor tag'i yok. Tablo, ölçek, periyot, gecikme yazılı değil. Gerçek bağlantı yok, HAKYKY yazılamaz |
| G6 MES modeli | Bölüm 26 tablolarının hiçbiri yok | Faz 1 şeması ve historian ekleme-yalnız tabloları yazılacak |
| G7 Handoff | `docs/handoff/` yok | Her sözleşme sürümü için dosya açılacak |

## Kurala aykırı mevcut alanlar

| Alan | Sorun | Plan kuralı |
|---|---|---|
| `efficiencyPct` | Tek verimlilik yüzdesi | Bölüm 7: OEE üç bileşen ayrı |
| `outputToday` | Vardiya üretimi alanı yok, ekran günlüğü kullanıyor olabilir | Bölüm 7: günlük, vardiya yerine geçmez |
| `stopMinutesToday` | Güncel duruş alanı yok | Bölüm 7: güncel duruş günlük toplamdan türetilmez |

## Proje sahibinin kararı gereken çelişkiler

1. **Mod değerleri.** Bölüm 3 D7 `SIMULÝASIÝA / KÖNE / MAGLUMAT ÝOK` diyor. Bölüm 29 G3 ASCII `SIMULYASIYA | KONE | MAGLUMAT_YOK` diyor. Bugünkü API Unicode `ÝOK` kullanıyor. Öneri: API'de ASCII kod, ekranda Türkmence metin. Bu değişiklik frontend'i kırar, handoff ile yapılır.
2. **Kirli ağaç.** `backend/` altında 7 dosyada kaydedilmemiş değişiklik var, frontend ve paket dosyalarında da var. Kime ait olduğu belirsiz. K17 için önce bunlar commit edilmeli.
3. **Yol adları.** Plan `KAYNAK-KOD/backend` ve `site/` diyor. Bunlar paket içi adlar. Kaynakta karşılığı `backend/` ve `frontend/`, `sunum/`. Plan paket adlarıyla okunacak.
4. **D10 adresleri.** `/tv/a/`, `/tv/b/` Codex işi. Backend `/api/tv/{tvId}` ucu bugün `1` ve `2` kimliğiyle çalışıyor; `a` ve `b` takma adı eklenmeli mi?

## Önerilen sıra

1. Kirli ağacı sahibiyle birlikte commit et.
2. Sözleşme v2.0.0: dört mod, alan başına `staleAfterSec` ve `sourceTs`, eksik alanlar `MAGLUMAT_YOK` ile.
3. `openapi.json`, örnekler, şema testi, KÖNE testi. K13, K14, K15.
4. HANDOFF-2026-10-26-001 yayınla. K16. Codex tüketir.
5. Üç tag belgesi ve Faz 1 şeması.

## Güncelleme 26.10.2026 — sözleşme v2.0.0

| Görev | Durum | Kanıt |
|---|---|---|
| G1 Sözleşme kilidi | Yapıldı | `docs/api/openapi.json`, `docs/api/API-SOZLESMESI.md`, `backend/app/contract.py` |
| G2 Zorunlu alanlar | Yapıldı. Gerçek kaynakta enerji, OEE, ürün `MAGLUMAT_YOK` | `docs/api/examples/` |
| G3 Veri modu | Yapıldı. ASCII kod, alan başına `sourceTs` ve `staleAfterSec` | `tests/test_contract.py` |
| G4 Akış | Sunucu tarafı tamam. İstemci tarafı KÖNE Codex'te | `test_stream_carries_age_limits_for_client_side_kone` |
| G5 Üç tag | Açık | — |
| G6 MES Faz 1 | Açık | — |
| G7 Handoff | Yapıldı | `docs/handoff/HANDOFF-2026-10-26-001.md` |

Kabul: K13, K14, K15, K16 için kanıt dosyaları var. Test: 103/103. Kararı açık kalan: `/api/tv/a`, `/api/tv/b` takma adı.
