// All visible dashboard text is Turkmen. Keep labels here, not in components.
import type { AlarmState, DataMode, RunStatus, Severity } from "../data/types";

export const NAV = [
  { href: "/", label: "Baş panel" },
  { href: "/gipsokarton", label: "Gipsokarton" },
  { href: "/gury-garyndy", label: "Gury garyndy" },
  { href: "/duyduryslar", label: "Duýduryşlar" },
  { href: "/calsyk", label: "Çalşyk" },
  { href: "/tv", label: "TV görnüşi" },
] as const;

export const STATUS: Record<RunStatus, string> = {
  RUNNING: "Işleýär",
  STOPPED: "Durdy",
  FAULT: "Näsazlyk",
  UNKNOWN: "Belli däl",
};

export const SEVERITY: Record<Severity, string> = {
  CRITICAL: "Howply",
  WARNING: "Duýduryş",
  INFO: "Maglumat",
};

export const ALARM_STATE: Record<AlarmState, string> = {
  ACTIVE: "Işjeň",
  ACKNOWLEDGED: "Tassyklandy",
  CLEARED: "Ýapyldy",
};

export const MODE: Record<DataMode, string> = {
  "SIMULÝASIÝA": "SIMULÝASIÝA",
  HAKYKY: "HAKYKY MAGLUMAT",
  "ÝOK": "MAGLUMAT ÝOK",
};

export const LINE_SHORT: Record<string, string> = {
  gipsokarton: "Gipsokarton",
  "gury-garyndy": "Gury garyndy",
};

const MONTHS = ["ýanwar", "fewral", "mart", "aprel", "maý", "iýun", "iýul", "awgust", "sentýabr", "oktýabr", "noýabr", "dekabr"];
const WEEKDAYS = ["Ýekşenbe", "Duşenbe", "Sişenbe", "Çarşenbe", "Penşenbe", "Anna", "Şenbe"];

/** Thousands separated by a space, decimal comma: 12 345,6 */
export function num(value: number | null | undefined, decimals = 0): string {
  if (value === null || value === undefined || Number.isNaN(value)) return "—";
  const fixed = Math.abs(value).toFixed(decimals);
  const [int, frac] = fixed.split(".");
  const grouped = int.replace(/\B(?=(\d{3})+(?!\d))/g, " ");
  return `${value < 0 ? "−" : ""}${grouped}${frac ? `,${frac}` : ""}`;
}

/** Timestamps arrive as ISO strings with the +05:00 offset; read the wall clock directly. */
export function clock(iso: string): string {
  return iso.slice(11, 16);
}

export function longDate(iso: string): string {
  const [y, m, d] = iso.slice(0, 10).split("-").map(Number);
  const weekday = new Date(Date.UTC(y, m - 1, d)).getUTCDay();
  return `${d} ${MONTHS[m - 1]} ${y}, ${WEEKDAYS[weekday]}`;
}

export function duration(minutes: number): string {
  const total = Math.max(0, Math.round(minutes));
  const h = Math.floor(total / 60);
  const m = total % 60;
  if (h === 0) return `${m} min`;
  return `${h} sag ${m.toString().padStart(2, "0")} min`;
}
