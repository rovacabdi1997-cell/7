"use client";

import { useEffect, useState, type CSSProperties, type ReactNode } from "react";
import manifest from "@/public/tv/asset-manifest.json";
import { useData } from "@/features/data/DataProvider";
import type { Alarm, Equipment, Flow, Line, Metric } from "@/features/data/types";
import { MODE, num } from "@/features/i18n/tk";
import "@/styles/tv-line.css";

/** Fixed screens. Machine order and asset keys come from the backend snapshot;
    only the asset line code and the material token are chosen here. */
const SCREENS = {
  "tv-1": { lineId: "gipsokarton", code: "gk", material: "tg-material-board.png" },
  "tv-2": { lineId: "gury-garyndy", code: "gg", material: "tg-material-bag.png" },
} as const;
type TvId = keyof typeof SCREENS;

// Stage geometry in 1920×1080 design pixels (see CLAUDE-HANDOFF.md).
const STAGE_W = 1920;
const STAGE_H = 1080;
const SIDE = 48;
const SCENE_H = 548;

const SEVERITY_RANK = { CRITICAL: 0, WARNING: 1, INFO: 2 } as const;

// Image files are looked up by line + asset key, never by position, so the
// machine order can change without renaming files.
const ASSETS = new Map(
  (manifest as { machines: { line: string; assetKey: string; file: string; moving: string }[] }).machines.map((m) => [
    `${m.line}:${m.assetKey}`,
    { base: `/tv/machines/${m.file.split("/").pop()}`, moving: `/tv/machines/${m.moving.split("/").pop()}` },
  ]),
);

/** Flow animation period: base / max(flowRate, 0.15), never shorter than 0.75 s. */
function flowMs(baseMs: number, rate: number): number {
  return Math.max(750, baseMs / Math.max(rate, 0.15));
}

function asgabatNow(): Date {
  return new Date(Date.now() + 5 * 3600 * 1000);
}

function useStageScale(): number {
  const [scale, setScale] = useState(1);
  useEffect(() => {
    const fit = () => setScale(Math.min(window.innerWidth / STAGE_W, window.innerHeight / STAGE_H));
    fit();
    // ResizeObserver also catches size changes that fire no resize event
    // (display mode switches on the TV PC, kiosk start-up).
    const observer = new ResizeObserver(fit);
    observer.observe(document.documentElement);
    window.addEventListener("resize", fit);
    // Last safety net for kiosk PCs whose display changes while the page is hidden.
    const timer = setInterval(fit, 2000);
    return () => {
      observer.disconnect();
      window.removeEventListener("resize", fit);
      clearInterval(timer);
    };
  }, []);
  return scale;
}

function useTick(ms: number): number {
  const [now, setNow] = useState(() => Date.now());
  useEffect(() => {
    const timer = setInterval(() => setNow(Date.now()), ms);
    return () => clearInterval(timer);
  }, [ms]);
  return now;
}

function Header({ line }: { line: Line | null }) {
  useTick(1000);
  // The page is prerendered at build time; drawing the clock before mount would
  // not match the browser's time (React hydration error #418).
  const [mounted, setMounted] = useState(false);
  useEffect(() => setMounted(true), []);
  const now = mounted ? asgabatNow().toISOString() : "0000-00-00T--:--:--";
  const date = mounted ? `${now.slice(8, 10)}.${now.slice(5, 7)}.${now.slice(0, 4)}` : "";
  return (
    <header className="ltv-header">
      <div className="ltv-brand">
        <img src="/tv/support/logo.png" alt="" />
        <span>TÜRKMEN GIPS HJ</span>
      </div>
      <h1>{line ? line.name.toLocaleUpperCase("tk") : ""}</h1>
      <div className="ltv-clock tabular">
        {now.slice(11, 16)}
        <span>{now.slice(16, 19)}</span>
        <em>{date}</em>
      </div>
    </header>
  );
}

// ---------------------------------------------------------------- scene
//
// Reads like a process-flow diagram: machines stand on the top row, a flow bus
// runs underneath with one numbered node per machine. Material moves along the
// bus only where the backend marks the link active; machines themselves are static.

