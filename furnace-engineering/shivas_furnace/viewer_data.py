"""Collect what the 3D viewer shows besides the model: check summary, decisions, open items, assumptions."""
from __future__ import annotations

import json
import re

from .basis import B, ROOT


def _tables(md: str):
    tables, cur = [], None
    for line in md.splitlines():
        if line.startswith("|"):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if set("".join(cells)) <= set("-: "):
                continue
            if cur is None:
                cur = {"head": cells, "rows": []}
                tables.append(cur)
            else:
                cur["rows"].append(cells)
        else:
            cur = None
    return tables


def _plain(s):
    return re.sub(r"\*\*(.+?)\*\*", r"\1", s).replace("`", "")


def build():
    res = json.loads((ROOT / "out" / "calc" / "results.json").read_text())
    checks = []
    for c in res["calcs"]:
        for ch in c["checks"]:
            checks.append({"calc": c["id"], "title": c["title"], "name": ch["name"], "value": ch["value"], "unit": ch["unit"],
                           "limit": ch["limit"], "kind": ch["kind"], "status": ch["status"], "note": ch["note"]})
    dec = _tables((ROOT / "basis" / "decision_register.md").read_text())[0]
    op = _tables((ROOT / "basis" / "open_items.md").read_text())
    t_open = next(t for t in op if t["head"][1] == "Item" and t["head"][0] == "#")
    t_hold = next((t for t in op if t["head"][0] == "Hold"), {"rows": []})
    t_ass = next(t for t in op if t["head"][1] == "Assumption")
    data = {"doc": "SHV-FUR-6700", "rev": B.meta["rev"], "date": str(B.meta["date"]), "counts": res["counts"], "checks": checks,
            "decisions": [{"id": r[0], "what": _plain(r[1]), "why": _plain(r[2]), "src": _plain(r[3]), "ev": _plain(r[4])} for r in dec["rows"]],
            "open": [{"id": r[0], "what": _plain(r[1]), "owner": _plain(r[2]), "effect": _plain(r[3])} for r in t_open["rows"]],
            "holds": [{"id": r[0], "what": _plain(r[1]), "where": _plain(r[2])} for r in t_hold["rows"]],
            "assumptions": [{"id": r[0], "what": _plain(r[1]), "cons": _plain(r[2])} for r in t_ass["rows"]],
            "sources": B.sources, "n_basis": len(B.leaves)}
    out = ROOT / "out" / "cad" / "viewer_data.json"
    out.write_text(json.dumps(data, indent=1))
    return out


if __name__ == "__main__":
    print(build())
