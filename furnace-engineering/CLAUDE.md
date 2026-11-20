# CLAUDE.md — SHV-FUR-6700 furnace engineering project

This folder is a stand-alone engineering project. It is not part of the website in the parent repository, and the
website brief in `../CLAUDE.md` does not apply here.

## Rules
- `basis/design_basis.yaml` is the single source of truth. Change a number there, never in the calc, CAD or drawing code.
- Every value carries a source key and a status: C confirmed in a SHIVAS document, D decided in this design (log it in
  `basis/decision_register.md`), A assumption, O open (log it in `basis/open_items.md`). Never invent a value without marking it A.
- Units are mm, °C, kW, Nm³/h and mmWC. Coordinates: origin at the kettle centre on plan at FFL ±0.000, X east, Y north, Z up.
- After any change, run `python3 build.py --fast` and check that every part is still a valid solid and that the calc report has no new FAIL.
  Run the full `python3 build.py` before committing outputs.
- Calculation results are drafts until a qualified engineer signs the report. Do not write "checked" or "approved".
- Do not claim CE, ISO 9001 or EN 746 compliance. Combustion safety is an open review item (O-13).

## Layout
- `shivas_furnace/basis.py`: loader + derived geometry `G` (all positions come from here)
- `shivas_furnace/calc/`: `engine.py` (calcs C-01…C-14), `report.py` (HTML report + results.json)
- `shivas_furnace/cad/`: `lib.py` (primitives, registry, colours), `furnace.py`, `combustion.py`, `loop.py`, `build.py`
- `shivas_furnace/drawings/`: `sheets.py` (HLR views, filled sections, dims, title block), `make.py` (GA-001…006)
- `viewer/`: three.js viewer (`index.html`) and drawing register (`drawings.html`); `build.py` stages `out/site/`
