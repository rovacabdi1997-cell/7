# Türkmen Gips · Sanly Zawod — Tam Planlama ve Uygulama Dosyası

| Alan | Değer |
|---|---|
| Sürüm | 9.0 |
| Tarih | 26.10.2026 |
| Durum | Yürürlükte — kilitli |
| Kapsam | TV panosu · sunum panosu · MES veri katmanı · açılış |
| Sahipler | Claude (veri/API/MES) · Codex (tasarım/frontend) |
| Hakem | Proje sahibi |
| Kaynak | Uzun proje görüşmelerinin konsolidasyonu |

Bu belge, projenin tamamının tek kaynağıdır. Kilitli kararlar, tasarım sistemi, veri sözleşmesi, iki ajanın talimatı ve açılış hazırlığı buradadır. Belge dışında alınan karar geçersiz sayılır.

> Kaynak: proje sahibinin 26.10.2026'da verdiği PDF/HTML belgesinin Markdown kopyası. Paketlerde `BELGELER/TAM-PLAN-v9.md` olarak yer alır. Ajanlar bu sürümü okur.

## Nasıl kullanılır

| Kim | Ne okur | Ne yapar |
|---|---|---|
| Claude | Bölüm 3–7, 24–29, 32, 34 | Veri sözleşmesi, MES şeması, API, handoff |
| Codex | Bölüm 3–7, 8–23, 30, 33, 34 | Tasarım token'ı, ekranlar, animasyon, testler |
| Sanatçı / 3D | Bölüm 13–14, 19–20 | İllüstrasyon ve diorama |
| Proje sahibi | Tamamı | Karar, hakemlik, saha işleri |

---

## Bölüm 1 — Yönetici özeti

Fabrikadaki iki adet 100 inç TV ve sunum salonu için uzaktan okunur, dürüst ve profesyonel bir üretim panosu; bunu besleyen MES veri katmanı; ve açılış töreni hazırlığı.

### Altı temel karar

1. Üç katman: Sunum (açık), Kontrol odası (koyu), Tehniki. Aynı token, farklı yoğunluk.
2. Mevcut koyu ekran korunur. Üstüne açık sunum katmanı eklenir. Yıkım yok.
3. 3D abartılmaz. Ana panolar 2.5D SVG. Gerçek 3D yalnızca tek bağlam ekranı.
4. Token tek kaynak. Sabit renk, ölçü, font yok.
5. Veri dürüst. Dört veri modu, sessiz geçiş yok, eksik değer sıfır değil.
6. Gerçek veri için üç tag. Açılıştan önce PLC'den üç canlı değer okunur.

**En yüksek getirili tek iş:** PLC'den hat hızı, üretim sayacı ve hat çalışıyor/duruyor tag'lerini okumak. Üç tag, ekranı "simülasyon"dan "çalışan sistem"e çevirir.

### Bitiş tanımı

Kabul matrisinin tüm satırları yeşil, `workingTreeDirty: false`, DOSYA-DOGRULAMA güncel, kapanış raporu yazılı. Bunlar olmadan sürüm bitmiş sayılmaz.

## Bölüm 2 — Açık maddeler ve bulgular

| # | Bulgu | Önem |
|---|---|---|
| 1 | `workingTreeDirty: true` — "FINAL" adlı sürüm kirli ağaçtan üretilmiş | P1 |
| 2 | Merkez IP 127.0.0.1, API adresi boş, veri kaynağı kayit — TV'ler merkezi bulamaz, hepsi demo | P1 |
| 3 | İki adres seti çakışıyor: bir belge `/tv/a/`, diğeri `/tv/1/` diyor | P1 |
| 4 | Gilroy uygulanmamış, font klasörü yok, ² ³ glifi yok | P1 |
| 5 | Üç ayrı stil dosyası var, token yok — çakışma riski | P1 |
| 6 | 2.5D makine PNG + motion overlay sistemi zaten kurulu — 3D tartışması yarı çözülmüş | — |
| 7 | WinCC adaptörü var ama bağlantı dizesi yok — demo API açılıyor | P2 |
| 8 | Dosya bütünlük doğrulaması iyi kurulmuş — korunmalı | — |

### Sahada bekleyen maddeler (ajanlar yapamaz)

- Gerçek merkez IP adresi ve ağ yapılandırması
- PLC marka/model ve tag listesi
- Sıcaklık, nem, ağırlık PLC tag listeleri
- Resmî reçete kodları ve kronometraj
- Kapasite ve ekipman eşleştirme teyidi
- 100 inç / 4 metre okuma testi ve 72 saat çalışma testi
- ERP (PEKAS / Logo Tiger 3) salt-okunur erişim

## Bölüm 3 — Kilitli kararlar

Tartışmaya kapalı. İki ajan da uyar.

| No | Karar |
|---|---|
| D1 | 3D: Mevcut 2.5D PNG + motion overlay sistemi korunur ve bitirilir. Gerçek 3D yalnızca tek bağlam ekranı (`/tv/3d/`). Trend ve sütun grafiği asla 3D değildir. |
| D2 | Font: Başlık Gilroy, veri Inter (tabular-nums). Gilroy lisansı yoksa Urbanist. ² ³ veri fontundan. Türkmen harf kapsamı tam. |
| D3 | Tema: Koyu varsayılan (kontrol odası), açık tema sunum ve salon için. Aynı token, iki değer grubu. |
| D4 | Renk: Nötr zemin, renk yalnız anormallik için. Durum = renk + şekil + yazı. |
| D5 | Ölçü: 4 metre mesafe. Taban 40 px, kritik 64 px, sunum katmanı 180–260 px. Altına inen metin yok. |
| D6 | Rakam: Ondalık virgül, binlik boşluk → 13 795,3 m² |
| D7 | Veri modu: SIMULÝASIÝA / HAKYKY / KÖNE / MAGLUMAT ÝOK. Sessiz demo geçişi yok. |
| D8 | Dil: Türkmence. Büyük İ yok (Işjeň). y = ı sesi, ý = y sesi. |
| D9 | Token: Sabit renk, ölçü, font, gölge yok. Hepsi token'dan. |
| D10 | Adres: Kanonik beş route: `/tv/a/` `/tv/b/` `/tv/3d/` `/kontrol/` `/sunum/`. `/tv/1/` ve `/tv/2/` yönlendirme. |
| D11 | Sunum katmanı: A katmanında MAGLUMAT ÝOK gösterilmez, demo değeri gösterilir. Ekran asla boş görünmez. |
| D12 | Hareket: Sadece anlam taşıyan hareket. Kamera sarsıntısı, zoom, süs animasyonu yok. prefers-reduced-motion desteklenir. |

## Bölüm 4 — Kapsam kilidi

