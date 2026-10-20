# İki TV — teknik tasarım (v1, 2026-10-20)

Üst plan: [IKI-TV-PLANI.md](IKI-TV-PLANI.md). Görsel üretimi:
[CHATGPT-TASARIM-PROMPTU.md](CHATGPT-TASARIM-PROMPTU.md).

Bu belge kod yazılmadan önceki son adımdır. Backend işleri ChatGPT görsellerini
beklemez. Görseller gelince yalnız dosya yerleştirme ve eşleme kontrolü kalır.

## 1. Başlangıç durumu

| Konu | Bulgu |
|---|---|
| Yerel depo | `turkmen-gips-monitoring`, 3 commit, çalışma ağacı temiz |
| `tmgips.rar` içindeki sürüm | Yerel deponun üst kümesi, 18 Ekim 18:05 tarihli |
| Backend farkı | Yok. Satır sonu dışında birebir aynı |
| Frontend farkı | 8 dosya değişmiş, 1 dosya yeni (`ProcessFlow.tsx`) |
| USB farkı | `usb/server.js` artık `SITE_DIR` ile `site-live` sunabiliyor |
| Test durumu | Son kayıt 44 backend testi geçti |

### Birleştirme adımları

1. Rar'daki 9 dosyayı yerel depoya kopyala:
   `AppShell.tsx`, `Card.tsx`, `ProcessFlow.tsx`, `LineScreen.tsx`,
   `Overview.tsx`, `TvView.tsx`, `next.config.mjs`, `globals.css`,
   `usb/server.js`.
2. Rar'daki USB kökündeki `TV-1-GIPSOKARTON.bat`, `TV-2-KURU-KARISIM.bat`,
   `IKI-TV.ps1`, `IKI-TV-AYARLARI.json`, `IKI-TV-KURULUM.txt`,
   `CANLI-SQL-TV-BASLAT.bat`, `MERKEZ-*.bat` dosyalarını `usb/` altına al.
3. `BELGELER/tasarim_tv_sql.md` dosyasını `docs/` altına al.
4. Backend testlerini ve `npm run build` çalıştır.
5. Ayrı bir commit at: "Merge two-TV package from tmgips.rar (2026-10-18)".

Risk düşük, çünkü yerelde commit edilmemiş değişiklik yok.

## 2. Mevcut koddaki sorunlar

| No | Sorun | Etki | Çözüm |
|---|---|---|---|
| S1 | Demo duruşu "Kagyz bobinasy" makine listesinde yok | Planlı duruşta hiçbir makine kaynak olarak işaretlenmiyor | Duruş "Formirleme stoly" makinesine bağlanır, mesaj korunur |
| S2 | Hat durunca bütün makineler `STOPPED` oluyor | Gury garyndy hattında tampon silo ve bunker etkisi görünmüyor | Hat tipine göre yayılım kuralı, bölüm 4 |
| S3 | Planda `IDLE` yazıyor, modelde yok | Belge ile kod uyuşmuyor | Plan `UNKNOWN` olarak düzeltilir |
| S4 | SSE olaylarında `id` ve `retry` yok | Kopmada tarayıcı ne zaman yeniden bağlanacağını bilmiyor | Bölüm 3.4 |
| S5 | `/api/stream` iki hattı birden gönderiyor | Her TV gereksiz veri alıyor | `?line=` filtresi |

## 3. Veri sözleşmesi eklemeleri

Kural: mevcut alanların hiçbiri silinmez veya yeniden adlandırılmaz. Yalnız
yeni alan eklenir. Eski panel ekranları değişmeden çalışmaya devam eder.

### 3.1 `Equipment` modeli

| Alan | Tip | Anlam |
|---|---|---|
| `id` | str | Mevcut, örnek `gipsokarton-06` |
| `name` | str | Mevcut, Türkmence ad |
| `status` | RunStatus | Mevcut |
| `order` | int | Yeni. Hattaki sıra, 1'den başlar |
| `assetKey` | str | Yeni. Görsel dosya kökü, örnek `tg-gk-06-kesiji` |
| `kind` | `process` veya `buffer` | Yeni. Silo ve bunker `buffer` olur |
| `mode` | DataMode | Yeni. Makine bazında veri modu |

