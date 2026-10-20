"use client";

import { AlarmTable } from "@/components/AlarmTable";
import { PageTitle, WithSnapshot } from "@/components/AppShell";
import { Card } from "@/components/Card";
import { EquipmentGrid } from "@/components/EquipmentGrid";
import { Kpi, Progress } from "@/components/Kpi";
import { StatusPill } from "@/components/StatusPill";
import { ProcessFlow } from "@/components/ProcessFlow";
import { TrendChart, TrendLegend } from "@/components/TrendChart";
import type { Line, Snapshot } from "@/features/data/types";
import { duration, num } from "@/features/i18n/tk";

function Board({ l }: { l: Line }) {
  return (
    <>
      <Kpi label="Häzirki önümçilik tizligi" metric={l.speed} decimals={1} emphasis />
      <Kpi label="Öndürilen mukdar" metric={l.outputToday} emphasis />
      <Kpi label="Durmalar" metric={l.stopsToday} hint={`Jemi: ${duration(l.stopMinutesToday.value ?? 0)}`} emphasis />
      <Kpi label="Ýalňyşlyklar" metric={l.errorsToday} emphasis />
    </>
  );
}

function DryMix({ l }: { l: Line }) {
  return (
    <>
      <Kpi label="Häzirki öndürijilik" metric={l.speed} decimals={1} emphasis />
      <Kpi label="Önüm mukdary" metric={l.outputToday} decimals={1} emphasis />
      <Kpi label="Gaplanan halta sany" metric={l.bagsToday} emphasis />
      <Kpi label="Durmalar" metric={l.stopsToday} hint={`Jemi: ${duration(l.stopMinutesToday.value ?? 0)}`} emphasis />
    </>
  );
}

function Body({ s, lineId }: { s: Snapshot; lineId: Line["id"] }) {
  const l = s.lines.find((x) => x.id === lineId);
  if (!l) return <p className="text-muted">Liniýa tapylmady</p>;
  const isBoard = lineId === "gipsokarton";
  const alarms = s.alarms.filter((a) => a.lineId === lineId);
  return (
    <>
      <PageTitle title={l.name}>
        <div className="flex items-center gap-3 text-sm text-muted">
          {l.section}
          <span className="h-4 w-px bg-line" />
          <span>{isBoard ? "Liniýanyň ýagdaýy" : "Önümçilik ýagdaýy"}:</span>
          <StatusPill status={l.status} large />
        </div>
      </PageTitle>

      <div className="mb-4"><ProcessFlow line={l} /></div>

      <Card>
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 xl:grid-cols-4">{isBoard ? <Board l={l} /> : <DryMix l={l} />}</div>
      </Card>

      <div className="mt-4 grid grid-cols-1 gap-4 xl:grid-cols-3">
        <Card title={isBoard ? "Önümçilik meýilnamasy" : "Meýilnama we ýerine ýetiriliş"}>
          <div className="space-y-4">
            <Kpi label="Gündelik meýilnama" metric={l.planToday} />
            <Kpi label="Şu wagta çenli meýilnama" metric={l.planToDate} />
            <div>
              <Kpi label="Ýerine ýetiriliş" metric={l.fulfilmentPct} decimals={1} />
              <div className="mt-2"><Progress pct={l.fulfilmentPct.value} /></div>
            </div>
            <Kpi label="Önümçilik netijeliligi" metric={l.efficiencyPct} decimals={1} hint={l.efficiencyPct.source} />
          </div>
        </Card>
        <Card title="Önümçilik tendensiýasy" aside={<TrendLegend unit={l.unit} />} className="xl:col-span-2">
          <TrendChart points={l.trend} unit={l.unit} height={260} />
        </Card>
      </div>

      <div className="mt-4 grid grid-cols-1 gap-4 xl:grid-cols-2">
        <Card title="Enjamlaryň ýagdaýy"><EquipmentGrid items={l.equipment} /></Card>
        <Card title={isBoard ? "Durmalar we ýalňyşlyklar" : "Duýduryşlar"} aside={<span className="tabular text-xs text-muted">{num(alarms.length)} ýazgy</span>}>
          <AlarmTable alarms={alarms} showLine={false} compact />
        </Card>
      </div>
    </>
  );
}

export function LineScreen({ lineId }: { lineId: Line["id"] }) {
  return <WithSnapshot>{(s) => <Body s={s} lineId={lineId} />}</WithSnapshot>;
}
