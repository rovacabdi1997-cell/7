"""Read-only WinCC adapter.

Reads only fields whose status is VERIFIED in config/tag_mapping.json. Every
other field comes back empty with mode ÝOK. It never falls back to demo
values, so real and simulated data cannot mix on one screen.
"""
from datetime import datetime
from typing import Any, Callable, Optional, Protocol

from adapters.readonly_guard import assert_read_only
from app.config import plant_config, tag_mapping
from app.models import Alarm, Line, Metric, ShiftInfo, ShiftState, Snapshot
from app.timeutil import TM_TZ, now_tm, production_day_start
from services.flow import build_equipment, build_flow, machine_states
from services.kpi import pct
from services.shifts import shift_state

LINE_METRICS = ("speed", "outputToday", "outputMonth", "planToday", "bagsToday", "stopsToday", "stopMinutesToday", "errorsToday")
SEVERITY = {"CRITICAL": "CRITICAL", "WARNING": "WARNING", "INFO": "INFO"}
STATE = {"ACTIVE": "ACTIVE", "ACKNOWLEDGED": "ACKNOWLEDGED", "CLEARED": "CLEARED"}


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

    def _read(self, key: str, unit: str) -> Metric:
        field = self.verified.get(key)
        if not field:
            return Metric(value=None, unit=unit, mode="ÝOK", source="Çeşme tassyklanmadyk")
        if not self.executor:
            return Metric(value=None, unit=unit, mode="ÝOK", source="WinCC baglanyşygy sazlanmadyk")
        try:
            rows = self.executor.query(field["query"])
        except Exception as exc:  # report the failure, never invent a value
            self.notes.append(f"{key}: okap bolmady ({type(exc).__name__})")
            return Metric(value=None, unit=unit, mode="ÝOK", source="Okamak ýalňyşlygy")
        value = next(iter(rows[0].values()), None) if rows else None
        if value is None:
            return Metric(value=None, unit=unit, mode="ÝOK", source=field.get("candidate", key))
        self.read_any = True
        return Metric(value=float(value), unit=unit, mode="HAKYKY", source=field.get("candidate", key))

    def _line(self, line_id: str) -> Line:
        cfg = self.cfg["lines"][line_id]
        units = {"speed": cfg["rateUnit"], "outputToday": cfg["unit"], "outputMonth": cfg["unit"],
                 "planToday": cfg["unit"],
                 "bagsToday": "halta", "stopsToday": "san", "stopMinutesToday": "min", "errorsToday": "san"}
        m = {name: self._read(f"{line_id}.{name}", units[name]) for name in LINE_METRICS}
        empty = Metric(value=None, unit="%", mode="ÝOK", source="Hasaplamak üçin maglumat ýok")
        fulfil = empty
        if m["outputToday"].value is not None and m["planToday"].value:
            fulfil = Metric(value=pct(m["outputToday"].value, m["planToday"].value), unit="%",
                            mode="HAKYKY", source="outputToday / planToday")
        any_real = any(x.mode == "HAKYKY" for x in m.values())
        # No verified per-machine tags yet: every machine is UNKNOWN / ÝOK.
        equipment = build_equipment(line_id, cfg, machine_states(cfg, None, "ÝOK"), "ÝOK")
        return Line(
            id=line_id, name=cfg["name"], section=cfg["section"], unit=cfg["unit"], rateUnit=cfg["rateUnit"],
            status="UNKNOWN", mode="HAKYKY" if any_real else "ÝOK",
            speed=m["speed"], outputToday=m["outputToday"], outputMonth=m["outputMonth"],
            planToday=m["planToday"],
            planToDate=Metric(value=None, unit=cfg["unit"], mode="ÝOK", source="Tassyklanmadyk"),
            fulfilmentPct=fulfil, efficiencyPct=empty,
            bagsToday=m["bagsToday"] if line_id == "gury-garyndy" else None,
            stopsToday=m["stopsToday"], stopMinutesToday=m["stopMinutesToday"], errorsToday=m["errorsToday"],
            trend=[], equipment=equipment, flow=build_flow(equipment, cfg, 0.0),
        )

    def _alarms(self, now: datetime) -> list[Alarm]:
        field = self.verified.get("alarms.active")
        if not field or not self.executor:
            return []
        try:
            rows = self.executor.query(field["query"])
        except Exception as exc:
            self.notes.append(f"alarms.active: okap bolmady ({type(exc).__name__})")
            return []
        cols = field.get("columns", {})
        alarms = []
        for row in rows:
            started = row.get(cols.get("startedAt", "startedAt"))
            if not isinstance(started, datetime):
                continue
            if started.tzinfo is None:
                started = started.replace(tzinfo=TM_TZ)
            alarms.append(Alarm(
                id=str(row.get(cols.get("id", "id"), "")), lineId=field.get("lineId", "gipsokarton"),
                equipment=str(row.get(cols.get("equipment", "equipment"), "")),
                message=str(row.get(cols.get("message", "message"), "")),
                severity=SEVERITY.get(str(row.get(cols.get("severity", "severity"), "")).upper(), "WARNING"),
                state=STATE.get(str(row.get(cols.get("state", "state"), "")).upper(), "ACTIVE"),
                startedAt=started, durationMin=round((now - started).total_seconds() / 60, 1), mode="HAKYKY",
            ))
        self.read_any = self.read_any or bool(alarms)
        return alarms

    def snapshot(self) -> Snapshot:
        self.notes, self.read_any = [], False
        now = self.clock()
        if not self.verified:
            self.notes.append("Tassyklanan çeşme ýok. Ähli meýdanlar boş görkezilýär.")
        lines = [self._line(line_id) for line_id in ("gipsokarton", "gury-garyndy")]
        alarms = self._alarms(now)
        state = shift_state(self.cfg["shifts"], now)
        shift = ShiftState(
            current=ShiftInfo(**state["current"]), next=ShiftInfo(**state["next"]),
            schedule=[ShiftInfo(**s) for s in self.cfg["shifts"]],
            elapsedMin=state["elapsedMin"], remainingMin=state["remainingMin"], onBreak=state["onBreak"],
            staffCount=self._read("shift.staffCount", "adam"),
            safetyNotices=self.cfg["safetyNotices"], mode="SIMULÝASIÝA", source=self.cfg["shiftSource"],
        )
        return Snapshot(
            timestamp=now, dataMode="HAKYKY" if self.read_any else "ÝOK", adapter=self.name,
            productionDayStart=production_day_start(now, self.cfg["productionDayStartHour"]),
            lines=lines, alarms=alarms, shift=shift, notes=self.notes,
        )
