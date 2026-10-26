# API sözleşmesi — sürüm 2.0.0

Bu dosya `scripts/export_contract.py` ile koddan üretilir. Elle düzenlenmez.
Şema: [openapi.json](openapi.json). Örnekler: [examples/](examples/).
Kaynak plan: `TAM-PLAN-v9.md` bölüm 7, 24, 29.

## Genel kurallar

- Her değer alanı şu altı bilgiyi taşır: ad (anahtar), tip, `unit`, `source` + `sourceType`, `mode`, `staleAfterSec`.
- `sourceTs`: değerin kaynakta üretildiği an. ISO 8601 UTC, `Z` ile biter. Ekran Asia/Ashgabat saatiyle gösterir.
- Eksik değer `value: null` ve `mode: MAGLUMAT_YOK` olur. Asla 0 yazılmaz.
- Sözleşmede olmayan alan frontend'de varsayılmaz.

## Veri modu kodları

API ASCII kod gönderir. Ekran Türkmence metni gösterir.

| Kod | Ekran metni | Anlamı |
|---|---|---|
| `HAKYKY` | Hakyky | Canlı kaynaktan, yaş eşiği içinde |
| `SIMULYASIYA` | Simulýasiýa | Test verisi veya tesis teyidi olmayan sabit değer |
| `KONE` | Köne | Gerçek değer, `staleAfterSec` aşıldı. Değer korunur, soluk gösterilir, yeşil kalmaz |
| `MAGLUMAT_YOK` | Maglumat ýok | Hiç değer gelmedi. `value` null |

KONE kuralı sunucuda uygulanır: `HAKYKY` bir alanın `snapshot.timestamp − sourceTs` farkı
`staleAfterSec` değerini aşarsa alan `KONE` olur. `sourceTs` olmayan `HAKYKY` alan da `KONE` olur.
Akış koparsa istemci aynı kuralı kendi saatiyle uygular: son gelen değerlerin yaşı eşiği aşınca `KONE` gösterir.
Sessiz demo geçişi yoktur.

`Line.mode` ve `Snapshot.dataMode` alanlardan özetlenir: `KONE` > `HAKYKY` > `SIMULYASIYA` > `MAGLUMAT_YOK`.
`sourceType: CONFIG` alanları (nominal kapasite) özete girmez.

## sourceType kodları

| Kod | Anlamı |
|---|---|
| `PLC_TAG` | PLC / WinCC tag'i |
| `CALCULATED` | Başka alanlardan hesaplanır |
| `MANUAL` | Kullanıcı veya iş emri girer |
| `CONFIG` | `plant.json` sabiti (ör. Sanjin nominal kapasitesi) |

`sourceType` alanın tesise bağlandığında nereden geleceğini söyler. Şu an bağlı olup olmadığını `mode` söyler.

## Bağlantı

`Snapshot.connection.state`: `ONLINE` | `OFFLINE` | `NOT_CONFIGURED` | `SIMULATED`.
`connection.lastOkTs`: son başarılı okuma, UTC. Hiç okuma yoksa null.

## Alan tablosu

Birimde `{unit}` hat birimidir (m² veya t), `{rateUnit}` hız birimidir (m/min veya t/sag),
`{nominalUnit}` saatlik nominaldir (m²/sag veya t/sag).

