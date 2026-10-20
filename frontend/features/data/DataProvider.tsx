"use client";

import { createContext, useContext, useEffect, useState, type ReactNode } from "react";
import type { Snapshot } from "./types";
import { presentationSnapshot } from "./presentation";

export type Connection = "connecting" | "live" | "lost";

interface DataState {
  snapshot: Snapshot | null;
  connection: Connection;
  receivedAt: number | null;
}

const DataContext = createContext<DataState>({ snapshot: null, connection: "connecting", receivedAt: null });

// Same host as the page by default, so a TV on the plant network works
// without any per-device setting. `?api=http://IP:8010` overrides it on site,
// so a TV can be pointed at another server without rebuilding.
export function apiBase(): string {
  if (typeof window !== "undefined") {
    const fromUrl = new URLSearchParams(window.location.search).get("api");
    if (fromUrl && /^https?:\/\/[^/?#]+$/.test(fromUrl)) return fromUrl;
  }
  if (process.env.NEXT_PUBLIC_API_URL) return process.env.NEXT_PUBLIC_API_URL;
  if (typeof window === "undefined") return "http://localhost:8010";
  return `${window.location.protocol}//${window.location.hostname}:8010`;
}

const REPLAY = process.env.NEXT_PUBLIC_DATA_SOURCE === "replay";

interface ReplayDay {
  stepMinutes: number;
  dayStartHour: number;
  snapshots: Snapshot[];
}

interface ReplayLoop {
  stepSeconds: number;
  cycleSeconds: number;
  snapshots: Snapshot[];
}

/** Current Asgabat wall clock as an ISO string with the +05:00 offset. */
function asgabatNowIso(): string {
  const shifted = new Date(Date.now() + 5 * 3600 * 1000);
  return `${shifted.toISOString().slice(0, 19)}+05:00`;
}

function onlyLine(snapshot: Snapshot, line?: string): Snapshot {
  if (!line) return snapshot;
  return {
    ...snapshot,
    lines: snapshot.lines.filter((l) => l.id === line),
    alarms: snapshot.alarms.filter((a) => a.lineId === line),
  };
}

/** Offline USB build: picks a pre-generated demo snapshot. Values stay
    labelled SIMULÝASIÝA, as in the API.
    - Line TVs play the 6-minute presentation loop (fault and recovery), in step
      with the clock so both TVs show the same moment; `?sunum=0` switches back.
    - Other screens follow the production day; `?saat=21:15` pins a time of day. */
function useReplay(setState: (s: DataState) => void, line?: string) {
  useEffect(() => {
    if (!REPLAY) return;
    const params = new URLSearchParams(window.location.search);
    const loop = Boolean(line) && params.get("sunum") !== "0";
    let day: ReplayDay | null = null;
    let cycle: ReplayLoop | null = null;
    let timer: ReturnType<typeof setInterval> | undefined;
    const tick = () => {
      const live = asgabatNowIso();
      let snap: Snapshot | undefined;
      let now = live;
      if (cycle) {
        const second = (Number(live.slice(14, 16)) * 60 + Number(live.slice(17, 19))) % cycle.cycleSeconds;
        snap = cycle.snapshots[Math.floor(second / cycle.stepSeconds) % cycle.snapshots.length];
      } else if (day) {
        const pinned = params.get("saat");
        now = pinned && /^\d{2}:\d{2}$/.test(pinned) ? `${live.slice(0, 11)}${pinned}:00+05:00` : live;
        const minute = Number(now.slice(11, 13)) * 60 + Number(now.slice(14, 16));
        const sinceStart = (minute - day.dayStartHour * 60 + 1440) % 1440;
        snap = day.snapshots[Math.floor(sinceStart / day.stepMinutes) % day.snapshots.length];
      }
      if (snap) setState({ snapshot: onlyLine({ ...snap, timestamp: now }, line), connection: "live", receivedAt: Date.now() });
    };
    fetch(loop ? "/replay/sunum.json" : "/replay/day.json")
      .then((r) => r.json())
      .then((data: ReplayDay | ReplayLoop) => {
        if (loop) cycle = data as ReplayLoop;
        else day = data as ReplayDay;
        tick();
        timer = setInterval(tick, loop ? 1000 : 5000);
      })
      .catch(() => setState({ snapshot: null, connection: "lost", receivedAt: null }));
    return () => clearInterval(timer);
  }, [setState, line]);
}

/** `line` limits the stream to one production line (one factory TV). */
export function DataProvider({ children, line }: { children: ReactNode; line?: string }) {
  const [state, setState] = useState<DataState>({ snapshot: null, connection: "connecting", receivedAt: null });
  useReplay(setState, line);

  useEffect(() => {
    if (REPLAY) return;
    // EventSource reconnects by itself after a dropped connection.
    const query = line ? `?line=${encodeURIComponent(line)}` : "";
    const source = new EventSource(`${apiBase()}/api/stream${query}`);
    source.addEventListener("snapshot", (event) => {
      try {
        const snapshot = JSON.parse((event as MessageEvent).data) as Snapshot;
        setState({ snapshot, connection: "live", receivedAt: Date.now() });
      } catch {
        setState((s) => ({ ...s, connection: "lost" }));
      }
    });
    source.onerror = () => setState((s) => ({ ...s, connection: "lost" }));
    return () => source.close();
  }, [line]);

  const presented = state.snapshot ? { ...state, snapshot:presentationSnapshot(state.snapshot) } : state;
  return <DataContext.Provider value={presented}>{children}</DataContext.Provider>;
}

export function useData(): DataState {
  return useContext(DataContext);
}
