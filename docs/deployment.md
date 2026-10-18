# Kurulum

## Gereksinimler

- Windows 10/11
- Python 3.11+ (test edildi: 3.14)
- Node.js 20+ (test edildi: 24)

## Backend

```bash
pip install -r backend/requirements.txt
python -m uvicorn app.main:app --app-dir backend --host 0.0.0.0 --port 8010
```

Ortam değişkenleri:

| Değişken | Varsayılan | Açıklama |
|---|---|---|
| `DATA_SOURCE` | `demo` | `demo` veya `wincc` |
| `REFRESH_SECONDS` | `5` | SSE yenileme aralığı |
| `WINCC_CONNECTION_STRING` | boş | Yalnız `wincc` modunda |
| `CORS_ORIGINS` | `http://localhost:3010,...` | Arayüz adresleri |

## Frontend

```bash
cd frontend
npm install
npm run build
npm run start
```

Arayüz `http://<sunucu>:3010` adresinde açılır. API adresini sayfanın kendi sunucusundan `:8010` olarak bulur. Farklıysa build öncesi `NEXT_PUBLIC_API_URL` verin.

İnternetsiz makinede `npm install` çalışmaz. `node_modules` klasörünü internetli makinede hazırlayıp kopyalayın.

## TV kiosk

86" ve 100" TV'ler için Chrome veya Edge kiosk modu:

```bash
msedge --kiosk "http://<sunucu>:3010/tv" --edge-kiosk-type=fullscreen --no-first-run
```

- Slayt 15 saniyede bir değişir. Süre için `?interval=20`.
- Tek slayt göstermek için `?slide=0` (genel), `1` (gipsokarton), `2` (gury garyndy), `3` (alarmlar).
- 1920×1080 ve 3840×2160 çözünürlükte taşma olmadan test edildi.
- Kiosk dışı tarayıcıda "Doly ekran" düğmesi tam ekrana geçer.

## Testler

```bash
python -m pytest tests
npm --prefix frontend run typecheck
npm --prefix frontend run check:tk
```