| Anahtar | Tip | Birim | sourceType | staleAfterSec | Açıklama |
|---|---|---|---|---|---|
| `line.status` | RunStatus | — | PLC_TAG | 15 | Hat çalışıyor / durdu / arıza. Hat 1 ve hat 2 ayrı. |
| `line.speed` | number | {rateUnit} | PLC_TAG | 15 | Anlık hat hızı. |
| `line.outputToday` | number | {unit} | PLC_TAG | 60 | Üretim günü başından üretim sayacı. |
| `line.outputMonth` | number | {unit} | CALCULATED | 60 | Ay başından günlük sayaçların toplamı. |
| `line.planToday` | number | {unit} | MANUAL | 86400 | Günlük hedef. |
| `line.planToDate` | number | {unit} | CALCULATED | 86400 | Günlük hedefin şu ana kadarki payı. |
| `line.shiftOutput` | number | {unit} | PLC_TAG | 60 | Aktif vardiya başından üretim. Günlükten ayrı. |
| `line.shiftPlan` | number | {unit} | MANUAL | 86400 | Aktif vardiya hedefi. Günlük hedeften ayrı. |
| `line.fulfilmentPct` | number | % | CALCULATED | 60 | outputToday ÷ planToDate × 100. |
| `line.capacityPct` | number | % | CALCULATED | 15 | Anlık üretim hızı ÷ nominal kapasite × 100. |
| `line.nominalRate` | number | {nominalUnit} | CONFIG | 86400 | Nominal kapasite. Kaynak Sanjin teklifi, tesis teyidi yok. |
| `line.oee.availability` | number | % | CALCULATED | 60 | Kullanılabilirlik: çalışma süresi ÷ planlı süre × 100. |
| `line.oee.performance` | number | % | CALCULATED | 60 | Performans: üretim ÷ (nominal × çalışma süresi) × 100. |
| `line.oee.quality` | number | % | MANUAL | 3600 | Kalite: sağlam ürün ÷ toplam ürün × 100. Kalite ölçümü gelene kadar kaynak yok. |
| `line.oee.oee` | number | % | CALCULATED | 60 | availability × performance × quality ÷ 10000. |
| `line.productName` | string | — | MANUAL | 86400 | Üretilen ürün (iş emrinden). |
| `line.thicknessMm` | number | mm | MANUAL | 86400 | Levha kalınlığı, 9,5 veya 12,5. Yalnız gipsokarton. |
| `line.boardType` | string | — | MANUAL | 86400 | Levha tipi. Yalnız gipsokarton. |
| `line.bagsToday` | number | halta | PLC_TAG | 60 | Günlük torba sayısı. Yalnız gury garyndy. |
| `line.stopsToday` | number | san | CALCULATED | 60 | Bugünkü duruş sayısı. |
| `line.stopMinutesToday` | number | min | CALCULATED | 60 | Bugünkü toplam duruş süresi. |
| `line.errorsToday` | number | san | CALCULATED | 60 | Bugünkü arıza ve uyarı sayısı. |
| `line.currentStop` | CurrentStop | — | PLC_TAG | 15 | Şu anki duruş: başlangıç, süre, neden. Günlük toplamdan türetilmez. |
| `line.trend` | HourlySeries | {unit} | CALCULATED | 3600 | Saatlik üretim serisi ve saatlik hedef. |
| `energy.powerKw` | number | kW | PLC_TAG | 15 | Anlık güç. Sayaç kaynağı yok. |
| `energy.energyKwhToday` | number | kWh | PLC_TAG | 300 | Üretim günü enerjisi. Anlık güçten ayrı. |
| `shift.staffCount` | number | adam | MANUAL | 86400 | Vardiyadaki kişi sayısı. |

## Uçlar

| Uç | Yanıt |
|---|---|
| `GET /api/health` | sürüm, `contractVersion`, mod, bağlantı |
| `GET /api/snapshot` | tam `Snapshot` |
| `GET /api/overview` | hatlar (trend ve ekipman hariç), alarm sayıları, vardiya, enerji |
| `GET /api/lines/{lineId}` | tek `Line` |
| `GET /api/alarms?state=open\|all&line=` | `Alarm[]`, `priority` sonra en yeni |
| `GET /api/shift` | `ShiftState` |
| `GET /api/tv/{tvId}` | TV yerleşimi ve makine sırası |
| `GET /api/stream?line=` | `text/event-stream`, `event: snapshot`, `retry: 3000`, aradaki `: ping` |

## v1 → v2 kırılan değişiklikler

| v1 | v2 |
|---|---|
| mod `SIMULÝASIÝA`, `ÝOK` | `SIMULYASIYA`, `MAGLUMAT_YOK`; yeni `KONE` |
| `line.status: "RUNNING"` | `line.status: {value: "RUNNING", mode, sourceTs, ...}` |
| `line.trend: TrendPoint[]` | `line.trend: {points: TrendPoint[], unit, mode, ...}` |
| `line.efficiencyPct` | kaldırıldı; `line.oee.{availability, performance, quality, oee}` |
| zaman damgaları +05:00 | UTC `Z` |
| — | yeni: `shiftOutput`, `shiftPlan`, `capacityPct`, `nominalRate`, `productName`, `thicknessMm`, `boardType`, `currentStop`, `alarm.priority`, `snapshot.energy`, `snapshot.connection`, `snapshot.contractVersion`, alan başına `sourceType`, `sourceTs`, `staleAfterSec` |