Bu sürümde yeni fikir kapsamı genişletmez. Yeni fikir `BELGELER/v10-FIKIRLER.md` dosyasına yazılır.

| GİRER | GİRMEZ |
|---|---|
| Token tek kaynak | Yeni ekran |
| Tipografi ve tabular rakam | Tam 3D fabrika modeli |
| 4 m okunurluk ölçüsü | PLC'ye yazma |
| Durum kodlaması | Tam OEE hesap motoru |
| Dört veri modu görseli | Bakım, depo, kalite modülleri |
| Açık sunum katmanı (A) | Yeni font arayışı |
| Tehniki katman (C) | Yeni stil dosyası açmak |
| Tören modu | Süs animasyonu |
| 2.5D sisteminin bitirilmesi | Grafik kütüphanesi değiştirmek |
| 3D ekranının bağlanması | Token dışı yeni renk |
| Adres temizliği | Ses (panoda) |
| Türkmence imla denetimi | |
| 72 saat dayanıklılık testi | |

## Bölüm 5 — Sahiplik ve sınırlar

| Alan | Sahip | Yazma yetkisi |
|---|---|---|
| `KAYNAK-KOD/backend/**` | Claude | Yalnız Claude |
| `docs/api/**` | Claude | Yalnız Claude |
| `config/tag_mapping.json`, adapters, servisler, SQL | Claude | Yalnız Claude |
| `site/**` | Codex | Yalnız Codex |
| Tüm CSS / JS / HTML, `tokens/`, görsel varlıklar | Codex | Yalnız Codex |
| `BELGELER/**` | Ortak | Koordinasyon kaydı ile |
| `RELEASE.json`, `DOSYA-DOGRULAMA.json` | Ortak | Kapanışta birlikte |

**Üç yasak:** Claude `site/**` dosyasına yazmaz. Codex backend'e yazmaz. Ortak dosyaya koordinasyon kaydı olmadan yazılmaz.

### Handoff sırası

Handoff sıralıdır: önce Claude sözleşmeyi yayınlar, sonra Codex tüketir. Aynı anda yazmazlar. Her handoff `BELGELER/handoff/HANDOFF-YYYY-MM-DD-NNN.md` dosyasına düşer ve şunları içerir: sürüm (semver), değişen alanlar, geriye uyum, örnek istek ve yanıt, karşı tarafın yapacağı tek adım.

## Bölüm 6 — Anlaşmazlık ve rapor kuralı

- İki ajan anlaşamazsa bu belge kazanır.
- Belgede yoksa proje sahibi karar verir ve karar belgeye yazılır.
- Tartışma dosyaya yazılmadan koda geçilmez.
- Her teslimde beş satırlık rapor zorunludur.

### Zorunlu rapor formatı

```
1. Ne yaptım:
2. Hangi dosya:
3. Hangi kilitli karara hizmet ediyor:
4. Hangi kabul kriterini karşıladı + kanıt dosyası:
5. Hangi soru açık kaldı:
```

### Durma koşulu

Ajanın işi, kabul matrisindeki kendi satırları yeşil olduğunda biter. Yeşil olmadan yeni iş açılmaz. Kanıt dosyası olmayan satır yeşil sayılmaz; "yapıldı" demek yetmez.

## Bölüm 7 — Veri kuralları ve veri modları

| Mod | Anlamı | Gösterim |
|---|---|---|
| HAKYKY | Canlı kaynaktan, yaş eşiği içinde | Normal, tam kontrast |
| SIMULÝASIÝA | Test verisi, kaynak yok | Normal + küçük gri etiket |
| KÖNE | Veri var, yaş eşiği aşıldı | Soluk + işaretli, yeşil kalmaz |
| MAGLUMAT ÝOK | Hiç veri gelmedi | Nötr gri, asla sıfır veya yeşil değil |

### Değişmez kurallar

- Eksik değer sıfır yapılmaz.
- Veri eskimişse çalışma rengi korunmaz.
- API kesilince sessiz demo geçişi yapılmaz; eski veri işareti ve yeniden bağlanma gösterilir.
- Günlük üretim, vardiya üretimi yerine kullanılmaz. Vardiya hedefi ayrı alandır.
- Güncel duruşun nedeni ve süresi, günlük toplamdan türetilmez.
- OEE = kullanılabilirlik × performans × kalite ÷ 10000. Tek verimlilik yüzdesi OEE değildir.
- Her yanıtta ISO 8601 UTC zaman damgası ve kaynak modu zorunlu.
- Zaman damgaları UTC saklanır, yerel gösterilir.
- Silme yok, yalnız ekleme.

## Bölüm 8 — Tasarımın tek cümlesi ve altı ilke

**Tasarımın tek cümlesi:** Açık zeminde beş sayı, bir çubuk, bir hat şeridi. Başka hiçbir şey.

### Altı ilke

1. Beş öğe kuralı. Bir ekranda en fazla beş bilgi bloğu. Altıncıyı eklemek istiyorsan birini sil.
2. Referanssız sayı yok. Her sayının yanında hedefi, nominali veya sıfırı olur.
3. Renk sadece anormallik için. Normal durumda ekran neredeyse renksiz.
4. Renk + şekil + yazı. Üçü birlikte. Renk körü biri de okur.
5. Boş ekran yok. Sunum katmanında demo değeri gösterilir.
6. Işık yönü sabit. Yukarı-sol. Tüm illüstrasyon ve tonlama aynı yönden.

### Kaynak sentezi

| Kaynak | Alınan | Alınmayan |
|---|---|---|
| Modern SaaS dashboard | Sadelik, açık zemin, nefes alan boşluk | Yoğunluk — 27 inç için yapılmış |
| OEE sunum panosu | İçerik mantığı: hedef, gerçekleşen, kayıp | 3D pahlı şerit, gradyan, gölge |
| Endüstriyel HMI | Durum renkleri, birim, referans, dürüstlük | Karanlık ve sıkışık düzen |

## Bölüm 9 — Üç katman sistemi

Aynı token seti, üç farklı yoğunluk.

| | A — Sunum | B — Kontrol odası | C — Tehniki |
|---|---|---|---|
| Kim | Müdür, bakanlık, cumhurbaşkanı | Operatör, vardiya şefi | Bakım, elektrikçi |
| Nerede | Salon, açılış | Kontrol odası | Atölye PC |
| Tema | Açık | Koyu | Koyu |
| Sayı adedi | 5 | 12 | 20+ |
| En küçük yazı | 40 px | 32 px | 24 px |
| İçerik | Üretim, hız, alarm, hedef çubuğu | Makine durumu, duruş, alarm, trend | Akım, devir, sıcaklık, titreşim, tag |
| Etkileşim | Yok, sadece bakış | Kısıtlı | Var |

**Kural:** B katmanı zaten var ve iyidir. Silinmez, bozulmaz. A ve C onun yanına eklenir. Aynı token setinden üretilir.

