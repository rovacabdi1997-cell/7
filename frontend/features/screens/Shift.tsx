"use client";

import { PageTitle, WithSnapshot } from "@/components/AppShell";
import { Card } from "@/components/Card";
import { Kpi, Progress } from "@/components/Kpi";
import { ModeBadge } from "@/components/ModeBadge";
import type { Snapshot } from "@/features/data/types";
import { duration } from "@/features/i18n/tk";

function Body({ s }: { s: Snapshot }) {
  const sh = s.shift;
  const total = sh.elapsedMin + sh.remainingMin;
  return (
    <>
      <PageTitle title="Çalşyk we işgärler">
        <ModeBadge mode={sh.mode} />
      </PageTitle>
      <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
        <Card title="Çalşyk">
          <div className="text-3xl font-semibold text-brand-900">{sh.current.name}</div>
          <div className="mt-4 text-sm text-muted">Iş wagty</div>
          <div className="tabular text-xl font-semibold">{sh.current.start} – {sh.current.end}</div>
          <div className="mt-3"><Progress pct={total ? (sh.elapsedMin / total) * 100 : null} /></div>
          <div className="tabular mt-2 flex justify-between text-xs text-muted">
            <span>Geçen: {duration(sh.elapsedMin)}</span>
            <span>Galan: {duration(sh.remainingMin)}</span>
          </div>
        </Card>
        <Card title="Arakesme wagty">
          <div className="tabular text-3xl font-semibold">{sh.current.breakStart} – {sh.current.breakEnd}</div>
          <div className={`mt-3 text-sm font-medium ${sh.onBreak ? "text-warn" : "text-muted"}`}>
            {sh.onBreak ? "Häzir arakesme" : "Arakesme däl"}
          </div>
          <div className="mt-6 text-sm text-muted">Nobatdaky çalşyk</div>
          <div className="text-xl font-semibold">{sh.next.name}</div>
          <div className="tabular text-sm text-muted">{sh.next.start} – {sh.next.end}</div>
        </Card>
        <Card title="Işgärleriň sany">
          <Kpi label="Häzirki çalşykda" metric={sh.staffCount} emphasis />
          <p className="mt-4 text-xs text-muted">{sh.staffCount.source}</p>
        </Card>
      </div>
      <div className="mt-4 grid grid-cols-1 gap-4 lg:grid-cols-2">
        <Card title="Howpsuzlyk bildirişleri">
          <ul className="space-y-3">
            {sh.safetyNotices.map((n) => (
              <li key={n} className="flex gap-3 text-base">
                <span className="mt-2 h-2 w-2 shrink-0 rounded-full bg-warn" />{n}
              </li>
            ))}
          </ul>
        </Card>
        <Card title="Çalşyk tertibi">
          <table className="w-full text-sm">
            <thead className="text-xs uppercase tracking-wide text-muted">
              <tr className="border-b border-line">
                <th className="py-2 text-left font-medium">Çalşyk</th>
                <th className="py-2 text-left font-medium">Iş wagty</th>
                <th className="py-2 text-left font-medium">Arakesme</th>
              </tr>
            </thead>
            <tbody>
              {sh.schedule.map((x) => (
                <tr key={x.id} className={`border-b border-line last:border-0 ${x.id === sh.current.id ? "font-semibold text-brand-700" : ""}`}>
                  <td className="py-2.5">{x.name}</td>
                  <td className="tabular py-2.5">{x.start} – {x.end}</td>
                  <td className="tabular py-2.5">{x.breakStart} – {x.breakEnd}</td>
                </tr>
              ))}
            </tbody>
          </table>
          <p className="mt-3 text-xs text-muted">{sh.source}</p>
        </Card>
      </div>
    </>
  );
}

export function Shift() {
  return <WithSnapshot>{(s) => <Body s={s} />}</WithSnapshot>;
}
