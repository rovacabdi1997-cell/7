"""Single source of the per-field contract (TAM-PLAN-v9 §24).

Adapters build every value through `metric()` / `text()` so unit, sourceType and
staleAfterSec always come from this table. scripts/export_contract.py writes the
same table into docs/api/API-SOZLESMESI.md. A field missing here cannot be built.

`unit` may name a line config key in braces: {unit} = m² | t, {rateUnit} = m/min | t/sag."""
from datetime import datetime
from typing import Optional

from app.models import DataMode, Metric, TextValue

# key: (type, unit, sourceType, staleAfterSec, description)
FIELDS: dict[str, tuple[str, str, str, int, str]] = {
    "line.status": ("RunStatus", "", "PLC_TAG", 15, "Hat çalışıyor / durdu / arıza. Hat 1 ve hat 2 ayrı."),
    "line.speed": ("number", "{rateUnit}", "PLC_TAG", 15, "Anlık hat hızı."),
    "line.outputToday": ("number", "{unit}", "PLC_TAG", 60, "Üretim günü başından üretim sayacı."),
    "line.outputMonth": ("number", "{unit}", "CALCULATED", 60, "Ay başından günlük sayaçların toplamı."),
    "line.planToday": ("number", "{unit}", "MANUAL", 86400, "Günlük hedef."),
    "line.planToDate": ("number", "{unit}", "CALCULATED", 86400, "Günlük hedefin şu ana kadarki payı."),
    "line.shiftOutput": ("number", "{unit}", "PLC_TAG", 60, "Aktif vardiya başından üretim. Günlükten ayrı."),
    "line.shiftPlan": ("number", "{unit}", "MANUAL", 86400, "Aktif vardiya hedefi. Günlük hedeften ayrı."),
    "line.fulfilmentPct": ("number", "%", "CALCULATED", 60, "outputToday ÷ planToDate × 100."),
    "line.capacityPct": ("number", "%", "CALCULATED", 15, "Anlık üretim hızı ÷ nominal kapasite × 100."),
    "line.nominalRate": ("number", "{nominalUnit}", "CONFIG", 86400, "Nominal kapasite. Kaynak Sanjin teklifi, tesis teyidi yok."),
    "line.nominalSpeed": ("number", "{rateUnit}", "CONFIG", 86400, "Nominal hat hızı, hız ile aynı birimde. Gipsokarton: nominalRate ÷ levha eni ÷ 60. Kaynak Sanjin teklifi."),
    "line.oee.availability": ("number", "%", "CALCULATED", 60, "Kullanılabilirlik: çalışma süresi ÷ planlı süre × 100."),
    "line.oee.performance": ("number", "%", "CALCULATED", 60, "Performans: üretim ÷ (nominal × çalışma süresi) × 100."),
    "line.oee.quality": ("number", "%", "MANUAL", 3600, "Kalite: sağlam ürün ÷ toplam ürün × 100. Kalite ölçümü gelene kadar kaynak yok."),
    "line.oee.oee": ("number", "%", "CALCULATED", 60, "availability × performance × quality ÷ 10000."),
    "line.productName": ("string", "", "MANUAL", 86400, "Üretilen ürün (iş emrinden)."),
    "line.thicknessMm": ("number", "mm", "MANUAL", 86400, "Levha kalınlığı, 9,5 veya 12,5. Yalnız gipsokarton."),
    "line.boardType": ("string", "", "MANUAL", 86400, "Levha tipi. Yalnız gipsokarton."),
    "line.bagsToday": ("number", "halta", "PLC_TAG", 60, "Günlük torba sayısı. Yalnız gury garyndy."),
    "line.stopsToday": ("number", "san", "CALCULATED", 60, "Bugünkü duruş sayısı."),
    "line.stopMinutesToday": ("number", "min", "CALCULATED", 60, "Bugünkü toplam duruş süresi."),
    "line.errorsToday": ("number", "san", "CALCULATED", 60, "Bugünkü arıza ve uyarı sayısı."),
    "line.currentStop": ("CurrentStop", "", "PLC_TAG", 15, "Şu anki duruş: başlangıç, süre, neden. Günlük toplamdan türetilmez."),
    "line.trend": ("HourlySeries", "{unit}", "CALCULATED", 3600, "Saatlik üretim serisi ve saatlik hedef."),
    "energy.powerKw": ("number", "kW", "PLC_TAG", 15, "Anlık güç. Sayaç kaynağı yok."),
    "energy.energyKwhToday": ("number", "kWh", "PLC_TAG", 300, "Üretim günü enerjisi. Anlık güçten ayrı."),
    "shift.staffCount": ("number", "adam", "MANUAL", 86400, "Vardiyadaki kişi sayısı."),
}


def spec(key: str) -> tuple[str, str, str, int, str]:
    return FIELDS[key]


def unit_for(key: str, line_cfg: Optional[dict] = None) -> str:
    unit = FIELDS[key][1]
    if unit.startswith("{") and line_cfg is not None:
        name = unit[1:-1]
        return nominal_unit(line_cfg) if name == "nominalUnit" else line_cfg[name]
    return unit


def nominal_unit(line_cfg: dict) -> str:
    # nominalPerHour is per hour of output: m²/sag for board, t/sag for dry mix.
    return f"{line_cfg['unit']}/sag"


def meta(key: str, mode: DataMode, source: str, source_ts: Optional[datetime]) -> dict:
    _, _, source_type, stale, _ = FIELDS[key]
    return {"mode": mode, "source": source, "sourceType": source_type,
            "sourceTs": source_ts, "staleAfterSec": stale}


def metric(key: str, value: Optional[float], mode: DataMode, source: str,
           source_ts: Optional[datetime], line_cfg: Optional[dict] = None) -> Metric:
    if value is None:
        mode = "MAGLUMAT_YOK"
    return Metric(value=None if value is None else round(float(value), 2),
                  unit=unit_for(key, line_cfg), **meta(key, mode, source, source_ts))


def text(key: str, value: Optional[str], mode: DataMode, source: str,
         source_ts: Optional[datetime]) -> TextValue:
    if value is None:
        mode = "MAGLUMAT_YOK"
    return TextValue(value=value, **meta(key, mode, source, source_ts))


def empty(key: str, source: str, line_cfg: Optional[dict] = None) -> Metric:
    """A field with no data: value None, never 0."""
    return metric(key, None, "MAGLUMAT_YOK", source, None, line_cfg)
