"""Flue duct, heat-recovery loop (trenches, mixing box, recirculation blower), 4-position dryer, bleed & stack,
zinc enclosure (optional), sample loads, scale figures."""
from __future__ import annotations

import math

from ..basis import B, G
from .lib import box, compound, cyl, duct, frame, ibeam, merge, pipe, quarter_ring, sph, tube

FLOWCOL = {"HRL-02a": "retn", "HRL-02b": "retn", "HRL-03": "suct", "HRL-04": "suct", "HRL-08a": "supp", "HRL-08b": "supp"}
FLOWNAME = {"HRL-02a": "Return trench 900 × 1,000 (from the dryer)", "HRL-02b": "Return trench 900 × 1,000 (to the junction)",
            "HRL-03": "Three-way junction 1,000 × 1,000 (return + flue → suction)", "HRL-04": "Suction trench 1,000 × 1,000",
            "HRL-08a": "Discharge trench 1,100 × 1,000 (under the blower)", "HRL-08b": "Discharge trench 1,100 × 1,000 (to the supply box)"}
FLOWSPEC = {"HRL-02a": "28,614 Nm³/h at 100 °C = 10.86 m³/s, 12.1 m/s", "HRL-02b": "28,614 Nm³/h at 100 °C, 12.1 m/s",
            "HRL-03": "10.86 + 1.41 = 12.27 m³/s, radiused merge", "HRL-04": "12.27 m³/s at ≈124–130 °C, 12.3 m/s",
            "HRL-08a": "48,000 m³/h at 120 °C = 13.33 m³/s, 12.1 m/s", "HRL-08b": "dryer flow 11.44 m³/s at 120 °C after the bleed"}


def build_flue(R):
    g = G
    x0, x1, yc, zc = -2150, -g.cXo, g.flueY, -450
    W, H = 700, 400
    t_l, t_s = 150, 6
    outer = box(x0, x1, yc - W / 2 - t_l - t_s, yc + W / 2 + t_l + t_s, zc - H / 2 - t_l - t_s, zc + H / 2 + t_l + t_s)
    shell = outer.cut(box(x0 - 1, x1 + 1, yc - W / 2 - t_l, yc + W / 2 + t_l, zc - H / 2 - t_l, zc + H / 2 + t_l))
    lining = box(x0, x1, yc - W / 2 - t_l, yc + W / 2 + t_l, zc - H / 2 - t_l, zc + H / 2 + t_l).cut(box(x0 - 1, x1 + 1, yc - W / 2, yc + W / 2, zc - H / 2, zc + H / 2))
    flange = frame(x1 - 20, x1, yc - 560, yc + 560, x1 - 21, x1 + 1, yc - 506, yc + 506, zc - 410, zc + 410)
    flange = box(x1 - 20, x1, yc - 560, yc + 560, zc - 410, zc + 410).cut(box(x1 - 21, x1 + 1, yc - 350, yc + 350, zc - 150, zc + 150))
    stools = compound(*[box(x - 60, x + 60, yc - 450, yc + 450, -1000, zc - H / 2 - t_l - t_s) for x in (-2000, -1650)])
    R.add("FLU-01 Lined flue duct", merge(shell, flange), "flue", "fluesteel", tag="FLU-01", title="Lined flue duct (D-10)",
          spec="700 × 400 clear (0.28 m², ≈5.4 m/s at 800 °C), 6 mm steel, casing flange over the 1,000 × 600 cut-out; on stools in a vented RCC trench",
          src="D-10 (replaces the Rev H refractory-lined trench)", status="D", note="Skin ≈81 °C, trench RCC ≈64 °C with 45 °C trench air (C-04).")
    R.add("FLU-02 Flue duct lining", lining, "flue", "module", tag="FLU-02", title="Flue duct lining", spec="100 mm folded module 128 kg/m³ + 50 mm microporous", src="D-10 · C-04", status="D")
    R.add("FLU-03 Duct stools", stools, "flue", "steel2", tag="FLU-03", title="Flue duct support stools", spec="Fabricated, sliding plates (expansion)", src="D-10", status="D")
    R.add("FLOW-flue Flue gas", box(x0, -g.lfX, yc - W / 2, yc + W / 2, zc - H / 2, zc + H / 2), "flue", "flue", tag="FLOW", title="Flue gas 800 °C",
          spec="1,386 Nm³/h at design λ (Rev H 1,296), 1.54 m³/s", src="C-01 · C-07", status="C", alpha=0.45, layer="flow")


