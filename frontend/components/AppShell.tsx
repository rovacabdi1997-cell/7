"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import type { ReactNode } from "react";
import { useData } from "@/features/data/DataProvider";
import { NAV, clock, longDate } from "@/features/i18n/tk";
import { ModeBadge } from "./ModeBadge";

export function ConnectionNote() {
  const { snapshot, connection } = useData();
  if (connection === "live") return null;
  if (connection === "connecting" && !snapshot) return null;
  return (
    <div className="border-b border-red-200 bg-red-50 px-6 py-2 text-sm font-medium text-bad" role="alert">
      Serwer bilen aragatnaşyk ýok.
      {snapshot ? ` Görkezilen maglumat ${clock(snapshot.timestamp)} wagtyndaky ýagdaý.` : " Maglumat alynmady."}
    </div>
  );
}

export function SimulationNote() {
  const { snapshot } = useData();
  if (!snapshot || snapshot.dataMode !== "SIMULÝASIÝA") return null;
  return (
    <div className="border-b border-amber-200 bg-amber-50 px-6 py-1.5 text-xs font-medium text-amber-900">
      SIMULÝASIÝA: ekrandaky bahalar hakyky önümçilik maglumaty däl. Hakyky çeşme tassyklanandan soň çalşyrylar.
    </div>
  );
}

export function AppShell({ children }: { children: ReactNode }) {
  const pathname = usePathname();
  const { snapshot } = useData();
  return (
    <div className="flex min-h-screen flex-col lg:flex-row">
      <aside className="border-b border-brand-900 bg-brand-900 text-white lg:w-60 lg:shrink-0 lg:border-b-0">
        <div className="px-5 py-5">
          <div className="text-xs uppercase tracking-[0.18em] text-brand-200">Önümçilik</div>
          <div className="text-lg font-semibold leading-tight">Gözegçilik ulgamy</div>
        </div>
        <nav className="flex gap-1 overflow-x-auto px-3 pb-3 lg:flex-col lg:overflow-visible">
          {NAV.map((item) => {
            const active = item.href === "/" ? pathname === "/" : pathname.startsWith(item.href);
            return (
              <Link key={item.href} href={item.href}
                className={`whitespace-nowrap rounded-md px-3 py-2 text-sm font-medium transition-colors ${active ? "bg-brand-600 text-white" : "text-brand-100 hover:bg-brand-700"}`}>
                {item.label}
              </Link>
            );
          })}
        </nav>
      </aside>
      <div className="flex min-w-0 flex-1 flex-col">
        <header className="flex flex-wrap items-center justify-between gap-3 border-b border-line bg-surface px-6 py-3">
          <div className="text-sm text-muted">{snapshot ? longDate(snapshot.timestamp) : "Maglumat ýüklenýär"}</div>
          <div className="flex items-center gap-4">
            {snapshot && <ModeBadge mode={snapshot.dataMode} />}
            <div className="tabular text-2xl font-semibold text-brand-900">{snapshot ? clock(snapshot.timestamp) : "--:--"}</div>
          </div>
        </header>
        <ConnectionNote />
        <SimulationNote />
        <main className="flex-1 px-4 py-5 sm:px-6">{children}</main>
      </div>
    </div>
  );
}

export function PageTitle({ title, children }: { title: string; children?: ReactNode }) {
  return (
    <div className="mb-5 flex flex-wrap items-end justify-between gap-3">
      <h1 className="text-2xl font-semibold text-brand-900">{title}</h1>
      {children}
    </div>
  );
}

/** Renders children only once a snapshot exists. */
export function WithSnapshot({ children }: { children: (s: NonNullable<ReturnType<typeof useData>["snapshot"]>) => ReactNode }) {
  const { snapshot, connection } = useData();
  if (!snapshot) {
    return (
      <div className="rounded-lg border border-line bg-surface px-6 py-16 text-center text-muted">
        {connection === "lost" ? "Serwer bilen aragatnaşyk ýok. API işleýändigini barlaň." : "Maglumat ýüklenýär…"}
      </div>
    );
  }
  return <>{children(snapshot)}</>;
}
