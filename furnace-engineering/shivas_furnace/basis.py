"""Design basis loader + derived geometry.

Everything downstream (calcs, CAD, drawings, viewer) imports from here. Geometry is in mm,
origin = kettle centre on plan at FFL 0.000, X east, Y north, Z up (see design_basis.yaml).
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
BASIS_FILE = ROOT / "basis" / "design_basis.yaml"
STATUS = {"C": "confirmed", "D": "decided here", "A": "assumption", "O": "open"}


def _parse_leaf(item):
    """[value..., unit, source, status, note?] -> dict. Values containing commas may have been
    split by YAML; the status token (C/D/A/O) preceded by a known source key anchors the parse."""
    if not isinstance(item, list):
        return None
    for i in range(len(item) - 1, 1, -1):
        if isinstance(item[i], str) and item[i] in STATUS and isinstance(item[i - 1], str) and item[i - 1] in _SOURCES:
            vals = item[: i - 2]
            value = vals[0] if len(vals) == 1 else ", ".join(str(v) for v in vals)
            note = ", ".join(str(n) for n in item[i + 1:]) if len(item) > i + 1 else ""
            return {"value": value, "unit": item[i - 2], "src": item[i - 1], "status": item[i], "note": note}
    return None


_RAW = yaml.safe_load(BASIS_FILE.read_text())
_SOURCES = _RAW["sources"]


class Basis:
    """Dotted access: B.v('kettle.L_in') -> 6700 ; B.leaf('kettle.L_in') -> full record."""

    def __init__(self, raw):
        self.raw = raw
        self.sources = raw["sources"]
        self.meta = raw["meta"]
        self.leaves: dict[str, dict] = {}
        self._walk(raw, "")

    def _walk(self, node, path):
        if isinstance(node, dict):
            for k, v in node.items():
                if path == "" and k in ("sources", "meta"):
                    continue
                self._walk(v, f"{path}.{k}" if path else k)
        else:
            leaf = _parse_leaf(node)
            if leaf is not None:
                self.leaves[path] = leaf

    def leaf(self, path):
        return self.leaves[path]

    def v(self, path):
        return self.leaves[path]["value"]

    def table(self):
        """Rows for reports: (path, value, unit, source title, status)."""
        return [(p, l["value"], l["unit"], l["src"], l["status"], l["note"]) for p, l in self.leaves.items()]


B = Basis(_RAW)


# ------------------------------------------------------------------------------------------
@dataclass
class Geo:
    """Derived geometry (mm). Names follow the drawing tags."""

    # kettle
    kLi: float = B.v("kettle.L_in")
    kWi: float = B.v("kettle.W_in")
    kDi: float = B.v("kettle.D_in")
    kt: float = B.v("kettle.plate")
    kri: float = B.v("kettle.corner_r_in")
    rim: float = B.v("levels.kettle_rim")
    zinc: float = B.v("levels.zinc_surface")
    flw: float = B.v("kettle.flange_w")
    flt: float = B.v("kettle.flange_t")
    lipw: float = B.v("kettle.lip_w")
    lipt: float = B.v("kettle.lip_t")
    # casing
    cL: float = B.v("casing.L")          # inner
    cW: float = B.v("casing.W")          # inner
    ct: float = B.v("casing.wall_plate")
    cfp: float = B.v("casing.floor_plate")
    cbase: float = B.v("levels.casing_base")
    ctop: float = B.v("levels.casing_top")
    captop: float = B.v("levels.cap_beam_top")
    deck: float = B.v("levels.deck_top")
    lin: float = B.v("lining.wall_total")
    reb: float = B.v("lining.wall_rebate")
    # burners
    bZ: float = B.v("levels.burner_axis")
    bX: float = B.v("burners.offset_X")
    flame_d: float = B.v("burners.flame_dia")
    # civil
    pad_bot: float = B.v("levels.pad_underside")
    bpit_floor: float = B.v("levels.burner_pit_floor")
    bpit_slab: float = B.v("levels.burner_pit_slab_under")
    trench_floor: float = B.v("levels.trench_clear_floor")

    def __post_init__(self):
        g = self
        g.kLo, g.kWo = g.kLi + 2 * g.kt, g.kWi + 2 * g.kt          # 6800 x 1350
        g.kro = g.kri + g.kt                                         # 300
        g.k_in_bot = g.rim - g.kDi                                   # -1010
        g.k_out_bot = g.k_in_bot - g.kt                              # -1060
        g.fl_bot = g.rim - g.flt                                     # +260 flange underside
        g.lip_top = g.fl_bot - B.v("kettle.lip_below_flange")        # +60
        g.hdb_top = g.lip_top + 25                                   # +85
        g.topins_top = g.hdb_top + 150                               # +235 (25 clear under the deck datum)
        # casing (inner 8200 x 2750) + 6 mm plate
        g.cXi, g.cYi = g.cW / 2, g.cL / 2                            # 1375, 4100
        g.cXo, g.cYo = g.cXi + g.ct, g.cYi + g.ct                    # 1381, 4106
        g.lfX, g.lfY = g.cXi - g.lin, g.cYi - g.lin                  # lining face 1125, 3850
        g.lrX, g.lrY = g.lfX + g.reb, g.lfY + g.reb                  # rebated face 1175, 3900
        # floor build-up (D-04)
        g.f_plate_top = g.cbase + g.cfp                              # -1565
        g.f_casi_top = g.f_plate_top + 50                            # -1515  2 x 25 CaSi
        g.f_mpi_top = g.f_casi_top + 25                              # -1490  25 microporous
        g.f_blk_top = g.f_mpi_top + 150                              # -1340  3 x 50 blanket 64 (A-B-A)
        g.f_top = g.f_blk_top + 25                                   # -1315  HD board wear face = hearth
        # ventilated foundation (D-15): ISMB 150 grillage at 600 c/c on the pad, channels open to the pit gaps
        g.grill_h = 150
        g.pad_top = g.cbase - g.grill_h                              # -1725
        g.pad_bot = g.pad_top - 600                                  # -2325
        g.hearth_clear = g.k_out_bot - g.f_top                       # 280
        # cap beam 300 x 100 on casing top
        g.cap_in_X, g.cap_in_Y = g.cXo - 300, g.cYo - 300            # 1081, 3806
        # support ring
        g.strip_top, g.strip_bot = g.fl_bot, g.fl_bot - 8            # 260 / 252
        g.ring_top = g.strip_bot                                     # 252
        g.ring_out_X = g.kWo / 2 + g.flw                             # 795
        g.ring_out_Y = g.kLo / 2 + g.flw                             # 3520
        g.rib_top, g.rib_bot = g.deck - 6 - 2, g.deck - 6 - 2 - 200  # 248 / 48
        # alleys
        g.gap = g.lfX - g.kWo / 2                                    # 450
        g.burner_to_lining = g.lfX - g.bX                            # 178.5
        g.flame_to_lining = g.burner_to_lining - g.flame_d / 2       # 80
        g.flame_to_kettle = g.bX - g.kWo / 2 - g.flame_d / 2         # 173
        # pits (D-08)
        g.pitX = 1500                                                # inner half-width of furnace + burner pits
        g.pitw = 200
        g.bpitY0, g.bpitY1 = g.cYo, g.cYo + 1800                     # 4106 .. 5906
        # flue (D-10)
        g.flueY = -2500
        g.flue_cut = (1000, 600)                                     # Y x Z
        g.flue_cut_z = (-750, -150)
        g.flue_pass = (700, 300)
        g.flue_pass_z = (-600, -300)
        # dryer (D-11): clear 6000 x 7500 x 1400, centre X -7500
        g.dX0, g.dX1, g.dY = -10500, -4500, 3750
        g.d_floor = -1400
        g.d_lin = 100                                                # D-14
        g.d_wall = 250
        g.dP = [-9750, -8250, -6750, -5250]
        # trenches (clear, Z -1000..0) as (x0, x1, y0, y1)
        g.trenches = {
            "HRL-02a": (-4150, -2200, -450, 450),      # return, from dryer east wall (RCC outer face -4150)
            "HRL-02b": (-3100, -2200, -2000, -450),    # return, down to the junction
            "HRL-03":  (-3150, -2150, -3000, -2000),   # three-way junction
            "HRL-04":  (-3150, -2150, -6950, -3000),   # suction to the mixing box
            "HRL-08": (-11950, -10850, -8650, 500),    # discharge: from the blower at the SW corner north to the supply box (D-22)
        }
        g.flue_trench = (-2150, -g.pitX - g.pitw, g.flueY - 630, g.flueY + 630)   # 1260 wide envelope
        # mixing box S2
        g.mb = (-3400, -1900, -8250, -6950, -1100, 1600)
        # recirculation blower
        g.rb_axis = (-11950, -11200, -7600, 900)     # scroll x0, x1, y, z: SW corner, axis on the Ø1,114 cut-out at +0.90 (D-22)
        g.suction = (g.mb[0] - 60, -10050, -7600, 900, 550)   # from the mixing-box outlet flange  # Ø1100 duct x0 -> x1 along Y -7600 at +0.90
        g.rb_r = 950
        # stack + bleed
        g.bleed = (-11400, -6100)                    # riser out of the discharge trench just downstream of the blower
        g.stack = (-7600, -14900)
        g.bleed_route = [(-11400, -6100, -500), (-11400, -6100, 4000), (-7600, -6100, 4000), (-7600, -14700, 4000), (-7600, -14900, 4000)]
        # combustion air
        g.ring = (2125, 4850, 500)                   # half X, half Y, Z
        g.cb = (2700, 4100, -5700, -4500)            # blower plinth x0,x1,y0,y1
        g.pf = {"PF-N": (2600, 3200, 5200, 5800), "PF-S": (2600, 3200, -6800, -6200)}
        g.skid_y, g.skid_x_a11, g.skid_pitch = -7600, 4180, 620
        g.gas_hdr_x = 1900
        # gas routes (pipe centrelines, mm) per SH-PID-02A Rev U:
        # NG-65-001 header on sleepers at +0.140 (with a capped tee for furnace 2) -> NG-50-101 furnace main to both pits,
        # ending in each pit at a high-level manifold at -0.150 from which the DN40 main leg and the DN15 ignition leg drop.
        gz = B.v("levels.gas_header_cl")
        g.pit_manifold_z = -150
        g.leg_main = (-700, g.cYo + 1044)        # north burner: main leg X, Y (5150); south is the point reflection
        g.leg_ign = (-450, g.cYo + 1044)
        g.merge_z = -1450
        g.gas_header = [(g.skid_x_a11 - 400, g.skid_y, 1100), (g.skid_x_a11 - 400, g.skid_y, gz),
                        (g.gas_hdr_x, g.skid_y, gz), (g.gas_hdr_x, -6600, gz)]
        g.gas_f2 = [(2600, g.skid_y, gz), (2600, g.skid_y - 900, gz)]           # capped branch: furnace 2 main NG-50-201
        my = g.leg_main[1]
        g.gas_main_N = [(g.gas_hdr_x, -6600, gz), (g.gas_hdr_x, 6600, gz), (153.5, 6600, gz), (153.5, 5800, gz),
                        (153.5, 5800, g.pit_manifold_z), (153.5, my, g.pit_manifold_z), (g.leg_main[0], my, g.pit_manifold_z)]
        g.gas_main_S = [(g.gas_hdr_x, -6600, gz), (-153.5, -6600, gz), (-153.5, -5800, gz), (-153.5, -5800, g.pit_manifold_z),
                        (-153.5, -my, g.pit_manifold_z), (-g.leg_main[0], -my, g.pit_manifold_z)]
        g.gas_vent = [(g.skid_x_a11 + 7 * g.skid_pitch, g.skid_y, 1400), (g.skid_x_a11 + 7 * g.skid_pitch, g.skid_y, 12500)]

    @staticmethod
    def plen(pts):
        return sum(math.dist(a, b) for a, b in zip(pts, pts[1:]))

    def summary(self):
        keys = ["kLo", "kWo", "k_out_bot", "fl_bot", "lip_top", "cXo", "cYo", "lfX", "lfY", "f_top",
                "hearth_clear", "gap", "flame_to_lining", "flame_to_kettle", "ring_out_X", "cap_in_X"]
        return {k: getattr(self, k) for k in keys}


G = Geo()

if __name__ == "__main__":
    print(B.meta)
    print(len(B.leaves), "basis entries")
    for k, v in G.summary().items():
        print(f"{k:16s} {v}")
    bad = [p for p in B.leaves if B.leaves[p]["src"] not in B.sources]
    print("unknown sources:", bad)
