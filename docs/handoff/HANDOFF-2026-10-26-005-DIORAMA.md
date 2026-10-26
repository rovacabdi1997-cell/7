# HANDOFF-2026-10-26-005 — A katmanı "kil diorama" brief'i

| Alan | Değer |
|---|---|
| Gönderen | Claude, proje sahibinin onayıyla |
| Alan | Codex (frontend) |
| Yerine geçtiği | HANDOFF-003'ün yerleşim bölümü. 003'teki veri modu, biçim ve kabul kuralları geçerli |
| Plan | TAM-PLAN-v9 değişiklik kaydı 9.2 |
| Görsel referans | `A-KATMANI-TASLAK-v2-DIORAMA.html`, `v2-diorama-*.png`, `referans-optivion.png` |
| Veri | Sözleşme v2.1.0 (HANDOFF-001 ve 004) |
| Ön koşul | HANDOFF-004 uygulanmış olmalı: `nominalSpeed`, makine sırası |

## Neden yeniden

Önceki ekran proje sahibi tarafından reddedildi. Ret nedenleri, tekrarlanmayacak:

| Önceki ekranda | Bu sefer |
|---|---|
| Makine etiketleri üst üste ve kesik | Etiket makinenin üstünde yüzer, hiçbir etiket başka etiketle veya makineyle kesişmez |
| 3D sahne ekranın küçük bir köşesinde | Sahne ekranın üçte ikisi, sol kolon üçte bir |
| Kartlarda "Maglumat ýok" kalabalığı | A katmanında demo değeri ve başlıkta "Simulýasiýa" (D11, D7) |
| "SIMULATED", "m/dk" | Yalnız Türkmence, birim `m/min` |
| Bej üstüne bej, kontrast yok | Açık plaka, koyu cam kartlar, tek vurgu rengi turuncu akış |

## Ne yapılacak

Mevcut `LineTv.tsx` içindeki açık tema yerleşimini taslağa göre yeniden kur. Yeni route yok, giriş `/tv/a/?tema=acik` ve `/tv/b/?tema=acik`. Koyu B katmanına dokunma.

## Yerleşim (3840 × 2160)

| Bölge | Konum | İçerik |
|---|---|---|
| Üst çubuk | üst 48, yükseklik 120 | Logo, `Türkmen Gips` ve hat adı. Hap: durum, vardiya, veri modu. Sağda büyük saat ve `Gün · gg.aa.yyyy · Aşgabat` |
| Sol kolon | sol 72, genişlik 1000 | 3 koyu cam kart: Hat tizligi, Duýduryşlar, Görkezijiler |
| Sahne | sol 1100'den sağ kenara | İzometrik plaka, U hat, akış çizgileri, yüzen etiketler, arıza kartı |
| Lejant | sağ alt | Baglanyşyk ve Ýagdaý |

## Görsel dil

| Öğe | Kural | Token önerisi |
|---|---|---|
| Zemin | Radyal geçiş, merkez sahne üstünde | `#C3BCB4` → `#9C958C` |
| Plaka | İzometrik, 2:1 oran, üst ve iki yan yüzey, altta yumuşak gölge | üst `#D9D4CE`, sol `#B7B0A8`, sağ `#A69F97` |
| Makine | Mevcut `public/tv/machines/*-base.png`. Kil filtresi: gri tonlu, hafif sıcak, yumuşak gölge | `grayscale(.92) sepia(.18) brightness(1.12) contrast(.92)` |
| Arızalı makine | Kırmızıya döner ve kırmızı ışır. Sahnede başka renkli nesne yok | `--ariza: #E5484D` |
| Akış çizgisi | Turuncu, 6 px, altında bulanık parıltı. Üstünde akan açık noktalar | `--akis: #F08A2E` |
| Besleme | Kagyz ve köpük beslemesi kesikli turuncu | |
| Kopuk akış | Arızalı makineye giren ve çıkan çizgi kırmızı kesikli, akmaz | |
| Bağlantı düğümü | Köşelerde 28 px açık kare, turuncu kenar | |
| Etiket | Açık hap, 40 px kalın yazı, durum noktası. Arızada kırmızı çerçeve ve üçgen | |
| Kart | Koyu cam, ince açık kenar, 28 px köşe, yumuşak gölge | `rgba(58,53,50,.78)` |
| Font | Manrope veya Urbanist, yerel WOFF2, tabular rakam | |
| Hareket | Yalnız akış noktaları ve durum noktası nabzı. `prefers-reduced-motion` ile durur | |