def build_trenches(R):
    g = G
    clears = dict(g.trenches)
    clears["FLUE"] = g.flue_trench
    mb = g.mb
    clears["MBPIT"] = (mb[0], mb[1], mb[2], mb[3])
    outer, inner = None, None
    for k, (x0, x1, y0, y1) in clears.items():
        t = 250 if k == "MBPIT" else 200
        zf = -1100 if k == "MBPIT" else -1000
        o = box(x0 - t, x1 + t, y0 - t, y1 + t, zf - t, 0)
        i = box(x0 - 1, x1 + 1, y0 - 1, y1 + 1, zf, 10)
        outer = o if outer is None else outer.union(o)
        inner = i if inner is None else inner.union(i)
    rcc = outer.cut(inner)
    rcc = rcc.cut(box(-g.pitX - 210, -g.pitX - 190, g.flueY - 630, g.flueY + 630, -1000, 0))   # open into the furnace pit wall sleeve
    R.add("CIV-10 Loop trenches and mixing-box pit", rcc, "civil", "concrete2", tag="CIV-10", title="Heat-recovery trenches and mixing-box pit (RCC)",
          spec="RCC 200 walls and floor, waterproofed; clear depth 1,000 (Hold H1); mixing-box pit 1,500 × 1,300, floor −1.100, 250 walls, excavation −1.350",
          src="Rev H · SH-MB-01 Rev A · HDG", status="O", note="Hold H1: R-02 foundation drawings show −1,400 / −1,000 (O-01).")
    covers = []
    for k, (x0, x1, y0, y1) in g.trenches.items():
        c = box(x0 - 100, x1 + 100, y0 - 100, y1 + 100, -8, 0)
        if k == "HRL-08a":
            c = c.cut(cyl((g.bleed[0], g.bleed[1], -20), (g.bleed[0], g.bleed[1], 20), 210))
            c = c.cut(box(g.rb_axis[0], g.rb_axis[0] + 675, g.rb_axis[2] - 950, g.rb_axis[2] - 50, -20, 20))
        for x in range(int(x0), int(x1), 1000):
            c = c.cut(box(x - 2, x + 2, y0 - 101, y1 + 101, -9, 1)) if (x1 - x0) > (y1 - y0) else c
        covers.append(c)
    R.add("CIV-11 Trench cover plates", compound(*covers), "civil", "deck", tag="CIV-11", title="Trench cover plates",
          spec="8 mm chequered plate in 1 m removable sections on embedded angles", src="Rev H · HDG", status="C")
    fx0, fx1, fy0, fy1 = g.flue_trench
    R.add("CIV-12 Flue trench grating", box(fx0 - 100, fx1, fy0 - 100, fy1 + 100, -40, 0), "civil", "grating", tag="CIV-12", title="Flue trench vented grating",
          spec="Grating so the trench breathes (D-10); the duct inside is lined", src="D-10", status="D")
    for k, (x0, x1, y0, y1) in g.trenches.items():
        R.add(f"FLOW-{k} {FLOWNAME[k]}", box(x0 + 20, x1 - 20, y0 + 20, y1 - 20, -980, -20), "loop", FLOWCOL[k], tag=k, title=FLOWNAME[k],
              spec=FLOWSPEC[k], src="Rev H heat-recovery loop · C-08 · C-09", status="C", alpha=0.35, layer="flow")