### 3.2 `Line.flow` listesi

```json
{
  "flow": [
    {"from": "gipsokarton-05", "to": "gipsokarton-06", "active": true,  "rate": 0.94},
    {"from": "gipsokarton-06", "to": "gipsokarton-07", "active": false, "rate": 0.0}
  ]
}
```

- `rate` 0 ile 1 arasıdır: anlık hız bölü nominal hız.
- Frontend animasyon hızını yalnız bu alandan alır.
- `active:false` ise o bağlantıda malzeme çizilmez.

### 3.3 TV yapılandırması: `GET /api/tv/{tvId}`

```json
{
  "tvId": "tv-1",
  "lineId": "gipsokarton",
  "title": "Gipsokarton önümçiligi",
  "section": "A bölümi",
  "assetBase": "/tv/",
  "flowAsset": "tg-flow-gk.png",
  "materialAsset": "tg-material-board.png",
  "kpis": ["speed", "outputToday", "fulfilmentPct", "efficiencyPct"],
  "alarmLimit": 3
}
```

| tvId | lineId | Malzeme görseli |
|---|---|---|
| `tv-1` | `gipsokarton` | `tg-material-board.png` |
| `tv-2` | `gury-garyndy` | `tg-material-bag.png` |

Bilinmeyen `tvId` için `404` döner. Yapılandırma `backend/config/tv.json`
dosyasında durur, kodda sabit yazılmaz.

### 3.4 Gerçek zamanlı akış: `GET /api/stream?line=gipsokarton`

```text
retry: 3000
id: 1842
event: snapshot
data: {"seq":1842,"staleAfterSec":15,"timestamp":"...","lines":[...],"alarms":[...]}
```

- `line` verilmezse eski davranış sürer, iki hat birlikte gelir.
- `line` verilirse `lines` tek eleman, `alarms` yalnız o hattın kaydı olur.
- `seq` her olayda bir artar. Frontend atlanan `seq` görürse sayfayı yenilemez,
  yalnız son değeri gösterir.
- `staleAfterSec` geçtiği halde yeni olay gelmezse ekran "Baglanyşyk ýok" der.
- Olaylar arasında her 5 sn `: ping` yorum satırı gider. Böylece ağdaki
  ara cihazlar bağlantıyı kapatmaz.

## 4. Akış ve durum yayılım kuralları

Durumu backend hesaplar. Frontend kendi başına tahmin yürütmez.

### 4.1 Gipsokarton: sürekli hat

Levha hattı tek parça bant gibidir. Bir makine durursa bütün hat durur.

| Olay | Kaynak makine | Diğer makineler | Bütün `flow` |
|---|---|---|---|
| Arıza | `FAULT` | `STOPPED` | `active:false` |
| Planlı duruş | `STOPPED` | `STOPPED` | `active:false` |
| Normal | `RUNNING` | `RUNNING` | `active:true` |

### 4.2 Gury garyndy: tamponlu hat

Silo ve bunker malzeme biriktirir. Tamponun öncesi ve sonrası bir süre
birbirinden bağımsız çalışabilir.

| Arızalı makine | Durum |
|---|---|
| Tampondan önce | Tampona kadar olanlar durur, tampondan sonrası çalışmaya devam eder |
| Tampondan sonra | Tampondan sonrası durur, öncesi tamponu doldurmaya devam eder |
| Tamponun kendisi | Bütün hat durur |

Demo bu kuralı deterministik uygular. Sahada tamponun dolma süresi
bilinmediği için gerçek modda yayılım hesaplanmaz. Her makine kendi
etiketinden okunur.

### 4.3 Veri yoksa

`mode: "ÝOK"` olan makinenin durumu `UNKNOWN` olur. Ona bağlı `flow`
kayıtları `active:false` döner. Ekranda makine soluk çizilir ve "Maglumat ýok"
yazar. Hiçbir zaman yeşil gösterilmez.

## 5. Görsel eşleme tablosu

Dosya adı = `assetKey` + `-base.png` veya `-moving.png`.

