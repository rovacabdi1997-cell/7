import type { Alarm, Severity } from "@/features/data/types";
import { ALARM_STATE, LINE_SHORT, SEVERITY, clock, duration } from "@/features/i18n/tk";

export const SEVERITY_TONE: Record<Severity, string> = {
  CRITICAL: "bg-red-50 text-bad ring-red-200",
  WARNING: "bg-amber-50 text-warn ring-amber-200",
  INFO: "bg-brand-50 text-brand-700 ring-brand-200",
};

export function SeverityTag({ severity }: { severity: Severity }) {
  return <span className={`inline-block rounded px-2 py-0.5 text-xs font-semibold ring-1 ${SEVERITY_TONE[severity]}`}>{SEVERITY[severity]}</span>;
}

export function AlarmTable({ alarms, showLine = true, compact = false }: { alarms: Alarm[]; showLine?: boolean; compact?: boolean }) {
  if (alarms.length === 0) {
    return <p className="py-6 text-center text-sm text-muted">Duýduryş ýok</p>;
  }
  const cell = compact ? "py-2" : "py-2.5";
  return (
    <div className="overflow-x-auto">
      <table className="w-full min-w-[640px] text-left text-sm">
        <thead className="text-xs uppercase tracking-wide text-muted">
          <tr className="border-b border-line">
            <th className="py-2 pr-3 font-medium">Derejesi</th>
            <th className="py-2 pr-3 font-medium">Enjam</th>
            <th className="py-2 pr-3 font-medium">Habar</th>
            {showLine && <th className="py-2 pr-3 font-medium">Liniýa</th>}
            <th className="py-2 pr-3 font-medium">Başlanan wagty</th>
            <th className="py-2 pr-3 font-medium">Dowamlylygy</th>
            <th className="py-2 font-medium">Ýagdaýy</th>
          </tr>
        </thead>
        <tbody>
          {alarms.map((a) => (
            <tr key={a.id} className={`border-b border-line last:border-0 ${a.state === "CLEARED" ? "text-muted" : ""}`}>
              <td className={`${cell} pr-3`}><SeverityTag severity={a.severity} /></td>
              <td className={`${cell} pr-3 font-medium`}>{a.equipment}</td>
              <td className={`${cell} pr-3`}>{a.message}</td>
              {showLine && <td className={`${cell} pr-3`}>{LINE_SHORT[a.lineId] ?? a.lineId}</td>}
              <td className={`${cell} tabular pr-3`}>{clock(a.startedAt)}</td>
              <td className={`${cell} tabular pr-3`}>{duration(a.durationMin)}</td>
              <td className={`${cell} font-medium ${a.state === "ACTIVE" ? "text-bad" : ""}`}>{ALARM_STATE[a.state]}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