def build_mixing_box(R):
    g = G
    x0, x1, y0, y1, zf, zr = g.mb
    t = 6
    steel = box(x0 - t, x1 + t, y0 - t, y1 + t, 0, zr + t).cut(box(x0, x1, y0, y1, -1, zr))
    steel = steel.cut(cyl((x0 - 10, (y0 + y1) / 2, 900), (x0 + 10, (y0 + y1) / 2, 900), 557))
    bands = [frame(x0 - t - 60, x1 + t + 60, y0 - t - 60, y1 + t + 60, x0 - t, x1 + t, y0 - t, y1 + t, z, z + 60) for z in (200, 700, 1200)]
    ring = tube((x0 - 60, (y0 + y1) / 2, 900), (x0 - t, (y0 + y1) / 2, 900), 640, 557)
    R.add("HRL-05 Mixing box S2", merge(steel, compound(*bands), ring), "loop", "steel2", tag="HRL-05", title="Mixing box, configuration S2",
          spec="1,500 × 1,300 × 2,700 internal (1,100 pit + 1,600 steel); floor −1.100, roof +1.600; 5.27 m³; rise 6.84 m/s, 0.40 s; blower cut-out Ø1,114 at +0.900 (west face)",
          src="SH-MB-01 Rev A", status="C", note="Blower cut-out face differs between Rev N and SH-MB-01 (O-09); the model follows SH-MB-01.")
    yc = (y0 + y1) / 2
    vane = quarter_ring(0, 0, 694, 700, x0, x1, (-1, -1))   # built about origin then placed
    vane = cyl((x0, y0 + 700, zf + 700), (x1, y0 + 700, zf + 700), 700).cut(cyl((x0 - 1, y0 + 700, zf + 700), (x1 + 1, y0 + 700, zf + 700), 694))
    vane = vane.intersect(box(x0, x1, y0, y0 + 700, zf, zf + 700))
    R.add("HRL-05a Turning deflector R700", vane, "loop", "galv", tag="HRL-05a", title="Turning deflector R700",
          spec="6 mm plate; cuts the turn loss from K 1.2 to 0.40 (9.2 mmWC)", src="SH-MB-01 Rev A", status="C")
    # fresh-air damper on the far (south) face, sleeve 500 at 30 deg down, damper at the outer end
    sx, sz = (x0 + x1) / 2, 700
    sleeve = box(sx - 175, sx + 175, y0 - 500, y0, sz - 175, sz + 175).rotate((sx, y0, sz), (sx + 1, y0, sz), -30)
    ang = math.radians(30)
    ex, ey, ez = sx, y0 - 500 * math.cos(ang), sz - 500 * math.sin(ang)
    damper = box(ex - 200, ex + 200, ey - 150, ey, ez - 200, ez + 200).rotate((ex, ey, ez), (ex + 1, ey, ez), -30)
    act = box(ex + 200, ex + 330, ey - 120, ey - 20, ez - 60, ez + 60)
    cowl = box(ex - 260, ex + 260, ey - 420, ey - 150, ez + 150, ez + 230).rotate((ex, ey, ez), (ex + 1, ey, ez), -30)
    R.add("HRL-06 Fresh-air make-up damper", merge(sleeve, damper, cowl), "loop", "galv", tag="HRL-06", title="Fresh-air make-up damper STL-MB-DMP-02",
          spec="350 × 350 opposed blade, GI, SS304 spindles, 1.6 mm blades with 10 mm hem; sleeve 500 at 30° below horizontal; cowl + bird mesh; min stop ≈15 % open; 3,433 Nm³/h",
          src="STL-MB-DMP-02 Rev A · Rev H", status="C")
    R.add("HRL-06a Damper actuator", act, "instr", "panel", tag="HRL-06a", title="Belimo LM230A-S actuator", spec="5 N·m on/off, PLC DO → relay", src="STL-MB-DMP-02 Rev A", status="C")
    R.add("FLOW-mix Mixing zone", box(x0 + 30, x1 - 30, y0 + 30, y1 - 30, zf + 30, zr - 30), "loop", "suct", tag="FLOW", title="Mixed gas ≈124 °C",
          spec="flue + return + fresh air (C-08 adiabatic mix 124 °C)", src="C-08", status="C", alpha=0.3, layer="flow")


