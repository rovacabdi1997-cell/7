# Türkmen Gips — Ana şartname (v1, 2026-10-20)

Bu belge, bugüne kadar verilen bütün direktiflerin tek ve bağlayıcı özetidir.
Önceki planlar (`IKI-TV-PLANI.md`, `IKI-TV-TEKNIK-TASARIM.md`, `BIRLESIK-SUNUM-PLANI.md`,
`GORSEL-IHTIYAC-LISTESI.md`, `CHATGPT-*.md`) bununla çelişirse **bu belge geçerlidir**.

## 1. Direktifler (kronolojik, hepsi geçerli)

| No | Direktif | Durum |
|---|---|---|
| 1 | Logo ve tasarım görselleri ChatGPT'de; backend ve asıl kod Claude'da | Uygulanıyor |
| 2 | İki TV, ayrı ayrı planlanır | Bitti, USB v3 |
| 3 | Devlet derecesinde ciddi görünüm | Sürüyor |
| 4 | Bütün yazılar **bold** | Sürüyor, TV'de güçlendirilecek |
| 5 | Makineler birbirine geçişli, mini animasyonlu | Bitti, akış şeması |
| 6 | Gerçek zamanlı veri | Bitti, SSE; saha verisi 0/14 |
| 7 | Her TV'ye mini PC; IP'ler tasarım onayından sonra; API'ye bağlanabilir olsun | Bitti |
| 8 | Makine yerleri CAD'e göre | Uygulanıyor |
| 9 | Animasyon akıcı, iş akış şeması gibi; grafikler fütüristik | Bitti |
| 10 | Makine listesi envanter ve belgeye dayanır | Bitti, bkz. §6 düzeltme |
| 11 | USB'de eskiye ait hiçbir şey olmaz | Bitti, v3 |
| 12 | Hazır ürünler durur: Bakanlık sunumu, akış şeması, teknik sunum | Korunuyor |
| 13 | Ekoloji teması: güneş panelli sistem | Planlandı |
| 14 | Son yapılan iki TV, sunumdaki sekmeyle harmanlanır | Planlandı |
| 15 | Öncü firmalar gibi: işçiye değer, makinenin dediğini anlayan iş akışı | Planlandı |
| 16 | Görseller gerçeğe uygun | Bu belge |
| 17 | **Görseller orijinal**: gerçek saha fotoğrafları kullanılır | Bu belge |
| 18 | Renk sistemi **beyaz ve mavi** | Bu belge |
| 19 | Sunumdaki mevcut renk skalası **açık mod / koyu mod** olarak kullanılır | Bu belge |
| 20 | TV gösterimi daha estetik ve daha bold | Bu belge |

## 2. Renk sistemi (tek kaynak)

Bakanlık sunumunun akış şemasındaki iki palet olduğu gibi alınır.
Varsayılan **açık mod** (beyaz-mavi). Koyu mod isteğe bağlıdır.

| Token | Açık mod | Koyu mod | Kullanım |
|---|---|---|---|
| `--bg` | `#EDF2F7` | `#071017` | Sayfa zemini |
| `--surface` | `#FFFFFF` | `#0D1820` | Kart |
| `--surface2` | `#F6F9FC` | `#111F29` | İkinci yüzey |
| `--floor` | `#E7EEF4` | `#152630` | Sahne zemini |
| `--line` | `#DAE4EC` | `#1D3441` | Çizgi |
| `--line2` | `#C2D3E0` | `#2B4A5A` | Güçlü çizgi |
| `--txt` | `#132330` | `#EAF3F7` | Ana yazı |
| `--muted` | `#63788A` | `#8FA7B5` | İkincil yazı |
| `--acc` | `#1E9BE0` | `#34C6F4` | Ana mavi, veri |
| `--acc2` | `#0C6FB8` | `#61D4F7` | Koyu mavi, başlık |
| `--acc3` | `#8FD3F7` | `#A2E6FA` | Açık mavi, dolgu |
| `--warn` | `#E0871F` | `#FFB454` | Uyarı |
| `--crit` | `#DC3A50` | `#FF6678` | Kritik |
| `--ok` | `#1E9E6A` | `#3DDC97` | Çalışıyor (yeşil yalnız durum ışığında) |

Kurallar:
- Mavi veri ve marka içindir. Kırmızı yalnız kritik durumda, turuncu yalnız uyarıda.
- Yazı tipleri: başlık `Bahnschrift` (yoksa `Segoe UI Semibold`), gövde `Segoe UI`, sayı `Cascadia Mono`.
- Mod seçimi: adreste `?tema=acik` / `?tema=koyu`; seçilmezse açık.
- Neon, parlama, kayan yazı, carousel yok (önceki teslim notu geçerli).

