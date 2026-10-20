# ChatGPT görsel promptları — SON SÜRÜM (2026-10-20)

Bu dosya önceki bütün ChatGPT prompt dosyalarının yerine geçer.
Toplam 14 görsel: 8 gerçek fotoğraf düzenlemesi (W) + 6 güneş enerjisi parçası (E).
Gerçek fotoğraflar `C:\Users\ADMIN\Downloads\` altındadır.

## Kural: orijinal fotoğraf aynı kalır

W1–W8'de ChatGPT yeni sahne üretmez. Gönderilen gerçek fotoğrafı **düzenler**:
hol, makineler, ışık, renkler, kamera açısı birebir kalır; yalnız insan ve gerekirse
tek bir nesne eklenir. Her W için yeni sohbet aç, fotoğrafı ekle, önce ORTAK KURALI,
sonra o görselin promptunu gönder.

## ORTAK KURAL (W1–W8, her sohbetin ilk mesajı)

```text
Edit the attached REAL photo of the TÜRKMEN GIPS gypsum plant. This is a
documentary photo of a real factory: keep EVERYTHING identical — building,
machines, colours, light, dust, camera angle, lens, framing and resolution.
Do not add, move, clean or recolour any machine or structure.
Only add what the next message asks for.

People rules:
- Turkmen men and women, 25–55 years old, calm and competent, natural working
  poses, nobody looks at the camera, no stock-photo smiles.
- Correct PPE: white hard hat, clear safety glasses, light grey work uniform
  with reflective stripes, safety shoes, work gloves where hands touch machines.
- No logos, no readable text, no name tags.
- Tablets and screens show a plain, evenly lit light-grey surface with no UI.
- People must match the photo's real scale, light direction, shadows, dust and
  grain, so they look photographed in the same moment.
Return one edited image, same aspect ratio as the input.
```

## W — işçi sahneleri (gerçek fotoğraf düzenlemesi)

| No | Ekle | Prompt | Çıktı | Sekme |
|---|---|---|---|---|
| W1 | `IMG_6191.jpeg` | `Add one operator standing on the yellow-railed platform, holding a tablet and looking down at the forming belt.` | `w1-operator-yas-uc.jpg` | Gipsokarton bölümi, TV 1 |
| W2 | `IMG_6204.jpeg` | `Add one maintenance technician kneeling beside the multi-deck dryer racks, holding a handheld vibration sensor against a drive motor, a small tool case on the floor.` | `w2-bakim-guradyjy.jpg` | Tehniki hyzmat |
| W3 | `IMG_6197.jpeg` | `Add one off-white plasterboard sheet lying on the yellow-guarded roller table, and a woman quality inspector measuring its edge with a steel ruler.` | `w3-hil-barlag.jpg` | Hil gözegçiligi |
| W4 | `IMG_6211.jpeg` | `Add one operator standing at the grey electrical cabinet of the blue BEUMER machine, one hand on the cabinet door, watching the machine.` | `w4-torbalama.jpg` | Gury garyndy bölümi, TV 2 |
| W5 | `IMG_6196.jpeg` | `Add a large wall-mounted display (about 2.5 m wide, plain light-grey screen) on a grey steel post beside the roller tables, and a shift leader pointing at it while two operators listen.` | `w5-hat-yani-ekran.jpg` | Umumy syn, Hasabatlar |
| W6 | `IMG_6185.jpeg` | `Add a shift handover: five workers (two women) standing in a loose semicircle in the foreground, one holding a tablet and speaking.` | `w6-calsyk-devri.jpg` | Işgärler |
| W7 | `IMG_6201.jpeg` | `Add an experienced mentor (about 55) and a young new worker (about 22) beside the line; the mentor explains, gesturing toward the red drive unit; both look at the machine.` | `w7-ussat-sagirt.jpg` | Işgärler |
| W8 | `IMG_6188.jpeg` | `Add a PPE station against the wall: a board with safety pictograms (no readable text), hooks with white hard hats and reflective vests, a first-aid box; one worker putting on safety glasses in front of it.` | `w8-howpsuzlyk.jpg` | Işgärler, giriş |

## E — güneş enerjisi parçaları (izometrik, şematik)

TV makine görsellerini ürettiğin sohbette gönder. Önce bu ana kural:

```text
Same visual system as the previous TÜRKMEN GIPS machine icons: clean isometric
3D render, true isometric 30° camera, same lens and scale, matte materials,
light grey steel, graphite frames, soft light from top-left, one soft contact
shadow. Colour system is WHITE and BLUE: accent blue #1E9BE0, dark blue #0C6FB8.
Solar modules: dark blue-black monocrystalline glass, thin silver frames.
Transparent PNG, 1254×1254, object ~70% of canvas, centred. No text, no
numbers, no logos, no people. Serious, government-grade engineering look.
Energy flows from LEFT-BACK to RIGHT-FRONT. One small empty grey status-lamp
socket on top. Reply with the image and file name only.
```

| No | Prompt | Dosya |
|---|---|---|
| E01 | `Section of a large white industrial hall roof carrying dense rows of solar panels tilted 25° south, maintenance walkways between rows, a cable tray to the right-front edge.` | `tg-eco-01-cati-ges.png` |
| E02 | `Solar carport: long steel canopy, graphite columns, blue beam caps, roof fully covered with panels, three empty truck bays below.` | `tg-eco-02-otopark-ges.png` |
| E03 | `Outdoor power skid on a concrete pad: four string inverter cabinets (light grey, blue side panels) and a compact medium-voltage transformer with radiator fins.` | `tg-eco-03-inverter.png` |
| E04 | `20-foot battery storage container, light grey with a blue stripe along the top, HVAC unit on the side, small fire-suppression cabinet beside it.` | `tg-eco-04-batareya.png` |
| E05 | `Indoor main switchboard: five tall light-grey cabinets with blue plinths, one with a small dark blank screen and a meter window.` | `tg-eco-05-pano.png` |
| E06 | `Compact grid substation: fenced enclosure, one transformer, a metering kiosk with a blue door, two insulator poles with short line stubs.` | `tg-eco-06-sebeke.png` |

Kampüs görünümünde güneş paneli (önceki E07/E08) **istenmiyor**: kampüs görselleri
gerçek fotoğraf değil model renderı. Güneş modülü izometrik parçalarla ve gerçek hol
fotoğraflarıyla anlatılır.

## Kontrol listesi

- W'de makine, hol, ışık ya da renk değişmiş mi? Değiştiyse reddet, yeniden iste.
- İnsanlar ölçekte ve ışıkta fotoğrafın içinden mi görünüyor, yapıştırılmış gibi mi?
- KKD tam mı (baret, gözlük, yelek)?
- Ekranda ya da panoda okunabilir yazı var mı? Varsa reddet.
- E'de mavi tonu `#1E9BE0` / `#0C6FB8` mi?
- Dosyaları `D:\turkmen gips\scratchpad\GORSELLER-2026-10-20\` klasörüne koy.
