"""Build the SHV-FUR-6700 assembly and export STEP, GLB, parts.json, bom.csv and flows.json."""
from __future__ import annotations

import csv
import json
import time

from ..basis import B, G, ROOT
from . import combustion, furnace, loop
from .lib import SYSTEMS, Registry

OUT = ROOT / "out" / "cad"


def flows():
    g = G
    a = g.bZ
    hx = g.lfX - 225          # alley centreline X (between kettle 675 and lining 1125)
    hy = g.lfY - 225
    rx, ry = g.ring[0], g.ring[1]

    def gasleg(sg):
        mx, my = g.leg_main
        P = lambda x, y, z: [sg * x, sg * y, z]
        return [P(mx, my, g.pit_manifold_z), P(mx, my, g.merge_z), P(-g.bX, my, g.merge_z), P(-g.bX, my, g.bZ), P(-g.bX, g.cYo + 794, g.bZ)]
    return {
        "flames": [{"p": [-g.bX, g.lfY, g.bZ], "d": [0, -1, 0], "len": 4200, "r": g.flame_d / 2},
                   {"p": [g.bX, -g.lfY, g.bZ], "d": [0, 1, 0], "len": 4200, "r": g.flame_d / 2}],
        "paths": [
            {"id": "alley1", "name": "Burner 1 gas, west alley → round the kettle", "c": "#FF6A1A", "T": 1000, "speed": 3.0,
             "pts": [[-g.bX, g.lfY, a], [-g.bX, -hy, a], [0, -hy, a], [hx, -hy, a], [hx, hy, a], [0, hy, a], [-hx, hy, a], [-hx, 0, a], [-hx, g.flueY, -450], [-g.cXo, g.flueY, -450]]},
            {"id": "alley2", "name": "Burner 2 gas, east alley → round the kettle", "c": "#FF8A2A", "T": 1000, "speed": 3.0,
             "pts": [[g.bX, -g.lfY, a], [g.bX, hy, a], [0, hy, a], [-hx, hy, a], [-hx, -1500, a], [-hx, g.flueY, -450], [-g.cXo, g.flueY, -450]]},
            {"id": "flue", "name": "Flue 800 °C → junction", "c": "#D7263D", "T": 800, "speed": 2.0,
             "pts": [[-g.cXo, g.flueY, -450], [-2650, g.flueY, -450], [-2650, -2600, -500]]},
            {"id": "return", "name": "Dryer return 100 °C", "c": "#E9C46A", "T": 100, "speed": 2.4,
             "pts": [[-4675, 0, -700], [-4300, 0, -650], [-3150, 0, -500], [-2650, -100, -500], [-2650, -2400, -500]]},
            {"id": "suction", "name": "Suction ≈124 °C → mixing box → Ø1100 duct → blower", "c": "#E8743B", "T": 124, "speed": 2.4,
             "pts": [[-2650, -2600, -500], [-2650, -7200, -500], [-2650, -7600, 300], [-2650, -7600, 900], [g.suction[0], -7600, 900], [g.rb_axis[1] + 150, -7600, 900]]},
            {"id": "fresh", "name": "Fresh air 30 °C", "c": "#2A9DF4", "T": 30, "speed": 1.6,
             "pts": [[-2650, -8900, 300], [-2650, -8700, 450], [-2650, -8250, 700], [-2650, -7800, 800]]},
            {"id": "discharge", "name": "Discharge 120 °C → corner → north to the supply box", "c": "#F2A541", "T": 120, "speed": 2.6,
             "pts": [[g.rb_axis[0] + 337, -8100, 900], [g.rb_axis[0] + 337, -8100, -500], [-11400, -7600, -500], [-11400, 0, -500], [-10850, 0, -650], [-10325, 0, -650]]},
            {"id": "bleed", "name": "Bleed → stack", "c": "#9AA1AA", "T": 120, "speed": 2.0,
             "pts": [list(p) for p in g.bleed_route] + [[g.stack[0], g.stack[1], 12500]]},
            *[{"id": f"zfe{k}", "name": "Zinc fume → lateral slots → header → Ø700 to the bag filter", "c": "#B9C8E8", "T": 60, "speed": 1.6,
               "pts": [[sx * 250, y, 400], [sx * 600, y, 3400], [sx * 1011, y, 4200], [sx * 1011, 4300, 4476], [0, 4400, 4476], [0, 5300, 4476], [4600, 5300, 4476]]}
              for k, (sx, y) in enumerate([(sx, y) for sx in (-1, 1) for y in (-3000, -1000, 1000, 3000)])],
            *[{"id": f"dry{k}", "name": "Drying air across the loads", "c": "#F2A541", "T": 120, "speed": 1.4,
               "pts": [[g.dX0 + 360, y, z], [g.dX1 - 360, y, z]]} for k, (y, z) in enumerate([(y, z) for y in (-2800, -1400, 0, 1400, 2800) for z in (-1050, -650, -300)])],
            {"id": "gas", "name": "Gas: train A → DN50 main → pit manifold → B leg → burner 1", "c": "#FFD100", "T": 35, "speed": 1.2,
             "pts": [list(p) for p in g.gas_header] + [list(p) for p in g.gas_main_N[1:]] + gasleg(1)},
            {"id": "gasS", "name": "Gas → burner 2", "c": "#FFD100", "T": 35, "speed": 1.2, "pts": [list(p) for p in g.gas_main_S] + gasleg(-1)},
            {"id": "air", "name": "Combustion air: blower → 7\" → 300 × 150 header → ring → burner 1", "c": "#66B3E8", "T": 35, "speed": 2.0,
             "pts": [[3625, -5050, 1320], [3625, -5050, 1600], [2350, -5050, 1600], [rx, -5050, 1600], [rx, -4600, 1600], [rx, -4600, 500],
                     [rx, ry, 500], [-g.bX, ry, 500], [-g.bX, ry, 60], [-g.bX, g.cYo + 617, 60], [-g.bX, g.cYo + 617, g.bZ + 330]]},
            {"id": "air2", "name": "Combustion air → burner 2", "c": "#66B3E8", "T": 35, "speed": 2.0,
             "pts": [[rx, -4600, 500], [rx, -ry, 500], [g.bX, -ry, 500], [g.bX, -ry, 60], [g.bX, -(g.cYo + 617), 60], [g.bX, -(g.cYo + 617), g.bZ + 330]]},
        ],
        "levels": [
            {"z": B.v("levels.kettle_rim"), "label": "Kettle rim +0.300"}, {"z": g.deck, "label": "Deck +0.256"},
            {"z": B.v("levels.zinc_surface"), "label": "Zinc +0.150"}, {"z": 0, "label": "FFL ±0.000"},
            {"z": g.bZ, "label": "Burner axis −0.390"}, {"z": g.k_out_bot, "label": "Kettle bottom −1.060"},
            {"z": g.f_top, "label": "Hearth −1.315"}, {"z": g.cbase, "label": "Casing base −1.575"},
            {"z": g.pad_top, "label": "Pad top −1.725"}, {"z": g.bpit_floor, "label": "Burner pit floor −1.750"},
            {"z": g.pad_bot, "label": "Pad underside −2.325"}, {"z": -1000, "label": "Trench floor −1.000"},
            {"z": g.d_floor, "label": "Dryer floor −1.400"},
            {"z": g.deck + B.v("enclosure.height"), "label": "Enclosure top +4.976"}, {"z": 900, "label": "Suction duct / fan axis +0.900"}],
        "systems": {k: v[0] for k, v in SYSTEMS.items()},
    }


