# HANDOFF-2026-10-26-002 — Üç canlı tag için yol (Görev 5)

| Alan | Değer |
|---|---|
| Gönderen | Claude (backend) |
| Alan | Proje sahibi ve saha ekibi. Codex'e iş yok |
| Sözleşme etkisi | Yok, v2.0.0 aynı kalır |
| Kaynak | `D:\turkmen gips\sql cart curt\` içindeki WinCC proje kopyaları |
| Kanıt | `docs/wincc/wincc-tag-listesi-2026-10-26.csv`, 417 tag |
| Durum | Tag adresleri bulundu. Canlı okuma yapılmadı. Hiçbir alan HAKYKY değil |

## Ne bulundu

İki WinCC V7.3 istasyonu var. İkisi de aynı PLC bağlantısını kullanıyor.

| Bilgi | Değer | Kaynak |
|---|---|---|
| CPI istasyonu | Islak uç: karıştırıcı, köpük, şekillendirme, kurutucu zinciri. 329 tag | `chengxing 2/chengxing/chengxing.mdf` |
| IOP istasyonu | Kuru uç: istifleme, hat testereleri. 115 tag | `二横wincc/chengxing/chengxing.mdf` |
| Bağlantı adı | `chengxingPLC` | iki MDF |
| Kanal | SIMATIC S7-1200, S7-1500 Channel | iki MDF |
| PLC adresi adayı | `192.168.10.6`. IOP'ta ayrıca `.7` ve `.8` geçiyor | iki MDF |

PLC IP'si sahada doğrulanmalı. `.7` ve `.8` adreslerinin HMI mi PLC mi olduğu bilinmiyor.

## Üç tag

| Hedef | WinCC tag'i | Anlamı | Adres | Tip | Durum |
|---|---|---|---|---|---|
| Hat hızı `gipsokarton.speed` | `凝固皮带速度` | Gataýan lenta tizligi, şekillendirme bandı hızı | CPI `%DB6.%DD418` | DWORD, büyük olasılıkla REAL | Güçlü aday |
| Üretim sayacı `gipsokarton.outputToday` | `1#堆垛计数`, `2#堆垛计数` | İstif içindeki levha sayısı | IOP `%DB66.%DW0`, `%DB66.%DW4` | WORD | Kısmi aday |
| Hat çalışıyor/duruyor `gipsokarton.status` | `凝固皮带运行信号` | Şekillendirme bandı çalışıyor | CPI `%DB6.%D154.0` | BIT | Vekil aday |

### Her tag için açık noktalar

**Hız.** Birim tag tanımında yok. Saha fotoğrafında WinCC ekranı 7.1 m/min gösterdi. Ölçek 1:1 varsayılırsa birim m/min olur. Sahada ekran değeri ile tag değeri yan yana okunmalı.

**Sayaç.** Kümülatif üretim sayacı bulunamadı. Bulunan tag'ler her istifin içindeki levhayı sayıyor. `清零` tag'i ile sıfırlanıyor, `目标计数` istif hedefi. Günlük m² şöyle hesaplanabilir: sayaçtaki her artış bir levha, levha alanı ürün ölçüsünden gelir. Bu hesap sürekli okuma ve historian ister. Tek okuma ile günlük toplam verilemez. PLC'de gizli bir toplam sayacı olup olmadığı otomasyon firmasına sorulmalı.

**Durum.** Hattın tek bir "çalışıyor" tag'i yok. Şekillendirme bandı durunca hat durur, bu yüzden vekil olarak seçildi. `总急停` (umumi awariýa duruzmasy) ayrıca okunabilir: CPI `%DB2.%D4.6`, IOP `%DB4.%D2.7`. 1 ve 0 değerlerinin anlamı sahada doğrulanmalı. Doğrulanmadan backend durumu `UNKNOWN` verir.

## Okuma yolu

| Konu | Karar | Not |
|---|---|---|
| Yol | WinCC OPC UA sunucusu, salt okuma | SQL kopyasında canlı değer yok. Tag Logging arşivi de yok |
| Uç | `opc.tcp://<CPI-PC>:4862`, `opc.tcp://<IOP-PC>:4862` | Port WinCC varsayılanı. Sahada doğrulanmalı |
| Okuma periyodu | 5 saniye | `REFRESH_SECONDS` |
| Bayatlık eşiği | Hız ve durum 15 s, sayaç 60 s | Sözleşme v2 |
| Beklenen gecikme | Tahminen 7 saniyenin altı | WinCC güncelleme çevrimi ile 5 s okuma. Ölçülmedi |
| Salt okuma garantisi | Ayrı OPC UA kullanıcısı, yalnız okuma yetkisi. Adaptörde yazma çağrısı yok. SQL yolu `readonly_guard` ile korunuyor | PLC'ye yazma kapsam dışı |

## Sıradaki adımlar

1. Sahada: PLC IP'si, iki istasyonun PC adı ve OPC UA'nın açık olduğu teyit edilir.
2. Sahada: hız tag'i ile ekran değeri karşılaştırılır, durum bitinin 1/0 anlamı yazılır.
3. Backend: salt okunur OPC UA adaptörü yazılır. Sözleşme değişmez, yalnız kaynak değişir.
4. Üç tag doğrulanınca `tag_mapping.json` içinde `VERIFIED` yapılır. Ancak o zaman `HAKYKY` görünür.

## Dürüstlük notu

Adresler bir SQL dosya kopyasından metin olarak çıkarıldı, SQL Server ile açılmadı. Her kayıtta adresin sonunda bir kayıt baytı bulunuyor. Bu bayt atıldı ve ham hali CSV'de `raw` sütununda duruyor. Sürücü blokları 14 baytlık düzenli aralıklarla diziliyor, bu çözümü destekliyor. Yine de tek kesin kaynak WinCC Explorer'dan alınacak tag dışa aktarımıdır.
