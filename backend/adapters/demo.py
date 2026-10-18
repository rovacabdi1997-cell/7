"""Deterministic demo adapter. Same clock -> same numbers, no randomness.
Every value it returns is labelled SIMULÝASIÝA."""
import math
from datetime import datetime, timedelta
from typing import Callable, Optional

from app.config import plant_config
from app.models import Alarm, Equipment, Line, Metric, ShiftInfo, ShiftState, Snapshot, TrendPoint
from app.timeutil import hhmm_to_minutes, now_tm, production_day_start
from services.kpi import overlap_minutes, pct
from services.shifts import shift_state

MODE = "SIMULÝASIÝA"
SOURCE = "Demo adapteri (SIMULÝASIÝA)"

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
        ("01:00", 20, "fault", "Elewator", "Elewatoryň guşagy typýar", "CRITICAL"),
    ],
}

# Warnings do not stop the line. (line, equipment, message, clock time, minutes)
WARNINGS = [
    ("gipsokarton", "Guradyjy", "Guradyjynyň 2-nji zolagynda temperatura ýokary", "18:00", 90),
    ("gury-garyndy", "Çig mal silosy", "Silosdaky material derejesi pes", "11:15", 50),
]

EQUIPMENT = {
    "gipsokarton": ["Gips berijisi", "Garyşdyryjy", "Köpük generatory", "Formirleme stoly",
                    "Gatama lentasy", "Kesiji", "Guradyjy", "Gyra kesiji", "Gaplaýjy"],
    "gury-garyndy": ["Çig mal silosy", "Dozirleýji", "Garyşdyryjy", "Elewator",
                     "Taýýar önüm bunkeri", "Gaplaýjy maşyn", "Palet örüji"],
}

STAFF = {"I": 46, "II": 41, "III": 28}


def _noise(seed: int) -> float:
    """Deterministic pseudo-noise in [-1, 1]."""
    x = math.sin(seed * 12.9898 + 78.233) * 43758.5453
    return (x - math.floor(x)) * 2 - 1


def _metric(value: Optional[float], unit: str, source: str = SOURCE) -> Metric:
    return Metric(value=None if value is None else round(value, 2), unit=unit, mode=MODE, source=source)


class DemoAdapter:
    name = "demo"

    def __init__(self, clock: Callable[[], datetime] = now_tm) -> None:
        self.clock = clock
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

    def _full_day(self, line_id: str, day_key: int) -> float:
        key = (line_id, day_key)
        if key not in self._day_cache:
            self._day_cache[key] = self._produce(line_id, day_key, 24 * 60)[0]
        return self._day_cache[key]

    def _line(self, line_id: str, day_start: datetime, elapsed: float) -> Line:
        cfg = self.cfg["lines"][line_id]
        stops = self._stops(line_id)
        day_key = day_start.toordinal()
        is_board = line_id == "gipsokarton"

        def stop_at(minute: float) -> Optional[dict]:
            return next((s for s in stops if s["start"] <= minute < s["end"]), None)

        total, hourly = self._produce(line_id, day_key, elapsed)
        month_total = total + sum(self._full_day(line_id, day_key - back) for back in range(1, day_start.day))

        current_stop = stop_at(elapsed)
        status = "RUNNING"
        if current_stop:
            status = "FAULT" if current_stop["kind"] == "fault" else "STOPPED"
        speed = 0.0 if current_stop else self._rate(line_id, int(elapsed), day_key)

        started = [s for s in stops if s["start"] <= elapsed]
        stop_minutes = sum(overlap_minutes(s["start"], s["end"], 0, elapsed) for s in started)
        warnings = [w for w in WARNINGS if w[0] == line_id and self._offset(w[3]) <= elapsed]
        errors = sum(1 for s in started if s["kind"] == "fault") + len(warnings)

        plan_day = cfg["planPerDay"]
        plan_to_date = plan_day * elapsed / (24 * 60)
        nominal_to_date = cfg["nominalPerHour"] * elapsed / 60

        plan_hour = plan_day / 24
        trend = [
            TrendPoint(hour=(day_start + timedelta(hours=h)).strftime("%H:00"),
                       actual=round(hourly.get(h, 0.0), 1), plan=round(plan_hour, 1))
            for h in range(int(elapsed // 60) + 1)
        ]

        equipment = []
        for index, name in enumerate(EQUIPMENT[line_id]):
            eq_status = "RUNNING"
            if current_stop:
                eq_status = "FAULT" if current_stop["equipment"] == name and current_stop["kind"] == "fault" else "STOPPED"
            equipment.append(Equipment(id=f"{line_id}-{index + 1:02d}", name=name, status=eq_status))

        bags = None
        if not is_board:
            bags = _metric(math.floor(total * cfg["packedShare"] * 1000 / cfg["bagKg"]), "halta")

        return Line(
            id=line_id, name=cfg["name"], section=cfg["section"], unit=cfg["unit"],
            rateUnit=cfg["rateUnit"], status=status, mode=MODE,
            speed=_metric(speed, cfg["rateUnit"]),
            outputToday=_metric(total, cfg["unit"]),
            outputMonth=_metric(month_total, cfg["unit"]),
            planToday=_metric(plan_day, cfg["unit"], cfg["planSource"]),
            planToDate=_metric(plan_to_date, cfg["unit"], cfg["planSource"]),
            fulfilmentPct=_metric(pct(total, plan_to_date), "%"),
            efficiencyPct=_metric(pct(total, nominal_to_date), "%", f"{SOURCE}; nominal: {cfg['nominalSource']}"),
            bagsToday=bags,
            stopsToday=_metric(len(started), "san"),
            stopMinutesToday=_metric(stop_minutes, "min"),
            errorsToday=_metric(errors, "san"),
            trend=trend,
            equipment=equipment,
        )

    def _alarms(self, day_start: datetime, elapsed: float) -> list[Alarm]:
        alarms = []
        entries = []
        for line_id in STOPS:
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
                message=message, severity=severity, state=state,
                startedAt=day_start + timedelta(minutes=start),
                durationMin=round(age if active else minutes, 1), mode=MODE,
            ))
        order = {"ACTIVE": 0, "ACKNOWLEDGED": 1, "CLEARED": 2}
        return sorted(alarms, key=lambda a: (order[a.state], -a.startedAt.timestamp()))

    def _shift(self, now: datetime) -> ShiftState:
        state = shift_state(self.cfg["shifts"], now)
        return ShiftState(
            current=ShiftInfo(**state["current"]), next=ShiftInfo(**state["next"]),
            schedule=[ShiftInfo(**s) for s in self.cfg["shifts"]],
            elapsedMin=state["elapsedMin"], remainingMin=state["remainingMin"], onBreak=state["onBreak"],
            staffCount=_metric(STAFF.get(state["current"]["id"]), "adam"),
            safetyNotices=self.cfg["safetyNotices"], mode=MODE, source=self.cfg["shiftSource"],
        )

    def snapshot(self) -> Snapshot:
        now = self.clock()
        day_start = production_day_start(now, self.cfg["productionDayStartHour"])
        elapsed = (now - day_start).total_seconds() / 60
        return Snapshot(
            timestamp=now, dataMode=MODE, adapter=self.name, productionDayStart=day_start,
            lines=[self._line(line_id, day_start, elapsed) for line_id in ("gipsokarton", "gury-garyndy")],
            alarms=self._alarms(day_start, elapsed),
            shift=self._shift(now),
            notes=["Ähli bahalar SIMULÝASIÝA. Hakyky çeşme tassyklanmadyk."],
        )
