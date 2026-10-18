import type { ReactNode } from "react";

export function Card({ title, aside, children, className = "" }: {
  title?: string;
  aside?: ReactNode;
  children: ReactNode;
  className?: string;
}) {
  return (
    <section className={`rounded-lg border border-line bg-surface ${className}`}>
      {title && (
        <header className="flex items-center justify-between gap-3 border-b border-line px-5 py-3">
          <h2 className="text-sm font-semibold uppercase tracking-wide text-muted">{title}</h2>
          {aside}
        </header>
      )}
      <div className="px-5 py-4">{children}</div>
    </section>
  );
}
