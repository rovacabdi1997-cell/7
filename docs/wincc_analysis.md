# WinCC analizi

## Proje

| Bilgi | Değer | Kaynak |
|---|---|---|
| Ürün | SIMATIC WinCC V7.3 | Saha fotoğrafları |
| Proje | `chengxing` (成型, şekillendirme) | `chengxing.MCP` |
| Aktif kopya | `二横wincc/chengxing` ("ikinci hat") | `ProjectOpened.lck` |
| İstasyonlar | `IOP`, `CPI` | Alarm arşivi dosya adları |
| Ekranlar | `GraCS/NewPdl0.Pdl`, `NewPdl1.Pdl` (yalnız CPI) | Arşiv |
| Dil | Çince (`PRT/chs`), İngilizce rapor şablonları | Arşiv |
| Redundancy | Kapalı | `UALogFile.txt` |

## Hangi hatta ait

Ekran fotoğrafında hat hızı (7.1 m/min), motor frekansları, sıcaklıklar ve konveyörler görüldü. Bu, **A bölümü gipsokarton** hattının şekillendirme ve kurutma kısmına uyuyor. Kesin eşleme tag listesi okununca doğrulanacak.

**B bölümü gury garyndy** için arşivde WinCC projesi yok. O bölümün kontrol sistemi ayrıca araştırılmalı.

## Veri erişim seçenekleri

| Yol | Avantaj | Dezavantaj |
|---|---|---|
| **OPC UA** (`opc.tcp://<PC>:4862`) | WinCC'de zaten açık, lisans çoğunlukla mevcut, canlı değer | Şu an güvenliksiz ayarlı; ayrı kullanıcı ve şifreleme gerekir |
| WinCC OLE DB (Connectivity Pack) | Alarm ve arşiv geçmişi | Ek lisans gerekebilir, Windows + pywin32 |
| SQL'e doğrudan sorgu | Basit | Arşiv verisi sıkıştırılmış olabilir; Siemens desteklemez |

**Öneri:** Canlı değerler için OPC UA, alarm geçmişi için OLE DB. Backend her ikisini salt-okunur adaptör olarak ekleyebilir. Şu an OLE DB adaptör iskeleti hazır (`backend/adapters/wincc_sql.py`).

## Açık işler

1. `chengxing.mdf` içinden tag listesini çıkar.
2. Fabrikada OPC UA sunucusunun çalıştığını ve portu doğrula.
3. Gury garyndy bölümünün kontrol sistemini tespit et.
4. Tag Logging'in canlı sistemde aktif olup olmadığını kontrol et.