## Bölüm 10 — Katman A — sunum · tam spec

Bu katman açılış ve yönetim içindir.

### Tuval ve boşluk

3840 × 2160 (4K). Yan boşluk 96 px. Alt boşluk 84 px. Satır arası 92 px.

### Yerleşim — yukarıdan aşağıya, tek sütun akış

| Öğe | Yükseklik | İçerik |
|---|---|---|
| Başlık bandı | 132 px | Solda sistem adı (44 px, beyaz). Sağda gün + tarih + saat (Türkmence, gg.aa.yyyy, 24 saat). Koyu milli yeşil #0F7A3D |
| KPI satırı | 520 px | 4 blok × 912 px, aralarında ince dikey ayırıcı |
| Ana satır | 1064 px | Solda 2400 px grafik, sağda 1200 px hat şeridi, arada 48 px boşluk |
| Hedef çubuğu | 96 px | Tam genişlik, yeşil dolgu, sol ve sağ etiket 44 px |

### KPI satırı içeriği

| Etiket (44 px) | Sayı | Birim |
|---|---|---|
| GÜNLÜK ÖNÜM | 260 px | m² |
| GÜNLÜK MAKSAT | 180 px | m² |
| HAT TIZLIGI | 180 px | m/dk |
| IŞJEŇ DUÝDURYŞ | 180 px | sany |

### Ana satır

- Sol: düz sütun grafik "Sagatlaýyn önümçilik". Soluk yeşil sütunlar, ince kesikli hedef çizgisi.
- Sağ: "Önümçilik akymy" — 11 makine tek satır, oklar, yeşil nokta.

**Kritik kural:** Arıza olduğunda yalnızca o kutu kırmızı olur. Ekran kararmaz, diğer on kutu yeşil kalır. Yönetici "her şey durdu" demez.

### Alt çubuk

Tam genişlik, yeşil dolgu, solda "Hedefiň ýerine ýetirilişi 100,6 %", sağda hat adı. Dolgu %100'de durur, etiket gerçek değeri yazar.

## Bölüm 11 — Katman B — kontrol odası · spec

Mevcut ekran. Şu düzeltmeleri alır:

- Palet token'a taşınır
- Makine isimleri 01, 02 yerine gerçek Türkmence adlar
- Veri modu göstergesi eklenir (üstte tek, kart başına tekrar yok)
- Bağlantı durumu ve veri yaşı görünür
- Alarm satırına önem sırası ve zaman eklenir
- Sayılar tabular-nums
- Durum üçlü kodlanır (renk + şekil + yazı)

İçerik: Hat tizligi · Vardiya önümi · Duruş (gün) · Işjeň duýduryş · Enjamlaryň ýagdaýy (11 ekipman) · Duýduryşlar listesi · Sagatlaýyn önümçilik grafiği

## Bölüm 12 — Katman C — tehniki · spec

Bakım ve elektrik ekibi için. Koyu tema, yoğun, etkileşimli.

- Motor: akım (A), devir (rpm), güç (kW), sargı sıcaklığı
- Titreşim ve yatak sıcaklığı
- Hidrolik/pnömatik basınç
- Bakım sayaçları: çalışma saati, son bakım, kalan ömür
- Tag tarayıcı: ad, değer, birim, zaman damgası, kalite
- Alarm geçmişi ve onay kaydı
- Trend: 1 saat / 8 saat / 24 saat seçmeli

C katmanı bu sürümde kurulur ama zenginleştirilmesi v10'a bırakılır.

## Bölüm 13 — Renk token'ları

Tek kaynak: `tokens/tokens.json`. Hiçbir dosyada sabit hex yok.

### Katman A — açık tema

| Token | Değer |
|---|---|
| zemin | #F7F8F7 |
| kart | #FFFFFF |
| bant / dolgu | #0F7A3D |
| yapısal yeşil | #0B5C2E |
| ana metin | #16181A |
| ikincil metin | #5C6360 |
| soluk / veri yok | #9AA19D |
| ayırıcı | #E2E6E3 |

### Katman B / C — koyu tema

| Token | Değer |
|---|---|
| zemin | #101413 |
| kart | #181D1B |
| ayırıcı | #262C29 |
| ana metin | #E8ECEA |
| ikincil metin | #98A19C |

### Durum renkleri (her iki tema)

| Token | Değer |
|---|---|
| A çalışıyor | #16A34A |
| A durdu | #E8A33D |
| A arıza | #D2382F |
| B çalışıyor | #22C55E |
| B durdu | #F0B429 |
| B arıza | #E5484D |
| ikincil vurgu | #D97706 |

