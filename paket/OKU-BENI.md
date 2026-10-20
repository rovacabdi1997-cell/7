# Türkmen Gips — birleşik v4, 20 Ekim 2026

`SUNUMU-AC.cmd` dosyasını açın. Windows için taşınabilir çalışma ortamı pakette bulunur; kurulum ve internet gerekmez. Sunum, iki TV, akış şeması ve teknik entegrasyon belgesi aynı pakettedir.

- `TV-1-AC.cmd`: gipsokarton; `TV-2-AC.cmd`: kuru karışım. İki ayrı ekrana yerleştirip F11 ile tam ekran açın.
- Varsayılan beyaz-mavi tema. Sunumdaki tema düğmesini veya TV adresinde `?tema=koyu` kullanın.
- `API-ILE-AC.cmd`: API bağlantısı için ayrı sürüm. Önce `API-ADRESI.txt` dosyasını düzenleyin. Mevcut adres yerel geliştirme adresidir; fabrika IP’si değildir. API pakete dahil değildir.
- Çevrimdışı sunum 3024, API görünümü 3025 portunu kullanır. Sunucu salt dosya sunar; PLC’ye yazmaz.

Önümçilik akymy sekmesinde A ve B alt sekmeleri TV’lerle aynı derlenmiş ekranı ve aynı altı dakikalık kaydı kullanır. Değerler **SIMULÝASIÝA** olarak etiketlidir. API görünümünde bağlantı koparsa eski veri işareti gösterilir; gerçek veri varmış gibi devam edilmez.

Gün energiýasy **TASLAMA** modülüdür; kurulu tesis iddiası değildir. Hesap: 1 250 kWp × 1 650 kWh/kWp = 2 062,5 MWh/yıl; 0,50 t/MWh varsayımıyla 1 031,3 t CO₂/yıl. Pasaport tüketimi 1 800 MWh/yıl, oran %114,6; bu oran öz tüketim veya özerklik oranı değildir.

İş kartları **yerel demo** olarak tarayıcıda saklanır ve JSON olarak alınabilir. Backend iş emri entegrasyonu değildir. Ekipman seçimi ve TV sahnesi aynı kimlikleri kullanır.

Gerçek fotoğraflar `site/sunum/photos/`, 8 düzenleme ve 6 şematik güneş görseli `site/sunum/visuals/` altındadır. Düzenlenen çalışan fotoğrafları WIZUALIZASIÝA olarak etiketlenir. Orijinal saha fotoğraflarına dokunulmadı. Yeni pakette eski yapay zekâ videoları ve akış şemasının eski gömülü yapay görselleri bulunmaz. Resmî kampüs renderları ve teknik entegrasyon sunumu korunur.

Kabul testleri ve sınırlar için `KABUL-RAPORU.md`; kaynak değişiklikleri için `KAYNAK-KOD/`; görsel kaynakları ve üretim promptları için `GORSEL-KAYNAKLAR/` klasörüne bakın. Fiziksel TV’de 4 metreden okuma testi sahada yapılmalıdır.
