import type { Equipment } from "@/features/data/types";
import { STATUS } from "@/features/i18n/tk";
import { STATUS_DOT } from "./StatusPill";

export function EquipmentGrid({ items }: { items: Equipment[] }) {
  if (items.length === 0) {
    return <p className="py-4 text-sm text-muted">Enjam maglumaty ýok</p>;
  }
  return (
    <ul className="grid grid-cols-1 gap-2 sm:grid-cols-2 xl:grid-cols-3">
      {items.map((e) => (
        <li key={e.id} className={`flex items-center justify-between rounded-md border px-3 py-2.5 ${e.status === "FAULT" ? "border-red-200 bg-red-50" : "border-line"}`}>
          <span className="truncate text-sm font-medium">{e.name}</span>
          <span className="flex shrink-0 items-center gap-1.5 text-xs text-muted">
            <span className={`h-2 w-2 rounded-full ${STATUS_DOT[e.status]} ${e.status === "FAULT" ? "pulse" : ""}`} />
            {STATUS[e.status]}
          </span>
        </li>
      ))}
    </ul>
  );
}
