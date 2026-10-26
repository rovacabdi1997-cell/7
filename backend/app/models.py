"""Response models, contract v2. Codes are ASCII; the frontend renders Turkmen labels.

Every value field carries the six contract facts (TAM-PLAN-v9 §24): name (the key),
type, unit, source + sourceType, mode, staleAfterSec. sourceTs is the time the value
was produced at its source; services/freshness.py turns HAKYKY into KONE when
it is older than staleAfterSec."""
from datetime import datetime, timezone
from typing import Annotated, Literal, Optional

from pydantic import BaseModel, PlainSerializer

# SIMULYASIYA = demo adapter, HAKYKY = verified real source within its age limit,
# KONE = real value older than its age limit, MAGLUMAT_YOK = nothing was received.
DataMode = Literal["SIMULYASIYA", "HAKYKY", "KONE", "MAGLUMAT_YOK"]
# Where the value comes from once the plant is connected (not whether it is connected).
SourceType = Literal["PLC_TAG", "CALCULATED", "MANUAL", "CONFIG"]
RunStatus = Literal["RUNNING", "STOPPED", "FAULT", "UNKNOWN"]
Severity = Literal["CRITICAL", "WARNING", "INFO"]
AlarmState = Literal["ACTIVE", "ACKNOWLEDGED", "CLEARED"]
ConnectionState = Literal["ONLINE", "OFFLINE", "NOT_CONFIGURED", "SIMULATED"]
# process = on the main chain, buffer = silo/bunker that decouples the chain,
# feed = side input into a main-chain machine (paper reels).
EquipmentKind = Literal["process", "buffer", "feed"]

PRIORITY: dict[str, int] = {"CRITICAL": 1, "WARNING": 2, "INFO": 3}


def _utc(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


# Stored and sent as ISO 8601 UTC ("...Z"); the screens show Asia/Ashgabat time.
UtcDatetime = Annotated[datetime, PlainSerializer(_utc, return_type=str, when_used="always")]


class FieldMeta(BaseModel):
    mode: DataMode
    source: str
    sourceType: SourceType
    sourceTs: Optional[UtcDatetime] = None
    staleAfterSec: int


class Metric(FieldMeta):
    value: Optional[float] = None
    unit: str


class TextValue(FieldMeta):
    value: Optional[str] = None


class StatusValue(FieldMeta):
    value: RunStatus


class Equipment(BaseModel):
    id: str
    name: str
    status: RunStatus
    order: int = 0
    assetKey: str = ""
    kind: EquipmentKind = "process"
    mode: DataMode = "MAGLUMAT_YOK"
    sourceTs: Optional[UtcDatetime] = None
    staleAfterSec: int = 15
    # Baumak inventory code (1-005-605) or Sanjin item number; "" if unknown.
    ref: str = ""
    # Explicit Baumak/CAD equipment codes written in plant.json (`cadCodes`); [] when none is documented.
    # A code here is a reference, not proof that a CAD instance is this machine (see /api/cad/identity).
    equipmentCodes: list[str] = []


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


class HourlySeries(FieldMeta):
    unit: str
    points: list[TrendPoint]


class Oee(BaseModel):
    """Three components and their product, never a single efficiency figure.
    oee = availability × performance × quality ÷ 10000."""
    availability: Metric
    performance: Metric
    quality: Metric
    oee: Metric


class CurrentStop(FieldMeta):
    """The stop happening now. Measured from its own start, never derived from daily totals."""
    startedAt: UtcDatetime
    durationMin: float
    planned: bool
    # Downtime reason dictionary code (MES phase 2); None until the dictionary exists.
    reasonCode: Optional[str] = None
    reasonText: str
    equipmentId: Optional[str] = None


class Line(BaseModel):
    id: str
    name: str
    section: str
    unit: str
    rateUnit: str
    status: StatusValue
    mode: DataMode
    speed: Metric
    outputToday: Metric
    outputMonth: Metric
    planToday: Metric
    planToDate: Metric
    shiftOutput: Metric
    shiftPlan: Metric
    fulfilmentPct: Metric
    capacityPct: Metric
    nominalRate: Metric
    oee: Oee
    productName: TextValue
    # Board line only: thickness in mm and board type. None on the dry-mix line.
    thicknessMm: Optional[Metric] = None
    boardType: Optional[TextValue] = None
    bagsToday: Optional[Metric] = None
    stopsToday: Metric
    stopMinutesToday: Metric
    errorsToday: Metric
    currentStop: Optional[CurrentStop] = None
    trend: HourlySeries
    equipment: list[Equipment]
    flow: list[Flow] = []


class Alarm(BaseModel):
    id: str
    lineId: str
    equipment: str
    message: str
    severity: Severity
    # 1 = CRITICAL, 2 = WARNING, 3 = INFO; lists sort by priority, then newest first.
    priority: int
    state: AlarmState
    startedAt: UtcDatetime
    durationMin: float
    mode: DataMode
    # Equipment.id of the machine that raised the alarm, resolved by the adapter from verified
    # configuration; None when it cannot be resolved without guessing. Never matched by name here.
    assetId: Optional[str] = None


class Energy(BaseModel):
    """Plant-level energy: instantaneous power and the production day's energy, separately."""
    powerKw: Metric
    energyKwhToday: Metric


class Connection(BaseModel):
    state: ConnectionState
    source: str
    lastOkTs: Optional[UtcDatetime] = None


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
    contractVersion: str
    timestamp: UtcDatetime
    dataMode: DataMode
    adapter: str
    connection: Connection
    productionDayStart: UtcDatetime
    lines: list[Line]
    alarms: list[Alarm]
    energy: Energy
    shift: ShiftState
    notes: list[str] = []
