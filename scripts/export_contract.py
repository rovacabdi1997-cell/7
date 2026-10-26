"""Write the API contract files from the code: docs/api/openapi.json,
docs/api/examples/*.json and docs/api/API-SOZLESMESI.md.

    python scripts/export_contract.py          # write
    python scripts/export_contract.py --check  # exit 1 if a file is out of date (used by tests)

Examples use fixed clocks, so the output is deterministic."""
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "backend"))

from adapters.demo import DemoAdapter  # noqa: E402
from adapters.wincc_sql import WinCCSqlAdapter  # noqa: E402
from app.config import API_VERSION  # noqa: E402
from app.contract import FIELDS  # noqa: E402
from app.main import create_app  # noqa: E402
from app.timeutil import TM_TZ  # noqa: E402

API_DIR = ROOT / "docs" / "api"
EXAMPLE_DIR = API_DIR / "examples"
EXAMPLE_DAY = datetime(2026, 10, 18, tzinfo=TM_TZ)


def _clock(hour: int, minute: int = 0, second: int = 0):
    return lambda: EXAMPLE_DAY.replace(hour=hour, minute=minute, second=second)


class _Rows:
    """Fixed read-only source for the HAKYKY / KONE examples."""

    def __init__(self, rows):
        self.rows, self.fail = rows, False

    def query(self, sql):
        if self.fail:
            raise ConnectionError("baglanyşyk kesildi")
        return self.rows


def _verified(key: str, **extra) -> dict:
    return {"key": key, "status": "VERIFIED", "query": "SELECT v FROM nusga", "candidate": f"Nusga tag: {key}", **extra}


def _kone_example() -> dict:
    """Speed read at 13:00:00, the source drops, the 13:00:30 snapshot still carries it as KONE."""
    source = _Rows([{"v": 31.4}])
    clock = {"now": EXAMPLE_DAY.replace(hour=13)}
    adapter = WinCCSqlAdapter(source, lambda: clock["now"], {"fields": [_verified("gipsokarton.speed")]})
    adapter.snapshot()
    source.fail = True
    clock["now"] += timedelta(seconds=30)
    return adapter.snapshot().model_dump()


def examples() -> dict[str, dict]:
    live = WinCCSqlAdapter(_Rows([{"v": 31.4}]), _clock(13), {"fields": [_verified("gipsokarton.speed")]})
    return {
        "snapshot-simulyasiya.json": DemoAdapter(_clock(13, 7)).snapshot().model_dump(),
        "snapshot-simulyasiya-durus.json": DemoAdapter(_clock(15, 25)).snapshot().model_dump(),
        "snapshot-maglumat-yok.json": WinCCSqlAdapter(None, _clock(13), {"fields": []}).snapshot().model_dump(),
        "snapshot-hakyky-bir-tag.json": live.snapshot().model_dump(),
        "snapshot-kone.json": _kone_example(),
    }


def openapi() -> dict:
    spec = create_app().openapi()
    spec["info"]["x-contract"] = "docs/api/API-SOZLESMESI.md"
    return spec


def contract_md() -> str:
    rows = "\n".join(
        f"| `{key}` | {typ} | {unit or '—'} | {src} | {stale} | {desc} |"
        for key, (typ, unit, src, stale, desc) in FIELDS.items()
    )
    return f"""# API sözleşmesi — sürüm {API_VERSION}

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

Birimde `{{unit}}` hat birimidir (m² veya t), `{{rateUnit}}` hız birimidir (m/min veya t/sag),
`{{nominalUnit}}` saatlik nominaldir (m²/sag veya t/sag).

| Anahtar | Tip | Birim | sourceType | staleAfterSec | Açıklama |
|---|---|---|---|---|---|
{rows}

## Uçlar

| Uç | Yanıt |
|---|---|
| `GET /api/health` | sürüm, `contractVersion`, mod, bağlantı |
| `GET /api/snapshot` | tam `Snapshot` |
| `GET /api/overview` | hatlar (trend ve ekipman hariç), alarm sayıları, vardiya, enerji |
| `GET /api/lines/{{lineId}}` | tek `Line` |
| `GET /api/alarms?state=open\\|all&line=` | `Alarm[]`, `priority` sonra en yeni |
| `GET /api/shift` | `ShiftState` |
| `GET /api/tv/{{tvId}}` | TV yerleşimi ve makine sırası |
| `GET /api/stream?line=` | `text/event-stream`, `event: snapshot`, `retry: 3000`, aradaki `: ping` |

## v1 → v2 kırılan değişiklikler

| v1 | v2 |
|---|---|
| mod `SIMULÝASIÝA`, `ÝOK` | `SIMULYASIYA`, `MAGLUMAT_YOK`; yeni `KONE` |
| `line.status: "RUNNING"` | `line.status: {{value: "RUNNING", mode, sourceTs, ...}}` |
| `line.trend: TrendPoint[]` | `line.trend: {{points: TrendPoint[], unit, mode, ...}}` |
| `line.efficiencyPct` | kaldırıldı; `line.oee.{{availability, performance, quality, oee}}` |
| zaman damgaları +05:00 | UTC `Z` |
| — | yeni: `shiftOutput`, `shiftPlan`, `capacityPct`, `nominalRate`, `productName`, `thicknessMm`, `boardType`, `currentStop`, `alarm.priority`, `snapshot.energy`, `snapshot.connection`, `snapshot.contractVersion`, alan başına `sourceType`, `sourceTs`, `staleAfterSec` |
"""


def outputs() -> dict[Path, str]:
    files = {API_DIR / "openapi.json": json.dumps(openapi(), ensure_ascii=False, indent=2) + "\n",
             API_DIR / "API-SOZLESMESI.md": contract_md()}
    for name, body in examples().items():
        files[EXAMPLE_DIR / name] = json.dumps(body, ensure_ascii=False, indent=2) + "\n"
    return files


def main() -> int:
    check = "--check" in sys.argv
    stale = []
    for path, body in outputs().items():
        if check:
            if not path.is_file() or path.read_text(encoding="utf-8") != body:
                stale.append(path.relative_to(ROOT).as_posix())
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(body, encoding="utf-8", newline="\n")
    if stale:
        print("Köne sözleşme faýllary:", ", ".join(stale))
        return 1
    print("docs/api ýazyldy" if not check else "docs/api täze")
    return 0


if __name__ == "__main__":
    sys.exit(main())