## 3. TV ekranı: daha estetik, daha bold

| Öğe | Şimdi | Yeni |
|---|---|---|
| Başlık şeridi | Beyaz, ince | Koyu mavi `--acc2` şerit, beyaz yazı, logo beyaz zeminde |
| Hat adı | 46 px, 800 | 56 px, 900, harf aralığı geniş |
| Ana rakam | 96 px | 120 px, 900, tabular |
| Kart başlığı | 28 px | 30 px, 900, büyük harf |
| Makine sırası | Sahne genişliği × 1,12 | Sahne yüksekliğinin %62'si, daha büyük |
| Akış hattı | 5 px noktalı | 8 px dolu ray + akan noktalar, mavi degrade |
| Arıza | Kırmızı etiket | Tam genişlik kırmızı bant: makine adı + "Näme etmeli" ilk adımı |
| Kartlar | Beyaz, ince köşe | Üstte 4 px mavi şerit, gölge yok, köşe çizgisi kalır |
| Gerçek fotoğraf | Yok | Sahne zemininde hattın gerçek fotoğrafı, %8 opaklık, soluk |

Kabul: 4 metreden okunur; 1080p ve 4K'da aynı yerleşim; konsol hatası yok.

## 4. Ürünler ve kapsam

| Ürün | Durum | Bu aşamada |
|---|---|---|
| İki TV USB v3 | Kabul testi geçti | Renk ve boldluk güncellemesi → v4 |
| Bakanlık sunumu | Korunur | D1–D8 düzeltmeleri, renk sistemi, orijinal görseller |
| Akış şeması | Korunur | Açık/koyu mod, orijinal görseller |
| Teknik entegrasyon sunumu | Korunur | Değişmez |
| Önümçilik akymy sekmesi | Harmanlanır | İki TV sahnesi alt sekme olarak |
| Gün energiýasy sekmesi | Yeni | `TASLAMA` etiketli modül |
| İş kartı sistemi | Yeni | Makine diýýär → Näme etmeli → Jogapkär → işçinin cevabı |

## 5. Görsel stratejisi: orijinal önce

1. **Gerçek saha fotoğrafları** her yerde birinci tercih. 24 fotoğraf, `Downloads\IMG_6185`–`IMG_6227`.
2. Gerçek fotoğrafta olmayan şey (işçi, ekran, güneş paneli) için **gerçek fotoğrafın düzenlenmesi**
   istenir: fotoğraf aynı kalır, yalnız eksik öğe eklenir.
3. Sıfırdan üretim yalnız gerçek karşılığı olmayan şematik parçalar içindir (TV makine ikonları,
   güneş sistemi izometrik parçaları).
4. Eski yapay zekâ görselleri ve videoları kaldırılır: 8 video, akış şemasına gömülü 10 görsel.
   Kampüs model renderları resmî tasarım çıktısı olduğu için kalır.

### Gerçek fotoğrafların eşlemesi

| Foto | İçerik | Kullanılacağı yer |
|---|---|---|
| IMG_6185–6188 | Boş hol, 3 açıklık, beton zemin | Umumy syn, Ammar, Zawod meýilnamasy |
| IMG_6191 | Yaş uç, sarı platform, şekillendirme bandı (dikey) | Gipsokarton bölümi, TV 1 |
| IMG_6194–6195 | Eğimli konveyör, rulolu masalar | Önümçilik akymy |
| IMG_6196–6197 | Çok şeritli rulolu masalar, sarı koruyucular | Kesim, Hil gözegçiligi |
| IMG_6198 | Koyu şekillendirme bandı | Gatama lentasy |
| IMG_6199–6202 | Aktarma, çapraz konveyör, kırmızı tahrik | Kesiji, Tehniki hyzmat |
| IMG_6203 | Rulolu hat, sarı yürüme yolu (dikey) | Kuru uç |
| IMG_6204–6210 | Çok katlı kurutucu rafları, motorlar | Guradyjy, Energiýa |
| IMG_6211 | Mavi BEUMER paletleyici | Gury garyndy bölümi, TV 2 |
| IMG_6227 | Hazneler ve filtre | Çig mal we bişiriş |

## 6. Düzeltilecek bilinen hatalar

- **Gyra kesiji TV 1'e geri döner.** Saha fotoğrafları ve brief: kuru uçta kenar testereleri var.
  Sıra: Guradyjy → Gyra kesiji → Bukjalaýjy → Gaplaýjy.
- Bakanlık sunumu D1–D8 (`BIRLESIK-SUNUM-PLANI.md` §2).
- Gömülü yapay zekâ görsellerindeki işçiler Doğu Asyalı; kaldırılır, yerine Türkmen işçili düzenlemeler.

