"use client";

import { createContext, useContext, useEffect, useState, type ReactNode } from "react";
import type { Snapshot } from "./types";

export type Connection = "connecting" | "live" | "lost";

interface DataState {
  snapshot: Snapshot | null;
  connection: Connection;
  receivedAt: number | null;
}

const DataContext = createContext<DataState>({ snapshot: null, connection: "connecting", receivedAt: null });

// Same host as the page by default, so a TV on the plant network works
// without any per-device setting.
export function apiBase(): string {
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

/** Current Asgabat wall clock as an ISO string with the +05:00 offset. */
function asgabatNowIso(): string {
  const shifted = new Date(Date.now() + 5 * 3600 * 1000);
  return `${shifted.toISOString().slice(0, 19)}+05:00`;
}

/** Offline USB build: picks the pre-generated demo snapshot for the current
    time of day. Values stay labelled SIMULÝASIÝA, as in the API. */
function useReplay(setState: (s: DataState) => void) {
  useEffect(() => {
    if (!REPLAY) return;
    let day: ReplayDay | null = null;
    let timer: ReturnType<typeof setInterval> | undefined;
    const tick = () => {
      if (!day) return;
      // ?saat=21:15 pins the presentation to a chosen time of day.
      const pinned = new URLSearchParams(window.location.search).get("saat");
      const live = asgabatNowIso();
      const now = pinned && /^\d{2}:\d{2}$/.test(pinned) ? `${live.slice(0, 11)}${pinned}:00+05:00` : live;
      const minute = Number(now.slice(11, 13)) * 60 + Number(now.slice(14, 16));
      const sinceStart = (minute - day.dayStartHour * 60 + 1440) % 1440;
      const snap = day.snapshots[Math.floor(sinceStart / day.stepMinutes) % day.snapshots.length];
      setState({ snapshot: { ...snap, timestamp: now }, connection: "live", receivedAt: Date.now() });
    };
    fetch("/replay/day.json")
      .then((r) => r.json())
      .then((data: ReplayDay) => {
        day = data;
        tick();
        timer = setInterval(tick, 5000);
      })
      .catch(() => setState({ snapshot: null, connection: "lost", receivedAt: null }));
    return () => clearInterval(timer);
  }, [setState]);
}

export function DataProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<DataState>({ snapshot: null, connection: "connecting", receivedAt: null });
  useReplay(setState);

  useEffect(() => {
    if (REPLAY) return;
    // EventSource reconnects by itself after a dropped connection.
    const source = new EventSource(`${apiBase()}/api/stream`);
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
  }, []);

  return <DataContext.Provider value={state}>{children}</DataContext.Provider>;
}

export function useData(): DataState {
  return useContext(DataContext);
}