const MACHINE_Y = 214; // centre of the machine row inside the scene
const BUS_Y = 432; // flow bus
const NODE_R = 18;

interface Placed {
  e: Equipment;
  x: number; // centre
  y: number;
  size: number;
  width?: number;
}

function layout(line: Line): Placed[] {
  const chain = line.equipment.filter((e) => e.kind !== "feed");
  const slot = (STAGE_W - 2 * SIDE) / chain.length;
  const size = SCENE_H * 0.62;
  const placed: Placed[] = chain.map((e, i) => ({ e, x: SIDE + slot * (i + 0.5), y: MACHINE_Y, size, width:slot * 1.08 }));
  // Side feeds (paper reels) stand above and behind the machine they feed.
  for (const e of line.equipment.filter((m) => m.kind === "feed")) {
    const link = line.flow.find((f) => f.fromId === e.id);
    const target = placed.find((p) => p.e.id === link?.toId);
    if (!target) continue;
    placed.push({ e, x: target.x - slot * 0.5, y: 134, size: 140 });
  }
  return placed;
}

type Tone = "running" | "stopped" | "fault" | "nodata";

function tone(e: Equipment): Tone {
  if (e.mode === "ÝOK" || e.status === "UNKNOWN") return "nodata";
  return e.status.toLowerCase() as Tone;
}

function linkPath(a: Placed, b: Placed): string {
  if (a.e.kind === "feed") {
    // Paper web from the reel stand down into the machine it feeds.
    const x1 = a.x + a.size * 0.18;
    const y1 = a.y + a.size * 0.22;
    const x2 = b.x - b.size * 0.12;
    const y2 = b.y - b.size * 0.02;
    return `M${x1},${y1} C${x1 + 50},${y1 + 10} ${x2 - 40},${y2 - 30} ${x2},${y2}`;
  }
  return `M${a.x + NODE_R + 6},${BUS_Y} L${b.x - NODE_R - 6},${BUS_Y}`;
}

function FlowLayer({ placed, flow, material, frozen }: { placed: Placed[]; flow: Flow[]; material: string; frozen: boolean }) {
  const byId = new Map(placed.map((p) => [p.e.id, p]));
  return (
    <svg className="ltv-flow" viewBox={`0 0 ${STAGE_W} ${SCENE_H}`} width={STAGE_W} height={SCENE_H} aria-hidden="true">
      <defs>
        <linearGradient id="ltv-flow-grad" gradientUnits="userSpaceOnUse" x1="0" x2={STAGE_W} y1="0" y2="0">
          <stop offset="0" stopColor="var(--acc2)" />
          <stop offset="1" stopColor="var(--acc)" />
        </linearGradient>
      </defs>
      {flow.map((f) => {
        const a = byId.get(f.fromId);
        const b = byId.get(f.toId);
        if (!a || !b) return null;
        const d = linkPath(a, b);
        const live = f.active && !frozen;
        const feed = a.e.kind === "feed";
        const dur = flowMs(feed ? 2200 : 3000, f.flowRate);
        const midX = (a.x + b.x) / 2;
        return (
          <g
            key={`${f.fromId}-${f.toId}`}
            className={`${live ? "is-live" : "is-idle"} ${feed ? "is-feed" : ""}`}
            style={{ "--dur": `${dur}ms` } as CSSProperties}
          >
            <path d={d} className="rail" />
            <path d={d} className="pulse-line" />
            {!feed && <path d={`M${midX - 7},${BUS_Y - 9} L${midX + 5},${BUS_Y} L${midX - 7},${BUS_Y + 9}`} className="chevron" />}
            {live &&
              !feed &&
              [0, 0.5].map((phase) => (
                <image key={phase} href={`/tv/support/${material}`} width="44" height="44" x="-22" y="-38">
                  <animateMotion dur={`${dur}ms`} begin={`-${(dur * phase) / 1000}s`} repeatCount="indefinite" path={d} />
                </image>
              ))}
          </g>
        );
      })}
    </svg>
  );
}

