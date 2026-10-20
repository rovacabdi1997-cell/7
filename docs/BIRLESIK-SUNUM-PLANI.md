# Birleşik sunum planı: Bakanlık sunumu + iki TV + güneş enerjisi (v1, 2026-10-20)

Kaynak: `TURKMEN-GIPS-USB-TAM-SUNUM-v3-FINAL-2026-09-14.zip`
Referans: Inductive Automation semineri ve Bosch ActiveCockpit basın dosyası.

## 1. Eski pakette ne var

| Dosya | İçerik | Karar |
|---|---|---|
| `TURKMEN-GIPS-BAKANLIK-SUNUMU.html` | Açılış ekranı ve 11 sekmeli uygulama | Ana ürün, kalır, düzeltilir |
| `TURKMEN-GIPS-AKYM-SHEMASY.html` | 9 senaryolu akış şeması, koyu tema | Kalır, açık temaya alınır |
| `TURKMEN-GIPS-TEHNIKI-INTEGRASIYA.html` + PDF + 4K PNG | 4 dilli teknik sunum | Olduğu gibi kalır |
| `assets/` | 8 video, 10 kampüs görseli, logo, plan PDF | Kalır |
| `raporlar/`, `belgeler/` | Teknik rapor, teklif, resmi belge metinleri | Kalır |

Bakanlık sunumundaki 11 sekme: Umumy syn, Önümçilik akymy, Ammar we çig mal,
Hil gözegçiligi, Tehniki hyzmat, Energiýa, Işgärler, Hasabatlar, Kuwwat hasaby,
Ekologiýa pasporty, Zawod meýilnamasy.

## 2. Eski üründe düzeltilecekler

| No | Sorun | Nerede | Düzeltme |
|---|---|---|---|
| D1 | Tarih Rusça çıkıyor ("вторник, 20 октября") | Üst sağ saat | Tarayıcı `tk-TM` dilini tanımıyor; ay ve gün adları elle Türkmence yazılır |
| D2 | Görselin üstünde "HIGGSFIELD • SIMULÝASIÝA" yazıyor | Sağ panel görsel etiketi | Araç adı kaldırılır, yalnız "WIZUALIZASIÝA" kalır |
| D3 | KPI başlıkları kesiliyor ("A BÖLÜMI • GIPSOKARTO…") | Üst KPI şeridi | Başlık kısaltılır, iki satıra izin verilir |
| D4 | Silo adları uydurma (S-01 Alçydaşy …) | Çig mal silolary kartı | Envanter kodları: `1-005-510` … `1-005-590` |
| D5 | Akış şeması koyu temada, diğer ekranlar açık | `AKYM-SHEMASY.html` | Yeni TV'lerin açık teması ve renk tokenları |
| D6 | Sayı biçimi `de-DE` | Bütün rakamlar | Türkmence biçim: binlik boşluk, ondalık virgül |
| D7 | 250.000 t/ýyl ile pasporttaki 50.000 t/ýyl çelişkisi | Kuwwat hasaby, Ekologiýa | Uyarı kalır; iki rakam aynı ekranda kaynaklarıyla gösterilir |
| D8 | TV'deki makine adlarıyla sunumdaki adımlar farklı | Tur adımları (Çig mal, Şekillendiriş …) | TV listesiyle aynı adlar ve sıra |

## 3. Birleştirme: iki TV sistemi sunuma giriyor

"Önümçilik akymy" sekmesi yeni iki TV sahnesini kullanır.

- Sekmenin içinde iki alt sekme olur: **A bölümi · Gipsokarton** ve **B bölümi · Gury garyndy**.
- Sahne, KPI kartları, akış animasyonu ve 6 dakikalık sunum döngüsü TV'lerdekiyle aynıdır.
- Veri tek kaynaktan gelir: `sunum.json` (çevrimdışı) veya API (canlı).
- TV paketi (`v3`) ayrı ürün olarak durur; aynı kodu paylaşır.
- Açılış ekranına beşinci düğme eklenir: **▣ IKI TV GÖRNÜŞI**.

## 4. Yeni modül: Gün energiýasy (güneş paneli)

Ekoloji temasıyla yeni sekme: **Gün energiýasy**, Ekologiýa pasportunun hemen altına.