## 6a. Kullanıcı notları (2026-10-20) — **5'i de uygulandı**, son pakette (`outputs/TURKMEN-GIPS-BIRLESIK-SON-2026-10-20`)

Bakanlık sunumunun büyük bölüm görsellerinde (ekran: `docs/notlar/not-ekran-sunum-hil.webp`)
kullanıcının verdiği iki görsel kullanılacak:

| Görsel | İçerik | Önerilen yer |
|---|---|---|
| `docs/notlar/not-gorsel-torbalama-markali.webp` | Markalı mavi tulumlu operatör, Türkmen Gips logolu torbalar, dolum makinesi | Gury garyndy bölümi başlık görseli, TV 2 tarafı |
| `docs/notlar/not-gorsel-yas-uc-operator.webp` | Sarı platformda tabletli operatör, şekillendirme bandı, kurutucu bacaları (dikey) | Gipsokarton bölümi başlık görseli, TV 1 tarafı |

Ek not (aynı gün): `Hasabatlar` sekmesindeki büyük başlık görseli
("Öňünden duýdurma we hasabat", ekran: `docs/notlar/not-ekran-sunum-hasabat.webp`)
yerine `docs/notlar/not-gorsel-kontrol-odasi.webp` kullanılacak: hole bakan cam duvarlı
kontrol odası, üç operatör masası, dikey görsel. Geniş alana masalar ve hol görünümü
ortada kalacak şekilde kırpılmalı; "WIZUALIZASIÝA" etiketi taşımalı.

Ek not 2 (aynı gün):
- **Gün energiýasy sayfası kaldırılacak** (ekran: `docs/notlar/not-ekran-gun-energiyasy-kaldir.webp`).
  Yan menüdeki "Gün energiýasy" girişi ve sayfanın kendisi pakette kalmayacak.
  Bu, §4'teki "Gün energiýasy sekmesi — Yeni" kararını iptal eder.
- **Ekoloji hareketi logosunun etrafındaki beyaz yuvarlak zemin kaldırılacak**
  (ekran: `docs/notlar/not-logo-beyaz-zemin.png`). Logo, başlık kutusunun mavi zemininde
  doğrudan, beyaz daire, iç boşluk ve gölge olmadan durmalı. Kaynak: `.eco-hero .eco-logo` kuralındaki
  `background:#fff; padding; box-shadow`.

Uygulamada dikkat:
- Torbalama ve operatör görsellerinde iş kıyafetinde ve torbalarda **Türkmen Gips logosu var**. Önceki
  "logo yok" kuralı bu görseller için kullanıcı tarafından aşılmış sayılır.
- Dikey görsel geniş başlık alanına operatör odakta kalacak şekilde kırpılmalı.
- İkisi de düzenlenmiş/üretilmiş görsel; "WIZUALIZASIÝA" etiketi taşımalı.

## 7. İş sırası

| Sıra | İş | Görsel bekler mi |
|---|---|---|
| 1 | Renk sistemi: açık/koyu tokenlar, TV ve sunum | Hayır |
| 2 | TV boldluk güncellemesi + Gyra kesiji + gerçek foto zemin → USB v4 | Hayır |
| 3 | Bakanlık sunumu D1–D8 + orijinal fotoğraflar | Hayır |
| 4 | Önümçilik akymy harmanlama | Hayır |
| 5 | İş kartı sistemi | Hayır |
| 6 | ChatGPT düzenlemeleri gelince: işçi sahneleri, güneş modülü | Evet |
| 7 | Birleşik paket ve kabul testi | Evet |

## 6b. Kullanıcı istekleri (2026-10-20, uygulandı)

| İstek | Uygulama |
|---|---|
| Laboratuvar görseli → Hil gözegçiligi | Bakanlık aşama 3 başlık görseli + akış şeması `s7` |
| Video duvarı → Kuwwat hasaby | Kuwwat hasaby sayfasının üstünde etiketli görsel bandı |
| Jeneratör/trafo odaları → Energiýa | Bakanlık aşama 6 başlık görseli + akış şeması `s9` |
| Çig mal siloslary ayrı sekmeye + bütün makineler | Yeni "Enjamlar" sekmesi: 9 silo (`1-005-510…590`) + gipsokarton 11 + gury garyndy 6 makine, görsel ve kodlarıyla (`plant.json`'dan üretildi). Silo kartı canlı panodan kalktı. |

Dikkat: Energiýa görselinde "aksa" ve "ASTOR" marka logoları var. Tesisteki gerçek
tedarikçiler değilse sunumda yanıltıcı olur; doğrulanmalı veya logosuz sürüm istenmeli.