def build(step=True):
    t0 = time.time()
    R = Registry()
    furnace.build(R)
    combustion.build(R)
    loop.build(R)
    t1 = time.time()
    bad = [p.name for p in R.parts if not p.shape.val().isValid()]
    OUT.mkdir(parents=True, exist_ok=True)
    assy = R.assembly()
    assy.export(str(OUT / "SHV-FUR-6700.glb"), tolerance=1.5, angularTolerance=0.25)
    t2 = time.time()
    if step:
        assy.export(str(OUT / "SHV-FUR-6700.step"))
    t3 = time.time()
    meta = R.meta()
    (OUT / "parts.json").write_text(json.dumps({"doc": "SHV-FUR-6700", "rev": B.meta["rev"], "units": "mm", "up": "Z (GLB is Y-up, metres×1000)",
                                                "systems": {k: v[0] for k, v in SYSTEMS.items()}, "parts": meta}, indent=1))
    (OUT / "flows.json").write_text(json.dumps(flows(), indent=1))
    with open(OUT / "bom.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["Tag", "Item", "System", "Qty", "Specification", "Material", "Source", "Status", "Note"])
        for p in sorted(R.parts, key=lambda p: (list(SYSTEMS).index(p.system), p.tag)):
            if p.layer == "flow":
                continue
            w.writerow([p.tag, p.title or p.name, SYSTEMS[p.system][0], p.qty, p.spec, p.material, p.src, p.status, p.note])
    print(f"{len(R.parts)} parts; invalid {bad}; build {t1 - t0:.1f}s, glb {t2 - t1:.1f}s, step {t3 - t2:.1f}s")
    return R


if __name__ == "__main__":
    import sys
    build(step="--no-step" not in sys.argv)
