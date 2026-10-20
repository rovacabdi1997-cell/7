import type { Equipment, Line } from "@/features/data/types";
import { num, STATUS } from "@/features/i18n/tk";
import { STATUS_DOT } from "./StatusPill";

function MachineIcon({ index }: { index: number }) {
  const variant = index % 5;
  return (
    <svg viewBox="0 0 96 72" aria-hidden="true" className="process-icon">
      <g fill="none" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2">
        {variant === 0 && <><path d="M24 17h48l-8 24H32z" /><path d="M37 41v15m22-15v15M26 56h44" /><path d="M38 24h20" /></>}
        {variant === 1 && <><rect x="27" y="13" width="42" height="45" rx="5" /><path d="M48 13V5m-12 53v8m24-8v8M34 30h28M39 38c7 7 11 7 18 0" /></>}
        {variant === 2 && <><path d="M13 48h70M18 39h57l8 9H13z" /><circle cx="26" cy="57" r="6" /><circle cx="68" cy="57" r="6" /><path d="M31 28h26l8 11H23z" /></>}
        {variant === 3 && <><path d="M25 60V22h46v38M20 60h56" /><path d="M34 22V11h28v11M34 34h28M34 45h28" /><path d="M42 60V45m12 15V45" /></>}
        {variant === 4 && <><path d="M22 58h52V28H22z" /><path d="M30 28V15h36v13M32 40h32M38 58V46h20v12" /><circle cx="31" cy="64" r="3" /><circle cx="65" cy="64" r="3" /></>}
      </g>
    </svg>
  );
}

function ProcessNode({ equipment, index }: { equipment: Equipment; index: number }) {
  return (
    <li className={`process-node process-${equipment.status.toLowerCase()}`}>
      <span className="process-step">{String(index + 1).padStart(2, "0")}</span>
      <MachineIcon index={index} />
      <span className="process-name">{equipment.name}</span>
      <span className="process-state">
        <span className={`process-dot ${STATUS_DOT[equipment.status]} ${equipment.status === "FAULT" ? "pulse" : ""}`} />
        {STATUS[equipment.status]}
      </span>
    </li>
  );
}

export function ProcessFlow({ line, compact = false, showHeader = true }: { line: Line; compact?: boolean; showHeader?: boolean }) {
  const completion = Math.max(0, Math.min(100, line.fulfilmentPct.value ?? 0));
  return (
    <section className={`process-flow ${compact ? "process-flow-compact" : ""}`}>
      {showHeader && (
        <header className="process-flow-header">
          <div>
            <span className="process-kicker">{line.section} · önümçilik akymy</span>
            <h3>{line.name}</h3>
          </div>
          <div className="process-output tabular">
            <span>Şu gün</span>
            <strong>{num(line.outputToday.value, line.unit === "t" ? 1 : 0)}</strong>
            <small>{line.outputToday.unit}</small>
          </div>
        </header>
      )}
      <div className="process-rail-wrap">
        <ol className="process-rail">
          {line.equipment.map((equipment, index) => <ProcessNode key={equipment.id} equipment={equipment} index={index} />)}
        </ol>
      </div>
      <svg className="process-blueprint" viewBox="0 0 900 250" preserveAspectRatio="none" aria-hidden="true">
        <g fill="none" stroke="currentColor" strokeWidth="2">
          <path d="M12 222h876M42 222v-52h92v52m22 0V96h112v126m18 0V146h104v76m24 0V68h118v154m22 0v-89h98v89m24 0V111h78v111" />
          <path d="M61 170v-36h54v36m62-74V53h23v43m42 0V44h18v52m54 50v-35h48v35m72-78V25h54v43m18 0V40h20v28m51 65V83h48v50m62-22V70h20v41m28 0V48h16v63" />
          <path d="M38 188h126v-24h133v30h124v-41h147v28h112v-34h164" />
          <circle cx="297" cy="194" r="8" /><circle cx="421" cy="153" r="8" /><circle cx="680" cy="181" r="8" />
        </g>
      </svg>
      {!compact && (
        <div className="process-progress">
          <div className="process-progress-copy">
            <span>Meýilnama boýunça ýerine ýetiriliş</span>
            <strong className="tabular">{num(line.fulfilmentPct.value, 1)}%</strong>
          </div>
          <div className="process-progress-track"><span style={{ width: `${completion}%` }} /></div>
        </div>
      )}
    </section>
  );
}
