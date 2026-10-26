"""CAD instance -> monitoring asset link table.

Rules (see docs/CAD-ENTEGRASYON.md):
- Key is the physical CAD instance (`cadInstanceId` = DWFX object_id). One code can have several instances;
  they are never merged.
- A link is created only from an explicit code written in `plant.json` (`cadCodes`). Name similarity is not
  evidence and is never used.
- Codes that lie inside a documented range (`cadCodeRange`) but are not written out are AMBIGUOUS: the target
  is listed as a candidate, never chosen.
- APPROVED exists only through `backend/cad/approvals.json` (a person, a date, a basis).
- The output is deterministic: no clock, sorted by CAD object index.
"""
import hashlib
import json
import re
from pathlib import Path
from typing import Optional

from services.flow import equipment_id

SCHEMA_VERSION = 1
STATUSES = ("UNMATCHED", "CANDIDATE", "EVIDENCED", "AMBIGUOUS", "APPROVED")
TARGET_PROJECT = "monitoring"
CODE_RE = re.compile(r"^(\d)-(\d{3})-(\d{3})$")


def canonical_hash(value) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def plant_assets(plant: dict) -> list[dict]:
    """Every configured machine with its stable ids, in config order."""
    assets = []
    for line_id, line in plant["lines"].items():
        for order, item in enumerate(line["equipment"], start=1):
            assets.append({
                "assetId": equipment_id(line_id, order), "lineId": line_id, "assetKey": item["assetKey"],
                "name": item["name"], "kind": item["kind"], "ref": item.get("ref", ""),
                "cadCodes": list(item.get("cadCodes", [])), "cadCodeRange": list(item.get("cadCodeRange", [])),
                "path": f"lines.{line_id}.equipment[{order - 1}]", "source": line.get("equipmentSource", ""),
            })
    return assets


def _in_range(code: str, bounds: list[str]) -> bool:
    if len(bounds) != 2:
        return False
    parsed = [CODE_RE.match(x) for x in (code, *bounds)]
    if not all(parsed):
        return False
    (a, b, c), (la, lb, lc), (ha, hb, hc) = (tuple(m.groups()) for m in parsed)
    return (a, b) == (la, lb) == (ha, hb) and int(lc) <= int(c) <= int(hc)


