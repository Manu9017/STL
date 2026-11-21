"""Combustion gas and air exactly per SH-PID-02A Rev U (sheets 1-2), one furnace (burners 1 & 2).

Every tagged item on the P&ID is its own part, carrying its tag (pid), make and model from the sheet-2 bill of
material, so the 3D model, the BOM and the viewer's P&ID tab agree.

  A  common gas train A1 → A11 (one factory-assembled Eclipse set; also serves furnace 2 via a capped tee)
  B  main gas leg per burner: B4 → B2 + B2 (double block) → B1 GIK 1:1 → B3 → B5 → merge tee
  C  ignition gas leg per burner, tapped upstream of B4: C3 → C1 → C2 + C2 → C4 → C19 → merge tee
     merge tee below the burner → one 2" NG-50-xx3 into the burner; C12 direct spark ignitor, C6 UV + C9/C11
     cooling air, C7 transformer close to the burner (C8 2.5 m), C5 BCU 370
  D  AEP-VB-2.5 7.5 HP blower, D7 inlet filter, D8 flexible, 7" discharge with D9, D1 and D4 + D3 on two short
     branches, 300 × 150 header, 150 × 150 closed ring, 4" branch per burner with D2, ¼" Cu impulse to B1,
     ½" UV cooling air from the 7" discharge to each C6.
"""
from __future__ import annotations

import math

from ..basis import B, G
from .lib import box, compound, cyl, duct, merge, pipe, sph

R_ = {"15": 10.65, "25": 16.7, "40": 24.15, "50": 30.15, "65": 36.5, "100": 57.15, "7in": 88.9, "quarter": 4.0, "half": 10.65}
BOM = {}
for grp in ("A", "B", "C", "D"):
    for tag, desc, make, model, qty in B.raw["pid"][grp]:
        BOM[tag] = (desc, make, str(model), qty)
SRC = "SH-PID-02A Rev U"


def spec(tag, extra=""):
    d, mk, md, q = BOM[tag]
    s = f"{d} · {mk} {md}".strip()
    return s + (f" · {extra}" if extra else "")


def add(R, tag, name, shape, system, color, grp, extra="", status="C", per_burner=True, note="", qty=None):
    d, mk, md, q = BOM[tag]
    R.add(name, shape, system, color, tag=tag, title=f"{tag} {d}" + (f" ({grp})" if per_burner else ""), spec=spec(tag, extra),
          material=f"{mk} {md}", src=SRC, status="O" if mk == "TO ORDER" else status, qty=str(qty or (1 if per_burner else q)),
          note=note or ("Not in either purchase order — raise it (H21)." if mk == "TO ORDER" else ""), pid=tag, pidgroup=grp)


# ------------------------------------------------------------------------------ valve shapes (along any axis)
def _axis(p, d, L):
    x, y, z = p
    dx, dy, dz = d
    return (x - dx * L / 2, y - dy * L / 2, z - dz * L / 2), (x + dx * L / 2, y + dy * L / 2, z + dz * L / 2)


def ball_valve(p, d, r, lever=(0, 1, 0)):
    a, b = _axis(p, d, 3.2 * r)
    body = compound(cyl(a, b, r * 1.25), sph(p, r * 1.7))
    x, y, z = p
    up = (0, 0, 1) if d[2] == 0 else (1, 0, 0)
    stem_top = (x + up[0] * r * 2.6, y + up[1] * r * 2.6, z + up[2] * r * 2.6)
    stem = cyl(p, stem_top, r * 0.3)
    lv = cyl(stem_top, (stem_top[0] + lever[0] * r * 5, stem_top[1] + lever[1] * r * 5, stem_top[2] + lever[2] * r * 5), r * 0.25)
    return compound(body, stem, lv)


def cock(p, d, r):
    a, b = _axis(p, d, 2.6 * r)
    x, y, z = p
    return merge(cyl(a, b, r * 1.35), box(x - r * 1.1, x + r * 1.1, y - r * 1.1, y + r * 1.1, z - r * 1.1, z + r * 1.1),
                 box(x - r * .2, x + r * .2, y - r * .2, y + r * 3.2, z - r * .2, z + r * .2))


