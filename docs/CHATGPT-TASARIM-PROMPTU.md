> **GEÇERSİZ (2026-10-20).** Yerine: [CHATGPT-GORSEL-PROMPTLARI-SON.md](CHATGPT-GORSEL-PROMPTLARI-SON.md) ve [ANA-SARTNAME.md](ANA-SARTNAME.md). Bu dosyadan ChatGPT'ye prompt gönderme.

# ChatGPT tasarım promptu — iki TV makine görselleri

Nasıl kullanılır: Aşağıdaki "ANA PROMPT" bloğunu ChatGPT'ye bir kez yapıştır.
Sonra "MAKİNE LİSTESİ" içindeki her satırı ayrı mesajla gönder. Her mesaj tek
görsel üretir. Logo görselini ve iki referans görseli de ilk mesaja ekle.

Görsellerde yazı olmayacak. Bütün metinler kodla, kalın Türkmence olarak basılır.
Animasyonu kod yapar; bu yüzden hareketli parçalar ayrı katman olarak istenir.

## ANA PROMPT

```text
You are the industrial illustrator for TÜRKMEN GIPS Hojalyk Jemgyýeti, a
state-level gypsum board and dry-mix plant in Turkmenistan. You are producing
machine illustrations for two 1920x1080 factory control-room TVs that will be
viewed by ministry officials. The tone must be serious, official and
engineering-accurate. No cartoon faces, no people, no mascots, no humor.

STYLE (apply to every image, never change between images)
- Clean isometric 3D render, true isometric camera 30 degrees, same camera
  height and same lens for every machine so they line up on one floor grid.
- Matte industrial materials: light grey painted steel, brushed metal, dark
  graphite frames and legs. Soft studio lighting from top-left, one soft
  contact shadow under the machine. No reflections of a room, no environment.
- Accent colour ONLY the brand blue #145BCC (dark #0A43A5, light #4D88E8).
  Use the accent on guards, motor housings and hoppers, like the orange in the
  attached pipe-mill reference but in brand blue.
- Background: fully transparent PNG. No floor tile, no text, no numbers, no
  labels, no logos on the machine body.
- Each machine sits on a 1-cell floor footprint of a shared isometric grid.
  Input side is on the LEFT-BACK, output side on the RIGHT-FRONT, so machines
  chain left to right.
- Size: 1024x1024 canvas, machine fills about 70% of it, centred, same scale
  between machines (a mixer must look smaller than a 100 m dryer).

LAYERS FOR ANIMATION
For every machine produce TWO images with identical framing:
  1. "base": the full machine with all static parts.
  2. "moving": ONLY the parts that move (rollers, belts, rotor, screw, fan
     blades, cutting blade), same position, everything else transparent.
Also mark one small round status-lamp socket on top of every machine, empty
grey, because the code colours it green/yellow/red.

DELIVERY
- File name pattern: tg-<line>-<nn>-<key>-base.png and ...-moving.png
- Reply with the image and the file name only.
```

## MAKİNE LİSTESİ

TV 1 — Gipsokarton hattı (`line` = `gk`)

| nn | key | Mesaj |
|---|---|---|
| 01 | gips-berijisi | Gypsum feeder: hopper with screw feeder, moving layer is the screw. |
| 02 | garysdyryjy | Gypsum slurry pin mixer, round housing on frame, moving layer is the rotor. |
| 03 | kopuk-generatory | Foam generator skid with small tank, pump and pipes, moving layer is the pump impeller. |
| 04 | formirleme-stoly | Board forming table with paper unwind rolls, moving layer is the paper rolls. |
| 05 | gatama-lentasy | Long setting belt conveyor section, moving layer is the belt surface and rollers. |
| 06 | kesiji | Rotary board cutter (knife drum over conveyor), moving layer is the knife drum. |
| 07 | guradyjy | Multi-deck board dryer section, long box with fans on top, moving layer is the fans. |
| 08 | gyra-kesiji | Edge trimming saw station, moving layer is the two saw blades. |
| 09 | gaplayjy | Board stacker and packer with a stack of boards, moving layer is the lift table. |

| 10 | kagyz-bobinasy | Ek makine, aşağıdaki ayrı prompt ile. |

### Ek makine: Kagyz bobinasy (2026-10-20 eklendi)

Ana hattın içine değil, Formirleme stolunun arkasına yan besleme olarak
yerleşir. Numarası bu yüzden 10; önceki 01–09 dosyaları değişmez.

```text
Same style, same camera, same scale as all previous TÜRKMEN GIPS machines.

Machine: paper reel unwind stand for a gypsum board line ("Kagyz bobinasy").
Two large paper reels, one above the other, each about 1.5 m diameter, cream
paper colour, mounted on a heavy graphite steel frame with brake discs and a
small brand-blue (#145BCC) motor housing. A flat paper web leaves both reels
toward the RIGHT-FRONT side, where it will feed the forming table.

Footprint: 1 grid cell, same floor grid as the forming table.

Produce two images with identical framing:
  1. base: full stand with both reels and frame.
  2. moving: ONLY the two paper reels and the paper web, everything else
     transparent. The code rotates the reels.
Include the empty grey status-lamp socket on top of the frame.

Transparent background. No text, no numbers, no logos.
File names: tg-gk-10-kagyz-bobinasy-base.png, tg-gk-10-kagyz-bobinasy-moving.png
```

Not: 04 Formirleme stoly görselinde kâğıt ruloları zaten çizildiyse yeniden
üretmeye gerek yok. Sahnede bobin standı formirleme stolunun arkasında durur.

TV 2 — Gury garyndy hattı (`line` = `gg`)

| nn | key | Mesaj |
|---|---|---|
| 01 | cig-mal-silosy | Tall raw-material silo with cone bottom and ladder, moving layer is the discharge valve. |
| 02 | dozirleyji | Weighing and dosing unit with load-cell hoppers, moving layer is the dosing screws. |
| 03 | garysdyryjy | Horizontal ploughshare dry mortar mixer, moving layer is the shaft with ploughs. |
| 04 | elewator | Bucket elevator, tall casing, moving layer is the bucket chain. |
| 05 | tayyar-onum-bunkeri | Finished product bunker with level sensor, moving layer is the outlet slide gate. |
| 06 | gaplayjy-masyn | Valve-bag packing machine with 25 kg bags, moving layer is the filling spout and a bag. |
| 07 | palet-oruji | Palletizer with stacked bags on a pallet, moving layer is the gripper arm. |

## EK GÖRSELLER

| Dosya | Mesaj |
|---|---|
| tg-flow-gk.png | Same style. One empty connecting conveyor piece, 1 grid cell long, transparent background. Used between gypsum board machines. |
| tg-flow-gg.png | Same style. One empty pipe or screw-conveyor piece, 1 grid cell long, transparent background. Used between dry-mix machines. |
| tg-material-board.png | Small gypsum board segment, white with grey paper edge, transparent, 128x128. |
| tg-material-bag.png | Small closed 25 kg paper bag, plain, no text, transparent, 128x128. |
| tg-floor-grid.png | 1920x560 very light grey isometric floor grid, subtle, no text, opaque #F4F7FB background. |

## KONTROL LİSTESİ (görsel gelince)

- Kamera açısı bütün makinelerde aynı mı?
- Görselde yazı, rakam, yabancı logo var mı? Varsa reddet.
- `base` ve `moving` aynı çerçevede mi, üst üste konunca kayma var mı?
- Mavi tonu logo mavisinden sapıyor mu?
- Dosyaları `frontend/public/tv/` altına koy; Claude anahtarları bağlar.
