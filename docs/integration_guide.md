# Gerçek veriye geçiş

Gerçek veriye geçmek için ekran kodu değişmez. Yalnız adaptör yapılandırılır.

## Adımlar

1. **Tag listesini çıkar.** `chengxing.mdf` kopyasından veya WinCC Explorer'dan. Sonucu `docs/sql_analysis.md` belgesine ekle.
2. **Alanı eşle.** `backend/config/tag_mapping.json` içinde ilgili alana `query` yaz. Durumu `CANDIDATE` olarak bırak.
3. **Salt-okunur test et.** Fabrika yetkilisiyle, üretimi etkilemeyen saatte tek sorgu çalıştır. Değeri WinCC ekranındakiyle karşılaştır.
4. **Doğrula.** Değer tutuyorsa durumu `VERIFIED` yap ve kaynağı belgeye yaz.
5. **Modu değiştir.** Backend'i `DATA_SOURCE=wincc` ile başlat.

```bash
set DATA_SOURCE=wincc
set WINCC_CONNECTION_STRING=Provider=WinCCOLEDBProvider.1;Catalog=CC_xxx_R;Data Source=IOP\WINCC
python -m uvicorn app.main:app --app-dir backend --host 0.0.0.0 --port 8010
```

## Sorgu örnekleri

Şablonlar `database/readonly_queries/` altında. İkisi de `CANDIDATE`.

- `wincc_alarms_active.sql`: `ALARMVIEW:SELECT * FROM AlgViewChs ...`
- `wincc_tag_last_value.sql`: `TAG:R,'<Arşiv>\<Tag>',...`

## Gereksinimler

- Backend, WinCC'ye ağdan erişebilen bir Windows makinede çalışmalı.
- `pip install pywin32`
- WinCC Connectivity Pack (OLE DB sağlayıcısı) kurulu olmalı.
- Ayrı, yalnız okuma yetkili bir Windows/SQL kullanıcısı.

## Yarım doğrulama

Bazı alanlar `VERIFIED`, bazıları değilse ekran karışık görünür. Doğrulanmamış kart "MAGLUMAT ÝOK" gösterir, demo değeri göstermez. Bu bilinçli bir tasarım kararıdır.