def build_blower(R):
    g = G
    sx0, sx1, yc, zc = g.rb_axis
    r = g.rb_r
    x0 = g.mb[0]
    # pedestals both sides of the discharge trench + base frame
    ped = compound(box(-7100, -4250, -7350, -6950, 0, 300), box(-7100, -4250, -9150, -8850, 0, 300))
    frm = compound(*[box(x - 50, x + 50, -9150, -6950, 300, 500) for x in (-7000, -6100, -5250, -4350)],
                   box(-7100, -4250, -7450, -7350, 300, 500), box(-7100, -4250, -8850, -8750, 300, 500))
    R.add("HRL-07a Blower pedestals", ped, "civil", "concrete2", tag="HRL-07a", title="Recirculation blower pedestals", spec="RCC, either side of the discharge trench", src="D-19", status="D")
    R.add("HRL-07b Blower base frame", frm, "loop", "steel", tag="HRL-07b", title="Blower base frame", spec="ISMC 200 grid bridging the discharge trench; outlet drops between the beams", src="D-19", status="D")
    scroll = cyl((sx0, yc, zc), (sx1, yc, zc), r)
    outlet = box(sx0, sx0 + 675, yc - 950, yc - 50, 0, zc - r + 40)
    saddles = compound(box(sx0 + 50, sx1 - 50, yc - 500, yc - 400, 500, zc - r + 60), box(sx0 + 50, sx1 - 50, yc + 400, yc + 500, 500, zc - r + 60))
    R.add("HRL-07 Recirculation blower", merge(scroll, outlet, saddles), "loop", "fan", tag="HRL-07", title="Recirculation blower AEP-ZA-9.0",
          spec="48,000 m³/h at 120 °C, 72 mmWC, 30 HP; Ø900 inlet, 900 × 675 outlet down into the 1,100 × 1,000 trench; casing and bearings limit 120 °C",
          src="Rev H · HDG", status="C", note="Confirm whether 72 mmWC is a 20 °C or 120 °C rating (O-07); loop needs ≈74 mmWC hot (C-09).")
    # offset inlet spool: cut-out Ø1114 at +0.900 -> fan inlet at +1.170, cruciform straightener in the straight part
    p = [(x0, (g.mb[2] + g.mb[3]) / 2, 900), (x0 - 150, yc, 900), (x0 - 450, yc, zc), (sx1 + 100, yc, zc)]
    spool = pipe(p, 450)
    flex = cyl((sx1 + 100, yc, zc), (sx1, yc, zc), 480)
    cross = compound(box(sx1 + 110, x0 - 460, yc - 440, yc + 440, zc - 2, zc + 2), box(sx1 + 110, x0 - 460, yc - 2, yc + 2, zc - 440, zc + 440))
    R.add("HRL-07c Inlet spool Ø900", merge(spool), "loop", "galv", tag="HRL-07c", title="Inlet spool Ø900 (offset)",
          spec="From the Ø1,114 cut-out at +0.900 to the fan eye at +1.170, cruciform straightener 2 × 4 mm ≈560 long (mandatory)", src="SH-MB-01 Rev A · D-19", status="D")
    R.add("HRL-07d Inlet flexible connector", flex, "loop", "rubber", tag="HRL-07d", title="Inlet flexible connector", spec="High-temperature fabric, 150 °C", src="this design", status="D")
    R.add("HRL-07e Cruciform straightener", cross, "loop", "steel2", tag="HRL-07e", title="Cruciform straightener", spec="2 × 4 mm plates ≈560 long; kills the swirl from two bends (≈11° and ≈8°)", src="SH-MB-01 Rev A", status="C")
    shaft = cyl((sx0, yc, zc), (-6100, yc, zc), 50)
    pb = compound(*[box(x - 120, x + 120, yc - 180, yc + 180, 500, zc - 60) for x in (-5450, -5850)])
    guard = box(-6250, -6000, yc - 180, yc + 180, 450, zc + 250)
    motor = cyl((-7050, yc, 760), (-6300, yc, 760), 260)
    mbase = box(-7050, -6300, yc - 260, yc + 260, 500, 520)
    R.add("HRL-07f Fan shaft and bearings", merge(shaft, pb), "loop", "gear", tag="HRL-07f", title="Fan shaft and plummer blocks", spec="Shaft Ø100, 2 × plummer blocks", src="HDG", status="C")
    R.add("HRL-07g Belt guard", guard, "loop", "yellow", tag="HRL-07g", title="Belt guard", spec="Expanded mesh, yellow", src="HDG", status="C")
    R.add("HRL-07h Blower motor 30 HP", merge(motor, mbase), "loop", "motor", tag="HRL-07h", title="Recirculation blower motor 30 HP (22 kW), VFD",
          spec="Cold start ≈16 kW shaft (C-11)", src="Rev H · C-11", status="C")


