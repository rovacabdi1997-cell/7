"""Builds the CAD identity link table and its report. Idempotent: same inputs -> same bytes.

    python -X utf8 scripts/cad/build_identity.py            # write backend/cad/identity.json + public copy + report
    python -X utf8 scripts/cad/build_identity.py --check    # fail if committed outputs differ from a fresh build
"""
import argparse
import csv
import io
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "backend"))

from services.cad_identity import load_inputs, validate_identity  # noqa: E402

BACKEND_CAD = ROOT / "backend" / "cad"
PUBLIC_CAD = ROOT / "frontend" / "public" / "cad"
REPORT_DIR = ROOT / "docs" / "cad"


def render_json(doc) -> str:
    return json.dumps(doc, ensure_ascii=False, indent=1) + "\n"


def csv_text(header, rows) -> str:
    buffer = io.StringIO()
    writer = csv.writer(buffer, lineterminator="\r\n")
    writer.writerow(header)
    writer.writerows(rows)
    return "﻿" + buffer.getvalue()


def build_outputs() -> dict[Path, str]:
    plant = json.loads((ROOT / "backend" / "config" / "plant.json").read_text(encoding="utf-8"))
    doc = load_inputs(BACKEND_CAD, plant)
    problems = validate_identity(doc, plant)
    if problems:
        sys.exit("Identity table invalid:\n" + "\n".join(problems))
    outputs: dict[Path, str] = {BACKEND_CAD / "identity.json": render_json(doc)}
    approvals = BACKEND_CAD / "approvals.json"
    if not approvals.exists():
        outputs[approvals] = "[]\n"

    s = doc["summary"]
    rows = doc["rows"]
    model_index_path = PUBLIC_CAD / "model-index.json"
    model_index = json.loads(model_index_path.read_text(encoding="utf-8")) if model_index_path.exists() else None

    outputs[REPORT_DIR / "kimlik-ornekleri.csv"] = csv_text(
        ["cadMarker", "equipmentCode", "matchStatus", "targetAssetId", "targetLineId", "group", "sourceLabel",
         "sourcePartNumber", "candidates", "issues"],
        [[r["cadMarker"], r["equipmentCode"], r["matchStatus"], r["targetAssetId"] or "", r["targetLineId"] or "", r["group"],
          r["sourceLabel"], r["sourcePartNumber"], " | ".join(r["candidates"]), " | ".join(r["issues"])] for r in rows])
    outputs[REPORT_DIR / "baglanmamis-varlyklar.csv"] = csv_text(
        ["assetId", "lineId", "name", "ref", "linkStatus", "cadCodes", "codesMissingInCad", "codesInInventoryWithoutCad"],
        [[a["assetId"], a["lineId"], a["name"], a["ref"], a["linkStatus"], " ".join(a["cadCodes"]),
          " ".join(a["codesMissingInCad"]), " ".join(a["codesInInventoryWithoutCad"])]
         for a in doc["assets"] if a["linkStatus"] != "LINKED"])
    if model_index:
        outputs[REPORT_DIR / "envanter-modelde-yok.csv"] = csv_text(
            ["excel_row", "code", "name_tr", "unit", "plant"],
            [[x["excel_row"], x["code"], x["name_tr"], x["unit"], x["plant"]] for x in model_index["unmatchedInventory"]])
        outputs[REPORT_DIR / "kaynak-kontrol-kayitlari.csv"] = csv_text(
            ["marker", "label", "issue"], [[x["marker"], x["label"], x["issue"]] for x in model_index["issues"]])

    linked = [r for r in rows if r["matchStatus"] in ("CANDIDATE", "EVIDENCED", "APPROVED")]
    ambiguous = [r for r in rows if r["matchStatus"] == "AMBIGUOUS"]
    lines = [
        "# CAD kimlik eşleme raporu", "",
        f"Model SHA256: `{doc['modelRevision']}`  ·  tablo şeması: {doc['schemaVersion']}  ·  hedef: `{doc['targetProject']}`", "",
        "Bu rapor `scripts/cad/build_identity.py` ile üretilir; aynı girdiden aynı baytlar çıkar.",
        (f"**{s['byStatus']['APPROVED']} satır `approvals.json` ile kişi tarafından onaylandı** "
         f"({', '.join(sorted({r['approvedBy'] for r in rows if r['approvedBy']}))}; saha doğrulaması bu onayın parçası değildir)."
         if s["byStatus"]["APPROVED"] else "**Hiçbir satır insan tarafından ONAYLANMADI** (approvals.json boş).")
        + "  İsim benzerliği kanıt sayılmadı.", "",
        "## Özet", "",
        f"- CAD montaj örneği: {s['cadInstances']} (benzersiz kod: {s['uniqueCodes']}); örnekler tek tek korunur.",
        *[f"- {k}: {v}" for k, v in s["byStatus"].items()],
        f"- İzleme varlığı: {s['assets']}; CAD örneğine bağlanan: {s['assetsLinked']}; kodu CAD'de bulunmayan: "
        f"{s['assetsCodeNotInCad']}; CAD kod göndermesi olmayan: {s['assetsWithoutCadCode']}", "",
        "## Bağlantılar (tam kod eşleşmesi)", "",
        "| Harita no | Kod | Örnek (CAD etiketi) | Varlık | Hat | Durum | Onaylayan / tarih | Not |", "|---|---|---|---|---|---|---|---|",
        *[f"| {r['cadMarker']} | {r['equipmentCode']} | {r['sourceLabel']} | {r['targetAssetId']} | {r['targetLineId']} | "
          f"{r['matchStatus']} | {(r['approvedBy'] or '—') + (' · ' + r['approvedAt'] if r['approvedAt'] else '')} | "
          f"{'; '.join(r['issues']) or '—'} |" for r in linked], "",
        f"## Belirsiz ({len(ambiguous)})", "",
        "Kod, `plant.json` içinde belgelenen bir aralığın (örn. 1-005-510…590) içinde ama tek tek yazılmamış. Hedef seçilmedi; "
        "aday listelendi. Onay yalnız `backend/cad/approvals.json` ile verilir.", "",
        "## Modelde karşılığı olmayan izleme varlıkları", "",
        "| Varlık | Hat | Gönderme | Durum | Envanterde var, CAD'de yok |", "|---|---|---|---|---|",
        *[f"| {a['name']} ({a['assetId']}) | {a['lineId']} | {a['ref'] or '—'} | {a['linkStatus']} | "
          f"{' '.join(a['codesInInventoryWithoutCad']) or '—'} |" for a in doc["assets"] if a["linkStatus"] != "LINKED"], "",
        "Gipsokarton varlıklarının göndermeleri Sanjin teklif numaralarıdır; Baumak/CAD kodu değildir. "
        "Bu yüzden CAD'e bağlanmadılar. DWFX'in 7 grubu alçıpan hattının tamamının doğrulandığı anlamına gelmez.", "",
        "## Diğer dosyalar", "",
        "- `kimlik-ornekleri.csv`: 513 CAD örneğinin tamamı ve durumları",
        "- `baglanmamis-varlyklar.csv`: bağlanamayan izleme varlıkları ve nedeni",
        "- `envanter-modelde-yok.csv`: envanterde olup CAD etiketlerinde eşleşmeyen 193 kod",
        "- `kaynak-kontrol-kayitlari.csv`: etiket/Part Number farkı dahil 98 kaynak kontrol kaydı", "",
    ]
    outputs[REPORT_DIR / "KIMLIK-ESLEME-RAPORU.md"] = "\n".join(lines)
    return outputs


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    outputs = build_outputs()
    stale = []
    for path, text in outputs.items():
        if args.check:
            if not path.exists() or path.read_bytes().decode("utf-8") != text:
                stale.append(str(path.relative_to(ROOT)))
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8", newline="\n")
    if not args.check:
        PUBLIC_CAD.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(BACKEND_CAD / "identity.json", PUBLIC_CAD / "identity.json")
        print(f"identity written: {len(outputs)} files")
    elif stale:
        sys.exit("stale outputs: " + ", ".join(stale))
    else:
        print("identity outputs up to date")


if __name__ == "__main__":
    main()