### Veri dayanağı

| Değer | Kaynak | Etiket |
|---|---|---|
| Yıllık elektrik 1.800.000 kWh | Ekoloji pasportu | `OFFICIAL_DOCUMENT` |
| Kurulu güç ≈ 4.282 kW | Ekoloji pasportu | `OFFICIAL_DOCUMENT` |
| Panel gücü, üretim, CO₂ | Hesap | `TASLAMA` |

Güneş sistemi henüz kurulu değil. Bütün güneş rakamları **TASLAMA** (proje)
etiketi taşır; ne `SIMULÝASIÝA` ne de gerçek ölçüm gibi gösterilir.

### Taslama varsayımları (onay gerekir)

| Parametre | Değer | Not |
|---|---|---|
| Çatı GES | 1,0 MWp | Üretim binası çatıları, ≈ 6.000 m² |
| Otopark GES | 0,25 MWp | Kamyon otoparkı üstü gölgelik |
| Özgül üretim | 1.650 kWh/kWp·ýyl | Türkmenistan için tahmin, ölçümle doğrulanmalı |
| Yıllık üretim | ≈ 2.060 MWh | 1,25 MWp × 1.650 |
| Pasporttaki yıllık tüketime oranı | ≈ %114 | Pasport rakamı düşük olabilir (bkz. D7) |
| Şebeke emisyon katsayısı | 0,50 tCO₂/MWh | Doğal gaz santrali varsayımı |
| Önlenen CO₂ | ≈ 1.030 t/ýyl | 2.060 × 0,50 |
| Batarya (BESS) | 500 kWh | Akşam yükü ve duruş koruması |

### Ekran

```text
┌ Gün energiýasy · TASLAMA ───────────────────────────────────────┐
│ Kampüs görseli: çatılarda paneller        │ Şu an  │ Bugün      │
│ (gündüz/gece döngüsü, güneş yayı)         │ 812 kW │ 5,1 MWh    │
├───────────────────────────────────────────┴────────┴────────────┤
│ Enerji akışı: GES → inverter → MCC → hatlar / batarya / şebeke  │
├──────────────┬──────────────┬──────────────┬────────────────────┤
│ Zawod payı % │ CO₂ t/ýyl    │ Batarya %    │ 24 saat eğrisi     │
└──────────────┴──────────────┴──────────────┴────────────────────┘
```

- Gün eğrisi saate bağlı ve deterministik: sabah artar, öğlen tepe, akşam sıfır.
- Enerji akışı, iki TV'deki akış şemasıyla aynı dilde çizilir: düğümler, akan noktalar.
- "Energiýa" sekmesindeki pasta grafiğe "Gün energiýasy" dilimi eklenir.

## 5. Referanslardan alınacaklar

| Kaynak | Alınacak fikir |
|---|---|
| Ignition / Saint-Gobain | Tek veri modeli: aynı makine kimliği bütün ekranlarda; kart tabanlı arayüz |
| Ignition / CES | Katmanlı mimari: saha → veri çekirdeği → ekranlar; rapor yerine canlı pano |
| Bosch ActiveCockpit | Hat yanında büyük ekran: durum ve sapma tek bakışta |
| Bosch Nexeed | OK / NOK eşikli eğri, tahmine dayalı bakım vurgusu |

Bu fikirler mevcut ürüne eklenir; marka, metin ve görsel kopyalanmaz.

## 6. Sahiplik notu

`CLAUDE.md`'ye göre sunum dosyaları Codex alanındadır. Bu iş kullanıcının
doğrudan isteğiyle yapılıyor; `ORTAK-CALISMA-PLANI.md`'ye handoff kaydı düşülecek.

## 7. İş sırası

| Sıra | İş | Görsel gerekir mi |
|---|---|---|
| 1 | D1–D8 düzeltmeleri | Hayır |
| 2 | Önümçilik akymy sekmesine iki TV sahnesi | Hayır, mevcut 16 görsel |
| 3 | Gün energiýasy hesap modülü ve sekme iskeleti | Hayır |
| 4 | ChatGPT görsellerini yerleştir | Evet, `CHATGPT-GUN-ENERGIYASY-PROMPTLARI.md` |
| 5 | Birleşik USB paketi ve kabul testi | Evet |
