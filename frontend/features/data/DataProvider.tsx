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

export function DataProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<DataState>({ snapshot: null, connection: "connecting", receivedAt: null });

  useEffect(() => {
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
