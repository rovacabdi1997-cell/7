"use client";

import { useState } from "react";
import { AlarmTable, SeverityTag } from "@/components/AlarmTable";
import { PageTitle, WithSnapshot } from "@/components/AppShell";
import { Card } from "@/components/Card";
import type { Snapshot } from "@/features/data/types";
import { LINE_SHORT, duration } from "@/features/i18n/tk";

type StateFilter = "open" | "all";
type LineFilter = "all" | "gipsokarton" | "gury-garyndy";

function Toggle<T extends string>({ value, options, onChange }: { value: T; options: [T, string][]; onChange: (v: T) => void }) {
  return (
    <div className="inline-flex rounded-md border border-line bg-surface p-0.5">
      {options.map(([key, label]) => (
        <button key={key} type="button" onClick={() => onChange(key)}
          className={`rounded px-3 py-1.5 text-sm font-medium ${value === key ? "bg-brand-600 text-white" : "text-muted hover:text-ink"}`}>
          {label}
        </button>
      ))}
    </div>
  );
}

function Body({ s }: { s: Snapshot }) {
  const [state, setState] = useState<StateFilter>("open");
  const [line, setLine] = useState<LineFilter>("all");
  const open = s.alarms.filter((a) => a.state !== "CLEARED");
  const rows = s.alarms.filter((a) => (state === "all" || a.state !== "CLEARED") && (line === "all" || a.lineId === line));
  const stopMinutes = s.lines.reduce((sum, l) => sum + (l.stopMinutesToday.value ?? 0), 0);

  return (
    <>
      <PageTitle title="Duýduryşlar we durmalar">
        <div className="flex flex-wrap gap-2">
          <Toggle value={state} onChange={setState} options={[["open", "Aktiw duýduryşlar"], ["all", "Hemmesi"]]} />
          <Toggle value={line} onChange={setLine} options={[["all", "Ähli liniýalar"], ["gipsokarton", LINE_SHORT.gipsokarton], ["gury-garyndy", LINE_SHORT["gury-garyndy"]]]} />
        </div>
      </PageTitle>
      <div className="mb-4 grid grid-cols-2 gap-4 lg:grid-cols-4">
        {(["CRITICAL", "WARNING", "INFO"] as const).map((sev) => (
          <Card key={sev}>
            <SeverityTag severity={sev} />
            <div className="tabular mt-2 text-3xl font-semibold">{open.filter((a) => a.severity === sev).length}</div>
            <div className="text-xs text-muted">aktiw</div>
          </Card>
        ))}
        <Card>
          <span className="text-sm text-muted">Şu günki durmalar</span>
          <div className="tabular mt-2 text-3xl font-semibold">{duration(stopMinutes)}</div>
          <div className="text-xs text-muted">iki liniýa boýunça jemi</div>
        </Card>
      </div>
      <Card title={state === "open" ? "Aktiw duýduryşlar" : "Şu günki ähli duýduryşlar"}>
        <AlarmTable alarms={rows} />
      </Card>
    </>
  );
}

export function Alarms() {
  return <WithSnapshot>{(s) => <Body s={s} />}</WithSnapshot>;
}
