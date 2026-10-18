"use client";

import { useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import { STATUS_DOT } from "@/components/StatusPill";
import { TrendChart } from "@/components/TrendChart";
import { useData } from "@/features/data/DataProvider";
import type { Line, Metric, Snapshot } from "@/features/data/types";
import { LINE_SHORT, MODE, SEVERITY, STATUS, clock, duration, num } from "@/features/i18n/tk";

const SLIDES = ["Umumy ýagdaý", LINE_SHORT.gipsokarton, LINE_SHORT["gury-garyndy"], "Duýduryşlar"];

function Big({ label, metric, decimals = 0 }: { label: string; metric: Metric | null | undefined; decimals?: number }) {
  return (
    <div>
      <div className="text-[1.6em] text-brand-100">{label}</div>
      <div className="tabular text-[4.6em] font-semibold leading-none">
        {num(metric?.value ?? null, decimals)}
        <span className="ml-3 text-[0.4em] font-medium text-brand-200">{metric?.unit}</span>
      </div>
    </div>
  );
}

function LineStatus({ l }: { l: Line }) {
  return (
    <span className="inline-flex items-center gap-[0.5em] text-[1.8em] font-semibold">
      <span className={`h-[0.7em] w-[0.7em] rounded-full ${STATUS_DOT[l.status]} ${l.status === "FAULT" ? "pulse" : ""}`} />
      {STATUS[l.status]}
    </span>
  );
}

function OverviewSlide({ s }: { s: Snapshot }) {
  return (
    <div className="grid h-full grid-cols-2 gap-[2em]">
      {s.lines.map((l) => (
        <div key={l.id} className="flex flex-col justify-between rounded-[0.6em] bg-brand-700/60 p-[2em]">
          <div className="flex items-center justify-between">
            <h2 className="text-[2.6em] font-semibold">{LINE_SHORT[l.id]}</h2>
            <LineStatus l={l} />
          </div>
          <Big label="Şu günki önümçilik" metric={l.outputToday} decimals={l.unit === "t" ? 1 : 0} />
          <div className="grid grid-cols-2 gap-[1.5em]">
            <Big label="Ýerine ýetiriliş" metric={l.fulfilmentPct} decimals={1} />
            <Big label="Netijelilik" metric={l.efficiencyPct} decimals={1} />
          </div>
        </div>
      ))}
    </div>
  );
}

function LineSlide({ l }: { l: Line }) {
  return (
    <div className="flex h-full flex-col gap-[2em]">
      <div className="flex items-center justify-between">
        <h2 className="text-[3em] font-semibold">{l.name}</h2>
        <LineStatus l={l} />
      </div>
      <div className="grid grid-cols-4 gap-[2em]">
        <Big label={l.id === "gipsokarton" ? "Tizlik" : "Öndürijilik"} metric={l.speed} decimals={1} />
        <Big label="Öndürilen" metric={l.outputToday} decimals={l.unit === "t" ? 1 : 0} />
        {l.bagsToday ? <Big label="Gaplanan halta" metric={l.bagsToday} /> : <Big label="Meýilnama" metric={l.planToday} />}
        <Big label="Durmalar" metric={l.stopsToday} />
      </div>
      <div className="flex-1 rounded-[0.6em] bg-white p-[1.2em] text-ink">
        <TrendChart points={l.trend} unit={l.unit} width={1500} height={440} fontSize={22} />
      </div>
    </div>
  );
}

function AlarmSlide({ s }: { s: Snapshot }) {
  const open = s.alarms.filter((a) => a.state !== "CLEARED").slice(0, 6);
  return (
    <div className="flex h-full flex-col gap-[1.2em]">
      <h2 className="text-[3em] font-semibold">Aktiw duýduryşlar</h2>
      {open.length === 0 && <div className="text-[2.4em] text-brand-200">Işjeň duýduryş ýok</div>}
      {open.map((a) => (
        <div key={a.id} className={`flex items-center justify-between rounded-[0.5em] px-[1.2em] py-[0.8em] text-[1.9em] ${a.severity === "CRITICAL" ? "bg-bad" : a.severity === "WARNING" ? "bg-warn" : "bg-brand-700"}`}>
          <span className="font-semibold">{SEVERITY[a.severity]} · {a.equipment}</span>
          <span className="mx-[1em] flex-1 truncate">{a.message}</span>
          <span className="tabular">{clock(a.startedAt)} · {duration(a.durationMin)}</span>
        </div>
      ))}
    </div>
  );
}

export function TvView() {
  const { snapshot: s, connection } = useData();
  const params = useSearchParams();
  const fixed = params.get("slide");
  const seconds = Math.max(5, Number(params.get("interval") ?? 15));
  const [index, setIndex] = useState(fixed ? Number(fixed) % SLIDES.length : 0);

  useEffect(() => {
    if (fixed) return;
    const timer = setInterval(() => setIndex((i) => (i + 1) % SLIDES.length), seconds * 1000);
    return () => clearInterval(timer);
  }, [fixed, seconds]);

  const fullscreen = () => {
    if (document.fullscreenElement) document.exitFullscreen();
    else document.documentElement.requestFullscreen().catch(() => undefined);
  };

  const critical = s?.alarms.find((a) => a.severity === "CRITICAL" && a.state !== "CLEARED");

  return (
    <div className="tv-root flex h-screen flex-col overflow-hidden bg-brand-900 text-white">
      <header className="flex items-center justify-between px-[2em] py-[1em]">
        <div className="flex items-center gap-[1.2em]">
          <span className="text-[2em] font-semibold">{SLIDES[index]}</span>
          <span className="flex gap-[0.4em]">
            {SLIDES.map((name, i) => <span key={name} className={`h-[0.5em] w-[1.6em] rounded-full ${i === index ? "bg-white" : "bg-brand-700"}`} />)}
          </span>
        </div>
        <div className="flex items-center gap-[1.5em]">
          {s && (
            <span className={`rounded-[0.3em] px-[0.8em] py-[0.3em] text-[1.2em] font-semibold ${s.dataMode === "SIMULÝASIÝA" ? "bg-amber-300 text-amber-950" : "bg-brand-700"}`}>
              {MODE[s.dataMode]}
            </span>
          )}
          <span className="tabular text-[2.6em] font-semibold">{s ? clock(s.timestamp) : "--:--"}</span>
          <button type="button" onClick={fullscreen} className="rounded-[0.3em] border border-brand-400 px-[0.8em] py-[0.3em] text-[1em] text-brand-100 hover:bg-brand-700">
            Doly ekran
          </button>
        </div>
      </header>

      {connection === "lost" && (
        <div className="bg-bad px-[2em] py-[0.5em] text-[1.4em] font-semibold">Serwer bilen aragatnaşyk ýok{s ? ` · soňky maglumat ${clock(s.timestamp)}` : ""}</div>
      )}

      <main className="min-h-0 flex-1 px-[2em] pb-[1.5em]">
        {!s ? (
          <div className="flex h-full items-center justify-center text-[2.4em] text-brand-200">Maglumat ýüklenýär…</div>
        ) : index === 0 ? <OverviewSlide s={s} />
          : index === 3 ? <AlarmSlide s={s} />
            : <LineSlide l={s.lines[index - 1]} />}
      </main>

      {critical && (
        <footer className="pulse bg-bad px-[2em] py-[0.7em] text-[1.9em] font-semibold">
          {SEVERITY.CRITICAL}: {LINE_SHORT[critical.lineId]} · {critical.equipment} · {critical.message}
        </footer>
      )}
    </div>
  );
}
