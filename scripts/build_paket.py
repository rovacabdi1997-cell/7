"""Builds the delivery package from this repository, nothing else.

    python scripts/build_paket.py --ad TURKMEN-GIPS-v6 --node <path to node.exe>

Output: <repo>/../outputs/<ad>/ and <ad>.zip
  site/              one static site: TV screens (Next export) + sunum/ presentation
  runtime/node.exe   portable Node for server.cjs
  KAYNAK-KOD/backend live-data API source (needs Python on the central PC)
  BELGELER/          handouts
  *.cmd, BASLAT.ps1, OTOMATIK-BASLAT.ps1, SAHA-AYARLARI.json, OKU-BENI.md
"""
import argparse
import os
import shutil
import subprocess
import sys
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
OUTPUTS = ROOT.parent / "outputs"
# Pages of the old management panel: never shipped (user decision 2026-10-20).
OLD_PAGES = ["calsyk", "duyduryslar", "gipsokarton", "gury-garyndy", "index.txt", "replay/day.json"]
# Presentation files kept in the repo but not shipped.
SUNUM_SKIP = {"TURKMEN-GIPS-TEHNIKI-INTEGRASIYA-TEK-DOSYA.html", "TURKMEN-GIPS-TEHNIKI-INTEGRASIYA.pdf"}
ROOT_INDEX = ('<!doctype html><meta charset="utf-8">'
              '<meta http-equiv="refresh" content="0; url=/sunum/TURKMEN-GIPS-BAKANLIK-SUNUMU.html">'
              '<title>TÜRKMEN GIPS</title>'
              '<a href="/sunum/TURKMEN-GIPS-BAKANLIK-SUNUMU.html">Sunum</a> · '
              '<a href="/tv/1/">TV 1</a> · <a href="/tv/2/">TV 2</a>\n')


