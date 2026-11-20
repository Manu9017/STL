#!/usr/bin/env python3
"""Build everything from the design basis:

    python3 build.py            calcs → CAD (STEP, GLB, BOM) → viewer data → drawings → site
    python3 build.py --fast     skip STEP and drawings (quick model + viewer refresh)

Outputs land in out/ (see README.md). The site folder out/site/ is what the 3D viewer artifact publishes.
"""
import shutil
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from shivas_furnace import viewer_data  # noqa: E402
from shivas_furnace.calc import report  # noqa: E402
from shivas_furnace.cad import build as cad  # noqa: E402


def stage_site():
    site = ROOT / "out" / "site"
    (site / "drawings").mkdir(parents=True, exist_ok=True)
    shutil.copy(ROOT / "viewer" / "index.html", site / "index.html")
    shutil.copy(ROOT / "viewer" / "drawings.html", site / "drawings.html")
    import base64
    glb = (ROOT / "out" / "cad" / "SHV-FUR-6700.glb").read_bytes()
    (site / "model.glb.b64.txt").write_text(base64.b64encode(glb).decode())   # claude.ai does not serve .glb
    (site / "model.glb").unlink(missing_ok=True)
    for f in ("parts.json", "flows.json", "viewer_data.json"):
        shutil.copy(ROOT / "out" / "cad" / f, site / f)
    shutil.copy(ROOT / "out" / "calc" / "SHV-FUR-6700-CR.html", site / "calc.html")
    for f in sorted((ROOT / "out" / "drawings").glob("SHV-FUR-6700-GA-00?.*")):
        if f.suffix in (".png", ".svg"):
            shutil.copy(f, site / "drawings" / f.name)
    return site


def main():
    fast = "--fast" in sys.argv
    t = time.time()
    print("calc report:", report.build())
    cad.build(step=not fast)
    print("viewer data:", viewer_data.build())
    if not fast:
        from shivas_furnace.drawings import make
        make.build()
    print("site:", stage_site())
    print(f"done in {time.time() - t:.0f}s")


if __name__ == "__main__":
    main()
