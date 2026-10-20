"""Response models. Codes are ASCII; the frontend renders Turkmen labels."""
from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel

# SIMULÝASIÝA = demo adapter, HAKYKY = verified real source, ÝOK = no data.
DataMode = Literal["SIMULÝASIÝA", "HAKYKY", "ÝOK"]
RunStatus = Literal["RUNNING", "STOPPED", "FAULT", "UNKNOWN"]
Severity = Literal["CRITICAL", "WARNING", "INFO"]
AlarmState = Literal["ACTIVE", "ACKNOWLEDGED", "CLEARED"]
# process = on the main chain, buffer = silo/bunker that decouples the chain,
# feed = side input into a main-chain machine (paper reels).
EquipmentKind = Literal["process", "buffer", "feed"]


class Metric(BaseModel):
    value: Optional[float] = None
    unit: str = ""
    mode: DataMode
    source: str


class Equipment(BaseModel):
    id: str
    name: str
    status: RunStatus
    order: int = 0
    assetKey: str = ""
    kind: EquipmentKind = "process"
    mode: DataMode = "ÝOK"
    # Baumak inventory code (1-005-605) or Sanjin item number; "" if unknown.
    ref: str = ""


class Flow(BaseModel):
    """Material link between two machines. The TV draws moving material only
    when `active`; animation speed follows `flowRate` (0..1 of nominal)."""
    fromId: str
    toId: str
    active: bool
    flowRate: float


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
    flow: list[Flow] = []


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