def build_dryer(R):
    g = G
    X0, X1, Y = g.dX0, g.dX1, g.dY
    li, wl = g.d_lin, g.d_wall
    zf = g.d_floor
    rx0, rx1, ry = X0 - li, X1 + li, Y + li                  # RCC inner
    ox0, ox1, oy = rx0 - wl, rx1 + wl, ry + wl              # RCC outer
    rcc = box(ox0, ox1, -oy, oy, zf - li - 250, 0).cut(box(rx0, rx1, -ry, ry, zf - li, 1))
    for xa, xb, w in ((ox0 - 1, X0 + 1, 500), (X1 - 1, ox1 + 1, 450)):
        rcc = rcc.cut(box(xa, xb, -w, w, -1000, -300))
    rcc = rcc.cut(cyl((-5000, ry - 10, -500), (-5000, oy + 10, -500), 70))
    R.add("CIV-20 Dryer pit", rcc, "civil", "rccpit", tag="CIV-20", title="Dryer pit (RCC)",
          spec=f"RCC 250 walls, 250 slab; inside RCC {rx1 - rx0:.0f} × {2 * ry:.0f}, clear chamber 6,000 × 7,500 × 1,400 after the 100 mm lining",
          src="Rev H · HDG · D-11 · D-14", status="D")
    pocket = box(-5600, -4400, oy, oy + 1000, -1200, 0).cut(box(-5400, -4600, oy - 1, oy + 800, -1000, 1))
    R.add("CIV-21 Chain-drive pocket", pocket, "civil", "rccpit", tag="CIV-21", title="Chain-drive pocket", spec="800 × 800 × 1,000 clear, chequered lid; the 5.5 kW gearmotor stays out of the hot air",
          src="this design", status="D")
    lin = box(rx0, rx1, -ry, ry, zf - li, 0).cut(box(X0, X1, -Y, Y, zf, 1))
    for xa, xb, w in ((rx0 - 1, X0 + 1, 500), (X1 - 1, rx1 + 1, 450)):
        lin = lin.cut(box(xa, xb, -w, w, -1000, -300))
    R.add("DRY-10 Pit lining", lin, "dryer", "alu", tag="DRY-10", title="Dryer pit lining",
          spec="100 mm ceramic-fibre board + 1 mm aluminium liner; RCC face ≈62 °C (C-04)", src="D-14", status="D")
    deck = box(ox0, ox1, -oy, oy, 0, 250).cut(box(-10350, -9150, -Y, Y, -1, 251)).cut(box(-5850, -4650, -Y, Y, -1, 251))
    R.add("DRY-11 Top deck and fixed cover", deck, "dryer", "insul", tag="DRY-11", title="Insulated top deck with fixed cover over P2–P3",
          spec="250 mm insulated steel-framed deck; openings P1 (X −10.35…−9.15) and P4 (X −5.85…−4.65), 1,200 × 7,500", src="D-16 · HDG", status="D")
    rails = compound(*[box(rx0, rx1, s * 3950 - 25, s * 3950 + 25, 250, 270) for s in (1, -1)])
    R.add("DRY-12 Door rails", rails, "dryer", "steel", tag="DRY-12", title="Door rails", spec="Flat bar 50 × 20 on the deck", src="SH-RBR-01/02", status="C")
    for key, xa, d, label in (("DRY-02", -10450, 1, "P1, entry; slides east"), ("DRY-03", -5950, -1, "P4, exit; slides west")):
        door = box(xa, xa + 1400, -3800, 3800, 300, 550)
        wheels = [cyl((xa + dx, s * 3950 - 40, 300), (xa + dx, s * 3950 + 40, 300), 90) for dx in (150, 1250) for s in (1, -1)]
        rack = box(xa - 40, xa + 1460, 4150, 4200, 270, 300)
        brk = box(xa - 40, xa + 1460, 3800, 4200, 420, 440)
        px = xa + (1420 if d > 0 else 0)
        drv = merge(box(px - 220, px + 220, 4230, 4710, 0, 100), box(px - 130, px + 130, 4250, 4530, 100, 360),
                    cyl((px, 4175, 348), (px, 4230, 348), 54), cyl((px + 130 * d, 4390, 340), (px + 590 * d, 4390, 340), 90))
        R.add(f"{key} Dryer door {label.split(',')[0]}", merge(door, compound(*wheels)), "dryer", "alu", tag=key, title=f"Dryer door {label}",
              spec="1,400 × 7,600 × 250 insulated, aluminium skinned; travel 1,450; interlocked with the chain (no index with a door open)",
              src="SH-RBR-01/02 · HDG", status="C")
        R.add(f"{key}r Door rack and drive", merge(rack, brk, drv), "dryer", "gear", tag=f"{key}r", title=f"Door rack & pinion drive ({label.split(',')[0]})",
              spec="Rack m6 1,500 × 60 × 60 EN8 (45–50 HRC); pinion m6 16T PCD 96 EN19; BK50 bevel 1.1 kW 4-pole 75.4:1, 19 rpm, 550 N·m; 2 eccentric backing rollers; Omron D4A-4516N-F limits",
              src="SH-RBR-01/02", status="C")
    # perforated boxes (D-12)
    for key, xa, xb, face_x, col, label, spec in (
            ("DRY-04", X0, X0 + 350, X0 + 350, "supp", "Perforated supply box", "centre fed through 1,000 × 700 from the discharge trench; feed 12.6 m/s, hole ΔP / feed VP = 2.05 (C-09)"),
            ("DRY-05", X1 - 350, X1, X1 - 350, "retn", "Perforated extraction box", "centre drawn into the 900 × 1,000 return trench")):
        bx = box(xa, xb, -3500, 3500, -1350, -50)
        R.add(f"{key} {label}", bx, "dryer", "galv", tag=key, title=label,
              spec="1,300 × 350 × 7,000; face 7,000 × 1,000 perforated Ø15 @ 37 staggered 60° (14.9 % open, ≈5,900 holes); " + spec,
              material="GI 2 mm, CNC turret punched, 4 sections of 1,750", src="D-12 · Rev H", status="D")
        R.add(f"{key}p {label} face", box(face_x - (2 if xa == X0 else -2), face_x + (2 if xa == X0 else -2) * 0 + (0 if xa == X0 else 0), -3500, 3500, -1200, -200).union(
            box(face_x - 3, face_x + 3, -3500, 3500, -1200, -200)), "dryer", col, tag=f"{key}p", title=f"{label}: perforated face",
            spec="Ø15 holes, 37 mm staggered pitch, 7,000 × 1,000", src="D-12", status="D", layer="perf")
    trs = merge(box(X0 - li - wl, X0, -500, 500, -1000, -300), box(X1, X1 + li + wl, -450, 450, -1000, -300))
    R.add("DRY-06 Wall transitions", trs, "dryer", "galv", tag="DRY-06", title="Supply and return transitions through the pit walls",
          spec="Supply 1,000 × 700; return 900 × 700; GI with flexible seal", src="D-12", status="D")
    # chain conveyor
    xh, xt, zc, R_s = -5000, -10000, -500, 150
    shafts = compound(cyl((xt, -3700, zc), (xt, 3700, zc), 35), cyl((xh, -3700, zc), (xh, 4700, zc), 35))
    spro, chain, rails2 = [], [], []
    for y in (-3550, 3550):
        for x in (xt, xh):
            d = cyl((x, y - 15, zc), (x, y + 15, zc), 172)
            spro.append(d)
        chain.append(box(xt, xh, y - 15, y + 15, zc + R_s - 12, zc + R_s + 12))
        chain.append(box(xt, xh, y - 15, y + 15, zc - R_s - 12, zc - R_s + 12))
        for x in (xt, xh):
            chain.append(cyl((x, y - 15, zc), (x, y + 15, zc), R_s + 12).cut(cyl((x, y - 16, zc), (x, y + 16, zc), R_s - 12)).intersect(
                box(x if x == xh else x - 200, x + 200 if x == xh else x, y - 20, y + 20, zc - 200, zc + 200)))
        rails2.append(box(xt + 150, xh - 150, y - 45, y + 45, zc + R_s - 57, zc + R_s - 12))
        rails2.append(box(xt + 150, xh - 150, y - 45, y + 45, zc - R_s - 57, zc - R_s - 12))
        for x in range(int(xt) + 400, int(xh), 1200):
            rails2.append(box(x - 30, x + 30, y - 30, y + 30, zf, zc - R_s - 57))
    R.add("DRY-07 Chain conveyor", compound(*chain), "dryer", "chain", tag="DRY-07", title="Two-strand chain conveyor",
          spec="Roller chain, 2 strands at Y ±3,550, head/tail at X −5.0 / −10.0 m; indexes one position (1,500) per pulse; hard stop at P4",
          src="HDG · dryer instrumentation notes", status="C")
    R.add("DRY-08 Sprockets and shafts", merge(compound(*spro), shafts), "dryer", "gear", tag="DRY-08", title="Sprockets 12T PCD 300 and shafts",
          spec="12T PCD 300 keyed; shafts Ø70; head shaft runs through the north wall to the drive pocket", src="HDG", status="C")
    R.add("DRY-09 Chain guides", compound(*rails2), "dryer", "steel", tag="DRY-09", title="Chain guide rails and return shoes", spec="UHMW wear strip on angle; posts @ 1,200", src="HDG", status="C")
    sad = compound(*[box(x - 140, x + 140, y - 70, y + 70, zc + R_s + 12, zc + R_s + 152) for x in g.dP for y in (-3550, 3550)])
    R.add("DRY-13 Saddles", sad, "dryer", "steel", tag="DRY-13", title="Chain saddles (jig ends ride on them)", spec="4 pairs at P1–P4, 1,500 pitch", src="HDG", status="C")
    gm = merge(box(-5300, -4700, 4200, 4750, -1000, -900), box(-5200, -4800, 4350, 4650, -900, -520), cyl((-5000, 4200, -500), (-5000, 4350, -500), 160))
    R.add("DRY-14 Chain drive", gm, "dryer", "motor", tag="DRY-14", title="Chain drive 5.5 kW geared motor",
          spec="5.5 kW, timed pulses from the PLC, one position per index; VFD or torque limiter open (O-14)", src="Dryer instrumentation notes", status="C")
    tw = merge(cyl((-7500, 3000, 250), (-7500, 3000, -750), 10), box(-7560, -7440, 2940, 3060, 250, 340))
    btn = merge(box(ox0 - 300, ox0 - 150, -oy - 300, -oy - 150, 0, 1200), box(ox0 - 290, ox0 - 160, -oy - 310, -oy - 290, 1000, 1100))
    arm = box(ox1 - 150, ox1 + 50, oy - 450, oy - 250, 250, 500)
    R.add("DRY-15 Dryer Pt100", tw, "instr", "galv", tag="DRY-15", title="Dryer temperature Pt100", spec="Duplex Pt100 Class A, Ø8 SS316, 1,000 insertion, through the fixed cover", src="Dryer instrumentation notes", status="C")
    R.add("DRY-16 P1 LOADED station and P4 trip arm", merge(btn, arm), "instr", "yellow", tag="DRY-16", title="P1 LOADED pushbutton + P4 trip-arm limit switch",
          spec="Switches stay in ambient air; P4 detector is a steel trip arm through the insulated wall", src="Dryer instrumentation notes", status="C")
    R.add("FLOW-dryer Dryer air", box(X0 + 350, X1 - 350, -3500, 3500, -1250, -150), "dryer", "supp", tag="FLOW", title="Drying air 120 → 100 °C",
          spec="11.44 m³/s cross-flow ≈1.6 m/s through all four loads; ≈209 kW (C-08)", src="Rev H · C-08", status="C", alpha=0.18, layer="flow")