def build_identity(instances_doc: dict, plant: dict, approvals: Optional[list] = None, instances_hash: str = "") -> dict:
    assets = plant_assets(plant)
    by_code: dict[str, list[dict]] = {}
    for asset in assets:
        for code in asset["cadCodes"]:
            by_code.setdefault(code, []).append(asset)
    approvals = approvals or []
    approval_by_instance = {a["cadInstanceId"]: a for a in approvals}
    known_ids = {i["cadInstanceId"] for i in instances_doc["instances"]}
    for entry in approvals:
        if entry["cadInstanceId"] not in known_ids:
            raise ValueError(f"approval for unknown CAD instance {entry['cadInstanceId']}")

    rows = []
    for inst in sorted(instances_doc["instances"], key=lambda x: x["cadObjectIndex"]):
        code = inst["equipmentCode"]
        exact = by_code.get(code, [])
        ranged = [a for a in assets if a["cadCodeRange"] and _in_range(code, a["cadCodeRange"]) and a not in exact]
        row = {
            "cadInstanceId": inst["cadInstanceId"], "cadObjectIndex": inst["cadObjectIndex"], "cadMarker": inst["cadMarker"],
            "equipmentCode": code, "sourceLabel": inst["sourceLabel"], "sourcePartNumber": inst["sourcePartNumber"],
            "group": inst["group"], "issues": inst["issues"],
            "targetProject": None, "targetAssetId": None, "targetAssetKey": None, "targetLineId": None,
            "matchStatus": "UNMATCHED", "candidates": [], "evidence": [],
            "approvedBy": None, "approvedAt": None, "revision": 1,
        }
        if len(exact) == 1:
            a = exact[0]
            row.update(targetProject=TARGET_PROJECT, targetAssetId=a["assetId"], targetAssetKey=a["assetKey"],
                       targetLineId=a["lineId"], matchStatus="CANDIDATE", candidates=[a["assetId"]])
            row["evidence"].append({"kind": "CODE_EXACT", "source": "backend/config/plant.json", "path": a["path"] + ".cadCodes",
                                    "value": code, "basis": a["source"] or a["ref"]})
        elif len(exact) > 1:
            row.update(matchStatus="AMBIGUOUS", candidates=[a["assetId"] for a in exact])
            row["evidence"].append({"kind": "CODE_EXACT_MULTIPLE_TARGETS", "source": "backend/config/plant.json",
                                    "value": code, "basis": "same code listed for several assets"})
        elif ranged:
            row.update(matchStatus="AMBIGUOUS", candidates=[a["assetId"] for a in ranged])
            for a in ranged:
                row["evidence"].append({"kind": "RANGE_MEMBER_UNVERIFIED", "source": "backend/config/plant.json",
                                        "path": a["path"] + ".cadCodeRange", "value": "…".join(a["cadCodeRange"]),
                                        "basis": "code lies inside a documented range; membership is not written out"})
        approval = approval_by_instance.get(inst["cadInstanceId"])
        if approval:
            target = next((a for a in assets if a["assetId"] == approval["targetAssetId"]), None)
            if target is None or target["assetId"] not in row["candidates"]:
                raise ValueError(f"approval for {inst['cadMarker']} names a target that is not one of its candidates")
            row.update(targetProject=TARGET_PROJECT, targetAssetId=target["assetId"], targetAssetKey=target["assetKey"],
                       targetLineId=target["lineId"], matchStatus="APPROVED", approvedBy=approval["approvedBy"],
                       approvedAt=approval["approvedAt"], revision=2)
            row["evidence"].append({"kind": "HUMAN_APPROVAL", "source": "backend/cad/approvals.json",
                                    "value": approval["targetAssetId"], "basis": approval["basis"]})
        rows.append(row)

    present = {r["equipmentCode"] for r in rows}
    inventory_only = set(instances_doc["unmatchedInventoryCodes"])
    asset_rows = []
    for a in assets:
        instance_ids = [r["cadInstanceId"] for r in rows if r["targetAssetId"] == a["assetId"]]
        missing = [c for c in a["cadCodes"] if c not in present]
        if instance_ids:
            status = "LINKED"
        elif a["cadCodes"]:
            status = "CODE_NOT_IN_CAD"
        else:
            status = "NO_CAD_CODE_REFERENCE"
        asset_rows.append({
            "assetId": a["assetId"], "lineId": a["lineId"], "assetKey": a["assetKey"], "name": a["name"], "ref": a["ref"],
            "cadCodes": a["cadCodes"], "linkStatus": status, "cadInstanceIds": instance_ids,
            "codesMissingInCad": missing, "codesInInventoryWithoutCad": [c for c in missing if c in inventory_only],
        })

    counts = {s: sum(1 for r in rows if r["matchStatus"] == s) for s in STATUSES}
    return {
        "schemaVersion": SCHEMA_VERSION, "modelRevision": instances_doc["modelRevision"], "targetProject": TARGET_PROJECT,
        "inputs": {"instancesSha256": instances_hash, "plantAssetsSha256": canonical_hash(assets),
                   "approvalsSha256": canonical_hash(approvals)},
        "summary": {"cadInstances": len(rows), "uniqueCodes": len(present), "byStatus": counts,
                    "assets": len(asset_rows), "assetsLinked": sum(1 for x in asset_rows if x["linkStatus"] == "LINKED"),
                    "assetsCodeNotInCad": sum(1 for x in asset_rows if x["linkStatus"] == "CODE_NOT_IN_CAD"),
                    "assetsWithoutCadCode": sum(1 for x in asset_rows if x["linkStatus"] == "NO_CAD_CODE_REFERENCE")},
        "note": "CANDIDATE = explicit code match, not approved. Name similarity is never evidence. "
                "A CAD part carries no live status of its own.",
        "assets": asset_rows, "rows": rows,
    }


def load_inputs(base: Path, plant: dict) -> dict:
    instances_path = base / "instances.json"
    raw = instances_path.read_bytes()
    approvals_path = base / "approvals.json"
    approvals = json.loads(approvals_path.read_text(encoding="utf-8")) if approvals_path.exists() else []
    return build_identity(json.loads(raw.decode("utf-8")), plant, approvals, hashlib.sha256(raw).hexdigest())


def validate_identity(doc: dict, plant: dict) -> list[str]:
    """Structural checks used by tests and the builder; returns a list of problems."""
    problems = []
    assets = {a["assetId"]: a for a in plant_assets(plant)}
    seen = set()
    for r in doc["rows"]:
        if r["cadInstanceId"] in seen:
            problems.append(f"duplicate instance {r['cadInstanceId']}")
        seen.add(r["cadInstanceId"])
        if r["matchStatus"] not in STATUSES:
            problems.append(f"{r['cadMarker']}: bad status")
        if r["matchStatus"] in ("CANDIDATE", "EVIDENCED", "APPROVED"):
            a = assets.get(r["targetAssetId"])
            if not a or a["assetKey"] != r["targetAssetKey"] or a["lineId"] != r["targetLineId"]:
                problems.append(f"{r['cadMarker']}: target does not exist in plant config")
            if not r["evidence"]:
                problems.append(f"{r['cadMarker']}: linked without evidence")
        elif r["targetAssetId"] is not None:
            problems.append(f"{r['cadMarker']}: {r['matchStatus']} must not carry a target")
        if r["matchStatus"] == "APPROVED" and not (r["approvedBy"] and r["approvedAt"]):
            problems.append(f"{r['cadMarker']}: approved without approver")
        if r["matchStatus"] != "APPROVED" and (r["approvedBy"] or r["approvedAt"]):
            problems.append(f"{r['cadMarker']}: approval fields on unapproved row")
    return problems
