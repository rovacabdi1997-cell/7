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
from pathlib import Path

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

    out = OUTPUTS / args.ad
    if out.exists():
        sys.exit(f"{out} zaten var; başka bir --ad verin.")
    node = Path(args.node)
    if not node.is_file():
        sys.exit(f"node.exe bulunamadı: {node}")

    # 1. Data for the offline loop, then the TV screens as a static export.
    run([sys.executable, "scripts/export_replay.py"], ROOT)
    shutil.rmtree(ROOT / "frontend" / ".next-usb", ignore_errors=True)
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
                    ignore=lambda d, names: [n for n in names if n in SUNUM_SKIP])

    # 3. Runtime, launchers, settings, backend source, handouts.
    (out / "runtime").mkdir()
    shutil.copy2(node, out / "runtime" / "node.exe")
    for f in (ROOT / "paket").iterdir():
        shutil.copy2(f, out / f.name)
    backend = out / "KAYNAK-KOD" / "backend"
    shutil.copytree(ROOT / "backend", backend,
                    ignore=shutil.ignore_patterns("__pycache__", ".claude", "*.pyc"))
    (out / "BELGELER").mkdir()
    pdf = ROOT / "sunum" / "TURKMEN-GIPS-TEHNIKI-INTEGRASIYA.pdf"
    if pdf.exists():
        shutil.copy2(pdf, out / "BELGELER" / pdf.name)
    shutil.copy2(ROOT / "docs" / "SAHA-KURULUM.md", out / "BELGELER" / "SAHA-KURULUM.md")

    if args.zip:
        archive = shutil.make_archive(str(out), "zip", root_dir=out.parent, base_dir=out.name)
        print("zip:", archive)
    size = sum(f.stat().st_size for f in out.rglob("*") if f.is_file())
    print(f"hazır: {out} ({size / 1e6:.0f} MB)")


if __name__ == "__main__":
    main()