function Nodes({ placed }: { placed: Placed[] }) {
  return (
    <svg className="ltv-nodes" viewBox={`0 0 ${STAGE_W} ${SCENE_H}`} width={STAGE_W} height={SCENE_H} aria-hidden="true">
      {placed
        .filter((p) => p.e.kind !== "feed")
        .map((p) => {
          const t = tone(p.e);
          return (
            <g key={p.e.id} className={`ltv-node node-${t}`}>
              <line x1={p.x} x2={p.x} y1={p.y + p.size * 0.36} y2={BUS_Y - NODE_R - 4} className="drop" />
              {t === "fault" && <circle cx={p.x} cy={BUS_Y} r={NODE_R} className="ring-pulse" />}
              <circle cx={p.x} cy={BUS_Y} r={NODE_R} className="ring" />
              <circle cx={p.x} cy={BUS_Y} r={7} className="core" />
              <text x={p.x} y={BUS_Y + 52} className="num">{String(p.e.order).padStart(2, "0")}</text>
            </g>
          );
        })}
    </svg>
  );
}

function Machine({ p, code }: { p: Placed; code: string }) {
  const { e, x, y, size } = p;
  const files = ASSETS.get(`${code}:${e.assetKey}`);
  const t = tone(e);
  const width = p.width ?? size;
  const style = { left: x - width / 2, top: y - size / 2, width, height: size } as CSSProperties;
  return (
    <div className={`ltv-machine is-${t} ${e.kind === "feed" ? "is-side-feed" : ""}`} style={style}>
      {files && (
        <>
          <img src={files.base} alt="" draggable={false} />
          {/* Moving parts are drawn in place; the machines never wobble. */}
          <img src={files.moving} alt="" draggable={false} />
        </>
      )}
      <span className={`ltv-lamp lamp-${t}`} />
      <span className="ltv-machine-name">{e.name}</span>
    </div>
  );
}

function Scene({ line, code, material, frozen }: { line: Line; code: string; material: string; frozen: boolean }) {
  const placed = layout(line);
  const allNoData = line.equipment.every((e) => tone(e) === "nodata");
  const running = line.equipment.filter((e) => e.status === "RUNNING").length;
  return (
    <section className={`ltv-scene ltv-scene-${code}`} style={{ height: SCENE_H }}>
      <div className="ltv-scene-tag">
        <b>TEHNOLOGIK AKYM</b>
        <span className="tabular">{running}/{line.equipment.length} enjam işleýär</span>
      </div>
      <Nodes placed={placed} />
      <FlowLayer placed={placed} flow={line.flow} material={material} frozen={frozen} />
      {placed
        .slice()
        .sort((a, b) => a.y - b.y)
        .map((p) => <Machine key={p.e.id} p={p} code={code} />)}
      {allNoData && <div className="ltv-nodata">Maglumat ýok</div>}
    </section>
  );
}

// ---------------------------------------------------------------- KPIs

function Value({ metric, decimals }: { metric: Metric; decimals: number }) {
  const text = num(metric.value, decimals);
  return (
    <div className="ltv-value tabular">
      <strong key={text}>{text}</strong>
      <small>{metric.unit}</small>
    </div>
  );
}

/** 240° arc gauge: share of nominal speed. */
function Gauge({ share }: { share: number }) {
  const r = 62;
  const sweep = 240;
  const start = 150; // degrees, clockwise from +x
  const point = (deg: number, radius = r) => {
    const rad = (deg * Math.PI) / 180;
    return [80 + radius * Math.cos(rad), 80 + radius * Math.sin(rad)];
  };
  const arc = (from: number, to: number) => {
    const [x1, y1] = point(from);
    const [x2, y2] = point(to);
    return `M${x1},${y1} A${r},${r} 0 ${to - from > 180 ? 1 : 0} 1 ${x2},${y2}`;
  };
  const clamped = Math.max(0, Math.min(1, share));
  const ticks = Array.from({ length: 13 }, (_, i) => start + (sweep * i) / 12);
  return (
    <svg className="ltv-gauge" viewBox="0 0 160 150">
      {ticks.map((deg, i) => {
        const [x1, y1] = point(deg, 74);
        const [x2, y2] = point(deg, i % 3 === 0 ? 66 : 70);
        return <line key={deg} x1={x1} y1={y1} x2={x2} y2={y2} className="tick" />;
      })}
      <path d={arc(start, start + sweep)} className="track" />
      {clamped > 0.005 && <path d={arc(start, start + sweep * clamped)} className="fill" />}
      <text x="80" y="86" className="pct tabular">{Math.round(clamped * 100)}%</text>
      <text x="80" y="108" className="cap">NOMINAL</text>
    </svg>
  );
}

