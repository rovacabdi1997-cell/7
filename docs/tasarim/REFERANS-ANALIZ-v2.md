# Referans analizi v2 — "kil diorama" yönü

Kaynak: proje sahibinin 26.10.2026'da verdiği referans (OptivionAI operasyon merkezi ekranı) ve Codex'in A katmanı ekranı.

## Codex ekranında ne bozuk

| Sorun | Neden |
|---|---|
| Makine etiketleri üst üste, adlar kesik | Etiketler makine görselinin üstüne değil, içine yerleştirilmiş. Sahne 1200 px'e sıkışmış |
| 3D sahne küçük ve bulanık | Diorama ekranın üçte birinde. Asıl yıldız olması gereken yer en küçük alan |
| "Maglumat ýok" kalabalığı | A katmanında yasaktı (D11). Demo değeri gösterilmeliydi |
| İngilizce "SIMULATED", "m/dk" | D8 ve karar 1'e aykırı |
| Renk çamurlu | Bej zemin, bej kart, bej sahne. Kontrast ve vurgu yok |

## Referansın estetik dili

| Katman | Referansta | Bizde karşılığı |
|---|---|---|
| Zemin | Sıcak gri, hafif ışık düşmesi. Düz renk değil, yumuşak radyal geçiş | `#BDB6AE` merkez, `#9F988F` kenar |
| Sahne | Ekranın üçte ikisi. Yüzen tek bir plaka, üstünde kil gibi mat makineler | Hattın kendisi: U şeklinde 11 makine, mevcut izometrik görseller kil filtresiyle |
| Işık | Yukarı-soldan tek ışık, uzun yumuşak gölge | v9 ışık kuralıyla aynı yön |
| Bağlantılar | Turuncu, parlayan ince çizgiler. Kesikli olanlar farklı bağlantı türü | Malzeme akışı turuncu ve akan. Kagyz ve köpük beslemesi kesikli |
| Vurgu | Sahnede tek renkli nesne: arızalı olan, kırmızı | Arızalı makine kırmızıya döner, üstünde bilgi kartı açılır |
| Etiket | Makinenin üstünde yüzen küçük açık hap | Ad ve durum noktası, makinenin üstünde, asla üstüne binmez |
| Kartlar | Sol kolonda koyu cam kartlar, ince açık kenar, yuvarlak köşe | Hız ve kapasite yayı, duýduryşlar, altı gösterge |
| Tipografi | Geometrik sans, büyük ince rakamlar, küçük başlık | Manrope veya Urbanist yerel WOFF2. Yedek Segoe UI Variable |
| Sayılar | Her göstergenin altında ince çubuk ve durum noktası | Aynı: değer, hedefe göre çubuk, nokta |
| Lejant | Sağ altta bağlantı türü ve durum | Aynı, Türkmence |

## v9'dan sapmalar (onay gerekiyor, kabul edilirse plan 9.2)

| v9 kuralı | Bu yönde | Gerekçe |
|---|---|---|
| D3/§10 açık düz zemin | Sıcak gri, radyal geçişli zemin | Derinlik hissi bu geçişten geliyor |
| §8 beş öğe kuralı | Sol kolonda 3 kart, içinde toplam 9 değer | Referans yoğunluğu. Sahne yine ana öğe |
| §16 kadran yasak | Hız kartında tek yarım yay | Referansın imza öğesi. Tek tane, sayı yine ana bilgi |
| §20 gölge ve parlama yasak | Makinelerde yumuşak gölge, akış çizgisinde hafif parıltı | Diorama hissi bunsuz oluşmuyor |
| §17 şerit 1200 × 400 px | Sahne ekranın üçte ikisi | Fabrika hissi isteği |
| D9 fontlar | Gilroy yerine Manrope veya Urbanist | Lisans ve Türkmen harf kapsamı |

Korunan kurallar: Türkmence metin, `13 795,3` biçimi, 40 px alt sınır, durum = renk + şekil + yazı, veri modu göstergesi tek ve görünür, sessiz demo geçişi yok, ışık yönü yukarı-sol, anlamsız hareket yok. Hareket yalnız malzeme akışı ve durum noktası.

## Taslak

`docs/tasarim/A-KATMANI-TASLAK-v2-DIORAMA.html`. Makine görselleri `frontend/public/tv/machines/` klasöründen okunur.
