"""Combustion system: gas skid, header, mains, burner trains; air blower, venturi, header, ring, branches;
burner pits: fans, rails, ladders, burner control units."""
from __future__ import annotations

import math

from ..basis import B, G
from .lib import box, compound, cyl, duct, merge, pipe, sph

DN = {"15": 10.7, "40": 24.15, "50": 30.15, "65": 36.5, "80": 44.45, "100": 57.15, "200": 109.5}   # outside radii (mm)


def _valve_ball(x, y, z, r, axis="x"):
    body = sph((x, y, z), r * 1.6)
    stem = box(x - 6, x + 6, y - 6, y + 6, z, z + r * 2.4)
    lever = box(x - 6, x + 6, y, y + r * 5, z + r * 2.4 - 8, z + r * 2.4)
    return merge(body, stem, lever)


def build_gas(R):
    g = G
    y, z = g.skid_y, 1100
    items = B.raw["gas_train"]["items"]
    xs = [g.skid_x_a11 + (len(items) - 1 - i) * g.skid_pitch for i in range(len(items))]   # A1 east ... A11 west (D-18)
    frame = [box(g.skid_x_a11 - 600, xs[0] + 600, y - 320, y + 320, z - 480, z - 400)]
    for px in (g.skid_x_a11 - 450, (g.skid_x_a11 + xs[0]) / 2, xs[0] + 450):
        for dy in (-260, 260):
            frame.append(box(px - 50, px + 50, y + dy - 50, y + dy + 50, 0, z - 400))
    R.add("GAS-01 Gas train skid frame", compound(*frame), "gas", "steel2", tag="GAS-01", title="Common gas train skid frame",
          spec=f"MS frame {xs[0] - g.skid_x_a11 + 1200:.0f} × 640 on 6 legs; pipe centreline +1.100", src="HDG · D-13", status="D")
    run = pipe([(xs[0] + 700, y, z), (g.skid_x_a11 - 400, y, z)], DN["65"])
    comps = []
    for (tag, kind, desc, model), x in zip(items, xs):
        if kind == "ball":
            comps.append(_valve_ball(x, y, z, 45))
        elif kind == "filter":
            comps.append(cyl((x, y, z - 220), (x, y, z + 180), 120))
        elif kind == "cock":
            comps.append(box(x - 70, x + 70, y - 70, y + 70, z - 70, z + 70).union(box(x - 8, x + 8, y - 8, y + 160, z - 8, z + 8)))
        elif kind == "reg":
            comps.append(merge(cyl((x, y, z + 40), (x, y, z + 300), 190), cyl((x, y, z - 220), (x, y, z + 40), 80)))
        elif kind == "sol":
            comps.append(merge(box(x - 110, x + 110, y - 110, y + 110, z - 120, z + 220), box(x - 60, x + 60, y - 60, y + 60, z + 220, z + 320)))
        elif kind == "gauge":
            comps.append(merge(cyl((x, y, z), (x, y, z + 140), 8), cyl((x, y - 20, z + 220), (x, y + 30, z + 220), 70)))
        elif kind == "sw":
            comps.append(merge(cyl((x, y, z), (x, y, z + 140), 8), box(x - 60, x + 60, y - 50, y + 50, z + 140, z + 300)))
    R.add("GAS-02 Gas train A1–A11", merge(run, compound(*comps)), "gas", "valve", tag="GAS-02", title="Common gas train A1 → A11",
          spec="; ".join(f"{t} {d} ({m})" for t, k, d, m in items) + ". Gas enters at A1 (east); A6/A7 trip every BCU; A10 leak-proved before each start.",
          src="SH-PID-02 Rev M (Eclipse PO STL/2026/206) · D-18", status="C")
    hdr = pipe(g.gas_header, DN["65"])
    sleepers = [box(g.gas_hdr_x - 120, g.gas_hdr_x + 120, yy - 100, yy + 100, 0, 90) for yy in range(-6400, 6601, 1500)]
    sleepers += [box(xx - 100, xx + 100, y - 120, y + 120, 0, 90) for xx in (2400, 3200)]
    R.add("GAS-03 Gas header DN65", hdr, "gas", "gas", tag="GAS-03", title="Gas header NG-65-001 DN65",
          spec=f"DN65 sch 40 on sleepers at +0.140; {G.plen(g.gas_header) / 1000:.1f} m skid → tee", material="ASTM A106 Gr B, canary yellow (IS 2379)",
          src="SH-PID-02 Rev M · C-06", status="C")
    R.add("GAS-04 Gas mains DN50", merge(pipe(g.gas_main_N, DN["50"]), pipe(g.gas_main_S, DN["50"])), "gas", "gas", tag="GAS-04",
          title="Furnace gas mains NG-50 DN50 to both burner pits",
          spec=f"DN50 sch 40; north {G.plen(g.gas_main_N) / 1000:.1f} m, south {G.plen(g.gas_main_S) / 1000:.1f} m; drops into the pits to −0.940",
          src="SH-PID-02 Rev M · C-06", status="C")
    R.add("GAS-05 Pipe sleepers", compound(*sleepers), "gas", "concrete2", tag="GAS-05", title="Pipe sleepers", spec="RCC 240 × 200 × 90 @ 1.5 m", src="SH-PID-02", status="C")
    vent = pipe(g.gas_vent, DN["15"] * 1.6)
    R.add("GAS-06 Relief vent", merge(vent, cyl((g.gas_vent[1][0], y, 12500), (g.gas_vent[1][0], y, 12700), 45)), "gas", "gas", tag="GAS-06",
          title="A5 relief vent", spec="Rises continuously to a safe place; no valve, no low pocket; rain cap", src="SH-PID-02 Rev M", status="C")
    # burner trains B4 -> B2 -> B1 -> B3 along the face, 300 out, at -0.940
    yg = g.bZ - 550
    for i, (bx, s) in enumerate(((-g.bX, 1), (g.bX, -1)), start=1):
        yy = s * (g.cYo + 300)
        xin = -s * -153.5 if s > 0 else -153.5          # riser from the main
        xin = 153.5 if s > 0 else -153.5
        xr = bx + (-s) * -350 if False else bx + (350 if s > 0 else -350)   # riser up to the burner gas inlet side
        line = pipe([(xin, yy, yg), (xr, yy, yg), (xr, yy, g.bZ), (xr, s * (g.cYo + 300), g.bZ), (bx + (220 if s > 0 else -220), s * (g.cYo + 300), g.bZ)], DN["40"])
        comps = []
        seq = [("B4", "ball"), ("B2", "sol"), ("B1", "ratio"), ("B3", "cock")]
        for k, (t, kind) in enumerate(seq):
            x = xin + (xr - xin) * (k + 0.6) / (len(seq) + 0.4)
            if kind == "ball":
                comps.append(_valve_ball(x, yy, yg, 30))
            elif kind == "sol":
                comps.append(merge(box(x - 90, x + 90, yy - 80, yy + 80, yg - 90, yg + 160), box(x - 45, x + 45, yy - 45, yy + 45, yg + 160, yg + 240)))
            elif kind == "ratio":
                comps.append(merge(cyl((x, yy, yg + 30), (x, yy, yg + 120), 110), cyl((x, yy, yg - 60), (x, yy, yg + 30), 55)))
                imp = pipe([(x, yy, yg + 120), (x, yy, g.bZ + 330), (bx, yy, g.bZ + 330), (bx, s * (g.cYo + 617), g.bZ + 330)], 5, elbows=False)
                comps.append(imp)
            else:
                comps.append(box(x - 55, x + 55, yy - 55, yy + 55, yg - 55, yg + 55))
        ign = pipe([(xin, yy + s * 120, yg), (xin, yy + s * 120, g.bZ - 60), (bx + 90, yy + s * 120, g.bZ - 60), (bx + 90, s * (g.cYo + 800), g.bZ - 60)], DN["15"], elbows=False)
        R.add(f"GAS-1{i} Burner {i} gas train", merge(line, compound(*comps)), "gas", "valve", tag=f"GAS-1{i}",
              title=f"Burner {i} gas train on the face",
              spec="B4 ball valve 1½\" → B2 double solenoid VAS240R/NW DN40 → B1 air/gas ratio controller GIK40R02-5B (impulse line to the air plenum) → B3 flow-adjusting cock GEH40R50; DN15 ignition gas to the spark ignitor",
              src="SH-PID-02 Rev M · burner valve GA", status="C")
        R.add(f"GAS-2{i} Burner {i} ignition gas", ign, "gas", "gas", tag=f"GAS-2{i}", title=f"Burner {i} DN15 ignition gas line",
              spec="DN15 from the main ahead of B4 to the ignitor (no pilot burner)", src="SH-PID-02 Rev M", status="C")


