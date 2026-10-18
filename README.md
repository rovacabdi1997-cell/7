# Turkmen Gips önümçilik gözegçiligi

Gipsokarton (A bölümi) ve gury garyndy (B bölümi) üretimini izleyen salt-okunur panel. Arayüz Türkmence, belgeler Türkçe.

**Durum:** Demo modunda çalışıyor. Bütün değerler `SIMULÝASIÝA`. Gerçek veri kaynağı henüz doğrulanmadı (0 / 14 alan).

## Hızlı başlangıç

```bash
pip install -r backend/requirements.txt
python -m uvicorn app.main:app --app-dir backend --port 8010
```

```bash
cd frontend
npm install
npm run build
npm run start
```

Panel: `http://localhost:3010`. TV: `http://localhost:3010/tv`. API belgesi: `http://localhost:8010/docs`.

## Yapı

```text
backend/
  app/        FastAPI uygulaması, modeller, ayarlar
  adapters/   demo.py (SIMULÝASIÝA), wincc_sql.py (salt-okunur), readonly_guard.py
  services/   KPI ve vardiya hesapları
  api/        uçlar ve SSE akışı
  config/     plant.json, tag_mapping.json
frontend/
  app/        6 ekran
  components/ kartlar, tablo, SVG grafik
  features/   veri akışı, Türkmence metinler, ekran içerikleri
database/readonly_queries/   WinCC sorgu şablonları (doğrulanmadı)
docs/         analiz, eşleme, mimari, kurulum, güvenlik
tests/        backend testleri
```

## Belgeler

| Belge | İçerik |
|---|---|
| [archive_inventory.md](docs/archive_inventory.md) | `sql cart curt.rar` envanteri |
| [wincc_analysis.md](docs/wincc_analysis.md) | WinCC projesi ve erişim yolları |
| [sql_analysis.md](docs/sql_analysis.md) | Veritabanları, neden henüz okunamadı |
| [tag_mapping.md](docs/tag_mapping.md) | Ekran alanı → kaynak eşlemesi |
| [dashboard_architecture.md](docs/dashboard_architecture.md) | Mimari ve API |
| [integration_guide.md](docs/integration_guide.md) | Gerçek veriye geçiş adımları |
| [security.md](docs/security.md) | Kontroller ve bilinen riskler |
| [deployment.md](docs/deployment.md) | Kurulum ve TV kiosk |
| [test_report.md](docs/test_report.md) | Test sonuçları |

## Kurallar

- PLC veya SCADA'ya yazma yok. API yalnız `GET`.
- Doğrulanmamış alan gerçek veri gibi gösterilmez.
- Panelde şirket logosu yok.
