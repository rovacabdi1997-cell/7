> **GEÇERSİZ (2026-10-20).** Yerine: [CHATGPT-GORSEL-PROMPTLARI-SON.md](CHATGPT-GORSEL-PROMPTLARI-SON.md) ve [ANA-SARTNAME.md](ANA-SARTNAME.md). Bu dosyadan ChatGPT'ye prompt gönderme.

# ChatGPT görsel listesi: Gün energiýasy modülü (2026-10-20)

Toplam 8 görsel: 6 izometrik parça ve 2 fotogerçekçi kampüs düzenlemesi.
Önümçilik akymy sekmesi için yeni görsel gerekmez; mevcut 16 makine görseli kullanılır.

Kullanım:
1. İzometrik parçalar için iki TV makinelerini ürettiğin sohbeti kullan; stil aynı kalsın.
2. Önce "ANA PROMPT"u gönder, sonra E01–E06'yı tek tek gönder.
3. E07 ve E08 için yeni sohbet aç ve ilgili kampüs görselini ekle.
4. Dosya adlarını değiştirme; kod görselleri bu adlarla bağlar.

## Liste

| No | Dosya | Ne | Tür |
|---|---|---|---|
| E01 | `tg-eco-01-cati-ges.png` | Üretim binası çatısında güneş paneli dizisi | İzometrik |
| E02 | `tg-eco-02-otopark-ges.png` | Kamyon otoparkı üstünde panelli gölgelik | İzometrik |
| E03 | `tg-eco-03-inverter.png` | Inverter dolapları ve orta gerilim trafo | İzometrik |
| E04 | `tg-eco-04-batareya.png` | Batarya depolama konteyneri (BESS) | İzometrik |
| E05 | `tg-eco-05-mcc.png` | Ana dağıtım ve enerji yönetim panosu | İzometrik |
| E06 | `tg-eco-06-sebeke.png` | Şebeke bağlantı trafo merkezi | İzometrik |
| E07 | `kampus-ges-hava.jpg` | Kampüs hava görünümü, çatılarda paneller | Fotogerçekçi düzenleme |
| E08 | `kampus-ges-cati.jpg` | Üretim binası önden, çatıda paneller | Fotogerçekçi düzenleme |

## ANA PROMPT (E01–E06)

```text
Same visual system as all previous TÜRKMEN GIPS machines: clean isometric 3D
render, true isometric camera 30 degrees, same camera height and lens, matte
industrial materials, light grey painted steel, graphite frames, soft studio
light from top-left, one soft contact shadow. Accent colour ONLY brand blue
#145BCC (dark #0A43A5, light #4D88E8). Solar modules are dark blue-black
monocrystalline glass with thin silver frames, no rainbow reflections.

Transparent background PNG, 1254x1254 canvas, object about 70% of canvas,
centred. No text, no numbers, no logos, no people, no vehicles unless asked.
Serious, government-grade engineering look. No neon, no glow, no lens flare.

Energy flows from LEFT-BACK to RIGHT-FRONT, like the production machines:
cable entry on the left-back side, cable exit on the right-front side.
Include one small empty grey status-lamp socket on top of each object.

Reply with the image and the file name only.
```

## E01: Çatı GES

```text
Isometric section of a large white industrial production hall roof (only the
top part of the building, about one grid cell wide), carrying a dense array of
solar panels in neat rows tilted 25 degrees to the south, maintenance walkways
between rows, a cable tray running to the right-front edge.
File: tg-eco-01-cati-ges.png
```

## E02: Otopark GES

```text
Isometric solar carport: a long steel canopy structure with graphite columns
and brand-blue beam caps, roof fully covered with solar panels, three empty
truck parking bays marked with white lines underneath, no trucks. Cable
conduit exits at the right-front column.
File: tg-eco-02-otopark-ges.png
```

## E03: Inverter ve trafo

```text
Isometric outdoor power skid on a concrete pad: a row of four string inverter
cabinets (light grey with brand-blue side panels and small cooling grilles)
connected to a compact medium-voltage transformer with radiator fins, cable
trench cover on the ground, short fence posts at the corners.
File: tg-eco-03-inverter.png
```

## E04: Batarya depolama

```text
Isometric battery energy storage container (20-foot size), light grey with a
brand-blue stripe along the top, double doors on the front slightly visible,
HVAC unit on the side wall, small fire-suppression cabinet next to it, on a
concrete pad.
File: tg-eco-04-batareya.png
```

## E05: Ana dağıtım ve enerji yönetimi

```text
Isometric indoor main low-voltage switchboard: a row of five tall electrical
cabinets, light grey with brand-blue top plinths, one cabinet with a small
dark screen (no text on it) and a power meter window, cable ladder entering
from the top left.
File: tg-eco-05-mcc.png
```

## E06: Şebeke bağlantısı

```text
Isometric compact grid connection substation: a fenced enclosure with one
medium-voltage transformer, a metering kiosk and two insulator poles with
short overhead line stubs ending at the right-front edge. Gravel ground,
graphite fence, brand-blue kiosk door.
File: tg-eco-06-sebeke.png
```

## E07: Kampüs hava görünümü + GES (ekle: `campus-aerial-master.jpg`)

```text
Edit the attached aerial render of the TÜRKMEN GIPS factory campus.
Keep EVERYTHING identical: camera angle, buildings, colours, trees, roads,
trucks, sky, light. Only add photorealistic solar panels:
- on the large flat roofs of the main production halls, in neat rows with
  maintenance gaps, covering about 70% of each roof;
- a solar carport canopy over the truck parking area.
Panels must follow the roof perspective exactly and cast correct soft shadows.
Do not add text, logos, people or new buildings. Same resolution as the input.
File: kampus-ges-hava.jpg
```

## E08: Üretim binası önden + GES (ekle: `campus-production-front.jpg`)

```text
Edit the attached render of the TÜRKMEN GIPS production building front.
Keep the building, camera, colours, landscaping and sky identical. Add
photorealistic solar panels on the visible roof surfaces, rows tilted toward
the sun, thin silver frames, plus a slim cable tray running down the side
wall into a small light-grey inverter cabinet at ground level.
No text, no logos, no people. Same resolution as the input.
File: kampus-ges-cati.jpg
```

## Kontrol listesi (görseller gelince)

- İzometrik parçaların kamera açısı makine görselleriyle aynı mı?
- Görselde yazı, rakam ya da logo var mı? Varsa reddet.
- E07 ve E08'de bina, ağaç veya yol değişmiş mi? Değiştiyse reddet.
- Mavi ton marka mavisi `#145BCC` mi?
- Dosyaları `frontend/public/tv/eco/` altına koy.
