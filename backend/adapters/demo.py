"""Deterministic demo adapter. Same clock -> same numbers, no randomness.
Every value it returns is labelled SIMULYASIYA; fields with no simulated source
(energy) are MAGLUMAT_YOK, never 0."""
import math
from datetime import datetime, timedelta
from typing import Callable, Optional

from app.config import API_VERSION, plant_config
from app.contract import empty, meta, metric, text
from app.models import (PRIORITY, Alarm, Connection, CurrentStop, Energy, HourlySeries, Line, Oee, ShiftInfo,
                        ShiftState, Snapshot, StatusValue, TrendPoint)
from app.timeutil import hhmm_to_minutes, now_tm, production_day_start
from services.freshness import mark_stale
from services.flow import build_equipment, build_flow, machine_states, resolve_asset_id
from services.kpi import oee, overlap_minutes, pct
from services.shifts import shift_span, shift_state

MODE = "SIMULYASIYA"
SOURCE = "Demo adapteri (SIMULYASIYA)"
# Simulated product on each line (TR-06 / TR-07 product names; no work order source yet).
PRODUCT = {
    "gipsokarton": {"name": "Gipsokarton list", "thicknessMm": 12.5, "boardType": "Adaty (GKL)"},
    "gury-garyndy": {"name": "Şpatlýowka"},
}
# No quality measurement exists; the demo shows a fixed, labelled figure so the three OEE bars can be drawn.
DEMO_QUALITY_PCT = 98.6

# (clock time, minutes, kind, equipment, message, severity)
STOPS = {
    "gipsokarton": [
        ("10:40", 18, "planned", "Kagyz bobinasy", "Kagyz bobinasy çalşyrylýar", "INFO"),
        ("15:20", 12, "fault", "Kesiji", "Kesijiniň ýerleşiş datçigi ýalňyşlyk berdi", "CRITICAL"),
        ("21:05", 35, "fault", "Garyşdyryjy", "Garyşdyryjynyň motor togy çäkden ýokary", "CRITICAL"),
        ("03:10", 15, "planned", "Formirleme stoly", "Formirleme stoly arassalanýar", "INFO"),
    ],
    "gury-garyndy": [
        ("09:30", 20, "fault", "Gaplaýjy maşyn", "Gaplaýjy maşynda halta dykylmasy", "CRITICAL"),
        ("14:00", 45, "planned", "Garyşdyryjy", "Meýilleşdirilen arassalaýyş", "INFO"),
        ("01:00", 20, "fault", "Tartym bunkeri", "Tartym bunkeriniň agram datçigi ýalňyşlyk berdi", "CRITICAL"),
    ],
}

# Warnings do not stop the line. (line, equipment, message, clock time, minutes)
WARNINGS = [
    ("gipsokarton", "Guradyjy", "Guradyjynyň 2-nji zolagynda temperatura ýokary", "18:00", 90),
    ("gury-garyndy", "Çig mal silolary", "Silosdaky material derejesi pes", "11:15", 50),
]

# Presentation loop (DEMO_SCENARIO=presentation): a 6-minute cycle so a fault
# and its recovery are always seen within a few minutes, on both TVs at once.
# (line, start second, end second, kind, equipment, message, severity)
PRESENTATION_CYCLE_S = 360
PRESENTATION_STOPS = [
    ("gipsokarton", 150, 210, "fault", "Kesiji", "Kesijiniň ýerleşiş datçigi ýalňyşlyk berdi", "CRITICAL"),
    ("gury-garyndy", 210, 270, "fault", "Garyşdyryjy", "Garyşdyryjynyň motor togy çäkden ýokary", "CRITICAL"),
]
# After a presentation stop the line ramps from 60% back to full speed.
PRESENTATION_RAMP_S = 60

STAFF = {"I": 46, "II": 41, "III": 28}


def _noise(seed: int) -> float:
    """Deterministic pseudo-noise in [-1, 1]."""
    x = math.sin(seed * 12.9898 + 78.233) * 43758.5453
    return (x - math.floor(x)) * 2 - 1


