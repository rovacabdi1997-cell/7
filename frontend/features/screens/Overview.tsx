"use client";

import Link from "next/link";
import { Card } from "@/components/Card";
import { Kpi, Progress } from "@/components/Kpi";
import { ModeBadge } from "@/components/ModeBadge";
import { StatusPill } from "@/components/StatusPill";
import { SeverityTag } from "@/components/AlarmTable";
import { TrendChart, TrendLegend } from "@/components/TrendChart";
import { PageTitle, WithSnapshot } from "@/components/AppShell";
import { ProcessFlow } from "@/components/ProcessFlow";
import type { Line, Snapshot } from "@/features/data/types";
import { LINE_SHORT, clock, duration, num } from "@/features/i18n/tk";

function PerLine({ title, lines, pick, decimals = 0 }: {
  title: string;
  lines: Line[];
  pick: (l: Line) => Line["outputToday"];
  decimals?: number;
}) {
  return (
    <Card title={title}>
      <div className="space-y-4">
        {lines.map((l) => <Kpi key={l.id} label={LINE_SHORT[l.id]} metric={pick(l)} decimals={decimals} />)}
      </div>
    </Card>
  );
}

function Body({ s }: { s: Snapshot }) {
  const open = s.alarms.filter((a) => a.state !== "CLEARED");
  const running = s.lines.filter((l) => l.status === "RUNNING").length;
  return (
    <>
      <PageTitle title="Baş dolandyryş paneli" />
      <div className="mb-4 grid grid-cols-1 gap-4 2xl:grid-cols-2">
        {s.lines.map((line) => <ProcessFlow key={line.id} line={line} compact />)}
      </div>
      <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-4">
        <PerLine title="Umumy önümçilik" lines={s.lines} pick={(l) => l.outputMonth} />
        <PerLine title="Şu günki önümçilik" lines={s.lines} pick={(l) => l.outputToday} />
        <PerLine title="Meýilnama" lines={s.lines} pick={(l) => l.planToday} />
        <Card title="Ýerine ýetiriliş">
          <div className="space-y-4">
            {s.lines.map((l) => (
              <div key={l.id}>
                <Kpi label={LINE_SHORT[l.id]} metric={l.fulfilmentPct} decimals={1} />
                <div className="mt-2"><Progress pct={l.fulfilmentPct.value} /></div>
              </div>
            ))}
          </div>
        </Card>

        <Card title="Işleýän liniýalar">
          <div className="tabular text-4xl font-semibold">{running}<span className="text-xl text-muted"> / {s.lines.length}</span></div>
          <ul className="mt-4 space-y-2">
            {s.lines.map((l) => (
              <li key={l.id} className="flex items-center justify-between">
                <Link href={`/${l.id}`} className="text-sm font-medium hover:text-brand-600">{LINE_SHORT[l.id]}</Link>
                <StatusPill status={l.status} />
              </li>
            ))}
          </ul>
        </Card>
        <Card title="Duýduryşlar" aside={<Link href="/duyduryslar" className="text-xs font-medium text-brand-600">Hemmesi</Link>}>
          <div className="flex gap-6">
            {(["CRITICAL", "WARNING", "INFO"] as const).map((sev) => (
              <div key={sev}>
                <div className="tabular text-3xl font-semibold">{open.filter((a) => a.severity === sev).length}</div>
                <SeverityTag severity={sev} />
              </div>
            ))}
          </div>
          <ul className="mt-4 space-y-1.5 text-sm">
            {open.slice(0, 3).map((a) => (
              <li key={a.id} className="truncate"><span className="tabular text-muted">{clock(a.startedAt)}</span> {a.equipment}: {a.message}</li>
            ))}
            {open.length === 0 && <li className="text-muted">Işjeň duýduryş ýok</li>}
          </ul>
        </Card>
        <PerLine title="Önümçilik netijeliligi" lines={s.lines} pick={(l) => l.efficiencyPct} decimals={1} />
        <Card title="Çalşyk ýagdaýy" aside={<ModeBadge mode={s.shift.mode} size="sm" />}>
          <div className="text-2xl font-semibold">{s.shift.current.name}</div>
          <div className="tabular mt-1 text-sm text-muted">{s.shift.current.start}–{s.shift.current.end}</div>
          <div className="mt-3 text-sm">Galan wagt: <span className="tabular font-semibold">{duration(s.shift.remainingMin)}</span></div>
          <div className="mt-1 text-sm">{s.shift.onBreak ? <span className="font-semibold text-warn">Arakesme wagty</span> : <>Nobatdaky: {s.shift.next.name} ({s.shift.next.start})</>}</div>
        </Card>
      </div>

      <div className="mt-4 grid grid-cols-1 gap-4 xl:grid-cols-2">
        {s.lines.map((l) => (
          <Card key={l.id} title={`${LINE_SHORT[l.id]}: önümçilik tendensiýasy`} aside={<TrendLegend unit={l.unit} />}>
            <TrendChart points={l.trend} unit={l.unit} />
            <div className="mt-2 text-xs text-muted">Durmalar: {num(l.stopsToday.value)} ({duration(l.stopMinutesToday.value ?? 0)})</div>
          </Card>
        ))}
      </div>
    </>
  );
}

export function Overview() {
  return <WithSnapshot>{(s) => <Body s={s} />}</WithSnapshot>;
}
