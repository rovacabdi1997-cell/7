import type { Snapshot } from "./types";

/** Temporary presentation-only correction until the backend publishes the
 * verified Gyra kesiji asset. Never invent equipment or readings for real data.
 * Idempotent: an API supplied cutter always takes precedence. */
export function presentationSnapshot(snapshot: Snapshot): Snapshot {
  return { ...snapshot, lines: snapshot.lines.map(line => {
    if (line.id !== "gipsokarton" || line.mode !== "SIMULÝASIÝA" || line.equipment.some(e => e.assetKey === "gyra-kesiji")) return line;
    const dryer = line.equipment.find(e => e.assetKey === "guradyjy");
    const bundle = line.equipment.find(e => e.assetKey === "bukjalayjy");
    if (!dryer || !bundle) return line;
    const id = "presentation:gk:gyra-kesiji";
    const equipment = line.equipment.flatMap(e => e.id === bundle.id ? [
      { id, assetKey:"gyra-kesiji", name:"Gyra kesiji", kind:"process" as const, order:e.order, status:e.status, mode:"SIMULÝASIÝA" as const },
      { ...e, order:e.order + 1 },
    ] : [{ ...e, order:e.kind !== "feed" && e.order > bundle.order ? e.order + 1 : e.order }]);
    const flow = line.flow.flatMap(f => f.fromId === dryer.id && f.toId === bundle.id ? [
      { ...f, toId:id }, { ...f, fromId:id },
    ] : [f]);
    return { ...line, equipment, flow };
  }) };
}