def solenoid(p, size):
    """VAS body + coil housing; size = body edge (mm)."""
    x, y, z = p
    h = size / 2
    return merge(box(x - h, x + h, y - h, y + h, z - h * .8, z + h * .8),
                 box(x - h * .55 + h * 1.0, x + h * .55 + h * 1.0, y - h * .55, y + h * .55, z - h * .6, z + h * .6),
                 cyl((x + h * 1.55, y, z), (x + h * 1.8, y, z), h * .25))


def governor(p, r_dome, r_body):
    x, y, z = p
    return merge(cyl((x, y, z - r_body), (x, y, z + r_body), r_body), cyl((x - r_body - 30, y, z), (x - r_body - 30 - r_dome * .55, y, z), r_dome),
                 cyl((x - r_body - 30, y, z), (x - r_body, y, z), r_body * .6))


def gauge(p, stem_dir, r=60):
    x, y, z = p
    t = (x + stem_dir[0] * 120, y + stem_dir[1] * 120, z + stem_dir[2] * 120)
    return merge(cyl(p, t, 7), cyl((t[0], t[1] - 18, t[2] + r), (t[0], t[1] + 18, t[2] + r), r), box(t[0] - 8, t[0] + 8, t[1] - 8, t[1] + 8, t[2], t[2] + r - 40))


def pswitch(p, stem_dir):
    x, y, z = p
    t = (x + stem_dir[0] * 110, y + stem_dir[1] * 110, z + stem_dir[2] * 110)
    return merge(cyl(p, t, 7), box(t[0] - 55, t[0] + 55, t[1] - 45, t[1] + 45, t[2], t[2] + 150), cyl((t[0] + 55, t[1], t[2] + 110), (t[0] + 85, t[1], t[2] + 110), 12))


