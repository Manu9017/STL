# SHV-FUR-6700 — HV pulse-fired galvanizing furnace and 4-position dryer

SHIVAS Technology Ltd · hot dip galvanizing division · design package Rev A · 2026-11-20 (updated 2026-11-21 for SH-PID-02A Rev U, the corner blower and the zinc enclosure)

This is a stand-alone engineering project, separate from the website in the rest of this repository. It holds one
high-velocity pulse-fired furnace with a 6,700 × 1,250 × 1,310 kettle, its combustion system per P&ID SH-PID-02A Rev U, the
zinc fume enclosure, the four-position pit dryer, the heat-recovery loop (trenches, mixing box S2, Ø1100 suction duct,
recirculation blower at the SW corner) and the bleed stack. Everything is generated from one
design basis by code, so a change in `basis/design_basis.yaml` flows through the calculations, the 3D model, the drawings
and the viewer.

**Status: preliminary, not for construction.** The calculations have not been checked by a qualified engineer, and the
open items in `basis/open_items.md` must be closed first.

**3D viewer, calculation report and drawings online:** https://claude.ai/artifact/EeeJZtDp1XxQ5DkykcjEhV (private to the owner until shared)

## What is in it

| Path | What |
|---|---|
| `basis/design_basis.yaml` | 171 values, each with its unit, source document and status: confirmed, decided here, assumed, or open; the P&ID bill of material tag for tag |
| `basis/decision_register.md` | 25 decisions where the SHIVAS documents disagreed, a check failed, or the owner instructed a change |
| `basis/open_items.md` | 19 open items, the 6 holds carried from the P&ID, and 13 assumptions, each with an owner |
| `shivas_furnace/calc/` | 14 calculations (Cantera combustion, heat balance and wall flux, linings, air, gas, flue, loop energy and pressure, fans, structure, stack, energy, insulation quantities, zinc-fume extraction) |
| `shivas_furnace/cad/` | CadQuery model, one builder per system: `furnace.py`, `combustion.py`, `loop.py` |
| `shivas_furnace/drawings/` | GA sheet generator: hidden-line views, filled sections, dimensions, levels, title blocks |
| `viewer/` | three.js 3D viewer and drawing register (published as a claude.ai artifact) |
| `out/calc/` | `SHV-FUR-6700-CR.html` calculation report and `results.json` |
| `out/cad/` | `SHV-FUR-6700.step` (master geometry, full assembly tree), `.glb`, `bom.csv`, `parts.json` |
| `out/drawings/` | `GA-001…007` as DXF, PDF and PNG previews, plus `SHV-FUR-6700-GA-set.pdf` |
| `.claude/skills/` | The mechanical-engineering skills (MIT) that shaped the method |

## Sources it is built from

The SHIVAS documents from earlier work. Each value in the basis names its source:

- Kettle & furnace confirmed basis **Rev K**: levels, kettle, casing, burners, foundation, thermocouples
- Furnace & dryer heat-recovery loop **Rev H**, with the SHIVAS validation of 12 Oct 2026
- **SH-PID-02A Rev U** combustion P&ID (as ordered, Eclipse PO STL/2026/206 and Bloom PO 1018): gas train A1–A11, burner main legs B1–B5,
  ignition legs C1–C19, direct-spark ignition, BCU 370, air D1–D9 on the AEP-VB-2.5 blower. It supersedes Rev M (D-23)
- **SHIVAS zinc fume enclosure annexure**: enclosure size, sliding roof covers, skimming doors, windows, lighting, lateral suction
- **Owner's instruction, 21 Nov 2026**: recirculation blower at the SW corner where the discharge turns into the dryer (D-22)
- **SH-INS-01..05 Rev B** ceramic-fibre insulation set and the 18–19 Nov reconciliation: top closure, band, corner shields
- **SH-MB-01 Rev A** mixing box S2 · **STL-MB-DMP-02 Rev A** fresh-air damper · **SH-RBR-01/02** dryer door drives
- **STL-EF Rev D**: suspended-kettle load path and lining material data
- SHIVAS HDG plant model: relative layout of the loop equipment

## Key results (calc report SHV-FUR-6700-CR)

| | |
|---|---|
| Capacity at the 25 kW/m² wall-flux limit | 5.6 t/h (Rev H convention) · 6.0 t/h (covers shut between dips) · 6.75 t/h (suspended kettle, hearth takes 10 %) |
| Fired duty at 6.0 t/h | ≈761 kW of 1,172 kW installed; 12.8 Nm³ gas per tonne; furnace efficiency ≈60 % |
| Casing skin | 61–65 °C at 900–1,000 °C hot face (175 module + 50 microporous + 25 CaSi) |
| Kettle support | 36 ribs 12 × 200, σ ≈ 100 MPa vs 140 allowable; kettle grows ≈39 mm, slides on a graphite strip |
| Loop | mix ≈124 °C, dryer ≈209 kW, bleed 4,729 Nm³/h ≈ 150 kW; loop needs ≈71 mmWC with the corner blower (O-07) |
| Zinc enclosure | 20,000 m³/h, 3.1 changes/min; 0.61 m/s open face with one door at the 1,000 mm skimming stop; ≈52 mmWC to the outlet flange |

## Build

```bash
pip install -r requirements.txt
python3 build.py          # ≈10 min: calcs, STEP/GLB, drawings, site
python3 build.py --fast   # ≈1 min: calcs, GLB, viewer data (no STEP, no drawings)
```

Coordinates: mm, origin at the kettle centre on plan at FFL ±0.000, X east, Y north, Z up. GLB is Y-up as glTF requires.

## Moving it to its own repository

The folder has no dependency on the website files. To split it out with its history:

```bash
git subtree split --prefix=furnace-engineering -b furnace-engineering
git push <new-repo-url> furnace-engineering:main
```