def build_stack(R):
    g = G
    bx, by = g.bleed
    sx, sy = g.stack
    riser = pipe([(bx, by, -500), (bx, by, 4000), (bx, sy + 300, 4000), (sx, sy + 200, 4000)], 203)
    bd = merge(cyl((bx, by, 1940), (bx, by, 2060), 245), box(bx + 245, bx + 400, by - 40, by + 40, 1950, 2050))
    R.add("HRL-09 Bleed duct Ø400", riser, "stack", "bleed", tag="HRL-09", title="Bleed duct Ø400",
          spec="4,729 Nm³/h = flue + fresh air (C-08), 15 m/s; open to the stack by geometry, never by a control action", src="Rev H · HDG", status="C")
    R.add("HRL-09a Balancing damper BD-1", bd, "stack", "red", tag="HRL-09a", title="Balancing damper BD-1", spec="Ø400 butterfly, 6 mm disc, locking quadrant, 120 °C", src="Rev H · BD-1/BD-2 notes", status="C")
    hx = merge(box(bx - 550, bx + 550, -11800, -10600, 3450, 4550), cyl((bx + 550, -11000, 3700), (bx + 800, -11000, 3700), 45), cyl((bx + 550, -11400, 4300), (bx + 800, -11400, 4300), 45))
    R.add("HRL-10 Flue-gas heat exchanger", hx, "stack", "steel2", tag="HRL-10", title="Flue-gas heat exchanger (hot water to flux and degreasing tanks)",
          spec="≈150 kW available in the bleed (C-08); closed hot-water loop with 3-way valve; optional in this scope", src="Rev H · SHIVAS flux tank heating", status="C")
    posts = compound(*[merge(box(bx - 700, bx - 600, y - 50, y + 50, 0, 3790), box(bx + 600, bx + 700, y - 50, y + 50, 0, 3790), box(bx - 700, bx + 700, y - 60, y + 60, 3690, 3790)) for y in (-9600, -13300)])
    R.add("HRL-11 Bleed duct supports", posts, "stack", "steel", tag="HRL-11", title="Goal-post supports for the bleed duct", spec="ISMB 100, at 3.7 m", src="this design", status="D")
    st = tube((sx, sy, 350), (sx, sy, 12000), 206, 200)
    base = merge(box(sx - 600, sx + 600, sy - 600, sy + 600, -500, 350), cyl((sx, sy, 350), (sx, sy, 370), 360))
    gus = compound(*[box(sx + 200 * math.cos(a) - 6 if abs(math.cos(a)) < .5 else sx + 200 * math.cos(a), sx + 350 * math.cos(a) + 6, sy - 6, sy + 6, 370, 620).rotate((sx, sy, 0), (sx, sy, 1), math.degrees(a)) for a in [k * math.pi / 4 for k in range(8)]])
    port = cyl((sx, sy + 200, 8000), (sx, sy + 350, 8000), 50)
    plat = merge(tube((sx, sy, 7700), (sx, sy, 7740), 1000, 210), *[cyl((sx + 1000 * math.cos(a), sy + 1000 * math.sin(a), 7740), (sx + 1000 * math.cos(a), sy + 1000 * math.sin(a), 8800), 20) for a in [k * math.pi / 4 for k in range(8)]],
                 tube((sx, sy, 8780), (sx, sy, 8810), 1010, 990))
    lad = compound(*[box(sx - 220 + d, sx - 200 + d, sy - 450, sy - 430, 370, 7700) for d in (0, 400)], *[cyl((sx - 200, sy - 440, z), (sx + 180, sy - 440, z), 10) for z in range(650, 7700, 300)])
    rod = cyl((sx, sy, 12000), (sx, sy, 13500), 10)
    R.add("STK-01 Stack Ø400 × 12 m", merge(st, rod), "stack", "bleed", tag="STK-01", title="Bleed stack Ø400 × 12 m",
          spec="6 mm MS, top +12.0; exit 15 m/s; draft ≈3 mmWC; lightning conductor; height to be confirmed against the SPCB consent (O-05)",
          src="HDG (single line) · Rev H (two lines → Ø600) · C-13", status="C")
    R.add("STK-02 Stack base", merge(base, gus), "stack", "concrete2", tag="STK-02", title="Stack foundation and base plate", spec="RCC 1,200 sq.; base plate Ø720 × 20 with 8 gussets", src="this design", status="D")
    R.add("STK-03 Sampling port and platform", merge(port, plat, lad), "stack", "galv", tag="STK-03", title="Sampling port, platform and ladder",
          spec="Ø100 port at +8.0 m; ring platform at +7.7 m with handrail; ladder", src="this design (CPCB practice)", status="D")
    R.add("FLOW-bleed Bleed gas", cyl((bx, by, -480), (bx, by, 3900), 150), "stack", "bleed", tag="FLOW", title="Bleed 120 °C", spec="4,729 Nm³/h", src="C-08", status="C", alpha=0.35, layer="flow")


