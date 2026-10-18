# Veri eşleme

Tek doğruluk kaynağı: `backend/config/tag_mapping.json`. Bu tablo onun özetidir. API'de `GET /api/mapping` aynı içeriği döner.

Durum anlamları:

- **VERIFIED**: Kaynak salt-okunur testle doğrulandı. Yalnız bu alanlar gerçek veri olarak okunur.
- **CANDIDATE**: Olası kaynak var, tag veya tablo adı doğrulanmadı.
- **NO_SOURCE**: Mevcut arşivde kaynak bulunamadı.

| Ekran alanı | Kaynak türü | Aday kaynak | Birim | Güncelleme | Durum |
|---|---|---|---|---|---|
| Gipsokarton: häzirki tizlik | WinCC tag | chengxing projesi, ekranda görüldü | m/min | Doğrulanacak | CANDIDATE |
| Gipsokarton: öndürilen mukdar | WinCC tag | Sayaç tag'i olabilir | m² | Doğrulanacak | CANDIDATE |
| Gipsokarton: aý başyndan | Hesaplanan | Günlük sayaçtan | m² | Doğrulanacak | CANDIDATE |
| Gipsokarton: meýilnama | Elle giriş | WinCC'de yok | m² | Günlük | NO_SOURCE |
| Gipsokarton: liniýa ýagdaýy | WinCC tag | Motor çalışma sinyalleri | durum | Doğrulanacak | CANDIDATE |
| Gipsokarton: durmalar | Hesaplanan | Durum tag'lerinden | adet | Doğrulanacak | CANDIDATE |
| Gipsokarton: ýalňyşlyklar | WinCC alarm | Alarm Logging | adet | Doğrulanacak | CANDIDATE |
| Gury garyndy: önüm mukdary | Bilinmiyor | Arşivde proje yok | t | — | NO_SOURCE |
| Gury garyndy: aý başyndan | Bilinmiyor | — | t | — | NO_SOURCE |
| Gury garyndy: gaplanan halta | Bilinmiyor | Paketleme makinesi sayacı olabilir | adet | — | NO_SOURCE |
| Gury garyndy: meýilnama | Elle giriş | — | t | Günlük | NO_SOURCE |
| Gury garyndy: enjam ýagdaýy | Bilinmiyor | — | durum | — | NO_SOURCE |
| Aktiw duýduryşlar | WinCC alarm | OLE DB `ALARMVIEW` şablonu | kayıt | Doğrulanacak | CANDIDATE |
| Işgärleriň sany | Bilinmiyor | WinCC'de yok | kişi | — | NO_SOURCE |

**Doğrulanmış alan sayısı: 0.** Bütün ekranlar şu an `SIMULÝASIÝA` modunda çalışır.

Ek notlar:

- Kapasite rakamları (2 500 m²/saat, 25 t/saat) Sanjin teklifinden geliyor. Fabrika onaylı değil.
- Vardiya düzeni (`plant.json`) varsayımdır, `SIMULÝASIÝA` olarak işaretli.
- `alarms.active` kolon adları (`MsgNr`, `Text1`, `DateTime` vb.) ilk testte doğrulanmalı.
