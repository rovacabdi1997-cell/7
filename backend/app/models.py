"""Response models. Codes are ASCII; the frontend renders Turkmen labels."""
from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel

# SIMULÝASIÝA = demo adapter, HAKYKY = verified real source, ÝOK = no data.
DataMode = Literal["SIMULÝASIÝA", "HAKYKY", "ÝOK"]
RunStatus = Literal["RUNNING", "STOPPED", "FAULT", "UNKNOWN"]
Severity = Literal["CRITICAL", "WARNING", "INFO"]
AlarmState = Literal["ACTIVE", "ACKNOWLEDGED", "CLEARED"]


class Metric(BaseModel):
    value: Optional[float] = None
    unit: str = ""
    mode: DataMode
    source: str


class Equipment(BaseModel):
    id: str
    name: str
    status: RunStatus


class TrendPoint(BaseModel):
    hour: str
    actual: Optional[float] = None
    plan: Optional[float] = None


class Line(BaseModel):
    id: str
    name: str
    section: str
    unit: str
    rateUnit: str
    status: RunStatus
    mode: DataMode
    speed: Metric
    outputToday: Metric
    outputMonth: Metric
    planToday: Metric
    planToDate: Metric
    fulfilmentPct: Metric
    efficiencyPct: Metric
    bagsToday: Optional[Metric] = None
    stopsToday: Metric
    stopMinutesToday: Metric
    errorsToday: Metric
    trend: list[TrendPoint]
    equipment: list[Equipment]


class Alarm(BaseModel):
    id: str
    lineId: str
    equipment: str
    message: str
    severity: Severity
    state: AlarmState
    startedAt: datetime
    durationMin: float
    mode: DataMode


class ShiftInfo(BaseModel):
    id: str
    name: str
    start: str
    end: str
    breakStart: str
    breakEnd: str


class ShiftState(BaseModel):
    current: ShiftInfo
    next: ShiftInfo
    schedule: list[ShiftInfo]
    elapsedMin: int
    remainingMin: int
    onBreak: bool
    staffCount: Metric
    safetyNotices: list[str]
    mode: DataMode
    source: str


class Snapshot(BaseModel):
    timestamp: datetime
    dataMode: DataMode
    adapter: str
    productionDayStart: datetime
    lines: list[Line]
    alarms: list[Alarm]
    shift: ShiftState
    notes: list[str] = []