| Equipment id | assetKey | kind |
|---|---|---|
| gipsokarton-01 | tg-gk-01-gips-berijisi | process |
| gipsokarton-02 | tg-gk-02-garysdyryjy | process |
| gipsokarton-03 | tg-gk-03-kopuk-generatory | process |
| gipsokarton-04 | tg-gk-04-formirleme-stoly | process |
| gipsokarton-05 | tg-gk-05-gatama-lentasy | process |
| gipsokarton-06 | tg-gk-06-kesiji | process |
| gipsokarton-07 | tg-gk-07-guradyjy | process |
| gipsokarton-08 | tg-gk-08-gyra-kesiji | process |
| gipsokarton-09 | tg-gk-09-gaplayjy | process |
| gipsokarton-10 | tg-gk-10-kagyz-bobinasy | feed |
| gury-garyndy-01 | tg-gg-01-cig-mal-silosy | buffer |
| gury-garyndy-02 | tg-gg-02-dozirleyji | process |
| gury-garyndy-03 | tg-gg-03-garysdyryjy | process |
| gury-garyndy-04 | tg-gg-04-elewator | process |
| gury-garyndy-05 | tg-gg-05-tayyar-onum-bunkeri | buffer |
| gury-garyndy-06 | tg-gg-06-gaplayjy-masyn | process |
| gury-garyndy-07 | tg-gg-07-palet-oruji | process |

Bir görsel eksikse ekran mevcut çizgi ikonunu (`ProcessFlow.tsx`) gösterir.
Sunum eksik görsel yüzünden bozulmaz. Bir test, bu tablodaki her anahtarın
`frontend/public/tv/` altında iki dosyası olup olmadığını raporlar.

## 6. Animasyon şartnamesi

| Öğe | Davranış | Süre |
|---|---|---|
| `moving` katmanı | `RUNNING` iken döner veya ileri geri gider | Tur süresi `1.6 sn / rate`, en yavaş 4 sn |
| Malzeme parçası | `flow.active` iken bağlantı boyunca kayar | Bir hücre `2.4 sn / rate` |
| Durum lambası | Yeşil sabit, sarı sabit, kırmızı nabız | Kırmızı nabız 1.2 sn |
| Durum değişimi | Renk ve hareket yumuşak geçer | 600 ms |
| Arıza vurgusu | Arızalı makinenin çevresine ince kırmızı çerçeve | Sabit |
| Bağlantı kopması | Bütün sahne yüzde 40 soluklaşır, hareket durur | 600 ms |

Kurallar:

- Yalnız `transform` ve `opacity` canlandırılır. TV mini PC'leri zayıf olabilir.
- Aynı anda en çok 9 makine ve 24 malzeme parçası hareket eder.
- Süs animasyonu yok: parlama, partikül, kamera hareketi kullanılmaz.
- Rakamlar animasyonsuz değişir. Devlet sunumunda sayı "sayarak" büyümez.
- Yazılar `font-weight: 800`, rakamlar `tabular-nums`.

## 7. Sunum senaryosu

Saate bağlı demo, sunum anında arıza göstermeyebilir. Bu yüzden ayrı bir mod
eklenir: `DEMO_SCENARIO=presentation`.

| Dakika (6 dk döngü) | TV 1 gipsokarton | TV 2 gury garyndy |
|---|---|---|
| 0:00–2:30 | Normal | Normal |
| 2:30–3:30 | Kesiji arıza, bütün hat durur | Normal |
| 3:30–4:30 | Toparlanma, hız yüzde 60'tan 100'e | Elewator arıza, bunker sonrası çalışır |
| 4:30–6:00 | Normal | Toparlanma |

- Döngü saatin dakikasından hesaplanır. Aynı anda açılan iki TV aynı şeyi gösterir.
- Bu modda da her değer `SIMULÝASIÝA` etiketlidir.
- Varsayılan mod değişmez. Sunum modu yalnız başlatma dosyasıyla açılır.

## 8. Hata durumları

| Durum | Ekranda görünen | Veri |
|---|---|---|
| Normal | Veri modu rozeti ve son güncelleme saati | Son olay |
| 15 sn olay yok | Sarı şerit: "Baglanyşyk ýok, soňky maglumat HH:MM:SS" | Son değer soluk |
| API kapalı | Kırmızı şerit, sahne durur | Son değer soluk |
| SQL koptu, API açık | Alanlar `ÝOK`, "Maglumat ýok" | Demo değerine dönülmez |
| Görsel yüklenemedi | Çizgi ikon | Etkilenmez |