class DemoAdapter:
    name = "demo"

    def __init__(self, clock: Callable[[], datetime] = now_tm, scenario: str = "clock") -> None:
        self.clock = clock
        self.scenario = scenario
        self.cfg = plant_config()
        self._day_cache: dict[tuple[str, int], float] = {}

    def _offset(self, clock_time: str) -> int:
        start = self.cfg["productionDayStartHour"] * 60
        return (hhmm_to_minutes(clock_time) - start) % (24 * 60)

    def _stops(self, line_id: str) -> list[dict]:
        return [
            {"start": self._offset(t), "end": self._offset(t) + d, "kind": k, "equipment": e,
             "message": m, "severity": s}
            for t, d, k, e, m, s in STOPS[line_id]
        ]

    def _rate(self, line_id: str, minute: int, day_key: int) -> float:
        """Per-minute output while running: m/min speed or t/h rate."""
        if line_id == "gipsokarton":
            return 33.5 + 1.1 * math.sin(2 * math.pi * minute / 97) + 0.5 * _noise(minute + day_key)
        return 21.5 + 1.5 * math.sin(2 * math.pi * minute / 131) + 0.8 * _noise(minute * 3 + day_key)

    def _produce(self, line_id: str, day_key: int, minutes: float) -> tuple[float, dict[int, float]]:
        """Output from production day start up to `minutes`, total and per hour."""
        cfg = self.cfg["lines"][line_id]
        stops = self._stops(line_id)
        hourly: dict[int, float] = {}
        total = 0.0
        for minute in range(int(minutes)):
            if any(s["start"] <= minute < s["end"] for s in stops):
                continue
            rate = self._rate(line_id, minute, day_key)
            produced = rate * cfg["boardWidthM"] if line_id == "gipsokarton" else rate / 60
            total += produced
            hourly[minute // 60] = hourly.get(minute // 60, 0.0) + produced
        return total, hourly

    def _output_since(self, line_id: str, day_key: int, elapsed: float, since: float) -> float:
        """Output between production-day minute `since` (negative = previous day) and `elapsed`."""
        today = self._produce(line_id, day_key, elapsed)[0]
        if since >= 0:
            return today - self._produce(line_id, day_key, since)[0]
        previous = self._full_day(line_id, day_key - 1) - self._produce(line_id, day_key - 1, 24 * 60 + since)[0]
        return previous + today

    def _full_day(self, line_id: str, day_key: int) -> float:
        key = (line_id, day_key)
        if key not in self._day_cache:
            self._day_cache[key] = self._produce(line_id, day_key, 24 * 60)[0]
        return self._day_cache[key]

    def _presentation(self, line_id: str, now: datetime) -> tuple[Optional[dict], float]:
        """Current presentation stop for the line and a speed factor (0.6..1)."""
        second = (now.minute * 60 + now.second) % PRESENTATION_CYCLE_S
        factor = 1.0
        for lid, start, end, kind, equipment, message, severity in PRESENTATION_STOPS:
            if lid != line_id:
                continue
            if start <= second < end:
                return {"kind": kind, "equipment": equipment, "message": message, "severity": severity,
                        "ageSec": second - start}, 0.0
            if end <= second < end + PRESENTATION_RAMP_S:
                factor = 0.6 + 0.4 * (second - end) / PRESENTATION_RAMP_S
        return None, factor

    def _line(self, line_id: str, day_start: datetime, elapsed: float, now: datetime, shift: dict) -> Line:
        cfg = self.cfg["lines"][line_id]
        stops = self._stops(line_id)
        day_key = day_start.toordinal()
        is_board = line_id == "gipsokarton"

        def m(key: str, value: Optional[float], source: str = SOURCE):
            return metric(key, value, MODE, source, now, cfg)

        def stop_at(minute: float) -> Optional[dict]:
            return next((s for s in stops if s["start"] <= minute < s["end"]), None)

        total, hourly = self._produce(line_id, day_key, elapsed)
        month_total = total + sum(self._full_day(line_id, day_key - back) for back in range(1, day_start.day))

        current_stop = stop_at(elapsed)
        stop_started = day_start + timedelta(minutes=current_stop["start"]) if current_stop else None
        factor = 1.0
        if self.scenario == "presentation":
            current_stop, factor = self._presentation(line_id, now)
            stop_started = now - timedelta(seconds=current_stop["ageSec"]) if current_stop else None
        status = "RUNNING"
        if current_stop:
            status = "FAULT" if current_stop["kind"] == "fault" else "STOPPED"
        running_rate = self._rate(line_id, int(elapsed), day_key) * factor
        speed = 0.0 if current_stop else running_rate

        started = [s for s in stops if s["start"] <= elapsed]
        stop_minutes = sum(overlap_minutes(s["start"], s["end"], 0, elapsed) for s in started)
        warnings = [w for w in WARNINGS if w[0] == line_id and self._offset(w[3]) <= elapsed]
        errors = sum(1 for s in started if s["kind"] == "fault") + len(warnings)

        plan_day = cfg["planPerDay"]
        plan_to_date = plan_day * elapsed / (24 * 60)
        plan_hour = plan_day / 24

        shift_output = self._output_since(line_id, day_key, elapsed, elapsed - shift["elapsedMin"])
        shift_plan = plan_day * shift_span(shift["current"]) / (24 * 60)

        # Output rate per hour (m²/sag or t/sag) against the nominal capacity.
        rate_per_hour = speed * cfg["boardWidthM"] * 60 if is_board else speed
        run_minutes = max(0.0, elapsed - stop_minutes)
        availability = pct(run_minutes, elapsed)
        performance = pct(total, cfg["nominalPerHour"] * run_minutes / 60)
        nominal_src = f"{SOURCE}; nominal: {cfg['nominalSource']}"

        trend = HourlySeries(
            unit=cfg["unit"],
            points=[TrendPoint(hour=(day_start + timedelta(hours=h)).strftime("%H:00"),
                               actual=round(hourly.get(h, 0.0), 1), plan=round(plan_hour, 1))
                    for h in range(int(elapsed // 60) + 1)],
            **meta("line.trend", MODE, SOURCE, now),
        )

        states = machine_states(cfg, current_stop, MODE)
        equipment = build_equipment(line_id, cfg, states, MODE, now)
        # Nominal running speed: m/min for board (m²/h over board width), t/h for dry mix.
        nominal = cfg["nominalPerHour"] / cfg["boardWidthM"] / 60 if is_board else cfg["nominalPerHour"]
        flow = build_flow(equipment, cfg, running_rate / nominal)

        stop = None
        if current_stop:
            stop = CurrentStop(
                startedAt=stop_started, durationMin=round((now - stop_started).total_seconds() / 60, 1),
                planned=current_stop["kind"] == "planned", reasonCode=None,
                reasonText=current_stop["message"],
                equipmentId=resolve_asset_id(self.cfg, line_id, current_stop["equipment"]),
                **meta("line.currentStop", MODE, SOURCE, now),
            )

        product = PRODUCT[line_id]
        return Line(
            id=line_id, name=cfg["name"], section=cfg["section"], unit=cfg["unit"],
            rateUnit=cfg["rateUnit"], mode=MODE,
            status=StatusValue(value=status, **meta("line.status", MODE, SOURCE, now)),
            speed=m("line.speed", speed),
            outputToday=m("line.outputToday", total),
            outputMonth=m("line.outputMonth", month_total),
            planToday=m("line.planToday", plan_day, cfg["planSource"]),
            planToDate=m("line.planToDate", plan_to_date, cfg["planSource"]),
            shiftOutput=m("line.shiftOutput", shift_output),
            shiftPlan=m("line.shiftPlan", shift_plan, cfg["planSource"]),
            fulfilmentPct=m("line.fulfilmentPct", pct(total, plan_to_date)),
            capacityPct=m("line.capacityPct", pct(rate_per_hour, cfg["nominalPerHour"]), nominal_src),
            nominalRate=m("line.nominalRate", cfg["nominalPerHour"], cfg["nominalSource"]),
            oee=Oee(
                availability=m("line.oee.availability", availability),
                performance=m("line.oee.performance", performance, nominal_src),
                quality=m("line.oee.quality", DEMO_QUALITY_PCT, f"{SOURCE}; hil ölçegi ýok"),
                oee=m("line.oee.oee", oee(availability, performance, DEMO_QUALITY_PCT)),
            ),
            productName=text("line.productName", product["name"], MODE, SOURCE, now),
            thicknessMm=m("line.thicknessMm", product["thicknessMm"]) if is_board else None,
            boardType=text("line.boardType", product["boardType"], MODE, SOURCE, now) if is_board else None,
            bagsToday=None if is_board else m(
                "line.bagsToday", math.floor(total * cfg["packedShare"] * 1000 / cfg["bagKg"])),
            stopsToday=m("line.stopsToday", len(started)),
            stopMinutesToday=m("line.stopMinutesToday", stop_minutes),
            errorsToday=m("line.errorsToday", errors),
            currentStop=stop,
            trend=trend,
            equipment=equipment,
            flow=flow,
        )

    def _alarms(self, day_start: datetime, elapsed: float, now: Optional[datetime] = None) -> list[Alarm]:
        alarms = []
        entries = []
        # In the presentation loop the clock-based stops are not happening, so
        # their alarms would contradict a running line; only warnings remain.
        for line_id in STOPS if self.scenario != "presentation" else []:
            for s in self._stops(line_id):
                entries.append((line_id, s["equipment"], s["message"], s["severity"], s["start"], s["end"] - s["start"]))
        for line_id, equipment, message, clock_time, minutes in WARNINGS:
            entries.append((line_id, equipment, message, "WARNING", self._offset(clock_time), minutes))

        for index, (line_id, equipment, message, severity, start, minutes) in enumerate(entries):
            if start > elapsed:
                continue
            active = elapsed < start + minutes
            age = elapsed - start
            state = "CLEARED"
            if active:
                state = "ACKNOWLEDGED" if age >= 10 else "ACTIVE"
            alarms.append(Alarm(
                id=f"SIM-{day_start:%Y%m%d}-{index + 1:03d}", lineId=line_id, equipment=equipment,
                message=message, severity=severity, priority=PRIORITY[severity], state=state,
                startedAt=day_start + timedelta(minutes=start),
                durationMin=round(age if active else minutes, 1), mode=MODE,
                assetId=resolve_asset_id(self.cfg, line_id, equipment),
            ))
        if self.scenario == "presentation":
            for line_id in STOPS:
                stop, _ = self._presentation(line_id, now)
                if stop:
                    alarms.append(Alarm(
                        id=f"SIM-SUNUM-{line_id}", lineId=line_id, equipment=stop["equipment"],
                        message=stop["message"], severity=stop["severity"],
                        priority=PRIORITY[stop["severity"]], state="ACTIVE",
                        startedAt=now - timedelta(seconds=stop["ageSec"]),
                        durationMin=round(stop["ageSec"] / 60, 1), mode=MODE,
                        assetId=resolve_asset_id(self.cfg, line_id, stop["equipment"]),
                    ))
        order = {"ACTIVE": 0, "ACKNOWLEDGED": 1, "CLEARED": 2}
        return sorted(alarms, key=lambda a: (order[a.state], a.priority, -a.startedAt.timestamp()))

    def _shift(self, now: datetime, state: dict) -> ShiftState:
        return ShiftState(
            current=ShiftInfo(**state["current"]), next=ShiftInfo(**state["next"]),
            schedule=[ShiftInfo(**s) for s in self.cfg["shifts"]],
            elapsedMin=state["elapsedMin"], remainingMin=state["remainingMin"], onBreak=state["onBreak"],
            staffCount=metric("shift.staffCount", STAFF.get(state["current"]["id"]), MODE, SOURCE, now),
            safetyNotices=self.cfg["safetyNotices"], mode=MODE, source=self.cfg["shiftSource"],
        )

    def snapshot(self) -> Snapshot:
        now = self.clock()
        day_start = production_day_start(now, self.cfg["productionDayStartHour"])
        elapsed = (now - day_start).total_seconds() / 60
        shift = shift_state(self.cfg["shifts"], now)
        return mark_stale(Snapshot(
            contractVersion=API_VERSION, timestamp=now, dataMode=MODE, adapter=self.name,
            connection=Connection(state="SIMULATED", source=SOURCE, lastOkTs=now),
            productionDayStart=day_start,
            lines=[self._line(line_id, day_start, elapsed, now, shift) for line_id in ("gipsokarton", "gury-garyndy")],
            alarms=self._alarms(day_start, elapsed, now),
            energy=Energy(powerKw=empty("energy.powerKw", "Energiýa hasaplaýjysy ýok"),
                          energyKwhToday=empty("energy.energyKwhToday", "Energiýa hasaplaýjysy ýok")),
            shift=self._shift(now, shift),
            notes=["Ähli bahalar SIMULYASIYA. Hakyky çeşme tassyklanmadyk."],
        ), now)