def build_enclosure(R):
    g = G
    x0, x1, y0, y1 = -g.cXo, g.cXo, -g.cYo, g.cYo
    yb, yt = g.deck, g.deck + 4720
    posts = [box(x - 60, x + 60, y - 60, y + 60, yb, yt) for x in (x0, x1) for y in [y0 + k * (y1 - y0) / 4 for k in range(5)]]
    tops = [box(x - 70, x + 70, y0, y1, yt - 120, yt) for x in (x0, x1)] + [box(x0, x1, y - 70, y + 70, yt - 120, yt) for y in (y0, y1)]
    sides = []
    for x in (x0, x1):
        s = box(x - 25, x + 25, y0, y1, 2400, yt - 120)
        for i in range(4):
            yy = y0 + 900 + i * 2130
            s = s.cut(box(x - 30, x + 30, yy, yy + 600, 3000, 3600))
        sides.append(s)
    ends = [box(x0, x1, y - 25, y + 25, yb, yt - 120) for y in (y0, y1)]
    roof = [box(g.kWo / 2 * 0 + x0 + 100 if s < 0 else 100, -100 if s < 0 else x1 - 100, y0, y1, yt + 80, yt + 220) for s in (-1, 1)]
    R.add("ZEN-01 Zinc enclosure", compound(*posts, *tops, *sides, *ends, *roof), "enclosure", "steel2", tag="ZEN-01", title="Zinc fume enclosure over the kettle",
          spec="8.2 × 2.75 × 4.72 m on the casing deck; 2 sliding roof covers (0.5 HP, VFD); skimming doors both sides on chain hoists; 4 × 600 × 600 windows per side; lateral suction to the ZFE",
          src="SHIVAS zinc fume enclosure annexure · HDG", status="C", hidden=True)


