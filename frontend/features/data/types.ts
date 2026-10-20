// Mirrors backend/app/models.py.
export type DataMode = "SIMULÝASIÝA" | "HAKYKY" | "ÝOK";
export type RunStatus = "RUNNING" | "STOPPED" | "FAULT" | "UNKNOWN";
export type Severity = "CRITICAL" | "WARNING" | "INFO";
export type AlarmState = "ACTIVE" | "ACKNOWLEDGED" | "CLEARED";

export interface Metric {
  value: number | null;
  unit: string;
  mode: DataMode;
  source: string;
}

export type EquipmentKind = "process" | "buffer" | "feed";

export interface Equipment {
  id: string;
  name: string;
  status: RunStatus;
  order: number;
  assetKey: string;
  kind: EquipmentKind;
  mode: DataMode;
}

/** Material link between two machines; decided by the backend, never guessed here. */
export interface Flow {
  fromId: string;
  toId: string;
  active: boolean;
  flowRate: number;
}

export interface TrendPoint {
  hour: string;
  actual: number | null;
  plan: number | null;
}

export interface Line {
  id: "gipsokarton" | "gury-garyndy";
  name: string;
  section: string;
  unit: string;
  rateUnit: string;
  status: RunStatus;
  mode: DataMode;
  speed: Metric;
  outputToday: Metric;
  outputMonth: Metric;
  planToday: Metric;
  planToDate: Metric;
  fulfilmentPct: Metric;
  efficiencyPct: Metric;
  bagsToday: Metric | null;
  stopsToday: Metric;
  stopMinutesToday: Metric;
  errorsToday: Metric;
  trend: TrendPoint[];
  equipment: Equipment[];
  flow: Flow[];
}

export interface Alarm {
  id: string;
  lineId: string;
  equipment: string;
  message: string;
  severity: Severity;
  state: AlarmState;
  startedAt: string;
  durationMin: number;
  mode: DataMode;
}

export interface ShiftInfo {
  id: string;
  name: string;
  start: string;
  end: string;
  breakStart: string;
  breakEnd: string;
}

export interface ShiftState {
  current: ShiftInfo;
  next: ShiftInfo;
  schedule: ShiftInfo[];
  elapsedMin: number;
  remainingMin: number;
  onBreak: boolean;
  staffCount: Metric;
  safetyNotices: string[];
  mode: DataMode;
  source: string;
}

export interface Snapshot {
  timestamp: string;
  dataMode: DataMode;
  adapter: string;
  productionDayStart: string;
  lines: Line[];
  alarms: Alarm[];
  shift: ShiftState;
  notes: string[];
  /** Present on SSE events only. */
  seq?: number;
  staleAfterSec?: number;
}