# ------------------------------------------------------------------------------ A: common gas train + header + main
def build_gas(R):
    g = G
    y, z = g.skid_y, 1100
    items = B.raw["pid"]["A"]
    xs = {tag: g.skid_x_a11 + (len(items) - 1 - i) * g.skid_pitch for i, (tag, *_r) in enumerate(items)}   # A1 east … A11 west (D-18)
    frame = [box(g.skid_x_a11 - 600, xs["A1"] + 600, y - 320, y + 320, z - 480, z - 400)]
    for px in (g.skid_x_a11 - 450, (g.skid_x_a11 + xs["A1"]) / 2, xs["A1"] + 450):
        for dy in (-260, 260):
            frame.append(box(px - 50, px + 50, y + dy - 50, y + dy + 50, 0, z - 400))
    R.add("GAS-01 Gas train A skid frame", compound(*frame), "gas", "steel2", tag="GAS-01", title="Common gas train A — skid frame",
          spec="One factory-assembled, pressure- and function-tested Eclipse unit serving all four burners (both furnaces)",
          src=SRC, status="C", pidgroup="A")
    run = merge(pipe([(xs["A1"] + 700, y, z), (xs["A4"] - 300, y, z)], R_["50"]), pipe([(xs["A4"] - 300, y, z), (g.skid_x_a11 - 400, y, z)], R_["65"]))
    R.add("GAS-02 Gas train A piping", run, "gas", "gas", tag="GAS-02", title="Gas train A piping (2\" in → 2½\" out)",
          spec="NATURAL GAS IN at A1; DN50 to A4, DN65 from A10 to A11", src=SRC, status="C", pidgroup="A")
    shapes = {
        "A1": lambda x: ball_valve((x, y, z), (1, 0, 0), R_["50"]),
        "A2": lambda x: merge(cyl((x, y, z - 230), (x, y, z + 190), 120), cyl((x - 160, y, z), (x + 160, y, z), 45)),
        "A3": lambda x: gauge((x, y, z + R_["50"]), (0, 0, 1)),
        "A4": lambda x: cock((x, y, z), (1, 0, 0), R_["40"]),
        "A5": lambda x: merge(cyl((x, y, z + 40), (x, y, z + 300), 190), cyl((x, y, z - 220), (x, y, z + 40), 80), cyl((x - 150, y, z), (x + 150, y, z), 55)),
        "A6": lambda x: pswitch((x, y, z + R_["65"]), (0, 0, 1)),
        "A7": lambda x: pswitch((x, y, z + R_["65"]), (0, 0, 1)),
        "A8": lambda x: gauge((x, y, z + R_["65"]), (0, 0, 1)),
        "A9": lambda x: cock((x, y, z), (1, 0, 0), R_["40"]),
        "A10": lambda x: merge(solenoid((x - 150, y, z), 230), solenoid((x + 150, y, z), 230)),
        "A11": lambda x: ball_valve((x, y, z), (1, 0, 0), R_["65"]),
    }
    for tag, *_r in items:
        add(R, tag, f"{tag} {BOM[tag][0]}", shapes[tag](xs[tag]), "gas", "valve" if tag not in ("A2", "A5", "A10") else ("gas" if tag != "A10" else "solenoid"),
            "A", per_burner=False, extra={"A5": "relief / SSOV vent to safe", "A6": "→ all BCUs + PLC, gas-pressure lockout",
                                          "A7": "→ all BCUs + PLC, gas-pressure lockout", "A10": "common to all four burners; must close on any lockout and E-stop (H6)"}.get(tag, ""))
    vent = merge(pipe([(xs["A5"], y, z + 300), (xs["A5"], y, 12500)], R_["25"]), cyl((xs["A5"], y, 12500), (xs["A5"], y, 12700), 50))
    R.add("GAS-06 A5 relief and SSOV vent", vent, "gas", "gas", tag="GAS-06", title="A5 relief / SSOV vent → safe",
          spec="Rises continuously to a safe outdoor place; no valve, no low pocket; rain cap", src=SRC, status="C", pid="A5 vent", pidgroup="A")
    hdr = pipe(g.gas_header, R_["65"])
    f2 = merge(pipe(g.gas_f2, R_["65"]), cyl(g.gas_f2[-1], (g.gas_f2[-1][0], g.gas_f2[-1][1] - 25, g.gas_f2[-1][2]), 85))
    R.add("NG-65-001 Main gas header DN65", merge(hdr, f2), "gas", "gas", tag="NG-65-001", title="NG-65-001 main gas header DN65 (2½\")",
          spec=f"A11 outlet → both furnace mains; on sleepers at +0.140; {G.plen(g.gas_header) / 1000:.1f} m to the furnace-1 tee; capped tee for furnace 2 main NG-50-201",
          material="ASTM A106 Gr B, canary yellow (IS 2379)", src=SRC, status="C", pid="NG-65-001", pidgroup="Lines")
    R.add("NG-50-101 Furnace main DN50", merge(pipe(g.gas_main_N, R_["50"]), pipe(g.gas_main_S, R_["50"])), "gas", "gas", tag="NG-50-101",
          title="NG-50-101 furnace main DN50 (2\") to burners 1 & 2",
          spec=f"Header tee → both burner pits, into a high-level manifold at −0.150 in each pit; north {G.plen(g.gas_main_N) / 1000:.1f} m, south {G.plen(g.gas_main_S) / 1000:.1f} m; branches off the top or side only",
          src=SRC, status="C", pid="NG-50-101", pidgroup="Lines")
    sl = [box(g.gas_hdr_x - 120, g.gas_hdr_x + 120, yy - 100, yy + 100, 0, 90) for yy in range(-6400, 6601, 1500)]
    sl += [box(xx - 100, xx + 100, y - 120, y + 120, 0, 90) for xx in (2400, 3200)] + [box(2480, 2720, y - 700, y - 500, 0, 90)]
    R.add("GAS-05 Pipe sleepers", compound(*sl), "gas", "concrete2", tag="GAS-05", title="Pipe sleepers", spec="RCC 240 × 200 × 90 @ 1.5 m", src=SRC, status="C")


# ------------------------------------------------------------------------------ B/C: burner trains (north = burner 1; south = point reflection)
def _P(s):
    return lambda x, y, z: (s * x, s * y, z)


