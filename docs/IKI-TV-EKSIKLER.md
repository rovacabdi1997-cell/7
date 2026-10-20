# İki TV — eksikler ve iş planı (2026-10-20)

## Biten

| İş | Durum |
|---|---|
| Rar birleştirmesi (9 dosya + başlatıcılar) | Diskte, commit yok |
| Backend: makine sırası, `assetKey`, `flow`, yayılım kuralları | Tamam, test edildi |
| Backend: hat filtreli SSE, `seq`, ping, `/api/tv/{tvId}` | Tamam, test edildi |
| Backend: sunum döngüsü `DEMO_SCENARIO=presentation` | Tamam, test edildi |
| Frontend: `/tv/1/`, `/tv/2/`, görsel paket bağlı | Çalışıyor, kısmen doğrulandı |
| Testler | 54/54 geçti |

## P0 — Sunumdan önce şart (bugün)

| No | Eksik | Neden şart | Sahip | Süre |
|---|---|---|---|---|
| P0-1 | Başlatıcılar eski adresi açıyor: `IKI-TV.ps1` hâlâ `/tv/?slide=1` | TV'ler yeni ekranı göstermez | Claude | 20 dk |
| P0-2 | `IKI-TV-AYARLARI.json` içine `apiUrl`, TV adresine `?api=` | Mini PC'ler merkez API'yi bulur | Claude | 15 dk |
| P0-3 | Sunum modu başlatıcısı: `MERKEZ-SUNUM-BASLAT.bat` | Arıza sahnesi sunumda kesin görünür | Claude | 15 dk |
| P0-4 | Offline USB verisi `day.json` yeniden üretilmeli | USB'de makine ve akış alanları yok | Claude | 10 dk |
| P0-5 | Tarayıcı doğrulaması: TV 1 arıza anı, bağlantı kopması, `ÝOK` modu, konsol | Kabul ölçütleri 4, 5, 7 | Claude | 30 dk |
| P0-6 | 1920×1080, 3840×2160, 1366×768 ekran görüntüleri | Kabul ölçütü 1 | Claude | 15 dk |
| P0-7 | USB paketini yeniden derle ve izole test et | Teslim edilecek paket | Claude | 30 dk |
| P0-8 | İki ayrı commit: birleştirme, iki TV özelliği | Geri dönüş noktası | Claude, onayla | 5 dk |

## P1 — Tasarım onayı için karar gereken

| No | Eksik | Karar veren | Etki |
|---|---|---|---|
| P1-1 | TV 2 sırası belgeye göre: Silos №4 → Elewator №5 → Silos №5 → dozirleýji → garyşdyryjy | Kullanıcı | Yalnız yapılandırma, yeni görsel yok |
| P1-2 | TV 1'de "Gyra kesiji" Sanjin listesinde yok; doubler, booker ve bundler eksik | Kullanıcı | Gerekirse 1 yeni görsel |
| P1-3 | Makine adları onaylı belge diliyle değil, genel adlarla yazılı (Silos №, Elewator №) | Kullanıcı | Yalnız `plant.json` |
| P1-4 | Türkmence metinler ana dil kontrolünden geçmedi | Kullanıcı | Metin düzeltmesi |
| P1-5 | Görsel onayı: iki TV ekran görüntüsü yönetime gösterilecek | Kullanıcı | Sonraki aşamanın kapısı |

## P2 — Kod borcu (onaydan sonra)

| No | Eksik | Not |
|---|---|---|
| P2-1 | Gury garyndy: tamponun öbür tarafı çalışırken hat durumu `STOPPED` görünüyor | Hat durumu tampon kuralıyla hesaplanmalı |
| P2-2 | Frontend `/api/tv/{tvId}` ucunu kullanmıyor, ekran tanımı kodda da var | Tek kaynağa indirilmeli |
| P2-3 | Makine PNG'leri 31 MB, 1254 px | Mini PC'de ilk yükleme yavaşsa 512 px'e küçültülmeli |
| P2-4 | Eski `/tv/?slide=` ekranı yeni ekranla çakışıyor | Kalsın mı, kaldırılsın mı |
| P2-5 | Belgeler: `dashboard_architecture.md` API tablosu, teknik tasarımdaki `from/to` adı `fromId/toId` oldu | Belge güncellemesi |
| P2-6 | `next@15.5.2` güvenlik açığı (CVE-2025-66478) | Fabrika ağına kurmadan önce yükseltme |

## P3 — Saha devreye alma (tasarım onayından sonra)

| No | Eksik | Gereken |
|---|---|---|
| P3-1 | Merkez PC ve iki mini PC'nin IP adresleri | Fabrika BT |
| P3-2 | Mini PC'de kiosk otomatik başlatma, Windows servisi | Kurulum günü |
| P3-3 | Gerçek veri: doğrulanmış alan 0/14 | WinCC erişimi, salt-okunur kullanıcı, tag eşleme |
| P3-4 | Makine bazında gerçek durum etiketleri | PLC tag listesi, hiçbir belgede yok |
| P3-5 | İki fiziksel TV kabul testi, 4 m okuma | Sahada |

## Sıra

1. P0-1 → P0-4: başlatıcılar ve USB verisi.
2. P0-5, P0-6: tarayıcı doğrulaması ve ekran görüntüleri.
3. P1 kararları gelince P1-1 ve P1-3 hemen uygulanır.
4. P0-7, P0-8: USB paketi ve commit.
5. P2 tasarım onayından sonra, P3 saha takvimine göre.