def build_air(R):
    g = G
    hx, hy, zr = g.ring
    # blower plinth + frame + AVMs + scroll + motor + inlet filter silencer
    x0, x1, y0, y1 = 2800, 4000, -5800, -4400
    plinth = box(x0, x1, y0, y1, 0, 150)
    frame = merge(box(x0 + 50, x1 - 50, y0 + 50, y0 + 150, 230, 330), box(x0 + 50, x1 - 50, y1 - 150, y1 - 50, 230, 330),
                  box(x0 + 50, x0 + 150, y0 + 50, y1 - 50, 230, 330), box(x1 - 150, x1 - 50, y0 + 50, y1 - 50, 230, 330))
    avm = [cyl((x, yy, 150), (x, yy, 230), 50) for x in (x0 + 100, x1 - 100) for yy in (y0 + 100, y1 - 100)]
    cx, cy, cz = 3300, -5050, 800
    scroll = cyl((cx, cy - 175, cz), (cx, cy + 175, cz), 450)
    pedestal = box(cx - 300, cx + 300, cy - 200, cy + 200, 330, cz - 350)
    outlet = box(cx + 200, cx + 450, cy - 125, cy + 125, cz, cz + 520)
    motor = cyl((cx, cy + 260, cz), (cx, cy + 680, cz), 150)
    mstool = box(cx - 150, cx + 150, cy + 260, cy + 680, 330, cz - 150)
    filt = cyl((cx, cy - 175, cz), (cx, cy - 575, cz), 200)
    R.add("AIR-01 Blower plinth and frame", merge(plinth, compound(frame, *avm)), "air", "concrete2", tag="AIR-01", title="Combustion blower plinth, base frame and AVMs",
          spec="RCC plinth 1,200 × 1,400 × 150; ISMC 100 base frame on 4 anti-vibration mounts; M16 anchors", src="D-13", status="D")
    R.add("AIR-02 Combustion air blower", merge(scroll, pedestal, outlet), "air", "fan", tag="AIR-02", title="Combustion air blower Mittal MBI-4040",
          spec="1,400 m³/h at 725 mmWC, VFD with modulating air damper; 8\" discharge with flexible connector",
          src="SH-PID-02 Rev M", status="C", note="At λ 1.125 full fire needs ≈1,430 m³/h at 35 °C (C-01, O-04).")
    R.add("AIR-03 Blower motor", merge(motor, mstool), "air", "motor", tag="AIR-03", title="Combustion blower motor", spec="5.5 kW (derived, A-06), VFD", src="C-11", status="A")
    R.add("AIR-04 Inlet filter-silencer", filt, "air", "galv", tag="AIR-04", title="Inlet filter-silencer", spec="Ø400 × 400, washable filter + absorptive silencer", src="this design", status="D")
    # 8" discharge -> flexible -> venturi -> 300 x 150 header -> ring
    ox, oz = cx + 325, cz + 520
    flex = cyl((ox, cy, oz), (ox, cy, oz + 150), DN["200"] + 15)
    p8 = pipe([(ox, cy, oz + 150), (ox, cy, 1300), (2900, cy, 1300)], DN["200"])
    ven = merge(cyl((2900, cy, 1300), (2750, cy, 1300), DN["200"]), box(2750, 2550, cy - 75, cy + 75, 1225, 1375), cyl((2550, cy, 1300), (2400, cy, 1300), DN["200"]))
    hdr = duct([(2400, cy, 1300), (hx, cy, 1300), (hx, cy, zr)], 300, 150)
    R.add("AIR-05 8\" discharge and flexible", merge(flex, p8), "air", "airduct", tag="AIR-05", title="8\" discharge with flexible connector", spec="8\" ERW, flexible connector at the blower", src="SH-PID-02 Rev M", status="C")
    R.add("AIR-06 Combustion venturi", ven, "air", "steel2", tag="AIR-06", title="Combustion-air venturi", spec="8\" inlet → 150 × 150 throat (16 m/s); flow measurement", src="Rev H", status="C")
    R.add("AIR-07 Air header 300 × 150", hdr, "air", "airduct", tag="AIR-07", title="Air header 300 × 150", spec="Joins the ring on its east side", src="SH-PID-02 Rev M", status="C")
    ring = duct([(-hx, -hy, zr), (hx, -hy, zr), (hx, hy, zr), (-hx, hy, zr), (-hx, -hy, zr)], 150, 150)
    R.add("AIR-08 Air ring 150 × 150", ring, "air", "airduct", tag="AIR-08", title="Closed air ring 150 × 150",
          spec="750 clear of the casing at +0.500; supports from the pit walls and deck", src="SH-PID-02 Rev M", status="C")
    prov = merge(box(2500, 2620, cy + 160, cy + 260, 1240, 1360), cyl((2560, cy + 160, 1300), (2560, cy + 75, 1300), 10),
                 cyl((2700, cy + 75, 1450), (2700, cy + 20, 1450), 60), box(2650, 2750, cy + 90, cy + 150, 1300, 1400))
    R.add("AIR-09 Air proving", prov, "instr", "panel", tag="AIR-09", title="Air proving set",
          spec="D4 cock DH15R50 → D3 gauge KFM160RB100 + D1 air pressure switch DG 10U-3 to BCU terminal DL/7; must make before any gas valve opens",
          src="SH-PID-02 Rev M", status="C")
    for i, (bx, s) in enumerate(((-g.bX, 1), (g.bX, -1)), start=1):
        top = g.bZ + 330
        pts = [(bx, s * hy, zr - 75), (bx, s * hy, 60), (bx, s * (g.cYo + 617), 60), (bx, s * (g.cYo + 617), top)]
        br = pipe(pts, DN["100"])
        bfly = cyl((bx, s * hy - 70, 300), (bx, s * hy + 70, 300), DN["100"] + 25)
        hand = box(bx - 10, bx + 10, s * hy - 10, s * hy + 10, 300, 420).union(box(bx - 10, bx + 140, s * hy - 10, s * hy + 10, 410, 430))
        R.add(f"AIR-1{i} Burner {i} air branch", merge(br, bfly, hand), "air", "air", tag=f"AIR-1{i}", title=f"Burner {i} 4\" air branch with butterfly D2",
              spec="4\" ERW from the ring into the pit to the burner air plenum; manual butterfly D2 for balancing", src="SH-PID-02 Rev M · C-05", status="C")