def build_burner_trains(R):
    g = G
    zt = g.pit_manifold_z
    for i, s in ((1, 1), (2, -1)):
        P = _P(s)
        grp = f"Burner {i}"
        bx = -g.bX                         # burner-1 X; P() mirrors for burner 2
        mx, my = g.leg_main
        ix, iy = g.leg_ign
        zm = g.merge_z
        rear = g.cYo + 702                 # plenum rear face
        # NG-40 main leg and NG-15 ignition leg (pipes)
        main = pipe([P(mx, my, zt), P(mx, my, zm)], R_["40"], elbows=False)
        ign = pipe([P(ix, my, zt), P(ix, iy, zm), P(mx, my, zm)], R_["15"])
        tee = sph(P(mx, my, zm), R_["50"] * 1.3)
        ng3 = pipe([P(mx, my, zm), P(bx, my, zm), P(bx, my, g.bZ), P(bx, rear + 92, g.bZ)], R_["50"])
        R.add(f"NG-40-1{i}1 Burner {i} main gas leg", main, "bc", "gas", tag=f"NG-40-1{i}1", title=f"NG-40-1{i}1 main gas leg DN40 (burner {i})",
              spec="Furnace main → merge tee, downstream of B3 (vertical drop from the pit manifold)", src=SRC, status="C", pid=f"NG-40-1{i}1", pidgroup=grp)
        R.add(f"NG-15-1{i}2 Burner {i} ignition gas", ign, "bc", "ign", tag=f"NG-15-1{i}2", title=f"NG-15-1{i}2 ignition gas DN15 (burner {i})",
              spec="Tapped upstream of B4 → merge tee, downstream of C4; IGNITION GAS line (direct spark — no pilot burner)", src=SRC, status="C", pid=f"NG-15-1{i}2", pidgroup=grp)
        R.add(f"NG-50-1{i}3 Burner {i} merged 2 inch inlet", merge(tee, ng3), "bc", "gas", tag=f"NG-50-1{i}3", title=f"NG-50-1{i}3 merge tee + 2\" burner inlet (burner {i})",
              spec="B3/B5 and C4/C19 meet at a tee below the burner; one 2\" line runs into the burner gas inlet (H1: confirm with Bloom)",
              src=SRC, status="O", pid=f"NG-50-1{i}3", pidgroup=grp, note="Hold H1.")
        # main leg components (top → bottom)
        zB = {"B4": -300, "B2a": -470, "B2b": -650, "B1": -850, "B3": -1050, "B5": -1230}
        lever = (0, s, 0)
        add(R, "B4", f"B4 Burner {i} ball valve", ball_valve(P(mx, my, zB["B4"]), (0, 0, 1), R_["40"], lever), "bc", "valve", grp)
        B2 = merge(solenoid(P(mx, my, zB["B2a"]), 170), solenoid(P(mx, my, zB["B2b"]), 170))
        add(R, "B2", f"B2 Burner {i} double solenoid", B2, "bc", "solenoid", grp, extra="2 × VAS 240R/NW in series = double block; nothing between the two valves", qty=2)
        gik = merge(cyl(P(mx, my, zB["B1"] - 60), P(mx, my, zB["B1"] + 60), 70), cyl(P(mx - s * 75, my, zB["B1"]), P(mx - s * 200, my, zB["B1"]), 115))
        add(R, "B1", f"B1 Burner {i} GIK ratio controller", gik, "bc", "valveb", grp, extra="1:1; air impulse from this burner's own branch after D2")
        add(R, "B3", f"B3 Burner {i} flow adjusting cock", cock(P(mx, my, zB["B3"]), (0, 0, 1), R_["40"]), "bc", "valve", grp)
        add(R, "B5", f"B5 Burner {i} gas-leg isolation", ball_valve(P(mx, my, zB["B5"]), (0, 0, 1), R_["40"], lever), "bc", "valve", grp, extra="immediately before the merge tee (NEW)")
        # ignition leg components
        zC = {"C3": -290, "C1": -460, "C2a": -640, "C2b": -780, "C4": -960, "C19": -1160}
        add(R, "C3", f"C3 Burner {i} ignition ball valve", ball_valve(P(ix, iy, zC["C3"]), (0, 0, 1), R_["15"], lever), "bc", "ign", grp)
        gdj = merge(cyl(P(ix, iy, zC["C1"] - 45), P(ix, iy, zC["C1"] + 45), 42), cyl(P(ix + s * 55, iy, zC["C1"]), P(ix + s * 150, iy, zC["C1"]), 70))
        add(R, "C1", f"C1 Burner {i} ignition gas governor", gdj, "bc", "ign", grp)
        C2 = merge(solenoid(P(ix, iy, zC["C2a"]), 110), solenoid(P(ix, iy, zC["C2b"]), 110))
        add(R, "C2", f"C2 Burner {i} ignition double solenoid", C2, "bc", "solenoid", grp, extra="2 × VAS 115R/NW = double block", qty=2)
        add(R, "C4", f"C4 Burner {i} ignition flow cock", cock(P(ix, iy, zC["C4"]), (0, 0, 1), R_["15"]), "bc", "ign", grp)
        add(R, "C19", f"C19 Burner {i} ignition-leg isolation", ball_valve(P(ix, iy, zC["C19"]), (0, 0, 1), R_["15"], lever), "bc", "ign", grp, extra="immediately before the merge tee (NEW)")
        # C12 spark ignitor on the body, C6 UV at the rear with C9 + C11 cooling air, C7 transformer close by, C5 BCU on the pit end wall
        ytop = g.cYo + 150
        c12 = merge(cyl(P(bx + 120, ytop, g.bZ + 150), P(bx + 120, ytop, g.bZ + 300), 14), cyl(P(bx + 120, ytop, g.bZ + 300), P(bx + 120, ytop, g.bZ + 360), 22))
        add(R, "C12", f"C12 Burner {i} direct spark ignitor", c12, "burner", "black", grp, extra="sparks the merged gas directly; no pilot burner, no pilot air")
        uvx = bx + 120
        c6 = merge(cyl(P(uvx, rear, g.bZ + 90), P(uvx, rear + 150, g.bZ + 90), 26), box(*sorted((P(uvx - 45, 0, 0)[0], P(uvx + 45, 0, 0)[0])),
                                                                                       *sorted((P(0, rear + 150, 0)[1], P(0, rear + 260, 0)[1])), g.bZ + 45, g.bZ + 135))
        add(R, "C6", f"C6 Burner {i} UV detector", c6, "instr", "black", grp, extra="½\" UV cooling air from this furnace's own blower")
        c7x0, c7x1 = -g.pitX + 10, -g.pitX + 140
        c7 = box(*sorted((P(c7x0, 0, 0)[0], P(c7x1, 0, 0)[0])), *sorted((P(0, ytop + 150, 0)[1], P(0, ytop + 330, 0)[1])), g.bZ + 140, g.bZ + 320)
        add(R, "C7", f"C7 Burner {i} ignition transformer", c7, "instr", "panel", grp, extra="on the pit side wall beside its burner: C8 is 2.5 m per burner")
        c8 = pipe([P(c7x1, ytop + 240, g.bZ + 230), P(bx + 120, ytop + 240, g.bZ + 330), P(bx + 120, ytop, g.bZ + 360)], 4, elbows=False)
        add(R, "C8", f"C8 Burner {i} HT ignition cable", c8, "instr", "black", grp, extra="≈0.7 m used of the 2.5 m allowance; keep away from the C6 cable", qty=1)
        wall = s * g.bpitY1
        c5 = box(*sorted((P(300, 0, 0)[0], P(700, 0, 0)[0])), *sorted((wall - s * 120, wall)), -950, -400)
        add(R, "C5", f"C5 Burner {i} BCU 370", c5, "instr", "panel", grp, extra="sequence controller (the 3500-148 has none): air proof → purge → spark → UV proof → main; lockout needs manual reset; to existing PLC S7-1500")
        # ¼" Cu air impulse from the branch after D2 to B1
        hy = g.ring[1]
        imp = pipe([P(bx + 60, hy, 150), P(-1060, hy, 150), P(-1060, my + 100, 150), P(-1060, my + 100, zB["B1"]), P(mx - 205, my + 100, zB["B1"])], R_["quarter"], elbows=False)
        R.add(f"IMP-{i} Burner {i} air impulse to B1", imp, "air", "copper", tag=f"IMP-{i}", title=f"¼\" Cu air impulse → B1 (burner {i})",
              spec="Tapped from this burner's 4\" branch downstream of D2 (H8: 1\" per the valve GA — measure on site)", src=SRC, status="C", pid="¼\" Cu", pidgroup=grp)
        # C9 + C11 on the UV cooling-air drop
        c9p = P(uvx, rear + 300, 100)
        add(R, "C9", f"C9 Burner {i} UV cooling-air cock", ball_valve(c9p, (0, 0, 1), R_["half"], (s, 0, 0)), "air", "uvair", grp)
        c11 = cyl(P(uvx, rear + 300, -230), P(uvx, rear + 300, g.bZ + 90), 16).union(cyl(P(uvx, rear + 300, g.bZ + 90), P(uvx, rear + 260, g.bZ + 90), 16))
        add(R, "C11", f"C11 Burner {i} UV flexible connector", c11, "air", "rubber", grp)


