# Türkmen Gips — İki TV planı (v1, 2026-10-20)

## Karar özeti

| Konu | Karar |
|---|---|
| TV 1 | Gipsokarton hattı, sabit ekran, döngü yok |
| TV 2 | Gury garyndy hattı, sabit ekran, döngü yok |
| Çözünürlük | 1920×1080 tasarım tabanı, 3840×2160'ta 2× ölçek |
| Dil | Türkmence, bütün metin kalın (700–800) |
| Renk | Mevcut `frontend/styles/globals.css` tokenları; yeni renk eklenmez |
| Görsel | ChatGPT izometrik makine görselleri üretir; animasyon kodla verilir |
| Veri | Merkez PC'de tek backend, iki TV aynı SSE akışının kendi hattını dinler |
| Ton | Devlet kurumu ciddiyeti: süs yok, şaka yok, neon yok, logo ve tarih her zaman görünür |

## İş bölümü

| Kim | Ne yapar | Teslim |
|---|---|---|
| ChatGPT | Makine görselleri, hat arka planı, ikon seti | `docs/CHATGPT-TASARIM-PROMPTU.md` içindeki listeye göre PNG |
| Claude | Backend, SSE sözleşmesi, akış/animasyon durum verisi, TV sayfalarının veri bağlantısı | Kod + test |
| Kullanıcı | Görselleri onaylar, saha verisini ve TV IP'lerini sağlar | Onay |

## TV ekran yerleşimi (ikisi aynı iskelet)

```text
┌────────────────────────────────────────────────────────────────────┐
│ LOGO  TÜRKMEN GIPS HJ        HAT ADI (dev, kalın)      SAAT  TARİH │ 96px
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│   İZOMETRİK HAT SAHNESİ: makineler soldan sağa, aralarında         │ ~52%
│   akan malzeme animasyonu, her makinenin üstünde durum ışığı       │
│                                                                    │
├──────────────┬──────────────┬──────────────┬───────────────────────┤
│ HAT HIZI     │ BUGÜN ÜRETİM │ PLAN / FARK  │ AKTİF DUÝDURYŞ        │ ~30%
│ dev rakam    │ dev rakam    │ ilerleme     │ en kritik 3 kayıt     │
├──────────────┴──────────────┴──────────────┴───────────────────────┤
│ VERİ MODU rozeti · son güncelleme zamanı · SALT-OKUNUR · çalşyk    │ 48px
└────────────────────────────────────────────────────────────────────┘
```

- TV 1 makineleri: Gips berijisi, Garyşdyryjy, Köpük generatory,
  Formirleme stoly, Gatama lentasy, Kesiji, Guradyjy, Gyra kesiji, Gaplaýjy.
- TV 2 makineleri: Çig mal silosy, Dozirleýji, Garyşdyryjy, Elewator,
  Taýýar önüm bunkeri, Gaplaýjy maşyn, Palet örüji.
- Rakamlar en az 96px, etiketler en az 28px; 4 metreden okunmalı.

## Animasyon kuralı

Animasyon süs değildir, makine durumunu gösterir.

| Durum | Makine | Aradaki akış |
|---|---|---|
| `RUNNING` | Hareketli parçalar döner, yeşil ışık | Malzeme akar, hız `flowRate` ile orantılı |
| `STOPPED` | Hareket yok, sarı ışık | Akış durur, hat yavaşça söner |
| `FAULT` | Hareket yok, kırmızı ışık nabız atar | Arızalı makineden sonraki akış durur |
| `UNKNOWN` / `ÝOK` veri | Görsel soluk, gri ışık, "Maglumat ýok" | Akış çizilmez |

Bir makine durunca sonraki makineye malzeme gitmez. Bu kural backend'den gelir,
frontend tahmin etmez. Ayrıntı ve hat tipine göre yayılım kuralı:
[IKI-TV-TEKNIK-TASARIM.md](IKI-TV-TEKNIK-TASARIM.md).

## Backend işleri (Claude)

| No | İş | Kabul ölçütü |
|---|---|---|
| TV-B1 | `Line` modeline `flow` listesi: `from`, `to`, `active`, `flowRate` (0–1) | Duran makinenin çıkış akışı `active:false`; test |
| TV-B2 | `GET /api/stream?line=gipsokarton` hat filtreli SSE | TV yalnız kendi hattını alır; eski `/api/stream` bozulmaz |
| TV-B3 | `GET /api/tv/{tvId}` ekran yapılandırması: hat, başlık, makine sırası, görsel anahtarları | `tv-1`, `tv-2` tanımlı; bilinmeyen id `404` |
| TV-B4 | Bağlantı sağlığı: her olaya `seq` ve `staleAfterSec`; SSE `retry` ve heartbeat | Kopmada ekran 15 sn içinde "Baglanyşyk ýok" gösterir |
| TV-B5 | Makine görsel anahtarı: her `Equipment` için `assetKey` | Görsel dosya adı ile birebir eşleşir |
| TV-B6 | Demo senaryosu: normal → arıza → toparlanma, deterministik | Sunumda aynı saat aynı durum |
| TV-B7 | Testler ve iki TV için tarayıcı doğrulaması | Tüm testler geçer, 1920×1080 ekran görüntüsü |

## Gerçek zamanlı veri

- Kaynak sırası: WinCC SQL salt-okunur → adaptör → tek `Snapshot` → SSE 5 sn.
- Bugün doğrulanmış gerçek alan sayısı 0/14. Bu yüzden canlı görünen her değer
  `SIMULÝASIÝA` rozeti taşır.
- `HAKYKY` rozeti yalnız `tag_mapping.json` içinde `VERIFIED` olan alanda çıkar.
- SQL koparsa ekran demo değerine dönmez, bağlantı kaybını gösterir.

## Açık noktalar

- `tmgips.rar` içindeki paket yerel depodan yeni: `tasarim_tv_sql.md`,
  `TV-1-GIPSOKARTON.bat`, `TV-2-KURU-KARISIM.bat` depoda yok. Önce birleştirilmeli.
- TV'lerin gerçek IP'si ve merkez PC IP'si bilinmiyor.
- Makine sırası demo listesidir; saha onayı yok.
- Türkmence metinler ana dil kontrolünden geçmedi.
