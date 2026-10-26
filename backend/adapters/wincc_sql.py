"""Read-only WinCC adapter.

Reads only fields whose status is VERIFIED in config/tag_mapping.json. Every
other field comes back empty with mode MAGLUMAT_YOK. It never falls back to demo
values, so real and simulated data cannot mix on one screen.

A failed read returns the last good value with its original sourceTs, so the
freshness check turns it into KONE once it is older than its staleAfterSec.
"""
from datetime import datetime
from typing import Any, Callable, Optional, Protocol

from adapters.readonly_guard import assert_read_only
from app.config import API_VERSION, plant_config, tag_mapping
from app.contract import empty, meta, metric, text
from app.models import (PRIORITY, Alarm, Connection, Energy, HourlySeries, Line, Metric, Oee, ShiftInfo,
                        ShiftState, Snapshot, StatusValue, TextValue)
from app.timeutil import TM_TZ, now_tm, production_day_start
from services.freshness import mark_stale
from services.flow import build_equipment, build_flow, machine_states, resolve_asset_key
from services.kpi import nominal_speed, pct
from services.shifts import shift_state

# Numeric line fields read straight from a verified source: mapping key suffix -> contract key.
LINE_METRICS = {
    "speed": "line.speed", "outputToday": "line.outputToday", "outputMonth": "line.outputMonth",
    "planToday": "line.planToday", "shiftOutput": "line.shiftOutput", "shiftPlan": "line.shiftPlan",
    "thicknessMm": "line.thicknessMm", "bagsToday": "line.bagsToday", "stopsToday": "line.stopsToday",
    "stopMinutesToday": "line.stopMinutesToday", "errorsToday": "line.errorsToday",
}
SEVERITY = {"CRITICAL": "CRITICAL", "WARNING": "WARNING", "INFO": "INFO"}
STATE = {"ACTIVE": "ACTIVE", "ACKNOWLEDGED": "ACKNOWLEDGED", "CLEARED": "CLEARED"}
NO_SOURCE = "Çeşme tassyklanmadyk"


class QueryExecutor(Protocol):
    def query(self, sql: str) -> list[dict[str, Any]]: ...


class AdoExecutor:
    """WinCC OLE DB provider through ADO. Needs pywin32 and the WinCC
    Connectivity Pack on the machine that runs the backend."""

    def __init__(self, connection_string: str) -> None:
        if not connection_string:
            raise ValueError("WINCC_CONNECTION_STRING is not set")
        self.connection_string = connection_string

    def query(self, sql: str) -> list[dict[str, Any]]:
        sql = assert_read_only(sql)
        import win32com.client  # optional dependency, Windows only

        conn = win32com.client.Dispatch("ADODB.Connection")
        conn.Mode = 1  # adModeRead
        conn.Open(self.connection_string)
        try:
            rs = win32com.client.Dispatch("ADODB.Recordset")
            rs.Open(sql, conn, 0, 1)  # adOpenForwardOnly, adLockReadOnly
            names = [rs.Fields.Item(i).Name for i in range(rs.Fields.Count)]
            rows = []
            while not rs.EOF:
                rows.append({n: rs.Fields.Item(n).Value for n in names})
                rs.MoveNext()
            rs.Close()
            return rows
        finally:
            conn.Close()


class GuardedExecutor:
    """Wraps any executor so the read-only check cannot be skipped."""

    def __init__(self, inner: QueryExecutor) -> None:
        self.inner = inner

    def query(self, sql: str) -> list[dict[str, Any]]:
        return self.inner.query(assert_read_only(sql))


def _aware(value: datetime) -> datetime:
    return value if value.tzinfo else value.replace(tzinfo=TM_TZ)