## 9. İş sırası

| Sıra | İş | Bağımlılık | Görsel gerekir mi |
|---|---|---|---|
| 1 | Rar birleştirme ve commit | Yok | Hayır |
| 2 | S1, S3 düzeltmeleri | 1 | Hayır |
| 3 | TV-B5 `order`, `assetKey`, `kind`, `mode` alanları | 1 | Hayır |
| 4 | TV-B1 `flow` ve yayılım kuralları | 3 | Hayır |
| 5 | TV-B2 ve TV-B4 hat filtreli SSE, `seq`, ping | 1 | Hayır |
| 6 | TV-B3 `GET /api/tv/{tvId}` ve `tv.json` | 3 | Hayır |
| 7 | TV-B6 sunum senaryosu | 4 | Hayır |
| 8 | TV sahne bileşeni, çizgi ikon yedekli | 4, 6 | Hayır |
| 9 | ChatGPT görsellerini yerleştir ve kontrol et | 8 | Evet |
| 10 | TV-B7 testler, iki TV ekran görüntüsü, USB paketi | 9 | Evet |

1'den 8'e kadar olan işler görselleri beklemeden yapılabilir.

## 10. Kabul testleri

| Test | Beklenen |
|---|---|
| Eski uçlar | `/api/snapshot`, `/api/stream` yanıtları eski alanları aynen taşır |
| Sürekli hat yayılımı | Kesiji `FAULT` iken gipsokarton `flow` kayıtlarının hepsi `active:false` |
| Tamponlu hat yayılımı | Elewator `FAULT` iken bunker sonrası `flow` aktif |
| Veri yok | `ÝOK` makinede `status` hiçbir zaman `RUNNING` değil |
| Hat filtresi | `?line=gury-garyndy` yanıtında gipsokarton alarmı yok |
| SSE sırası | Ardışık iki olayda `seq` bir artar |
| TV yapılandırması | `tv-1`, `tv-2` döner; `tv-9` için `404` |
| Sunum modu | Aynı dakikada iki istemci aynı durumu alır |
| Görsel eşleme | 16 anahtar için eksik dosya raporu |
| Salt-okunur | Bütün yeni uçlar yalnız `GET` |
| Ekran | 1920×1080 ve 3840×2160 ekran görüntüsü, konsol hatası yok |
| Uzaktan okuma | Rakam yüksekliği 1080p'de en az 96 px |

## 11. Kararlar (2026-10-20)

| Konu | Karar |
|---|---|
| TV cihazı | Her TV'ye mini PC bağlanır. Animasyon bütçesi bölüm 6'daki gibi kalır |
| IP adresleri | Tasarım onayından sonra. Şimdilik her şey tek API adresi ayarına bağlanır |
| Kagyz bobinasy | Ayrı makine: `gipsokarton-10`, `kind: feed`, formirleme stoluna yan besleme |

### API bağlantı ayarı

- TV sayfası API adresini yalnız bir yerden okur: `IKI-TV-AYARLARI.json`
  içindeki `serverUrl` ve yeni `apiUrl` alanı.
- Sayfa adresinde `?api=http://IP:8010` verilirse o kullanılır. Sahada dosya
  düzenlemeden test etmeye yarar.
- İkisi de yoksa sayfa kendi host'unun 8010 portunu dener.
- Backend `CORS_ORIGINS` ayarı mini PC'lerin adresini kabul eder; varsayılan
  yerel ağdır.

### Yan besleme kuralı

`kind: feed` makinesi ana zincirde değildir. `flow` listesinde
`gipsokarton-10 → gipsokarton-04` olarak görünür. Sürekli hat kuralı ona da
uygulanır: hat durursa bobin de durur.

## 12. Açık sorular

1. Merkez PC ve TV mini PC'lerinin IP adresleri, tasarım onayından sonra.
2. Diğer makine sıraları sahada doğru mu?
3. Sunum modu varsayılan olarak hangi başlatma dosyasında açık olsun?
4. Türkmence metinleri ana dili Türkmence olan biri kontrol edecek mi?
