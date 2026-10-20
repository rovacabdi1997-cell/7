# TV tasarımı ve SQL bağlantı akışı

## Tasarım kararı

Yeni ekranlar mavi-beyaz teknik infografik sistemiyle hazırlanmıştır. Makine
ikonları ve bağlantı çizgileri üretim sırasını anlatır; KPI panoları TV'den
uzaktan okunacak büyüklüktedir. Başka firmaya ait referans yalnız içerik
yoğunluğu ve okunabilirlik örneği olarak kullanılmış, marka ve metinler
kopyalanmamıştır.

Gipsokarton TV ekranında yalnız mevcut veri sözleşmesindeki alanlar gösterilir:

- hat hızı,
- günlük plan,
- şu ana kadarki plan,
- günlük üretim,
- plan farkı,
- verimlilik,
- duruş süresi ve aktif alarm sayısı.

Teorik/yıllık kapasite gibi doğrulanmamış alanlar gerçek değer gibi ekrana
konulmamıştır.

## Birbirine bağlı veri akışı

```text
WinCC / SQL (salt-okunur)
        ↓
WinCCSqlAdapter
        ↓
tek Snapshot modeli
        ↓
GET /api/stream (SSE, varsayılan 5 sn)
        ↓
panel + hat ekranları + TV kiosk
```

Bütün ekranlar aynı `Snapshot.timestamp` zamanını, aynı liniýa kimliğini ve
aynı enjam durumunu kullanır. Böylece TV'deki KPI, proses akışı ve alarm aynı
veri anına aittir.

## İki çalışma modu

1. `TV-BASLAT.bat`: internet ve kurulum gerektirmeyen deterministik sunum
   sürümü. Bütün değerler `SIMULÝASIÝA` etiketi taşır.
2. `CANLI-SQL-TV-BASLAT.bat`: `site-live` arayüzünü ve port 8010'daki API'yi
   kullanır. `SQL-AYARLARI.bat` olmadan başlamaz. SQL bağlantısı kesilirse demo
   değerine dönmez; ekranda bağlantı kaybını gösterir.

## Saha devreye alma kabul koşulları

- WinCC Connectivity Pack ve salt-okunur kullanıcı hazır olmalı.
- Bağlantı dizesi yetkili saha personeli tarafından doğrulanmalı.
- `tag_mapping.json` içindeki aday alanlar tek tek test edilip `VERIFIED`
  yapılmalı.
- TV bilgisayarı sunucunun 3010 ve 8010 portlarına erişebilmeli.
- İlk vardiyada TV KPI'ları WinCC ekranı ve vardiya raporuyla karşılaştırılmalı.

Bu pakette gerçek saha erişim bilgisi olmadığı için canlı SQL doğrulaması
yapılmamıştır; frontend'in `http://<aynı-host>:8010/api/stream` isteği ve
bağlantı kaybı davranışı test edilmiştir.
