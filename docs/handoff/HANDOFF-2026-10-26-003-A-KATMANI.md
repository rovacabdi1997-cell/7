# HANDOFF-2026-10-26-003 — A katmanı (sunum) uygulama brief'i

| Alan | Değer |
|---|---|
| Gönderen | Claude, proje sahibinin onayıyla |
| Alan | Codex (frontend) |
| Plan maddesi | TAM-PLAN-v9 bölüm 9, 10, 13–17. Talimat B, Görev 4 |
| Görsel referans | `docs/tasarim/A-SUNUM-TASLAK-v9.html`, proje sahibi 26.10.2026'da onayladı |
| Veri | Sözleşme v2.0.0, `HANDOFF-2026-10-26-001` |
| Ön koşul | `types.ts` ve `DataProvider.tsx` v2'ye geçmiş olmalı (handoff 001) |
| Kabul satırları | K1, K3, K4, K5, K6, K7, K8 bu ekran için |

## Codex'in yapacağı tek iş

Mevcut hat TV ekranına (`features/screens/LineTv.tsx`) açık temada çalışan A katmanı yerleşimini ekle. Taslak HTML görsel referanstır, kopyalanacak kod değildir.

## Nereye

- Yeni route açılmaz (bölüm 4 kapsam kilidi). A katmanı `/tv/a/?tema=acik` ve `/tv/b/?tema=acik` ile açılır.
- Mevcut `?tema=acik` mekanizması (`components/PresentationTheme.tsx`) kullanılır.
- Koyu B katmanı aynen kalır. Yalnız açık temada A yerleşimi devreye girer.
- Yeni stil dosyası açılmaz. Renk, ölçü ve font `tokens/tokens.json` kaynağından gelir (Talimat B, Görev 1).

## Yerleşim (3840 × 2160 tuval)

| Öğe | Ölçü | İçerik | API alanı |
|---|---|---|---|
| Başlık bandı | 132 px, `bant` rengi | Solda sistem adı 44 px. Sağda tek veri modu göstergesi, sonra `Gün · gg.aa.yyyy · ss:dd` (Asia/Ashgabat) | `snapshot.dataMode`, `snapshot.timestamp` |
| KPI satırı | 520 px, 4 eşit blok | Aşağıdaki tablo | |
| Ana satır | kalan yükseklik | Solda 2400 px saatlik grafik, 48 px boşluk, sağda 1200 px akış | |
| Hedef çubuğu | 96 px | Solda `Maksadyň ýerine ýetirilişi 100,6 %`, sağda hat adı | `line.fulfilmentPct`, `line.name` |
| Boşluklar | yan 96, üst 92, alt 84, satır arası 80 | Karar 3 | |

### KPI blokları

| Etiket | Büyüklük | Birim | API alanı | Alt satır |
|---|---|---|---|---|
| GÜNDELIK ÖNÜM | 260 px | m² / t | `line.outputToday` | `şu wagta çenli maksat {planToDate}` |
| GÜNDELIK MAKSAT | 180 px | m² / t | `line.planToday` | `{outputToday ÷ planToday} % ýerine ýetirildi` |
| HAT TIZLIGI | 180 px | `line.speed.unit` | `line.speed` | gipsokarton: `nominal {nominalRate ÷ boardWidth ÷ 60} m/min`; gury garyndy: `nominal {nominalRate} t/sag` |
| IŞJEŇ DUÝDURYŞ | 180 px | sany | açık alarmların sayısı, hat filtresiyle | yoksa `duýduryş ýok`, varsa en öncelikli alarmın makinesi |

Alarm sayısı sıfırdan büyükse sayı `ariza` rengini alır. Diğer sayılar nötr kalır.

### Saatlik grafik

- ECharts, düz sütun, `yapisal` yeşil, %55 opaklık. Sütun genişliği 48 px (karar 5).
- X ekseni üretim günü: 08:00'dan 07:00'a 24 dilim, etiket her 3 saatte.
- Hedef: kesikli çizgi, 2 px, `metin-2`, sağ uçta `maksat {değer}` etiketi.
- Son nokta devam eden saattir: %28 opaklık ve üstünde `{saat} · dowam edýär`.
- Kaynak: `line.trend.points[].actual` ve `.plan`.

### Önümçilik akymy

- Dikey liste, 11 makine, `line.equipment` sırasıyla (karar 2). Satırda sıra no, ad, durum.
- Durum renk, şekil ve yazıyla gösterilir (bölüm 15): Işleýär yeşil dolu daire, Durdy amber kare, Näsazlyk kırmızı üçgen.
- Arızada yalnız arızalı makinenin satırı kırmızı olur. Kalan satırlar A katmanında `Işleýär` görünür (karar 4). Ekran kararmaz.
- Arızalı makine `line.currentStop.equipmentId` alanından bulunur. Ad ile eşleme yapılmaz.

## Veri modu kuralları (A katmanı)

- Tek gösterge başlık bandında. Kart başına tekrar yok.
- `SIMULYASIYA`: gri nokta ve `Simulýasiýa` yazısı.
- A katmanında `MAGLUMAT_YOK` gösterilmez, demo değeri gösterilir (D11). Bu geçiş sessiz olamaz (D7): demo değeri gösterilen her an başlıktaki gösterge `Simulýasiýa` yazar. Gerçek ve demo değer aynı ekranda karışmaz; bir alan bile demoya düşerse gösterge `Simulýasiýa` olur.
- `KONE` alan soluk ve kesikli halkayla işaretlenir, yeşil kalmaz.

## Biçim

- Rakam: ondalık virgül, binlik ayırıcı U+00A0. Örnek `13 795,3`.
- Tarih `gg.aa.yyyy`, saat 24 saat, gün adları Türkmence (bölüm 22).
- Tüm sayılar `font-variant-numeric: tabular-nums`.
- En küçük yazı 40 px. İstisna yok.
- Değer değişiminde 200 ms ease-out. Durum noktası nabzı `prefers-reduced-motion` ile durur.

## Onaylanan altı karar (proje sahibi, 26.10.2026)

| No | Karar |
|---|---|
| 1 | Etiketler Türkmence: `Gündelik önüm`, `Gündelik maksat`, `Maksadyň ýerine ýetirilişi`. Birim `m/min` |
| 2 | Önümçilik akymy dikey liste. 11 ad 40 px ile 1200 px'e tek satır sığmıyor |
| 3 | Satır arası 80 px. Spec toplamı 2172 px idi |
| 4 | A katmanında arızada yalnız arızalı makine kırmızı, diğerleri yeşil. B katmanı backend durumunu aynen gösterir |
| 5 | Saatlik sütun 48 px |
| 6 | Font dosyaları gelene kadar sistem fontu yedek. Gilroy ve Inter yerel WOFF2 olarak eklenecek |

## Kabul kanıtları (`BELGELER/` altına)

| Kanıt | Nasıl |
|---|---|
| 1080p ve 4K ekran görüntüsü, normal ve arıza | Playwright, `docs/api/examples/snapshot-simulyasiya*.json` ile |
| 40 px altı yazı yok | Tüm metin düğümlerinin `font-size` listesi |
| Rakam ve imla | `13 795,3` biçimi ve büyük İ taraması |
| Renk körlüğü | Deuteranopi simülasyonunda üç durum ayırt ediliyor |

## Codex'e sorular

Yok. Belirsizlik çıkarsa koda geçmeden `docs/handoff/` altına yazılır (bölüm 6).