function AreaChart({ values, plan }: { values: number[]; plan: number | null }) {
  const W = 340;
  const H = 104;
  if (values.length < 2) return <svg className="ltv-area" viewBox={`0 0 ${W} ${H}`} />;
  const max = Math.max(...values, plan ?? 0, 1) * 1.12;
  const x = (i: number) => (i / (values.length - 1)) * (W - 8) + 4;
  const y = (v: number) => H - 6 - (v / max) * (H - 14);
  const line = values.map((v, i) => `${i ? "L" : "M"}${x(i).toFixed(1)},${y(v).toFixed(1)}`).join(" ");
  const lx = x(values.length - 1);
  const ly = y(values[values.length - 1]);
  return (
    <svg className="ltv-area" viewBox={`0 0 ${W} ${H}`} preserveAspectRatio="none">
      <defs>
        <linearGradient id="ltv-area-grad" x1="0" x2="0" y1="0" y2="1">
          <stop offset="0" stopColor="var(--acc)" stopOpacity="0.22" />
          <stop offset="1" stopColor="var(--acc)" stopOpacity="0" />
        </linearGradient>
      </defs>
      {[0.33, 0.66, 1].map((g) => <line key={g} x1="0" x2={W} y1={H - 6 - g * (H - 14)} y2={H - 6 - g * (H - 14)} className="grid" />)}
      {values.map((_, i) => <line key={i} x1={x(i)} x2={x(i)} y1={H - 6} y2={H - 1} className="hour" />)}
      {plan !== null && <line x1="0" x2={W} y1={y(plan)} y2={y(plan)} className="plan" />}
      <path d={`${line} L${lx},${H - 6} L4,${H - 6} Z`} fill="url(#ltv-area-grad)" />
      <path d={line} className="stroke" />
      <circle cx={lx} cy={ly} r="9" className="halo" />
      <circle cx={lx} cy={ly} r="4.5" className="dot" />
    </svg>
  );
}

function Segments({ pct }: { pct: number }) {
  const count = 32;
  const filled = Math.round((Math.max(0, Math.min(100, pct)) / 100) * count);
  return (
    <div className="ltv-segments">
      {Array.from({ length: count }, (_, i) => <span key={i} className={i < filled ? "on" : ""} />)}
    </div>
  );
}

function Card({ index, label, children, className = "" }: { index: string; label: string; children: ReactNode; className?: string }) {
  return (
    <div className={`ltv-card ${className}`}>
      <div className="ltv-card-head">
        <span className="ltv-index tabular">{index}</span>
        <span className="ltv-label">{label}</span>
      </div>
      {children}
    </div>
  );
}

function AlarmCard({ alarms }: { alarms: Alarm[] }) {
  const open = alarms
    .filter((a) => a.state !== "CLEARED")
    .sort((a, b) => SEVERITY_RANK[a.severity] - SEVERITY_RANK[b.severity] || b.startedAt.localeCompare(a.startedAt));
  const critical = open.some((a) => a.severity === "CRITICAL");
  return (
    <Card index="04" label="Işjeň duýduryş" className={`ltv-alarms ${critical ? "has-critical" : ""}`}>
      <div className="ltv-alarm-body">
        <strong className="tabular">{open.length}</strong>
        <ul>
          {open.length === 0 && <li className="calm">Duýduryş ýok</li>}
          {open.slice(0, 3).map((a) => (
            <li key={a.id} className={`sev-${a.severity.toLowerCase()}`}>
              <b>{a.equipment.toLocaleUpperCase("tk")}</b>
              <span className="tabular">{a.durationMin < 1 ? "<1" : num(a.durationMin, 0)} min</span>
            </li>
          ))}
        </ul>
      </div>
    </Card>
  );
}

