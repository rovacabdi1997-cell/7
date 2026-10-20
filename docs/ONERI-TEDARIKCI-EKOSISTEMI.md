# Öneri: çok tedarikçili tesis için sade dashboard (v1, 2026-10-21)

Kaynak: `E:\4K_ALCIPAN ZAWOT_23.09.2025.mp4` video inceleme notu (79 kare, 6:34),
Baumak envanteri, Sanjin teklifi, master brief v4, onaylı şema TR-06-2023.

## 1. Videodan çıkan ana ders

Aynı videoda dört farklı kaynak türü karışık:

| Tür | Videodaki örnek | Ekranda nasıl gösterilir |
|---|---|---|
| Gerçek saha | 00:05–01:10 şantiye ve drone | `HAKYKY SURAT` |
| 3D tanıtım | 01:15–02:45 kampüs, 43 m bina etiketi | `3D TANYTYM` — ölçüm değildir |
| Tedarikçi görüntüsü | 02:50–03:20 HAVER, BEUMER, kurutucu ekleri | `ÜPJÜN EDIJI` |
| Belge | Envanter, teklif, onaylı şema | `RESMI BELGE` |

Öneri 1: Sistemdeki her görsel ve her sayı bu dört etiketten birini taşır.
Bugünkü `SIMULÝASIÝA / HAKYKY / ÝOK` veri moduna ek olarak **kaynak türü** alanı.
Örnek: "43 m" bir 3D animasyon değeridir; ekranda `3D TANYTYM` etiketiyle görünür,
saha ölçümü gelene kadar teknik değer olarak kullanılmaz.

## 2. Tedarikçiler ve bölgeler

Ekran **tedarikçiye göre değil, üretim akışına göre** düzenlenir. Marka yalnız makine kartında görünür.

| Tedarikçi (doğru ad) | Bölge | Kanıt | Güven |
|---|---|---|---|
| GÜRSAN | Kırma ve eleme (karýer → döwüji) | Baumak listesi `1-001-100`, marka GÜRSAN | Belge |
| Claudius Peters | Öğütme / kalsinasyon ekipmanı | Video 03:00 öğütme kesiti | Doğrulanmalı |
| Baumak Mühendislik | Toz alçı, kalsit ve kuru karışım tesisleri; yerleşim | Baumak listesi, DWG | Belge |
| HAVER & BOECKER | Toz alçı torbalama | Video 02:50 "HAVER" | Video, doğrulanmalı |
| BEUMER Group | Kuru karışım paletleme ve streç-hood | Video 03:10, master brief | Video + saha fotoğrafı |
| Shandong Sanjin | Gipsokarton hattı (A bölümi) | Sanjin teklifi | Belge |

Ad düzeltmeleri: "hover" = **HAVER & BOECKER**, "bouer group" = **BEUMER Group**,
"gladius peters" = **Claudius Peters**, "boumak" = **Baumak**.
**Bucher Emhart Glass ile Sanjin farklı şirketlerdir.** Sanjin'in tam adı Shandong Sanjin
Glass Machinery. Bucher Emhart Glass, cam şişe makineleri üreten ayrı bir İsviçre şirketi.
Sahada Bucher Emhart ekipmanı varsa hangi bölümde olduğu belirtilmeli.

## 3. Sade dashboard: üç seviye, tek soru

| Seviye | Soru | Ekran |
|---|---|---|
| 1. Zawod | "Her şey yolunda mı?" | Tek kampüs haritası, 6 bölge, her biri yeşil/sarı/kırmızı |
| 2. Bölüm | "Bu bölümde ne oluyor?" | Akış şeması + en fazla 4 KPI + açık iş kartları |
| 3. Enjam | "Bu makineye ne olmuş, ne yapmalı?" | Makine kartı: durum, iş kartı, tedarikçi, kılavuz, yedek parça |

Kurallar:
- Bir ekranda en fazla 4 büyük sayı. Renk yalnız durum anlatır.
- Marka logosu ana ekranlarda yok; yalnız seviye 3 makine kartında küçük yazı.
- Her ekrandan bir sonrakine tek tıkla inilir, geri tek tıkla çıkılır.
- Tedarikçi filtresi yalnız bakım ekranında: "Bu hafta BEUMER bakımı ne?"

### 6 bölge (seviye 1)

1. Karýer we döwüji (GÜRSAN)
2. Bişiriş we üweme (Baumak, Claudius Peters doğrulanmalı)
3. Siloslar (Silos №1–8)
4. A bölümi · Gipsokarton (Sanjin) — TV 1
5. B bölümi · Gury garyndy (Baumak + BEUMER) — TV 2
6. Gaplama we ugratma (HAVER, BEUMER, yükleme alanı)

## 4. Videodan gelen yeni ekran fikirleri

| Fikir | Kaynak | Not |
|---|---|---|
| Tıklanabilir 3D kampüs haritası (seviye 1) | Video 01:15–02:00 | 3D kare `3D TANYTYM` etiketli altlık olur |
| Bölüm kesit görseli (seviye 2) | Video 02:30–03:00 | Çok katlı proses binası, öğütme kesiti |
| Gerçek/3D yan yana karşılaştırma | Video 03:15–03:20 | "Plan ↔ saha" farkını gösterir, devreye almada işe yarar |
| Tedarikçi bakım takvimi | — | Garanti, servis anlaşması, yedek parça |

## 5. Her tedarikçiden istenecekler (veri talebi)

Gerçek veriye geçiş bunlar olmadan olmaz. PLC tag listesi hiçbir belgede yok (`open-plc-tag-listesi`).

| İstek | Neden |
|---|---|
| PLC/HMI marka ve modeli, haberleşme (OPC UA, Profinet, SQL) | Bağlantı yöntemi |
| Tag listesi: durum, hız, alarm, sayaç | Ekrandaki her sayının kaynağı |
| Alarm listesi ve öncelikleri | İş kartlarının "Makine diýýär" metni |
| Bakım planı ve yedek parça listesi | Seviye 3 makine kartı |
| Kılavuzlar (PDF) | "Näme etmeli" adımları |
| Garanti ve servis iletişimi | Bakım ekranı |

Tek şablonla altı tedarikçiye gönderilir. Yanıt gelen tedarikçinin bölümü önce
`HAKYKY` olur; gelmeyenler `SIMULÝASIÝA` kalır.

## 6. Önerilen sıra

1. Kaynak türü etiketi (bölüm 1): küçük iş, güveni hemen artırır.
2. 6 bölgeli seviye 1 haritası: mevcut kampüs görselleri ile.
3. Makine kartına tedarikçi alanı: `plant.json`'a `vendor` eklenir.
4. Tedarikçi veri talebi şablonu gönderilir.
5. Gelen ilk tag listesiyle bir bölüm canlıya alınır (öneri: BEUMER veya Sanjin).