# ------------------------------------------------------------------------------ D: combustion air
def build_air(R):
    g = G
    hx, hy, zr = g.ring
    grp = "D"
    x0, x1, y0, y1 = 2800, 4000, -5800, -4400
    plinth = box(x0, x1, y0, y1, 0, 150)
    frame = merge(box(x0 + 50, x1 - 50, y0 + 50, y0 + 150, 230, 330), box(x0 + 50, x1 - 50, y1 - 150, y1 - 50, 230, 330),
                  box(x0 + 50, x0 + 150, y0 + 50, y1 - 50, 230, 330), box(x1 - 150, x1 - 50, y0 + 50, y1 - 50, 230, 330))
    avm = [cyl((x, yy, 150), (x, yy, 230), 50) for x in (x0 + 100, x1 - 100) for yy in (y0 + 100, y1 - 100)]
    R.add("AIR-01 Blower plinth and frame", merge(plinth, compound(frame, *avm)), "air", "concrete2", tag="AIR-01", title="Blower plinth, base frame and AVMs",
          spec="RCC plinth 1,200 × 1,400 × 150; ISMC 100 base frame on 4 anti-vibration mounts; M16 anchors", src="D-13", status="D", pidgroup=grp)
    cx, cy, cz = 3300, -5050, 800
    scroll = merge(cyl((cx, cy - 175, cz), (cx, cy + 175, cz), 450), box(cx - 300, cx + 300, cy - 200, cy + 200, 330, cz - 350),
                   box(cx + 200, cx + 450, cy - 125, cy + 125, cz, cz + 520))
    motor = merge(cyl((cx, cy + 260, cz), (cx, cy + 680, cz), 150), box(cx - 150, cx + 150, cy + 260, cy + 680, 330, cz - 150))
    add(R, "BLW", "BLW Combustion air blower AEP-VB-2.5", merge(scroll, motor), "air", "fan", grp, per_burner=False, qty=1,
        extra="1,400 m³/h at 725 mmWC (Rev H duty); serves this furnace's ring only", note="At λ 1.125 full fire needs ≈1,430 m³/h at 35 °C (C-01, O-04).")
    add(R, "D7", "D7 Blower inlet filter", cyl((cx, cy - 175, cz), (cx, cy - 575, cz), 200), "air", "galv", grp, per_burner=False, qty=1)
    ox, oz = cx + 325, cz + 520
    add(R, "D8", "D8 Flexible connection at blower", cyl((ox, cy, oz), (ox, cy, oz + 150), R_["7in"] + 18), "air", "rubber", grp, per_burner=False, qty=1)
    zd = 1600
    seven = pipe([(ox, cy, oz + 150), (ox, cy, zd), (2500, cy, zd)], R_["7in"])
    R.add("CA-200-101 7 inch blower discharge", seven, "air", "airduct", tag="CA-200-101", title="CA-200-101 7\" round blower discharge",
          spec="Blower → 300 × 150 header; D9 in the line, then two short branches (D1; D4 + D3)", src=SRC, status="C", pid="CA-200-101", pidgroup="Lines")
    add(R, "D9", "D9 Ball valve in the 7 inch discharge", ball_valve((3400, cy, zd), (1, 0, 0), 70, (0, 1, 0)), "air", "valve", grp, per_burner=False, qty=1)
    d1 = merge(pipe([(3200, cy, zd + R_["7in"]), (3200, cy, zd + 250)], R_["half"]), pswitch((3200, cy, zd + 250), (0, 0, 1)))
    add(R, "D1", "D1 Air pressure switch", d1, "instr", "panel", grp, per_burner=False, qty=1, extra="LOW combustion air → both BCUs + PLC (H2: a shut D2 is not seen)")
    d4p = (3000, cy, zd + R_["7in"] + 120)
    d4 = merge(pipe([(3000, cy, zd + R_["7in"]), (3000, cy, zd + 380)], R_["half"]), cock(d4p, (0, 0, 1), R_["half"]))
    add(R, "D4", "D4 Manual cock", d4, "instr", "valve", grp, per_burner=False, qty=1, extra="in series with D3")
    add(R, "D3", "D3 Air pressure gauge", gauge((3000, cy, zd + 380), (0, 0, 1)), "instr", "panel", grp, per_burner=False, qty=1)
    trans = merge(box(2500, 2350, cy - 150, cy + 150, zd - 75, zd + 75), cyl((2500, cy, zd), (2560, cy, zd), R_["7in"]))
    hdr = duct([(2350, cy, zd), (hx, cy, zd), (hx, -4600, zd), (hx, -4600, zr + 75)], 300, 150)
    R.add("CA-300-101 Air header 300 × 150", merge(trans, hdr), "air", "airduct", tag="CA-300-101", title="7\" → 300 × 150 header into the ring",
          spec="Joins the closed ring on its east side", src=SRC, status="C", pid="300×150", pidgroup="Lines")
    ring = duct([(-hx, -hy, zr), (hx, -hy, zr), (hx, hy, zr), (-hx, hy, zr), (-hx, -hy, zr)], 150, 150)
    R.add("CA-150-103 Closed air ring 150 × 150", ring, "air", "airduct", tag="CA-150-103", title="CA-150-103 closed air ring 150 × 150",
          spec="750 clear of the casing at +0.500; long sides and short/return sides; parasitic circulation (H3: allow for it in the purge time)",
          src=SRC, status="C", pid="CA-150-103", pidgroup="Lines")
    # ½" UV cooling air from the 7" discharge to both C6 heads
    uvx = -g.bX + 120
    rear = g.cYo + 702
    uv = merge(pipe([(2750, cy, zd - R_["7in"]), (2750, cy, 350), (2350, cy, 350), (2350, 5000, 350), (uvx, 5000, 350), (uvx, rear + 300, 350), (uvx, rear + 300, -230)], R_["half"]),
               pipe([(2350, cy, 350), (-uvx, cy, 350), (-uvx, -(rear + 300), 350), (-uvx, -(rear + 300), -230)], R_["half"]))
    R.add("CA-15-101 UV cooling air", uv, "air", "uvair", tag="CA-15-101", title="CA-15-101 ½\" UV cooling air",
          spec="From this furnace's own 7\" blower discharge to each C6 UV head via C9 and C11; pipe and fittings SHIVAS site scope", src=SRC, status="C",
          pid="CA-15-101", pidgroup="Lines")
    for i, (bx, s) in enumerate(((-g.bX, 1), (g.bX, -1)), start=1):
        pts = [(bx, s * hy, zr - 75), (bx, s * hy, 60), (bx, s * (g.cYo + 617), 60), (bx, s * (g.cYo + 617), g.bZ + 330)]
        R.add(f"CA-100-1{i} Burner {i} air branch", pipe(pts, R_["100"]), "air", "air", tag=f"CA-100-1{i}", title=f"CA-100-1{i} 4\" air branch (burner {i})",
              spec="From the 150 × 150 ring to the burner air plenum, via D2 (D6 deleted — the branch lands straight on the burner)", src=SRC, status="C",
              pid=f"CA-100-1{i}", pidgroup=f"Burner {i}")
        d2 = merge(cyl((bx, s * hy - 70, 300), (bx, s * hy + 70, 300), R_["100"] + 25),
                   box(bx - 10, bx + 10, s * hy - 10, s * hy + 10, 300, 420), box(bx - 10, bx + 140, s * hy - 10, s * hy + 10, 410, 430))
        add(R, "D2", f"D2 Burner {i} air butterfly", d2, "air", "red", f"Burner {i}", extra="balancing; the B1 impulse is tapped downstream of it")