function Kpis({ line, alarms }: { line: Line; alarms: Alarm[] }) {
  const board = line.unit !== "t";
  const share = Math.max(0, ...line.flow.map((f) => f.flowRate));
  const done = line.trend.slice(0, -1); // the running hour would look like a drop
  const planHour = done.find((t) => t.plan !== null)?.plan ?? null;
  return (
    <section className="ltv-kpis">
      <Card index="01" label="Liniýanyň tizligi">
        <div className="ltv-speed">
          <Value metric={line.speed} decimals={1} />
          <Gauge share={line.status === "RUNNING" ? share : 0} />
        </div>
      </Card>
      <Card index="02" label="Şu günki önüm">
        <Value metric={line.outputToday} decimals={board ? 0 : 1} />
        <AreaChart values={done.map((t) => t.actual ?? 0)} plan={planHour} />
      </Card>
      <Card index="03" label="Meýilnama">
        <Value metric={line.fulfilmentPct} decimals={1} />
        <Segments pct={line.fulfilmentPct.value ?? 0} />
        <div className="ltv-sub tabular">
          {num(line.outputToday.value, board ? 0 : 1)} / {num(line.planToDate.value, board ? 0 : 1)} {line.unit}
        </div>
      </Card>
      <AlarmCard alarms={alarms} />
    </section>
  );
}

function SourceStrip({ mode, stale, lastIso, shift }: { mode: string; stale: boolean; lastIso: string | null; shift: string | null }) {
  return (
    <footer className={`ltv-strip ${stale ? "is-stale" : ""}`}>
      <span className="ltv-mode">{mode}</span>
      <span className={`ltv-beat ${stale ? "" : "on"}`} />
      {stale ? (
        <span className="ltv-lost">Baglanyşyk ýok{lastIso ? ` · soňky maglumat ${lastIso.slice(11, 19)}` : ""}</span>
      ) : (
        <span className="tabular">Soňky täzelenme {lastIso ? lastIso.slice(11, 19) : "—"}</span>
      )}
      <span>Diňe okamak · PLC ýazgy ýok</span>
      {shift && <span className="ltv-shift">{shift}</span>}
    </footer>
  );
}

export function LineTv({ tvId }: { tvId: TvId }) {
  const screen = SCREENS[tvId];
  const { snapshot, connection, receivedAt } = useData();
  const scale = useStageScale();
  const now = useTick(1000);
  const line = snapshot?.lines.find((l) => l.id === screen.lineId) ?? null;
  const staleMs = (snapshot?.staleAfterSec ?? 15) * 1000;
  const stale = connection === "lost" || !receivedAt || now - receivedAt > staleMs;
  const mode = line?.mode === "SIMULÝASIÝA" ? "SIMULATED · SIMULÝASIÝA" : snapshot ? MODE[line?.mode ?? snapshot.dataMode] : MODE["ÝOK"];
  const alarms = (snapshot?.alarms ?? []).filter(a => a.lineId === screen.lineId);
  const critical = alarms.find(a => a.state !== "CLEARED" && a.severity === "CRITICAL");

  return (
    <div className="ltv-viewport">
      <div className="ltv-stage" style={{ width: STAGE_W, height: STAGE_H, transform: `translate(-50%, -50%) scale(${scale})` }}>
        <Header line={line} />
        <main className={`ltv-main ${stale ? "is-stale" : ""}`}>
          {line ? (
            <>
              <Scene line={line} code={screen.code} material={screen.material} frozen={stale} />
              {critical && <div className="ltv-critical" role="alert"><b>{critical.equipment}</b><span>Näme etmeli: Çalşyk ýolbaşçysyna habar beriň.</span></div>}
              <Kpis line={line} alarms={alarms} />
            </>
          ) : (
            <div className="ltv-nodata">{connection === "connecting" ? "Birikdirilýär…" : "Maglumat ýok"}</div>
          )}
        </main>
        <SourceStrip mode={mode} stale={stale} lastIso={snapshot?.timestamp ?? null} shift={snapshot?.shift.current.name ?? null} />
      </div>
    </div>
  );
}