def run(cmd, cwd, env=None):
    print("$", " ".join(cmd))
    subprocess.run(cmd, cwd=cwd, env=env, check=True, shell=os.name == "nt")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ad", required=True, help="package folder name")
    ap.add_argument("--node", required=True, help="portable node.exe to ship")
    ap.add_argument("--zip", action="store_true", help="also write <ad>.zip")
    args = ap.parse_args()
    if Path(args.ad).name != args.ad or '/' in args.ad or '\\' in args.ad:
        sys.exit('--ad yalnız bir klasör adı olmalı.')

    out = OUTPUTS / args.ad
    if out.exists():
        sys.exit(f"{out} zaten var; başka bir --ad verin.")
    node = Path(args.node)
    if not node.is_file():
        sys.exit(f"node.exe bulunamadı: {node}")

    # 1. Data for the offline loop, then the TV screens as a static export.
    run([sys.executable, "scripts/export_replay.py"], ROOT)
    run([str(node), "frontend/scripts/export-shared.cjs"], ROOT)
    build_cache = (ROOT / "frontend" / ".next-usb").resolve()
    if not build_cache.is_relative_to((ROOT / "frontend").resolve()):
        sys.exit('Build çıktısı frontend dışına yönleniyor; silinmedi.')
    shutil.rmtree(build_cache, ignore_errors=True)
    env = dict(os.environ, NEXT_PUBLIC_DATA_SOURCE="replay")
    run(["npx", "next", "build"], ROOT / "frontend", env)

    # 2. Site = TV export + presentation, without the old panel.
    site = out / "site"
    shutil.copytree(ROOT / "frontend" / ".next-usb", site)
    for rel in OLD_PAGES:
        p = site / rel
        if p.is_dir():
            shutil.rmtree(p)
        elif p.exists():
            p.unlink()
    (site / "index.html").write_text(ROOT_INDEX, encoding="utf-8")
    shutil.copytree(ROOT / "sunum", site / "sunum",
                    ignore=lambda d, names: [n for n in names if n in SUNUM_SKIP or n == ".claude"])

    # 3. Runtime, launchers, settings, backend source, handouts.
    (out / "runtime").mkdir()
    shutil.copy2(node, out / "runtime" / "node.exe")
    for f in (ROOT / "paket").iterdir():
        if f.is_file():
            shutil.copy2(f, out / f.name)
    backend = out / "KAYNAK-KOD" / "backend"
    shutil.copytree(ROOT / "backend", backend,
                    ignore=shutil.ignore_patterns("__pycache__", ".claude", "*.pyc"))
    shutil.copytree(ROOT / "database", out / "KAYNAK-KOD" / "database")
    (out / "BELGELER").mkdir()
    pdf = ROOT / "sunum" / "TURKMEN-GIPS-TEHNIKI-INTEGRASIYA.pdf"
    if pdf.exists():
        shutil.copy2(pdf, out / "BELGELER" / pdf.name)
    shutil.copy2(ROOT / "docs" / "SAHA-KURULUM.md", out / "BELGELER" / "SAHA-KURULUM.md")
    for folder in ("api", "handoff"):
        if (ROOT / "docs" / folder).is_dir():
            shutil.copytree(ROOT / "docs" / folder, out / "BELGELER" / folder)
    visual_audit = ROOT / "docs" / "visual-audit"
    if visual_audit.is_dir():
        shutil.copytree(visual_audit, out / "BELGELER" / "visual-audit")
    for name in ["ORTAK-CALISMA-PLANI.md", "SAHA-SON-KABUL-2026-10-21.md", "GRAFIK-MEYILNAMA-KABUL-2026-10-21.md", "AI-GUCLENDIRME-PLANI-2026-10-21.md", "SAHA-GORSEL-v3-KABUL-2026-10-21.md", "TV-BAGLAMSAL-v4-KABUL-2026-10-21.md", "TV-FINAL-v6-2026-10-21.md", "TV-DASHBOARD-v7-2026-10-22.md", "SUNUM-GORSEL-v8-2026-10-22.md", "TV-REFERANS-PANO-v9-2026-10-23.md", "TURKMEN_GIPS_3_MINI_PC_TV_AI_MASTER_PLAN_2026-10-22.md", "TAM-PLAN-v9.md", "v9-CLAUDE-BOSLUK-RAPORU.md"]:
        if (ROOT / "docs" / name).is_file():
            shutil.copy2(ROOT / "docs" / name, out / "BELGELER" / name)
    evidence = ROOT / 'docs' / 'saha-son-kabul-evidence'
    if evidence.is_dir():
        shutil.copytree(evidence, out / 'BELGELER' / 'saha-son-kabul-evidence')
    graphics_evidence = ROOT / 'docs' / 'grafik-panel-evidence'
    if graphics_evidence.is_dir():
        shutil.copytree(graphics_evidence, out / 'BELGELER' / 'grafik-panel-evidence')
    v3_evidence = ROOT / 'docs' / 'saha-gorsel-v3-evidence'
    if v3_evidence.is_dir():
        shutil.copytree(v3_evidence, out / 'BELGELER' / 'saha-gorsel-v3-evidence')
    tv_evidence = ROOT / 'docs' / 'tv-context-v4-evidence'
    if tv_evidence.is_dir():
        shutil.copytree(tv_evidence, out / 'BELGELER' / 'tv-context-v4-evidence')
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    dirty = bool(subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT, text=True).strip())
    release = {"releaseId": args.ad, "builtAt": datetime.now(timezone.utc).isoformat(), "referenceCommit": commit, "workingTreeDirty": dirty,
               "entryPoints": {"presentation": "/sunum/TURKMEN-GIPS-BAKANLIK-SUNUMU.html", "controlRoom": "/kontrol/", "tv1": "/tv/1/", "tv2": "/tv/2/"}}
    for target in [out / "RELEASE.json", site / "release.json"]:
        target.write_text(json.dumps(release, ensure_ascii=False, indent=2), encoding="utf-8")
    hashes = {str(p.relative_to(out)).replace('\\','/'): hashlib.file_digest(p.open('rb'), 'sha256').hexdigest() for p in out.rglob('*') if p.is_file()}
    (out / 'DOSYA-DOGRULAMA.json').write_text(json.dumps(hashes, ensure_ascii=False, indent=2), encoding='utf-8')

    if args.zip:
        archive = shutil.make_archive(str(out), "zip", root_dir=out.parent, base_dir=out.name)
        print("zip:", archive)
    size = sum(f.stat().st_size for f in out.rglob("*") if f.is_file())
    print(f"hazır: {out} ({size / 1e6:.0f} MB)")


if __name__ == "__main__":
    main()