def build_loads(R):
    g = G
    jigs = []
    for x in g.dP:
        zb = -350 + 150 + 12 + 152 - 12          # on the saddles
        zb = -500 + 150 + 12 + 140
        beam = box(x - 50, x + 50, -3700, 3700, zb, zb + 200)
        lugs = [box(x - 15, x + 15, y - 60, y + 60, zb + 200, zb + 320) for y in (-1600, 1600)]
        work = [box(x - 35, x + 35, y - 35, y + 35, zb - 1050, zb) for y in (-3000, -1000, 1000, 3000)]
        work += [box(x - 100, x + 100, -3200, 3200, zb - 1050 + k * 300, zb - 1000 + k * 300) for k in range(3)]
        work += [cyl((x, -3300, zb - 300), (x, 3300, zb - 300), 45)]
        jigs += [beam, *lugs, *work]
    R.add("JIG-01 Jigs in the dryer", compound(*jigs), "load", "work", tag="JIG-01", title="Jigs at P1–P4 (sample loads)",
          spec="Jig beam 7.4 m ISMB 200, lugs at ±1.6 m; work hung ≈1.05 m below the beam", src="HDG jig", status="C")
    # 1.75 m scale figures
    figs = []
    for (x, y, z) in ((600, 5200, g.bpit_floor), (-7500, -5200, 0), (2700, 2600, 0)):
        figs += [cyl((x - 90, y, z), (x - 90, y, z + 850), 60), cyl((x + 90, y, z), (x + 90, y, z + 850), 60),
                 box(x - 190, x + 190, y - 110, y + 110, z + 850, z + 1450), sph((x, y, z + 1600), 120)]
    R.add("REF-01 Scale figures 1.75 m", compound(*figs), "load", "yellow", tag="REF-01", title="Scale figures (1.75 m)", spec="For scale only", src="—", status="C")


def build(R):
    build_flue(R)
    build_trenches(R)
    build_mixing_box(R)
    build_blower(R)
    build_dryer(R)
    build_stack(R)
    build_enclosure(R)
    build_loads(R)