# ------------------------------------------------------------------------------ pits: fans, rails, ladders
def build_pits(R):
    g = G
    hx = g.pitX
    for key, (x0, x1, y0, y1) in g.pf.items():
        s = 1 if y0 > 0 else -1
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        base = box(x0, x1, y0, y1, 0, 100)
        sc = cyl((cx, cy - 100, 420), (cx, cy + 100, 420), 250)
        mot = cyl((cx, cy + 100, 420), (cx, cy + 400, 420), 100)
        dis = pipe([(cx + 180, cy, 600), (cx + 180, cy, 3000)], 140)
        cowl = cyl((cx + 180, cy, 3000), (cx + 180, cy, 3150), 220)
        yi = s * (g.bpitY1 - 200)
        suc = pipe([(cx - 250, cy, 420), (cx - 250, yi, 420), (hx - 120, yi, 420), (hx - 120, yi, g.bpit_floor + 300)], 140)
        R.add(f"VEN-{key} Pit fan", merge(base, sc, mot, dis, cowl), "pitvent", "fan", tag=f"VEN-{key}",
              title=f"Burner pit fan {'north' if s > 0 else 'south'} (3 HP)",
              spec="3 HP centrifugal; extracts at 300 above the pit floor (LPG is heavier than air); discharges at +3.0 m to atmosphere; ≥ 189 m³/h (20 ACH)",
              src="Crash-barrier annexure (pit fan) · D-09 · C-11", status="D")
        R.add(f"VEN-{key} Suction duct", suc, "pitvent", "galv", tag=f"VEN-{key}d", title=f"Pit fan suction duct {'north' if s > 0 else 'south'}",
              spec="Ø280 GI, over the pit wall, down to −1.450", src="D-09", status="D")
        ya, yb = s * g.bpitY0, s * (g.bpitY1 + 50)
        posts, rails = [], []
        for x in (-hx - 50, hx + 50):
            for yy in [ya + s * k for k in range(0, int(abs(yb - ya)) + 1, 900)] + [yb]:
                posts.append(box(x - 25, x + 25, yy - 25, yy + 25, 0, 1000))
            for zz, h in ((1000, 40), (500, 30)):
                rails.append(box(x - 20, x + 20, min(ya, yb), max(ya, yb), zz - h, zz))
            rails.append(box(x - 5, x + 5, min(ya, yb), max(ya, yb), 0, 100))
        for xx in range(int(-hx - 50), int(hx + 51), 750):
            posts.append(box(xx - 25, xx + 25, yb - 25, yb + 25, 0, 1000))
        for zz, h in ((1000, 40), (500, 30)):
            rails.append(box(-hx - 50, hx + 50, yb - 20, yb + 20, zz - h, zz))
        rails.append(box(-hx - 50, hx + 50, yb - 5, yb + 5, 0, 100))
        R.add(f"PIT-{key[-1]}1 Handrails", compound(*posts, *rails), "pitvent", "yellow", tag=f"PIT-{key[-1]}1",
              title=f"Burner pit handrails ({'north' if s > 0 else 'south'})", spec="1,000 top rail, 500 mid rail, 100 toe board, posts ≤ 900", src="HDG", status="C")
        lx, wall = 900, s * g.bpitY1
        lad = [box(lx - 220, lx - 200, wall - s * 170, wall - s * 150, g.bpit_floor, 1000), box(lx + 200, lx + 220, wall - s * 170, wall - s * 150, g.bpit_floor, 1000)]
        for zz in range(int(g.bpit_floor) + 250, 900, 280):
            lad.append(cyl((lx - 200, wall - s * 160, zz), (lx + 200, wall - s * 160, zz), 10))
        R.add(f"PIT-{key[-1]}2 Cat ladder", compound(*lad), "pitvent", "galv", tag=f"PIT-{key[-1]}2", title=f"Cat ladder ({'north' if s > 0 else 'south'} pit)",
              spec="GI stringers 50 × 20, Ø20 rungs @ 280", src="HDG", status="C")


def build(R):
    build_gas(R)
    build_burner_trains(R)
    build_air(R)
    build_pits(R)