def build_pits(R):
    g = G
    hx = g.pitX
    # pit fans (D-09)
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
        # handrails on the three open sides of the pit
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
        lx, wall = 1150, s * g.bpitY1
        lad = [box(lx - 220, lx - 200, wall - s * 170, wall - s * 150, g.bpit_floor, 1000), box(lx + 200, lx + 220, wall - s * 170, wall - s * 150, g.bpit_floor, 1000)]
        for zz in range(int(g.bpit_floor) + 250, 900, 280):
            lad.append(cyl((lx - 200, wall - s * 160, zz), (lx + 200, wall - s * 160, zz), 10))
        R.add(f"PIT-{key[-1]}2 Cat ladder", compound(*lad), "pitvent", "galv", tag=f"PIT-{key[-1]}2", title=f"Cat ladder ({'north' if s > 0 else 'south'} pit)",
              spec="GI stringers 50 × 20, Ø20 rungs @ 280", src="HDG", status="C")
        bcu = merge(box(450, 850, wall - s * 120, wall, -950, -400), box(950, 1250, wall - s * 110, wall, -1150, -950))
        R.add(f"BMS-{key[-1]} Burner control", bcu, "instr", "panel", tag=f"BMS-{key[-1]}",
              title=f"Burner control unit + ignition transformer ({'burner 1' if s > 0 else 'burner 2'})",
              spec="Kromschröder BCU 370 (air proof → purge → spark → UV proof → main; lockout on fault) + TZI8-12/100WE, on the pit end wall",
              src="SH-PID-02 Rev M", status="C")


def build(R):
    build_gas(R)
    build_air(R)
    build_pits(R)
