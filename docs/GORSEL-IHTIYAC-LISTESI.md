> **GEÇERSİZ (2026-10-20).** Yerine: [CHATGPT-GORSEL-PROMPTLARI-SON.md](CHATGPT-GORSEL-PROMPTLARI-SON.md) ve [ANA-SARTNAME.md](ANA-SARTNAME.md). Bu dosyadan ChatGPT'ye prompt gönderme.

# Görsel ihtiyaç listesi: gerçeğe uygun görseller ve işçi odaklı iş akışı (v1, 2026-10-20)

Doğruluk kaynağı: `Downloads\00_MASTER_FABRIKA_ICERIGI_v4.txt` (CAD ile doğrulanmış),
REF 01–10 saha fotoğrafları, P1 plan, P2/P3 blok modeller.

## 1. Amaç

Öncü firmaların (Bosch ActiveCockpit, Saint-Gobain) yaklaşımı:
- Makine durumunu işçinin anlayacağı dille söyler: ne oldu, neden, ne yapmalı.
- İşçi ekranın merkezindedir: vardiya, görev, eğitim, güvenlik.
- Görseller gerçek fabrikadır: işçi kendi hattını tanır.

Bu yüzden görsellerde iki kural var:
1. Fabrika görselleri CAD'e ve saha fotoğraflarına birebir uyar.
2. İnsan görünen her sahnede işçi saygın, güvenli ve işinin ustası olarak görünür.

## 2. Mevcut görsellerin denetimi

| Dosya | Kullanıldığı yer | Gerçekle uyum | Karar |
|---|---|---|---|
| `00-campus-film.mp4` | Çig mal, Taýýar önüm | Kampüs renderı, kabaca uyumlu | Kalır |
| `02-forming.mp4` | Önümçilik akymy, Işgärler | Dikey şekillendirme kulesi; gerçekte 3,6 m platform, 4 kağıt rulosu | **Değişir → R1** |
| `03-line-map.mp4` | Sanly karta | Kemerli hangar; gerçekte 3 açıklıklı beşik çatılı çelik hol | **Değişir → R2** |
| `04-cutting.mp4` | Hil gözegçiligi | Genel kesim hattı; gerçekte kırmızı kenar testereleri, sarı kapaklar | **Değişir → R4** |
| `05-dryer.mp4` | Guradyjy | Uzun kutu doğru; paslanmaz bacalar ve sarı üst platform eksik | **Değişir → R3** |
| `07-mcc.mp4` | Energiýa | Genel MCC odası | Kalır, "WIZUALIZASIÝA" etiketiyle |
| `08-control-room.mp4` | Umumy syn, Dolandyryş | Genel kontrol odası, insan yok | **Değişir → W5** |
| `09-flow-map.mp4` | AI / Hasabatlar | Hat düz çizilmiş; gerçekte U şeklinde | **Değişir → R6** |
| Kampüs JPG'leri (10 adet) | Açılış, Zawod meýilnamasy | Kampüs modelinden | Kalır |

Hiçbir mevcut görselde işçi yok. İşçi odaklı sistem için bu en büyük eksik.

Yanlış sekme eşleşmeleri de düzelecek:

| Sekme | Şu an gösterdiği | Olması gereken |
|---|---|---|
| Işgärler | Şekillendirme videosu | W6 vardiya devri, W7 eğitim |
| Tehniki hyzmat | Kampüs filmi | W2 kurutucu bakımı |
| Hil gözegçiligi | Genel kesim | W3 kalite kontrol |
| Hasabatlar | Akış haritası | W5 hat yanı ekranı |

## 3. Bulunan doğruluk hatası: Gyra kesiji

Brief'e göre kuru uçta kırmızı gövdeli, sarı kapaklı **kenar kesme testereleri var**
(REF 07, bölüm 5 Zone C). TV 1'den "Gyra kesiji"yi çıkarmak yanlıştı.

Doğru sıra: ... Guradyjy → **Gyra kesiji** → **Bukjalaýjy** → Gaplaýjy.
İki görsel de elde var; yalnız yapılandırma değişir.

## 4. İşçi odaklı iş akışı (ekranda nasıl görünecek)

Her arıza veya uyarı tek bir "iş kartı" olur:

```text
┌ KESIJI · Sanjin 13 ─────────────── 02:14 ┐
│ Makine diýýär: ýerleşiş datçigi ýalňyş   │  ← makinenin dili, sade Türkmence
│ Näme etmeli: 1) Datçigi arassala          │  ← adım adım talimat
│              2) Kalibrlemäni barla        │
│ Jogapkär: II çalşyk · mehanik             │  ← kim
│ [Kabul etdim] [Kömek gerek] [Ýapyldy]     │  ← işçinin cevabı
└───────────────────────────────────────────┘
```

Ekranlar: hat yanı TV (Bosch ActiveCockpit gibi), vardiya panosu, görev listesi,
eğitim kartları, güvenlik hatırlatmaları. Bu sunum aşamasında hepsi `SIMULÝASIÝA`.

## 5. ChatGPT görsel listesi

Toplam 22 görsel: R1–R6 gerçek hol, W1–W8 işçi sahneleri,
E01–E08 güneş enerjisi (`CHATGPT-GUN-ENERGIYASY-PROMPTLARI.md`).

### 5.1 Gerçek hol görselleri (R1–R6)

