import type { RunStatus } from "@/features/data/types";
import { STATUS } from "@/features/i18n/tk";

export const STATUS_DOT: Record<RunStatus, string> = {
  RUNNING: "bg-ok",
  STOPPED: "bg-warn",
  FAULT: "bg-bad",
  UNKNOWN: "bg-idle",
};

const STATUS_TEXT: Record<RunStatus, string> = {
  RUNNING: "text-ok",
  STOPPED: "text-warn",
  FAULT: "text-bad",
  UNKNOWN: "text-muted",
};

export function StatusPill({ status, large = false }: { status: RunStatus; large?: boolean }) {
  return (
    <span className={`inline-flex items-center gap-2 font-semibold ${STATUS_TEXT[status]} ${large ? "text-lg" : "text-sm"}`}>
      <span className={`inline-block rounded-full ${STATUS_DOT[status]} ${large ? "h-3.5 w-3.5" : "h-2.5 w-2.5"} ${status === "FAULT" ? "pulse" : ""}`} />
      {STATUS[status]}
    </span>
  );
}
