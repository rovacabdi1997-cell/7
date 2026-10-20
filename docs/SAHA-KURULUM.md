# Saha kurulumu (IP'ler geldiğinde)

1. Paketi merkez bilgisayara kopyala. `SAHA-AYARLARI.json` aç:
   `{"merkezIp":"<merkez IP>","sunumPort":3024,"apiPort":8010,"veriKaynagy":"kayit","tema":"acik"}`
2. Merkez PC: `MERKEZ-BASLAT.cmd` (site) ve gerçek veri için `API-BASLAT.cmd` (Python gerekir).
3. TV PC'ler: `merkezIp` değerini merkezin IP'si yap; `TV-1-AC.cmd` / `TV-2-AC.cmd`.
4. Gerçek veri: `veriKaynagy` = `api`. WinCC için `WINCC_CONNECTION_STRING` ortam değişkeni tanımla.
5. Kontrol: `KONTROL.cmd`. Açılışta otomatik başlatma: `OTOMATIK-BASLAT.ps1 -Ekran merkez|tv1|tv2` (kaldırmak için `-Kaldir`).

Not: gerçek PLC tag listesi gelene kadar tüm değerler SİMULÝASIÝA'dır.