**Yeşil çakışması kuralı:** Büyük alanlarda soluk yapısal yeşil (#0B5C2E), durum için parlak yeşil (#16A34A). Böylece "yeşil" iki anlam taşımaz.

## Bölüm 14 — Tipografi ve boşluk ölçeği

### Font

- Başlık: Gilroy (yerelden WOFF2, `font-display: swap`). Lisans yoksa Urbanist.
- Veri / sayı: Inter veya IBM Plex Sans, `font-variant-numeric: tabular-nums`.
- ² ve ³ glifi veri fontundan gelir. Gilroy'da yoksa birim yazımı veri fontuyla.
- Türkmen harf kapsamı dosya üzerinden test edilir: ň ý ž ä ş ç ö ü. Rapor zorunlu.

### Ölçek — 3840 × 2160 koordinatında

| Kullanım | Boyut | Ağırlık | Not |
|---|---|---|---|
| Kahraman sayı | 260 px | 700 | tabular-nums |
| Büyük sayı | 180 px | 700 | tabular-nums |
| Birim | 56 px | 500 | — |
| Bölüm başlığı | 48 px | 500 | Gilroy |
| Etiket | 44 px | 500 | büyük harf, ls .12em |
| Gövde / eksen | 40 px | 400 | taban |
| Alt bilgi | 36 px | 400 | istisna, min |

### Boşluk, yarıçap, gölge

| Token | Değer | Kullanım |
|---|---|---|
| boşluk | 8 / 16 / 24 / 48 / 92 / 96 px | İç boşluk, satır arası, kenar |
| yarıçap | 6 / 12 px | Rozet / kart |
| çizgi | 1 / 2 / 3 px | Ayırıcı / çizim / trend |
| gölge | %10 opaklık, tek yön | Sadece illüstrasyonda |

**4 m kuralı:** Hesaplanan alt sınır 38 px. Kural olarak 40 px uygulanır. 40 px altına inen metin yok.

## Bölüm 15 — Durum sistemi ve veri modu görselleri

| Durum | Renk | Şekil | Yazı |
|---|---|---|---|
| Işleýär | yeşil | dolu daire | Işleýär |
| Durdy | amber | kare | Durdy |
| Näsazlyk | kırmızı | üçgen | Näsazlyk |
| Maglumat ýok | gri | boş daire | Maglumat ýok |
| Köne | gri | kesikli halka | + veri yaşı |

Renk körlüğü simülasyonunda beşi de ayırt edilir, çünkü şekil farklı.

### Veri modu göstergesi

Tek gösterge, üst sağda. Kart başına tekrar yok. HAKYKY yeşil nokta, SIMULÝASIÝA gri nokta, KÖNE kesikli halka + yaş, MAGLUMAT ÝOK boş daire.

## Bölüm 16 — Grafik kuralları

| Ne | Nasıl |
|---|---|
| Saatlik üretim | Düz sütun, 24 px genişlik, 16 px aralık, soluk yeşil |
| Hedef çizgisi | İnce kesikli, koyu gri, 2 px |
| Trend | Çizgi, 3 px, en fazla 3 seri |
| Kapasite kullanımı | Yatay ince çubuk |
| OEE | Üç ayrı dikey çubuk (kullanılabilirlik, performans, kalite) + toplam sayı |
| Duruş dağılımı | Yatay yığılmış çubuk, neden koduyla |

**Asla:** 3D sütun · pasta · radar · kadran (gauge) · gradyanlı dolgu · gölgeli sütun · 3'ten fazla seri · çift eksen

Kadran yerine sayı + ince çubuk.

**Grafik motoru:** Tek motor Apache ECharts. Başka grafik kütüphanesi kullanılmaz.

## Bölüm 17 — Mini motion factory — hat şeridi

Küçük ölçekli, izometrik, hareketli fabrika illüstrasyonu. Teknik olarak doğru kalır.

| Kullanır | Kullanmaz |
|---|---|
| Ana panoda hat şeridi (yatay, ince) | Trend grafiği |
| `/tv/3d/` bağlam ekranı (büyük) | Sayı / KPI bloğu |
| Tören video döngüsü | Tablo, alarm listesi |
| Boş durum ekranı | Menü, buton |
| Açılış sunumu kapağı | Eksen etiketi |

**Boyut kuralı:** Şerit her zaman yatay ve ince. Ana panoda 1200 × 400 px'i geçmez.

### İçerik sırası

Kagyz bobinasy → Gips berijisi → Garyşdyryjy → Köpük generatory → Formirleme stoly → Gatama lentasy → Kesiji → Guradyjy → Gyra kesiji → Bukjalaýjy → Gaplaýjy

### Hareket bütçesi — sadece beş

1. Konveyör yüzeyi kayar, sabit hız, 8 saniyede bir tur
2. Üç silindir yavaş döner
3. Bacadan duman yükselir, 2 saniyede bir
4. İstifleme kolu iner-kalkar, 3 saniyede bir
5. Durum noktaları hafif nabız atar

**Yasak:** kamera sarsıntısı · zoom · nesne sallanması · sürekli renk değişimi · gölge hareketi · parlama · 5'ten fazla eşzamanlı hareket

### Teknik

| Konu | Karar |
|---|---|
| Ana pano şeridi | SVG + CSS animasyon. WebGL yok |
| `/tv/3d/` | Three.js, GLB, 30 fps, DPR 1.5 |
| Tören videosu | Blender render, 4K, 10 saniye, döngü |
| Döngü | Kesintisiz, baş ve son kare eşleşir, 8–12 saniye |
| Ses | Sadece tören videosunda |
| Düşük güç | prefers-reduced-motion → animasyon durur |
| WebGL çökerse | 2D izometrik görsele düşer |

### Stil kuralları

- İzometrik, paralel projeksiyon, 30° grid. Perspektif yok
- Düz renk, gradyan yok. Üç ton kuralı: üst açık, yan orta, ön koyu
- Işık yukarı-sol, hiç değişmez
- Yüzen diorama platform, tüm fabrika değil
- Her ekipman ayrı grup, Türkmence isimli node
- Tek yumuşak gölge, %10 opaklık

## Bölüm 18 — 3D bağlam ekranı

Tek route: `/tv/3d/`. Mevcut `/world/` prototipi buraya taşınır.

**Kural:** 3D ekranı veri taşımaz, bağlam taşır. Bir tane yeter. Ana panolar 2.5D kalır.

- Blender, ortografik kamera 45° azimut / 35,264° yükseklik, perspektif kapalı
- Düşük poly, < 200k üçgen. Flat mat malzeme. Sadece AO. Gerçek zamanlı gölge yok
- GLB + Draco, < 8 MB. Node isimleri Türkmence
- 30 fps sabit, DPR 1.5. Post-processing yok
- WebGL context loss yakalanır, 2D izometrik görsele düşer
- Ölçüler yerleşim planından gelir, fotoğraftan tahmin edilmez
- Verisi olmayan ekipman modellenmez

## Bölüm 19 — Tören modu

Gizli kısayolla açılır. Normal modun kopyası değil, ayrı bir görünüm katmanıdır.

### Açıkken

- Alarm gizli, tüm ekipman nötr durumda
- Sayı beşe iner, boşluk iki katına çıkar
- Açık tema, parlaklık salon koşuluna ayarlı
- Kritik sayı üst üçte birde
- Dış %5 çerçevede kritik bilgi yok (overscan)
- Animasyon yavaşlar, sadece sayaç akar
- Kurdele anı için ayrı ekran hazır
- Milli katkı ekranı hazır

### Tören akışı

| Zaman | Ekran |
|---|---|
| T-30 dk | Tören modu açık, tüm ekranlar canlı, değerler akıyor |
| Varış | Kahraman ekran: 3D diorama + sistem adı + milli program atfı |
| Kurdele | Ayrı ekran, sayaç sıfırdan başlar, hat canlanır |
| Yürüyüş | Güzergahtaki her ekran farklı sahne: hat 1 → hat 2 → enerji → kalite |
| Konuşma | Milli katkı ekranı |
| Ayrılış | Normal moda dönüş, prova edilmiş |

## Bölüm 20 — Hareket kuralları ve yasaklar

- Süre 200 ms, ease-out
- Sadece değer değişimi ve alarm animasyonlu
- Alarm: 3 kez nabız, sonra sabit
- prefers-reduced-motion desteklenir

**Genel yasaklar:** Yeni ekran · yeni stil dosyası · sabit renk veya px · 3D grafik · gradyan · gölge ve parlama · kadran · altıdan fazla öğe · Türkçe metin · büyük İ · nokta ondalık · MAGLUMAT ÝOK tekrarı · sessiz demo geçişi · kırmızıya boyanmış ekran · panoda ses · süs animasyonu

## Bölüm 21 — Türkmenistan yerelleştirme kuralları

| # | Kural |
|---|---|
| 1 | Yerel: tk-TM. Türkmen alfabe sırası geçerli, Türkçe sırası değil. |
| 2 | Rakam: ondalık virgül, binlik boşluk → 13 795,3. Yerel biçimlendirici kullanılır ama test edilir. |
| 3 | Saat: Asia/Ashgabat, UTC+5, yaz saati yok. |
| 4 | Font: Türkmen harfleri + ² ³ + tabular rakam üçü birden olmalı. Kapsam testi zorunlu. |
| 5 | Tatil takvimi vardiya planına ve rapora girer: 1 Ýanwar · 8 Mart · 21–22 Mart Nowruz · 18 Maý (Konstitusiýa we Baýdak güni) · 9 Maý · 6 Oktýabr (Hatyra güni) · 27 Sentýabr (Garaşsyzlyk güni) · 12 Dekabr (Bitaraplyk güni) · Oraza we Gurban baýramy |
| 6 | On-premise: bulut yok, CDN yok. Tüm font ve kütüphane yerelden. İnternet kesilince sistem çalışır. |
| 7 | Ağ: merkez IP gerçek yerel adres olmalı. |
| 8 | Ölçü ve standart: metrik SI. Levha standardı GOST 6266 / EN 520 referansı, kalınlık 9,5 ve 12,5 mm. |
| 9 | Para: TMT, simge m, iki hane. |
| 10 | Kurum adları: Türkmenistanyň Senagat we gurluşyk önümçiligi ministrligi · Türkmenistanyň Döwlet statistika komiteti · Türkmenstandartlary · Türkmenistanyň Senagatçylar we telekeçiler birleşmesi · Türkmenistanyň Söwda-senagat edarasy |
| 11 | Unvanlar: "Hormatly Prezidentimiz" · "Türkmenistanyň Milli Lideri, Arkadag". İki Berdimuhamedow karıştırılmaz. |
| 12 | Raporlama: devlet istatistiğine uyumlu günlük ve aylık üretim raporu, birim ve dönem tanımlı, salt okunur Excel/PDF dışa aktarım. |

### Devlet sembolleri

Bayrak kullanılırsa: yeşil zemin, 1:1.5 oran, hilal ve beş yıldız, gönder tarafında beş göl bulunan dikey şerit. Bayrak daire içine alınmaz. Gerilmez, kırpılmaz, döndürülmez.

## Bölüm 22 — Türkmen alfabesi ve imla

Alfabe sırası: a b ç d e ä f g h i j ž k l m n ň o ö p r s ş t u ü w y ý z

### Üç kural

1. Türkmencede büyük İ yoktur. Küçük i'nin büyüğü I'dır. "Işjeň", "Innowasiýa", "Import" — asla "İşjeň".
2. y = Türkçedeki ı sesi. ý = Türkçedeki y sesi. Türkçe "yok" → Türkmence "ýok".
3. ň ä ž ş ç ö ü zorunlu ve tam.

### Yaygın hatalar

| Yanlış | Doğru | Anlam |
|---|---|---|
| İşjeň | Işjeň | Aktif |
| Yok | Ýok | Yok |
| Yagday | Ýagdaý | Durum |
| Enjamlaryn | Enjamlaryň | Ekipmanların |
| Önümcilik | Önümçilik | Üretim |
| Türkmenistanyn | Türkmenistanyň | Türkmenistan'ın |
| 13.795,3 | 13 795,3 | Rakam formatı |

### Tarih ve saat

Format gg.aa.yyyy, saat 24 saat. Aylar: Ýanwar, Fewral, Mart, Aprel, Maý, Iýun, Iýul, Awgust, Sentýabr, Oktýabr, Noýabr, Dekabr. Günler: Duşenbe, Sişenbe, Çarşenbe, Penşenbe, Anna, Şenbe, Ýekşenbe.

## Bölüm 23 — Ekran mesajları

Çerçeve: dijitalleşme, gençlik, istihdam, ithal ikamesi, ihracat. Üç-dört tanesi kullanılır.

| Türkmence | Türkçe |
|---|---|
| Täze iş orunlary | Yeni iş yerleri |
| Importyň ornuny tutýan önüm | İthal ikamesi ürün |
| Eksport mümkinçiligi | İhracat potansiyeli |
| Sanly önümçilik | Dijital üretim |
| Innowasiýa tehnologiýalary | İnovasyon teknolojileri |
| Ýerli çig mal | Yerli hammadde |
| Energiýa tygşytlylygy | Enerji tasarrufu |
| Ekologiýa taýdan arassa | Çevre dostu |
| Türkmenistanda öndürilen | Türkmenistan'da üretilen |

### Kaçınma listesi

- Toplamayan rakam. Mühendis kafadan toplar.
- Teknik yanlış. Bilmiyorsan söyle, uydurma.
- Sembol ve unvan hatası.
- Karanlık, dağınık, "IT ekranı gibi" pano.
- Uzun ve sıkıcı sunum.
- Çalışmayan sistem.
- Aşırıya kaçan kült.

## Bölüm 24 — Veri sözleşmesi kuralları

Her API alanı için altı bilgi zorunludur: alan adı, tip, birim, kaynak (PLC tag / hesaplanan / kullanıcı), veri modu, bayatlık eşiği (saniye).

**Kural:** Sözleşmede olmayan alan frontend'de varsayılmaz. Alan adı uydurulmaz.

### Zorunlu alanlar

- Hat durumu — hat 1 ve hat 2 AYRI
- Makine durumu — tekil id ile
- Vardiya üretimi ve vardiya hedefi — günlük üretimden AYRI
- Ürün kalınlığı ve levha tipi
- Saatlik üretim serisi
- Kapasite kullanımı — hat 1: m²/saat, hat 2: t/saat
- Enerji — anlık kW ve dönem kWh AYRI
- Duruş — güncel neden ve süre, günlük toplamdan türetilmez
- Alarm listesi — önem sırası ve oluşma zamanı
- Bağlantı durumu ve son başarılı veri zamanı

### Akış

`GET /api/stream`, `text/event-stream`, `event: snapshot`. İstemci origin'ine CORS. Kopmada otomatik yeniden bağlanma, son veriyi KÖNE olarak işaretleme.

## Bölüm 25 — MES mimarisi ve altı faz

### Katmanlar — ISA-95 / IEC 62264

| Seviye | Katman | İçerik |
|---|---|---|
| 4 | ERP | Sipariş, muhasebe, satın alma. MES ile bağ API üzerinden |
| 3 | MES | İş emri, reçete, parti, kalite, OEE, duruş, izlenebilirlik |
| 2 | SCADA / HMI | Operatör ekranı, alarm, set değerleri |
| 1 | Kontrol | PLC, sürücü, lojik |
| 0 | Saha | Sensör, aktüatör, motor |

**Temel kural:** MES, ERP'nin kopyası değildir. MES üretimi yürütür, ERP muhasebeleştirir. Aradaki bağ API'dir, doğrudan veritabanı değildir.

### MESA-11 kontrol listesi

Kaynak ayırma · iş sıralama · veri toplama · kalite yönetimi · süreç yönetimi · üretim takibi · performans analizi · bakım yönetimi · ürün izlenebilirliği · işgücü yönetimi · doküman kontrolü. Her madde kapsam içi veya kapsam dışı olarak yazılı işaretlenir.

### Altı faz — sıra bağlayıcıdır

| Faz | İş | Çıktı |
|---|---|---|
| 1 | Veri toplama ve historian | Tag, örnekleme, ölü bant, zaman damgası, kaynak modu. Üç canlı tag ile başla |
| 2 | Duruş ve OEE | Neden kodu sözlüğü, vardiya tanımı, üç OEE bileşeni ayrı ayrı |
| 3 | İş emri ve reçete | ISA-88: ürün, kalınlık (9,5 / 12,5 mm), levha tipi, parti |
| 4 | İzlenebilirlik | Bobin, stucco, katkı, palet, torba. Parti soy ağacı sorgusu |
| 5 | Kalite | Ölçüm, tolerans, ret, fire, sınıf |
| 6 | Raporlama ve ERP | Vardiya raporu, B2MML veya REST entegrasyonu |

## Bölüm 26 — Veri modeli

Her tabloda `source` ve `data_mode` zorunlu. Zaman damgaları UTC saklanır. Silme yok.

```
equipment(id, tag, ad_tk, line, type, parent_id, active)
equipment_state(equipment_id, ts, state, source, data_mode)
work_order(id, no, product_id, thickness_mm, board_type,
           qty_target, qty_done, uom, planned_start, planned_end, status)
batch(id, work_order_id, lot_no, started_at, ended_at)
material_lot(id, material_id, lot_no, supplier, received_at, qty, uom)
batch_consumption(batch_id, material_lot_id, qty)
downtime_event(id, equipment_id, start_ts, end_ts, reason_code,
               source, comment, entered_by)
downtime_reason(code, name_tk, category, planned, sort)
quality_result(id, batch_id, ts, param, value, uom,
               spec_min, spec_max, pass)
alarm(id, equipment_id, ts, code, priority, state, ack_by, ack_ts)
shift(id, name_tk, start_time, end_time, crew)
kpi_snapshot(ts, equipment_id, avail, perf, qual, oee)
energy_meter(id, ts, kw, kwh)
data_source(id, name, mode, last_ok_ts, stale_after_s)
```

### Zorunlu testler

- OEE formülü test vektörleri (girdi ve çıktı tablosu)
- Duruş süreleri toplamı günlük toplama eşit
- Parti soy ağacı sorgusu doğru sonuç
- KÖNE senaryosu doğru işaretleniyor
- Vardiya sınırında gün geçişi doğru

## Bölüm 27 — Referans depolar

Yerel klon: `D:\turkmen gips\referans\`. Kurmak zorunlu değil, desen çıkar. Repo kodu toptan kopyalanmaz.

Öncelikli sekiz klon: openbridge/design-system · IBM/carbon · apache/echarts · frangoteam/FUXA · frappe/erpnext · pmndrs/react-three-fiber · fonttools/fonttools · unicode-org/cldr

### Endüstriyel tasarım sistemi

| Depo | Ne için | Lisans |
|---|---|---|
| openbridge/design-system | Endüstriyel HMI renk, alarm, ölçü kuralları — en önemli referans | Apache-2.0 |
| IBM/carbon | Kurumsal token yapısı, yoğun veri bileşenleri | Apache-2.0 |
| patternfly/patternfly | İzleme ve operasyon panosu desenleri | MIT |
| shadcn-ui/ui, radix-ui/primitives | Bağımlılıksız bileşenler | MIT |
| amzn/style-dictionary | Token JSON → CSS üretimi | Apache-2.0 |
| storybookjs/storybook | Bileşen kataloğu, görsel test | MIT |

### Grafik, protokol, veri, MES

| Depo | Ne için |
|---|---|
| apache/echarts | Ana grafik motoru |
| FreeOpcUa/opcua-asyncio | OPC UA, Python |
| pymodbus-dev/pymodbus, libmodbus/libmodbus | Modbus |
| gijzelaerr/python-snap7 | Siemens S7 |
| eclipse-mosquitto/mosquitto, emqx/emqx | MQTT broker |
| node-red/node-red | Kod yazmadan entegrasyon |
| timescale/timescaledb | Zaman serisi — önerilen |
| frangoteam/FUXA | Açık kaynak web SCADA — canlı mimari örneği |
| frappe/erpnext | MES referansı: Work Order, Job Card, BOM, Workstation, Downtime Entry |
| minio/minio | Yerel rapor ve PDF deposu |
| fonttools/fonttools | Türkmen harf ve tabular rakam testi |
| unicode-org/cldr | tk-TM yerel verisi ve alfabe sırası |
| microsoft/playwright, backstopjs/backstopjs | 4 m okuma testi, görsel regresyon |

**Yan bulgu:** FUXA MIT lisanslı, web tabanlı SCADA'dır; OPC UA, Modbus, S7, MQTT, BACnet, SNMP destekler ve gömülü historian içerir. PLC bağlantı katmanı için değerlendirilmeli.

## Bölüm 28 — Kabul matrisi

Bir satır yeşil olmadan sürüm bitmiş sayılmaz. Kanıt dosyası olmayan satır yeşil sayılmaz.

| # | Kriter | Sahip | Kanıt |
|---|---|---|---|
| K1 | Token tek kaynak, sabit değer yok | Codex | grep raporu |
| K2 | Font Türkmen harf kapsamı tam | Codex | fonttools çıktısı |
| K3 | tabular-nums aktif, kayma yok | Codex | ekran kaydı |
| K4 | 4 m: 40 px altı metin yok | Codex | ölçüm listesi |
| K5 | Renk körlüğünde durumlar ayırt edilir | Codex | simülasyon görüntüsü |
| K6 | Türkmen imla: büyük İ yok, y/ý doğru | Codex | denetim raporu |
| K7 | Rakam formatı virgül ve boşluk | Codex | denetim raporu |
| K8 | Dört veri modu görseli çalışıyor | Codex | mod geçiş kaydı |
| K9 | Tören modu ayrı katman, çalışıyor | Codex | prova kaydı |
| K10 | 72 saat kesintisiz, bellek artışı yok | Codex | 72 saat logu |
| K11 | Kiosk: imleç yok, kesinti sonrası açılır | Codex | kiosk testi |
| K12 | Hat şeridi beş hareketten fazlasını içermiyor | Codex | hareket denetimi |
| K13 | API sözleşmesi ve örnekler tam | Claude | openapi + examples |
| K14 | Her alanda birim, kaynak, mod, bayatlık | Claude | şema denetimi |
| K15 | KÖNE senaryosu doğru işaretleniyor | Claude | test kaydı |
| K16 | Handoff kaydı var, sürüm eşleşiyor | Claude | handoff dosyası |
| K17 | `workingTreeDirty: false` | Ortak | RELEASE.json |
| K18 | DOSYA-DOGRULAMA güncel | Ortak | hash dosyası |

## Bölüm 29 — Talimat A — Claude

```
ROL
Türkmen Gips Sanly Zawod projesinin backend, veri modeli ve MES mimarısın.
Bu belgeye tabisin.

ALANIN
KAYNAK-KOD/backend/**, docs/api/**, config/tag_mapping.json, adapters,
servisler, database/readonly_queries/**
site/** dosyasına YAZMAZSIN.

GÖREV 1 — API SÖZLEŞMESİNİ KİLİTLE
docs/api/openapi.json ve docs/api/examples/ altında her alan için altı bilgi
zorunlu: alan adı, tip, birim, kaynak (PLC tag / hesaplanan / kullanıcı),
veri modu, bayatlık eşiği (saniye).
Sözleşmede olmayan alan frontend'de varsayılmaz. Alan adı uydurulmaz.

GÖREV 2 — EKSİK ALANLARI TAMAMLA
Bölüm 24'teki zorunlu alan listesinin tamamı için sözleşme ve örnek yanıt üret.

GÖREV 3 — VERİ MODU
Her yanıtta alan bazlı veri modu: SIMULYASIYA | HAKYKY | KONE | MAGLUMAT_YOK.
Yaş eşiği aşılırsa KONE. Her snapshot'ta ISO 8601 UTC kaynak zaman damgası.
Sessiz demo geçişi yok.

GÖREV 4 — /api/stream
GET /api/stream, text/event-stream, event: snapshot. İstemci origin'ine CORS.
Kopmada otomatik yeniden bağlanma, son veriyi KONE olarak işaretleme.

GÖREV 5 — GERÇEK VERİYE HAZIRLIK (en yüksek öncelik)
PLC'den üç canlı tag için yolu aç: hat hızı, üretim sayacı, hat
çalışıyor/duruyor. Şunları netleştir ve BELGELER/handoff/ altına yaz:
hangi tag, hangi tablo, hangi birim, hangi ölçek, okuma periyodu,
beklenen gecikme, salt-okunur garantisi (readonly_guard).
Gerçek bağlantı kanıtı yoksa HAKYKY yazma.

GÖREV 6 — MES VERİ MODELİ VE ALTI FAZ
Bölüm 25 ve 26'ya uy. Faz 1 veri toplama ile başla, sıra bağlayıcıdır.

GÖREV 7 — HANDOFF
Her sözleşme değişikliğinde BELGELER/handoff/HANDOFF-YYYY-MM-DD-NNN.md:
sürüm (semver), değişen alanlar, geriye uyum, örnek istek/yanıt,
Codex'in yapacağı tek adım.
docs/api/API-SOZLESMESI.md başlık sürümünü openapi.json ile eşitle.

YAPMA
- site/** dosyasına yazma.
- Birim uydurma; emin değilsen "belirsiz" yaz.
- Eksik değeri 0 yapma.
- Günlük üretimi vardiya üretimi yerine koyma.
- OEE'yi tek yüzde olarak yayınlama.

TANIM: BİTMİŞ
K13, K14, K15, K16 satırları yeşil. Testler: şema doğrulama, örneklerin
şemaya uyumu, KONE senaryosu, kopma ve yeniden bağlanma, OEE test vektörleri,
duruş toplamı tutarlılığı, parti soy ağacı sorgusu.
```

## Bölüm 30 — Talimat B — Codex

```
ROL
Türkmen Gips Sanly Zawod projesinin tasarım sistemi ve frontend sahibisin.
Bu belgeye tabisin.

ALANIN
site/**, tüm CSS/JS/HTML, tokens/, görsel varlıklar.
KAYNAK-KOD/backend/** dosyasına YAZMAZSIN.

GÖREV 1 — TOKEN'I TEK KAYNAK YAP (en yüksek öncelik)
Üç stil dosyası var. Çakışan değerleri tek token dosyasına indir:
tokens/tokens.json -> CSS değişkenleri üretilir.
Sabit kodlanmış renk, ölçü, font, gölge, yarıçap kalmaz.
Kabul: grep ile sabit hex renk ve sabit px font arandığında token dışı
sonuç yok.

GÖREV 2 — TİPOGRAFİ
- Başlık: Gilroy (yerelden WOFF2, font-display: swap). Yoksa Urbanist.
- Veri/sayı: Inter veya IBM Plex Sans, font-variant-numeric: tabular-nums.
- ² ve ³ veri fontundan gelir.
- Türkmen harf kapsamı DOSYA ÜZERİNDEN test edilir: ň ý ž ä ş ç ö ü.
  Rapor: hangi harf var, hangi harf yok. Varsayımla geçilmez.
- Ölçek: Bölüm 14. Taban 40 px, kritik 64 px, sunum katmanı 180-260 px.

GÖREV 3 — DURUM VE VERİ MODU
Durum = renk + şekil + yazı. Renk körlüğü simülasyonunda tüm durumlar
ayırt edilir. Dört veri modu için görsel dil. Tek bağlantı durumu göstergesi
üstte. KÖNE durumunda değer soluk ve işaretli, yeşil kalmaz.

GÖREV 4 — AÇIK SUNUM KATMANI (A)
Bölüm 10'a birebir uy. Koyu kontrol odası ekranı (B) korunur.
Aynı token, iki değer grubu. Yeni stil dosyası açılmaz.
A katmanında "Maglumat ýok" gösterilmez, demo değeri gösterilir.
Teknik terim yok: OEE, t/sag, kW yerine Türkmence karşılıkları.
Arıza varsa YALNIZ o kutu kırmızı, ekran kararmaz.

GÖREV 5 — TEKNİK KATMAN (C)
Bölüm 12'ye uy. Motor akımı, devir, sıcaklık, titreşim, bakım sayaçları,
tag tarayıcı, alarm geçmişi.

GÖREV 6 — TÖREN MODU
Bölüm 19'a uy. Gizli kısayolla açılır. Ayrı görünüm katmanı, normal modun
kopyası değil.

GÖREV 7 — MİNİ MOTION FACTORY
Bölüm 17'ye uy. Mevcut PNG + motion overlay sistemi korunur. Ekipman
eşleşmesi tamamlanır, gerçek Türkmence adlarla etiketlenir.
SADECE beş hareket. Kamera sarsıntısı, zoom, süs yok.

GÖREV 8 — 3D BAĞLAM EKRANI
Tek route /tv/3d/. Mevcut /world/ prototipi buraya taşınır.
Veri taşımaz, bağlam taşır. WebGL çökerse 2D izometrik görsele düşer.

GÖREV 9 — ADRES TEMİZLİĞİ
Kanonik: /tv/a/ /tv/b/ /tv/3d/ /kontrol/ /sunum/
/tv/1/ ve /tv/2/ yönlendirme kalır. RELEASE.json entryPoints buna uyar.

GÖREV 10 — TÜRKMEN İMLA DENETİMİ
Bölüm 22'ye uy. Büyük İ yok. y/ý doğru. ň ä ž ş ç ö ü tam.
Rakam: ondalık virgül, binlik boşluk. Tarih gg.aa.yyyy, saat 24h.

GÖREV 11 — DAYANIKLILIK
72 saat: bellek artışı yok. Kiosk: imleç, bildirim, görev çubuğu yok.
Kesinti sonrası açılır. prefers-reduced-motion desteklenir.

YAPMA
- Yeni ekran ekleme.
- Yeni stil dosyası açma.
- Sabit renk/ölçü yazma.
- Trend grafiğini 3D yapma.
- Sözleşmede olmayan API alanı varsayma.
- Türkçe metin bırakma.
- A katmanında koyu tema kullanma.
- Beşten fazla hareket ekleme.

TANIM: BİTMİŞ
K1-K12 satırları yeşil. Kanıt dosyaları BELGELER/ altına yazılır.
```

## Bölüm 31 — Ortak kapanış talimatı

Bu talimat iki ajana birlikte verilir. Ayrı cevap verirler, birbirlerinin dosyasına yazmazlar.

1. Kabul matrisini satır satır uygula ve kanıt üret.
2. Kapsam kilidindeki GİRMEZ listesine yeni madde ekleme.
3. Bitince RELEASE.json güncelle: sürüm v9, entryPoints kanonik adresler.
4. DOSYA-DOGRULAMA.json yeniden üret (tüm dosyaların SHA-256'sı).
5. `workingTreeDirty: false` olana kadar iş bitmiş sayılmaz.
6. Kapanış raporu `BELGELER/v9-KAPANIS.md` yaz: ne yapıldı, hangi kriter karşılandı, hangi kanıt dosyası; v10'a devredilen maddeler; HÂLÂ SIMULYASIYA olan alanların açık listesi; saha bekleyen maddeler.
7. Sahaya ait ve sizde olmayan maddeleri tamamlanmış sayma.

**Kural:** Bir satır yeşil olmadan v9 bitmiş sayılmaz. Kanıt dosyası olmayan satır yeşil sayılmaz. "Yapıldı" demek yetmez, kanıt göster.

## Bölüm 32 — Açılış günü kontrol listesi

Son 48 saatte madde madde geçilir. Tören günü değişiklik yapılmaz.

1. **Yazım ve dil:** Tüm metinler Türkmence · büyük İ yok · y/ý doğru · ň ä ž ş ç ö ü tam · cumhurbaşkanı adı ve unvanı iki kez bağımsız kontrol edildi · İngilizce jargon yok · tarih gg.aa.yyyy · ay ve gün adları Türkmence · ekranda localhost yok.
2. **Rakam ve birim:** Ondalık virgül, binlik boşluk · birimler doğru · saatlik toplamlar günlüğe eşit · hedef ve gerçekleşme tutarlı · kısmi saat doğru okunuyor · uydurma değer "gerçek" diye etiketli değil.
3. **Devlet sembolleri ve mesaj:** Bayrak oranı doğru, daire içine alınmamış · milli yeşil tutarlı · iş orunlary, eksport, importyň ornuny tutýan paneli var · sanly ykdysadyýet bağlantısı var · yabancı marka milli adın önüne geçmiyor.
4. **Tören akışı:** Tören modu gizli kısayolla çalışıyor · alarm gizli · kurdele anı için ayrı ekran · sayaç sıfırdan başlıyor · milli katkı ekranı hazır · güzergahtaki her ekran farklı sahne · normal moda dönüş denenmiş · her ekranda görevli · 10 soru ve cevabı yazılı.
5. **Teknik ve dayanıklılık:** 72 saat testi geçti · bellek artışı yok · kiosk modu, imleç ve bildirim yok · Windows Update kapalı · ekran koruyucu kapalı · saat ve saat dilimi doğru · kesinti sonrası otomatik açılma test edildi · ağ kesilince donmuyor · WebGL varsa 30 fps · WebGL çökerse 2D'ye düşüyor · yedek PC ve HDMI hazır · kumandalar gizlendi.
6. **Ortam ve çekim:** 4 m okuma testi geçti, 40 px altı yok · yansıma yok · parlaklık salona göre ayarlı · kamera açısı denendi · dış %5 çerçevede kritik bilgi yok · kritik sayı üst üçte birde · 2 saniyelik bakışta okunuyor · açık tema seçili · ekranlar temiz.
7. **Acil durum:** Simülasyon açıklaması tek cümle Türkmence hazır · ekran çökerse 5 saniyede devreye girecek yedek plan · ağ yedeği hazır · teknik sorumlu numarası · tek sayfalık müdahale prosedürü.

## Bölüm 33 — Sözlük ve değişiklik kaydı

| Türkmence | Türkçe | Türkmence | Türkçe |
|---|---|---|---|
| Önümçilik | Üretim | Enjam | Ekipman |
| Gözegçilik | İzleme | Ýagdaý | Durum |
| Işleýär | Çalışıyor | Durdy | Durdu |
| Näsazlyk | Arıza | Duýduryş | Alarm |
| Hat tizligi | Hat hızı | Günlük maksat | Günlük hedef |
| Guradyjy | Kurutucu | Kesiji | Kesici |
| Garyşdyryjy | Karıştırıcı | Dozirleýji | Dozajlayıcı |
| Doldurylyş | Doluluk | Netijelilik | Verimlilik |
| Hil | Kalite | Datçik | Sensör |
| Ulgam | Sistem | Sanly | Dijital |
| Ýerine ýetiriliş | Gerçekleşme | Kuwwat | Güç, kapasite |
| Maglumat ýok | Veri yok | Köne | Bayat |

### Değişiklik kaydı

| Sürüm | Tarih | Değişiklik |
|---|---|---|
| 9.0 | 26.10.2026 | İlk yürürlük. Kilitli kararlar, kapsam kilidi, üç katman, token seti, mini motion spec, MES mimarisi, ajan talimatları, açılış listesi. |

Sonraki değişiklik bu tabloya satır olarak eklenir; mevcut maddeler sessizce değiştirilmez.

**Onay:** Proje sahibi / hakem — Tarih: ________