class WinCCSqlAdapter:
    name = "wincc"

    def __init__(self, executor: Optional[QueryExecutor], clock: Callable[[], datetime] = now_tm,
                 mapping: Optional[dict] = None) -> None:
        self.executor = GuardedExecutor(executor) if executor else None
        self.clock = clock
        self.cfg = plant_config()
        fields = (mapping or tag_mapping())["fields"]
        self.verified = {f["key"]: f for f in fields if f.get("status") == "VERIFIED" and f.get("query")}
        self.notes: list[str] = []
        self.read_any = False
        self.failed_any = False
        self.last_ok: Optional[datetime] = None
        # Last good raw read per mapping key: (value, sourceTs, source text).
        self._last: dict[str, tuple[Any, datetime, str]] = {}

    def _raw(self, key: str, now: datetime) -> tuple[Any, Optional[datetime], str, bool]:
        """(value, sourceTs, source, fresh). fresh is False when the value is a cached one."""
        field = self.verified.get(key)
        if not field:
            return None, None, NO_SOURCE, False
        if not self.executor:
            return None, None, "WinCC baglanyşygy sazlanmadyk", False
        source = field.get("candidate", key)
        try:
            rows = self.executor.query(field["query"])
        except Exception as exc:  # report the failure, never invent a value
            self.failed_any = True
            self.notes.append(f"{key}: okap bolmady ({type(exc).__name__})")
            if key in self._last:
                value, ts, src = self._last[key]
                return value, ts, f"{src}; soňky üstünlikli okalyş", False
            return None, None, "Okamak ýalňyşlygy", False
        row = rows[0] if rows else {}
        value = next(iter(row.values()), None)
        if value is None:
            return None, None, source, False
        # A `sourceTs` column carries the tag's own time stamp; otherwise the read time is used.
        ts = row.get("sourceTs")
        ts = _aware(ts) if isinstance(ts, datetime) else now
        self.read_any = True
        self.last_ok = now
        self._last[key] = (value, ts, source)
        return value, ts, source, True

    def _metric(self, key: str, contract_key: str, now: datetime, line_cfg: Optional[dict] = None) -> Metric:
        value, ts, source, _ = self._raw(key, now)
        if value is None:
            return empty(contract_key, source, line_cfg)
        return metric(contract_key, float(value), "HAKYKY", source, ts, line_cfg)

    def _text(self, key: str, contract_key: str, now: datetime) -> TextValue:
        value, ts, source, _ = self._raw(key, now)
        return text(contract_key, None if value is None else str(value),
                    "HAKYKY" if value is not None else "MAGLUMAT_YOK", source, ts)

    def _status(self, line_id: str, now: datetime) -> StatusValue:
        """Line state from a verified tag. Raw values map only through the field's own
        `values` table (e.g. {"1": "RUNNING", "0": "STOPPED"}); anything else is UNKNOWN."""
        key = f"{line_id}.status"
        value, ts, source, _ = self._raw(key, now)
        table = self.verified.get(key, {}).get("values", {})
        if value is None:
            return StatusValue(value="UNKNOWN", **meta("line.status", "MAGLUMAT_YOK", source, None))
        raw = str(int(value)) if isinstance(value, (int, float)) else str(value)
        return StatusValue(value=table.get(raw, "UNKNOWN"), **meta("line.status", "HAKYKY", source, ts))

    def _line(self, line_id: str, now: datetime, day_start: datetime) -> Line:
        cfg = self.cfg["lines"][line_id]
        is_board = line_id == "gipsokarton"
        m = {name: self._metric(f"{line_id}.{name}", key, now, cfg) for name, key in LINE_METRICS.items()}
        none = "Hasaplamak üçin maglumat ýok"

        plan_to_date = empty("line.planToDate", NO_SOURCE, cfg)
        if m["planToday"].value is not None:
            elapsed = (now - day_start).total_seconds() / 60
            plan_to_date = metric("line.planToDate", m["planToday"].value * elapsed / (24 * 60),
                                  m["planToday"].mode, "planToday × geçen wagt", m["planToday"].sourceTs, cfg)
        fulfil = empty("line.fulfilmentPct", none)
        if m["outputToday"].value is not None and plan_to_date.value:
            fulfil = metric("line.fulfilmentPct", pct(m["outputToday"].value, plan_to_date.value), "HAKYKY",
                            "outputToday / planToDate", min(m["outputToday"].sourceTs, plan_to_date.sourceTs))

        # No verified per-machine tags yet: every machine is UNKNOWN / MAGLUMAT_YOK.
        equipment = build_equipment(line_id, cfg, machine_states(cfg, None, "MAGLUMAT_YOK"), "MAGLUMAT_YOK")
        return Line(
            id=line_id, name=cfg["name"], section=cfg["section"], unit=cfg["unit"], rateUnit=cfg["rateUnit"],
            status=self._status(line_id, now), mode="MAGLUMAT_YOK",
            speed=m["speed"], outputToday=m["outputToday"], outputMonth=m["outputMonth"],
            planToday=m["planToday"], planToDate=plan_to_date,
            shiftOutput=m["shiftOutput"], shiftPlan=m["shiftPlan"],
            fulfilmentPct=fulfil,
            capacityPct=empty("line.capacityPct", none),
            # A supplier figure from plant.json, not a plant reading: never HAKYKY.
            nominalRate=metric("line.nominalRate", cfg["nominalPerHour"], "SIMULYASIYA", cfg["nominalSource"],
                               now, cfg),
            nominalSpeed=metric("line.nominalSpeed", nominal_speed(cfg), "SIMULYASIYA", cfg["nominalSource"],
                                now, cfg),
            oee=Oee(availability=empty("line.oee.availability", none),
                    performance=empty("line.oee.performance", none),
                    quality=empty("line.oee.quality", NO_SOURCE),
                    oee=empty("line.oee.oee", none)),
            productName=self._text(f"{line_id}.productName", "line.productName", now),
            thicknessMm=m["thicknessMm"] if is_board else None,
            boardType=self._text(f"{line_id}.boardType", "line.boardType", now) if is_board else None,
            bagsToday=None if is_board else m["bagsToday"],
            stopsToday=m["stopsToday"], stopMinutesToday=m["stopMinutesToday"], errorsToday=m["errorsToday"],
            currentStop=None,
            trend=HourlySeries(unit=cfg["unit"], points=[], **meta("line.trend", "MAGLUMAT_YOK", NO_SOURCE, None)),
            equipment=equipment, flow=build_flow(equipment, cfg, 0.0),
        )

    def _alarms(self, now: datetime) -> list[Alarm]:
        field = self.verified.get("alarms.active")
        if not field or not self.executor:
            return []
        try:
            rows = self.executor.query(field["query"])
        except Exception as exc:
            self.failed_any = True
            self.notes.append(f"alarms.active: okap bolmady ({type(exc).__name__})")
            return []
        cols = field.get("columns", {})
        alarms = []
        for row in rows:
            started = row.get(cols.get("startedAt", "startedAt"))
            if not isinstance(started, datetime):
                continue
            started = _aware(started)
            severity = SEVERITY.get(str(row.get(cols.get("severity", "severity"), "")).upper(), "WARNING")
            alarms.append(Alarm(
                id=str(row.get(cols.get("id", "id"), "")), lineId=field.get("lineId", "gipsokarton"),
                equipment=str(row.get(cols.get("equipment", "equipment"), "")),
                message=str(row.get(cols.get("message", "message"), "")),
                severity=severity, priority=PRIORITY[severity],
                state=STATE.get(str(row.get(cols.get("state", "state"), "")).upper(), "ACTIVE"),
                startedAt=started, durationMin=round((now - started).total_seconds() / 60, 1), mode="HAKYKY",
                # Only a verified assetKey column links an alarm to a machine; equipment text never does.
                assetId=resolve_asset_key(self.cfg, field.get("lineId", "gipsokarton"),
                                          str(row.get(cols["assetKey"], "")) if "assetKey" in cols else ""),
            ))
        if alarms:
            self.read_any, self.last_ok = True, now
        return sorted(alarms, key=lambda a: (a.priority, -a.startedAt.timestamp()))

    def _connection(self) -> Connection:
        if not self.executor or not self.verified:
            return Connection(state="NOT_CONFIGURED", source="WinCC baglanyşygy ýa-da tassyklanan tag ýok",
                              lastOkTs=self.last_ok)
        if self.read_any and not self.failed_any:
            return Connection(state="ONLINE", source="WinCC", lastOkTs=self.last_ok)
        return Connection(state="OFFLINE", source="WinCC okap bolmady", lastOkTs=self.last_ok)

    def snapshot(self) -> Snapshot:
        self.notes, self.read_any, self.failed_any = [], False, False
        now = self.clock()
        day_start = production_day_start(now, self.cfg["productionDayStartHour"])
        if not self.verified:
            self.notes.append("Tassyklanan çeşme ýok. Ähli meýdanlar boş görkezilýär.")
        lines = [self._line(line_id, now, day_start) for line_id in ("gipsokarton", "gury-garyndy")]
        alarms = self._alarms(now)
        state = shift_state(self.cfg["shifts"], now)
        shift = ShiftState(
            current=ShiftInfo(**state["current"]), next=ShiftInfo(**state["next"]),
            schedule=[ShiftInfo(**s) for s in self.cfg["shifts"]],
            elapsedMin=state["elapsedMin"], remainingMin=state["remainingMin"], onBreak=state["onBreak"],
            staffCount=self._metric("shift.staffCount", "shift.staffCount", now),
            # Shift times come from plant.json, not from a plant source.
            safetyNotices=self.cfg["safetyNotices"], mode="SIMULYASIYA", source=self.cfg["shiftSource"],
        )
        return mark_stale(Snapshot(
            contractVersion=API_VERSION, timestamp=now, dataMode="MAGLUMAT_YOK", adapter=self.name,
            connection=self._connection(),
            productionDayStart=day_start,
            lines=lines, alarms=alarms,
            energy=Energy(powerKw=self._metric("energy.powerKw", "energy.powerKw", now),
                          energyKwhToday=self._metric("energy.energyKwhToday", "energy.energyKwhToday", now)),
            shift=shift, notes=self.notes,
        ), now)