Brief'in kendi yöntemiyle üretilir (bölüm 0, YOL A):
1. Yeni sohbet. 1. mesaj: brief `.txt` + P1 + P2 + P3, "Do not generate yet."
2. 2. mesaj: REF 01–10.
3. Sonra aşağıdaki satırı gönder. Durum: **OPERATING** (bölüm 9.8).
4. Görsel gelince brief'teki 9.7 QA promptunu yapıştır.

| No | Dosya | Gönderilecek satır | Yerine geçtiği |
|---|---|---|---|
| R1 | `r1-yas-uc.jpg` | `Run PRESET 3 at the wet end: paper unwind stands and the elevated mixer platform, matching REF 03. OPERATING state.` | 02-forming |
| R2 | `r2-ic-genel.jpg` | `Run PRESET 2 with P3 as the exact composition. OPERATING state.` | 03-line-map |
| R3 | `r3-kurutucu.jpg` | `Run PRESET 4 (dryer hero), matching REF 06. OPERATING state.` | 05-dryer |
| R4 | `r4-kuru-uc.jpg` | `Run PRESET 5 (dry end with red edge-trim saws), matching REF 07–08. OPERATING state.` | 04-cutting |
| R5 | `r5-torbalama.jpg` | `Run PRESET 6 (BEUMER bagging), matching REF 09. OPERATING state.` | Yeni, B bölümi |
| R6 | `r6-kesit.jpg` | `Run PRESET 1 with P2 as the exact composition (aerial cutaway, U-shaped line). OPERATING state.` | 09-flow-map |

### 5.2 İşçi sahneleri (W1–W8)

Aynı sohbette, R2 onaylandıktan sonra gönder. Önce bu ortak kuralı yapıştır:

```text
PEOPLE RULES for the next images (keep all building, color and light rules
of the master brief; these scenes are inside the same real hall):
- Workers are Central Asian men and women, 25–55 years old, calm, competent,
  respectful body language. They are the heroes of the image, in focus.
- PPE always correct: white hard hat, clear safety glasses, grey work uniform
  with reflective stripes, safety shoes, gloves where hands touch machines.
  No logos, no readable name tags.
- Tablets and screens: show a plain, evenly lit light-grey screen surface with
  no UI and no text (the real interface is composited later).
- Photorealistic, documentary feel, natural poses, no posing to camera, no
  smiling-at-camera stock look. 16:9, 4K.
- Machines exactly as in REF photos: white frames, yellow guards and handrails,
  red edge-trim saws, blue only on BEUMER units.
```

| No | Dosya | Prompt | Sekme |
|---|---|---|---|
| W1 | `w1-operator-yas-uc.jpg` | `An operator stands on the yellow-railed mixer platform at the wet end, holding a tablet, looking down at the forming belt; a colleague checks a kraft paper roll on the unwind stand below. Camera eye level from the platform stair.` | Önümçilik akymy |
| W2 | `w2-bakim-kurutucu.jpg` | `A maintenance technician kneels on the dryer roof walkway beside a fan house, holding a handheld vibration sensor against a motor, tablet on the railing next to him. Stainless ducts and chimney behind.` | Tehniki hyzmat |
| W3 | `w3-kalite-kuru-uc.jpg` | `A quality inspector (woman) measures the edge of an off-white plasterboard sheet with a steel ruler and caliper at the white roller table just after the red edge-trim saws; a second sheet waits on the table.` | Hil gözegçiligi |
| W4 | `w4-torbalama-operator.jpg` | `An operator at the grey electrical cabinet of a blue BEUMER palletizer watches a pallet of white bags on the roller conveyor; the inclined conveyors descend from the south wall in the background.` | B bölümi |
| W5 | `w5-hat-yani-ekran.jpg` | `A large wall-mounted display (about 2.5 m wide, plain light-grey screen) stands on a steel post beside the dry-end line; a shift leader points at the screen while two operators listen. Like a line-side information board.` | Umumy syn, Hasabatlar |
| W6 | `w6-calsyk-devri.jpg` | `Shift handover: five workers (two women) stand in a semicircle at the west end near the administration doors, one holds a tablet and speaks; the hall stretches behind them in haze.` | Işgärler |
| W7 | `w7-egitim.jpg` | `An experienced mentor (55) explains a control panel to a young new worker (22) at a grey operator console of the dry end; both look at the panel, the mentor's hand gestures toward a button.` | Işgärler |
| W8 | `w8-howpsuzlyk.jpg` | `At a white sectional door, a worker puts on safety glasses in front of a PPE station: a wall board with pictograms (unreadable), hooks with hard hats and hi-vis vests, a first-aid box.` | Işgärler, giriş |

### 5.3 Güneş enerjisi (E01–E08)

Promptlar: `CHATGPT-GUN-ENERGIYASY-PROMPTLARI.md`. Değişiklik yok.

## 6. Kontrol listesi (her görsel için)

- Hol 3 açıklıklı ve beşik çatılı mı? Kemer, tek açıklık ya da sarı çelik varsa reddet.
- Hat U şeklinde mi (R6)? Düz hat varsa reddet.
- Sarı yalnız korkuluk, merdiven ve koruyucularda mı? Mavi yalnız BEUMER'da mı?
- İşçilerde baret, gözlük ve yelek tam mı?
- Ekranlarda yazı veya sahte arayüz var mı? Varsa reddet.
- Görselde okunabilir yazı ya da logo var mı? Varsa reddet.

## 7. Video

Eski sunumda 8 video vardı. Önce görseller onaylanır. Sonra istenirse onaylı
görsellerden kısa, yavaş kamera hareketli videolar üretilir. Sunum o zamana kadar
görselleri yavaş yakınlaştırma efektiyle gösterir.
