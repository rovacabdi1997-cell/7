"""Turns the accepted DWFX mapping package into app-ready, lazily loadable CAD assets.

Input : <source>/mapping-source/{MAPPING.json, assets/geometry-packed.{json,bin}, vendor/}
Output: frontend/public/cad/**  (model index, properties, per-section geometry, vendor three.js, manifest)
        backend/cad/instances.json  (the 513 CAD assembly instances, input of the identity builder)

Nothing is invented: coordinates, labels and codes are copied from MAPPING.json, geometry bytes are
sliced from geometry-packed.bin without changing a single byte. Re-running is idempotent.

Usage: python -X utf8 scripts/cad/build_cad_assets.py --source <DEVIR-ACILMIS dir>
"""
import argparse
import hashlib
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PUBLIC_CAD = ROOT / "frontend" / "public" / "cad"
BACKEND_CAD = ROOT / "backend" / "cad"
SCHEMA = 1


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(4 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json(path: Path, value, *, compact=True) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(value, ensure_ascii=False, separators=(",", ":") if compact else None,
                      indent=None if compact else 1)
    path.write_text(text + "\n", encoding="utf-8", newline="\n")


def r3(value):
    return None if value is None else round(float(value), 3)


def build(source: Path) -> None:
    mapping_dir = source / "mapping-source"
    mapping = json.loads((mapping_dir / "MAPPING.json").read_text(encoding="utf-8"))
    packed_meta = json.loads((mapping_dir / "assets" / "geometry-packed.json").read_text(encoding="utf-8"))
    packed_bin = mapping_dir / "assets" / "geometry-packed.bin"
    summary = mapping["summary"]
    revision = summary["source_sha256"]
    groups = summary["groups"]
    objects = mapping["objects"]
    if len(objects) != 5567 or len(mapping["equipment_occurrences"]) != 513:
        sys.exit("Unexpected mapping size; refusing to build.")
    index_of = {o["object_id"]: i for i, o in enumerate(objects)}
    group_index = {g["id"]: i for i, g in enumerate(groups)}
    PUBLIC_CAD.mkdir(parents=True, exist_ok=True)

    # --- geometry: one file per section, byte-identical slices of the packed binary -------------
    geo_dir = PUBLIC_CAD / "geometry"
    geo_dir.mkdir(parents=True, exist_ok=True)
    blob = packed_bin.read_bytes()
    section_meta = []
    for mesh in packed_meta["meshes"]:
        g = mesh["group"]
        start = mesh["p_offset"]
        end = mesh["f_offset"] + mesh["f_bytes"]
        assert start % 4 == 0, "section start must stay 4-byte aligned"
        # arrays keep the packer's order (alignment padding may sit between them) and typed-array alignment
        assert start <= mesh["n_offset"] <= mesh["object_offset"] <= mesh["owner_offset"] <= mesh["f_offset"]
        assert mesh["n_offset"] >= start + mesh["p_bytes"] and mesh["object_offset"] >= mesh["n_offset"] + mesh["n_bytes"]
        assert mesh["owner_offset"] >= mesh["object_offset"] + mesh["object_bytes"]
        assert mesh["f_offset"] >= mesh["owner_offset"] + mesh["owner_bytes"]
        assert mesh["object_offset"] % 2 == 0 and mesh["owner_offset"] % 2 == 0 and mesh["f_offset"] % 4 == 0
        name = f"section-{g}.bin"
        out = geo_dir / name
        data = blob[start:end]
        digest = hashlib.sha256(data).hexdigest()
        if not out.exists() or out.stat().st_size != len(data) or sha256_file(out) != digest:
            out.write_bytes(data)
        section_meta.append({
            "section": g, "groupId": groups[g]["id"], "file": f"geometry/{name}", "bytes": len(data),
            "sha256": digest,
            "vertices": mesh["vertices"], "triangles": mesh["triangles"], "bbox": [r3(v) for v in mesh["bbox"]],
            "p": [mesh["p_offset"] - start, mesh["p_bytes"]], "n": [mesh["n_offset"] - start, mesh["n_bytes"]],
            "object": [mesh["object_offset"] - start, mesh["object_bytes"]],
            "owner": [mesh["owner_offset"] - start, mesh["owner_bytes"]],
            "f": [mesh["f_offset"] - start, mesh["f_bytes"]],
        })
    geometry_meta = {
        "schemaVersion": SCHEMA, "modelRevision": revision, "normalComponent": packed_meta["normal_component"],
        "viewTransform": packed_meta["view_transform"], "previewKind": packed_meta["preview_kind"],
        "sourceObjectSurfaces": packed_meta["source_object_surfaces"],
        "finalPreviewTriangles": packed_meta["final_preview_triangles"],
        "emptyOwner": 65535, "sections": section_meta,
        "note": "Simplified native DWFX surfaces; source mapping coordinates are unchanged. Not registered to site/north.",
    }
    write_json(PUBLIC_CAD / "geometry.json", geometry_meta)

    # --- model index: compact objects (array position == tgObject value in the geometry) ----------
    inventory = {}
    for occ in mapping["equipment_occurrences"]:
        inventory.setdefault(occ["code"], occ["inventory"])
    compact = []
    for i, o in enumerate(objects):
        owner = o.get("code_owner_object_id")
        compact.append({
            "i": i, "id": o["object_id"], "p": index_of.get(o["parent_object_id"], -1), "l": o["label"],
            "g": group_index.get(o["group"], -1), "m": o.get("marker") or "", "nm": o.get("node_marker") or "",
            "c": o.get("direct_codes", []), "ac": o.get("associated_codes", []), "pn": o.get("part_number") or "",
            "d": o["depth"], "o": index_of.get(owner, -1) if owner else -1, "st": o["association_status"],
            "b": [r3(v) for v in o["bbox_model_m"]] if o.get("bbox_model_m") else None,
            "ct": [r3(v) for v in o["center_model_m"]] if o.get("center_model_m") else None,
            "or": [r3(v) for v in o["origin_model_m"]] if o.get("origin_model_m") else None,
            "mat": o.get("material") or "", "w": o.get("w3d_node"), "ap": o["assembly_path"], "e": o.get("entity_ref") or "",
            "gs": o.get("geometry_status") or "", "is": o.get("issues", []),
        })
    index = {
        "schemaVersion": SCHEMA, "modelRevision": revision, "sourceFile": "FabrikaGenelMontaj.dwfx",
        "units": summary["units"], "sourceUnits": summary["source_units"], "streamToMetre": summary["stream_to_m"],
        "coordinateSystem": summary["coordinate_system"],
        "coordinateRegistrationToSite": summary["coordinate_registration_to_site"],
        "viewTransform": "view=(source_y, source_x, -source_z); metres",
        "counts": {k: summary[k] for k in ("objects", "entities", "direct_object_matches", "unique_equipment_codes",
                                           "inventory_codes", "unmatched_inventory_codes", "source_code_without_inventory",
                                           "shell_geometry_objects", "direct_objects_with_geometry", "property_count",
                                           "issue_count")},
        "groups": [{"id": g["id"], "title": g["title"], "color": g["color"], "objectCount": g["object_count"],
                    "directObjectCount": g["direct_object_count"], "uniqueCodes": g["unique_codes"],
                    "geometryCount": g["geometry_count"], "file": section_meta[k]["file"], "bytes": section_meta[k]["bytes"],
                    "triangles": section_meta[k]["triangles"], "bbox": section_meta[k]["bbox"]}
                   for k, g in enumerate(groups)],
        "objects": compact,
        "inventory": inventory,
        "unmatchedInventory": mapping["unmatched_inventory"],
        "issues": [{"objectId": x["object_id"], "marker": x.get("marker", ""), "label": x["label"], "issue": x["issue"]}
                   for x in mapping["issues"]],
    }
    write_json(PUBLIC_CAD / "model-index.json", index)

    # --- properties (entities are shared by many instances; keep them once) ------------------------
    entities = {ref: [[p["name"], p["value"], p.get("category", "")] for p in e.get("properties", [])]
                for ref, e in mapping["entities"].items()}
    own = {str(i): [[p["name"], p["value"], p.get("category", "")] for p in o.get("own_properties", [])]
           for i, o in enumerate(objects) if o.get("own_properties")}
    write_json(PUBLIC_CAD / "properties.json", {"schemaVersion": SCHEMA, "modelRevision": revision,
                                                "entities": entities, "own": own})

    # --- vendor three.js (local, no CDN) ----------------------------------------------------------
    vendor = PUBLIC_CAD / "vendor"
    vendor.mkdir(exist_ok=True)
    for name in ("three.module.js", "three.core.js", "OrbitControls.js"):
        shutil.copyfile(mapping_dir / "vendor" / name, vendor / name)
    licenses = source / "mapping-viewer" / "THIRD-PARTY-LICENSES.txt"
    if licenses.exists():
        shutil.copyfile(licenses, vendor / "THIRD-PARTY-LICENSES.txt")

    # --- backend instance list: the 513 coded assembly instances -----------------------------------
    instances = []
    for occ in mapping["equipment_occurrences"]:
        instances.append({
            "cadInstanceId": occ["object_id"], "cadObjectIndex": index_of[occ["object_id"]], "cadMarker": occ["marker"],
            "equipmentCode": occ["code"], "sourceLabel": occ["label"], "sourcePartNumber": occ.get("part_number") or "",
            "group": occ["group"], "issues": occ.get("issues", []), "inventoryName": occ["inventory"].get("name_tr", ""),
        })
    write_json(BACKEND_CAD / "instances.json", {
        "schemaVersion": SCHEMA, "modelRevision": revision, "sourceFile": "FabrikaGenelMontaj.dwfx",
        "instanceCount": len(instances), "uniqueCodes": len({i["equipmentCode"] for i in instances}),
        "unmatchedInventoryCodes": sorted(x["code"] for x in mapping["unmatched_inventory"]),
        "instances": instances}, compact=False)

    # --- manifest (sizes + hashes of everything the viewer fetches) --------------------------------
    files = {}
    for path in sorted(PUBLIC_CAD.rglob("*")):
        if path.is_file() and path.name not in ("manifest.json", "identity.json"):
            files[path.relative_to(PUBLIC_CAD).as_posix()] = {"bytes": path.stat().st_size, "sha256": sha256_file(path)}
    write_json(PUBLIC_CAD / "manifest.json", {"schemaVersion": SCHEMA, "modelRevision": revision, "files": files}, compact=False)
    print(f"CAD assets ready: {len(files)} files, revision {revision[:12]}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True, type=Path, help="extracted handoff package root")
    build(parser.parse_args().source)