## Hat yerleşimi

Islak uç arkada soldan sağa, kurutucu sağda döner, kuru uç önde sağdan sola. 10 × 10 izometrik ızgara, `P(a, b)`:

| Makine | a | b | Not |
|---|---|---|---|
| Gips berijisi | 0,9 | 2,7 | |
| Garyşdyryjy | 2,9 | 2,7 | |
| Köpük generatory | 2,9 | 0,5 | Garyşdyryjy'ya besleme |
| Formirleme stoly | 5,0 | 2,7 | |
| Kagyz bobinasy | 5,0 | 5,0 | Formirleme'ye besleme |
| Gatama lentasy | 7,1 | 2,7 | |
| Kesiji | 9,3 | 2,7 | |
| Guradyjy | 9,2 | 5,6 | En büyük görsel |
| Gyra kesiji | 7,4 | 8,6 | |
| Bukjalaýjy | 5,2 | 8,6 | |
| Gaplaýjy | 3,0 | 8,6 | |

Makineler arkadan öne çizilir (`a + b` küçükten büyüğe). Etiketler bütün makinelerden sonra çizilir.

Gury garyndy TV'si (`/tv/b/`) aynı dili kullanır. Yerleşim ızgarası ayrıca hazırlanacak; o zamana kadar gury garyndy için zincir düz bir sırada dizilir.

## Sol kolon ve API

| Kart | Değer | API alanı |
|---|---|---|
| Hat tizligi | Büyük sayı ve yarım yay | `speed`, yay `capacityPct`, yan bilgi `nominalSpeed`, `capacityPct` |
| Duýduryşlar | En çok 2 satır, başlıkta işjeň sayısı | `alarms` hat filtresi, `priority` sırası. Etiket `Işjeň` / `Tassyklandy` / `Ýapyldy` |
| Görkezijiler | 2 × 3: Gündelik önüm, Gündelik maksat, Ýerine ýetiriliş, Çalşyk önümi, Duruş, OEE | `outputToday`, `planToday`, `fulfilmentPct`, `shiftOutput`/`shiftPlan`, `stopMinutesToday`, `oee.oee` |
| Arıza kartı | Makine adı, başlama saati, neden, süre, sebep kodu | `currentStop.startedAt`, `reasonText`, `durationMin`, `reasonCode`, makine `currentStop.equipmentId` |

Gösterge çubukları değerin hedefe oranıdır. Oran yoksa çubuk çizilmez, sıfır gösterilmez.

## Kabul kanıtları

| Kanıt | Ölçüt |
|---|---|
| 1080p ve 4K görüntü, normal ve arıza | Taslak PNG'leri ile yan yana. Proje sahibi görsel onay verir |
| Çakışma testi | Bütün `.etiket` kutuları birbiriyle ve ekran kenarıyla kesişmiyor. Tarayıcıda `getBoundingClientRect` ile ölçülür |
| 40 px | 4K tuvalde 40 px altı metin yok |
| Dil | Ekranda İngilizce ve Türkçe kelime yok, büyük İ yok |
| Performans | Mini PC'de 30 fps üstü. Makine PNG'leri 640 px'e küçültülür, toplam 8 MB altı |

Bitince 5 satırlık rapor (bölüm 6). Commit etme, önce proje sahibine göster.
