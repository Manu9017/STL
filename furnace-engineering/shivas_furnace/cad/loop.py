"""Flue duct, heat-recovery loop (trenches, mixing box, recirculation blower), 4-position dryer, bleed & stack,
zinc fume enclosure, sample loads, scale figures."""
from __future__ import annotations

import math

from ..basis import B, G
from .lib import box, compound, cyl, duct, frame, ibeam, merge, pipe, quarter_ring, sph, tube

FLOWCOL = {"HRL-02a": "retn", "HRL-02b": "retn", "HRL-03": "suct", "HRL-04": "suct", "HRL-08": "supp"}
FLOWNAME = {"HRL-02a": "Return trench 900 × 1,000 (from the dryer)", "HRL-02b": "Return trench 900 × 1,000 (to the junction)",
            "HRL-03": "Three-way junction 1,000 × 1,000 (return + flue → suction)", "HRL-04": "Suction trench 1,000 × 1,000",
            "HRL-08": "Discharge trench 1,100 × 1,000 (blower at the SW corner → supply box)"}
FLOWSPEC = {"HRL-02a": "28,614 Nm³/h at 100 °C = 10.86 m³/s, 12.1 m/s", "HRL-02b": "28,614 Nm³/h at 100 °C, 12.1 m/s",
            "HRL-03": "10.86 + 1.41 = 12.27 m³/s, radiused merge", "HRL-04": "12.27 m³/s at ≈124–130 °C, 12.3 m/s",
            "HRL-08": "48,000 m³/h at 120 °C = 13.33 m³/s from the blower, 11.44 m³/s after the bleed; 12.1 m/s"}


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
        if k == "HRL-08":
            c = c.cut(cyl((g.bleed[0], g.bleed[1], -20), (g.bleed[0], g.bleed[1], 20), 210))
            c = c.cut(box(g.rb_axis[0] - 101, g.rb_axis[1] + 50, g.rb_axis[2] - 1000, g.rb_axis[2] + 1000, -20, 20))
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
    """Recirculation blower at the SW corner where the discharge turns north into the dryer (D-22, user instruction).
    Fan axis at +0.90 on the mixing-box cut-out, so the long suction duct runs straight; outlet drops into HRL-08."""
    g = G
    sx0, sx1, yc, zc = g.rb_axis
    r = g.rb_r
    dx0, dx1, _yd, _zd, rd = g.suction                 # Ø1100 duct from the mixing box (dx0) to the reducer (dx1)
    ped = compound(box(-14100, -12150, -8800, -6400, 0, 300), box(-10650, -10050, -8800, -6400, 0, 300))
    frm = compound(*[box(-14000, -10100, y - 50, y + 50, 300, 500) for y in (-8750, -6450)],
                   *[box(x - 50, x + 50, -8800, -6400, 300, 500) for x in (-13950, -12250)], box(-10650, -10550, -8800, -6400, 300, 400))
    lugs = compound(box(sx0 + 60, sx1 - 60, -8750, -8550, 500, zc), box(sx0 + 60, sx1 - 60, -6650, -6450, 500, zc))
    R.add("HRL-07a Blower pedestals", ped, "civil", "concrete2", tag="HRL-07a", title="Recirculation blower pedestals",
          spec="RCC, west and east of the discharge trench at the SW corner", src="D-22", status="D")
    R.add("HRL-07b Blower base frame", merge(frm), "loop", "steel", tag="HRL-07b", title="Blower base frame",
          spec="ISMC 200 frame bridging the trench (east cross member lowered under the straightener spool); scroll on side lugs, outlet drops straight into HRL-08", src="D-22", status="D")
    scroll = cyl((sx0, yc, zc), (sx1, yc, zc), r)
    outlet = box(sx0, sx0 + 675, yc - 950, yc - 50, -400, zc - r + 40)
    R.add("HRL-07 Recirculation blower", merge(scroll, outlet, lugs), "loop", "fan", tag="HRL-07", title="Recirculation blower AEP-ZA-9.0 (SW corner)",
          spec="48,000 m³/h at 120 °C, 72 mmWC, 30 HP; Ø900 inlet facing east on the axis +0.900; 900 × 675 outlet straight down into the 1,100 × 1,000 trench where it turns north to the dryer",
          src="Rev H · user instruction 21 Nov · D-22", status="C", note="Confirm whether 72 mmWC is a 20 °C or 120 °C rating (O-07).")
    clad = 600
    duct = cyl((dx0, yc, zc), (dx1, yc, zc), clad).cut(cyl((dx0 - 1, yc, zc), (dx1 + 1, yc, zc), rd - 3))
    flange = tube((dx0 - 20, yc, zc), (dx0, yc, zc), 640, rd)
    red = __import__("cadquery").Workplane().add(__import__("cadquery").Solid.makeCone(rd + 50, 450 + 50, 400, __import__("cadquery").Vector(dx1, yc, zc),
                                                                                     __import__("cadquery").Vector(-1, 0, 0)))
    spool = tube((dx1 - 400, yc, zc), (sx1 + 150, yc, zc), 456, 450)
    flex = cyl((sx1 + 150, yc, zc), (sx1, yc, zc), 480)
    cross = compound(box(sx1 + 170, sx1 + 730, yc - 445, yc + 445, zc - 2, zc + 2), box(sx1 + 170, sx1 + 730, yc - 2, yc + 2, zc - 445, zc + 445))
    stools = compound(*[merge(box(x - 75, x + 75, yc - 450, yc + 450, 0, zc - clad - 60), box(x - 120, x + 120, yc - 420, yc + 420, zc - clad - 60, zc - clad - 1)) for x in (-9200, -6900, -4600)])
    L = (dx0 - dx1) / 1000
    R.add("HRL-12 Suction duct Ø1100", merge(duct, flange), "loop", "alu", tag="HRL-12", title="Suction duct Ø1100, mixing box → blower",
          spec=f"Ø1100 × 3 mm MS, {L:.2f} m straight at +0.900 from the Ø1,114 cut-out on the mixing-box west face; 50 mm mineral wool + 0.8 mm aluminium cladding (Ø1,200 over cladding); ≈12.9 m/s",
          src="user instruction 21 Nov · D-22 · SH-MB-01 Rev A", status="D", note="Lengthened when the blower moved to the SW corner; Ø1100 keeps the added loss ≈2 mmWC (C-09).")
    R.add("HRL-12a Reducer Ø1100 → Ø900", red, "loop", "galv", tag="HRL-12a", title="Concentric reducer Ø1100 → Ø900", spec="400 long, 3 mm MS", src="D-22", status="D")
    R.add("HRL-07c Straightener spool Ø900", spool, "loop", "galv", tag="HRL-07c", title="Straightener spool Ø900 at the fan inlet",
          spec="600 long; holds the cruciform straightener immediately ahead of the fan eye", src="SH-MB-01 Rev A · D-22", status="D")
    R.add("HRL-07d Inlet flexible connector", flex, "loop", "rubber", tag="HRL-07d", title="Inlet flexible connector", spec="High-temperature fabric, 150 °C", src="this design", status="D")
    R.add("HRL-07e Cruciform straightener", cross, "loop", "steel2", tag="HRL-07e", title="Cruciform straightener",
          spec="2 × 4 mm plates ≈560 long (mandatory per SH-MB-01)", src="SH-MB-01 Rev A", status="C")
    R.add("HRL-12b Duct stools", stools, "loop", "steel2", tag="HRL-12b", title="Suction duct support stools", spec="3 stools with sliding saddles; fixed point at the fan end", src="D-22", status="D")
    shaft = cyl((sx0, yc, zc), (-13050, yc, zc), 50)
    pb = compound(*[box(x - 120, x + 120, yc - 180, yc + 180, 500, zc - 60) for x in (-12350, -12750)])
    guard = box(-13250, -12950, yc - 180, yc + 180, 450, zc + 300)
    motor = cyl((-14000, yc, 760), (-13300, yc, 760), 260)
    mbase = box(-14000, -13300, yc - 260, yc + 260, 500, 520)
    R.add("HRL-07f Fan shaft and bearings", merge(shaft, pb), "loop", "gear", tag="HRL-07f", title="Fan shaft and plummer blocks", spec="Shaft Ø100, 2 × plummer blocks", src="HDG", status="C")
    R.add("HRL-07g Belt guard", guard, "loop", "yellow", tag="HRL-07g", title="Belt guard", spec="Expanded mesh, yellow", src="HDG", status="C")
    R.add("HRL-07h Blower motor 30 HP", merge(motor, mbase), "loop", "motor", tag="HRL-07h", title="Recirculation blower motor 30 HP (22 kW), VFD",
          spec="Cold start ≈16 kW shaft (C-11)", src="Rev H · C-11", status="C")
    R.add("FLOW-suction Suction duct gas", cyl((dx0 - 20, yc, zc), (sx1 + 160, yc, zc), 430), "loop", "suct", tag="FLOW", title="Mixed gas ≈124 °C to the blower",
          spec="12.27 m³/s", src="C-08", status="C", alpha=0.3, layer="flow")


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
    riser = pipe(g.bleed_route, 203)
    bd = merge(cyl((bx, by, 1940), (bx, by, 2060), 245), box(bx + 245, bx + 400, by - 40, by + 40, 1950, 2050))
    R.add("HRL-09 Bleed duct Ø400", riser, "stack", "bleed", tag="HRL-09", title="Bleed duct Ø400",
          spec="Out of the discharge trench just downstream of the blower; 4,729 Nm³/h = flue + fresh air (C-08), 15 m/s; open to the stack by geometry, never by a control action",
          src="Rev H · D-22 (route)", status="C")
    R.add("HRL-09a Balancing damper BD-1", bd, "stack", "red", tag="HRL-09a", title="Balancing damper BD-1", spec="Ø400 butterfly, 6 mm disc, locking quadrant, 120 °C", src="Rev H · BD-1/BD-2 notes", status="C")
    hxx = sx
    hx = merge(box(hxx - 550, hxx + 550, -11800, -10600, 3450, 4550), cyl((hxx + 550, -11000, 3700), (hxx + 800, -11000, 3700), 45), cyl((hxx + 550, -11400, 4300), (hxx + 800, -11400, 4300), 45))
    R.add("HRL-10 Flue-gas heat exchanger", hx, "stack", "steel2", tag="HRL-10", title="Flue-gas heat exchanger (hot water to flux and degreasing tanks)",
          spec="≈150 kW available in the bleed (C-08); closed hot-water loop with 3-way valve; optional in this scope", src="Rev H · SHIVAS flux tank heating", status="C")
    gp = lambda x, y, along_x: merge(box(x - 700, x - 600, y - 50, y + 50, 0, 3790), box(x + 600, x + 700, y - 50, y + 50, 0, 3790), box(x - 700, x + 700, y - 60, y + 60, 3690, 3790)) if not along_x else \
        merge(box(x - 50, x + 50, y - 700, y - 600, 0, 3790), box(x - 50, x + 50, y + 600, y + 700, 0, 3790), box(x - 60, x + 60, y - 700, y + 700, 3690, 3790))
    posts = compound(gp(-9500, -6100, True), gp(sx, -9000, False), gp(sx, -13300, False))
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


def _shs(x0, x1, y0, y1, z0, z1, t=6):
    """Square hollow section along Z."""
    o = box(x0, x1, y0, y1, z0, z1)
    return o.cut(box(min(x0, x1) + t, max(x0, x1) - t, min(y0, y1) + t, max(y0, y1) - t, z0 - 1, z1 + 1))


def _hollow(x0, x1, y0, y1, z0, z1, t=3, open_ends=""):
    """Sheet-metal box duct; open_ends in 'xXyY' leaves those faces open."""
    x0, x1 = sorted((x0, x1)); y0, y1 = sorted((y0, y1)); z0, z1 = sorted((z0, z1))
    ix0 = x0 - 1 if "x" in open_ends else x0 + t
    ix1 = x1 + 1 if "X" in open_ends else x1 - t
    iy0 = y0 - 1 if "y" in open_ends else y0 + t
    iy1 = y1 + 1 if "Y" in open_ends else y1 - t
    return box(x0, x1, y0, y1, z0, z1).cut(box(ix0, ix1, iy0, iy1, z0 + t, z1 - t))


def build_enclosure(R):
    """Zinc fume enclosure on the casing deck (SHIVAS ZEN annexure; D-24 frame and wall plane, D-25 door lift).

    Wall plane = casing outer face. Corner posts stand on the deck over the casing walls; both long sides open full length
    from the deck to the door-head girt and close with vertical-lift skimming doors outside the wall plane. Two roof covers
    split on the kettle centreline with a 200 mm rope slot and slide outward on end-wall rails. Lateral slot ducts inside
    both top edges collect into a header outside the north end wall and leave as Ø700 to the bag filter."""
    g = G
    xo, yo = g.cXo, g.cYo
    zb = g.deck
    zt = zb + B.v("enclosure.height")                 # +4.976 top of the top beams
    zg = zb + 2200                                     # door-head girt underside +2.456
    slot = B.v("enclosure.rope_slot")
    lift = B.v("enclosure.door_lift")
    travel = B.v("enclosure.cover_travel")
    sill = B.v("enclosure.window_sill")
    S = (-1, 1)
    # ---------------------------------------------------------------- frame
    corner = [_shs(sx * (xo - 120), sx * xo, sy * (yo - 120), sy * yo, zb + 16, zt - 150) for sx in S for sy in S]
    inter = [_shs(sx * (xo - 120), sx * xo, y - 60, y + 60, zg + 300, zt - 150) for sx in S for y in (-2050, 0, 2050)]
    plates = [box(sx * (xo - 200), sx * xo, sy * (yo - 200), sy * yo, zb, zb + 16) for sx in S for sy in S]
    R.add("ZEN-01 Enclosure posts", compound(*corner, *inter, *plates), "enclosure", "zenframe", tag="ZEN-01",
          title="Enclosure posts SHS 120 × 120 × 6",
          spec="4 corner posts on 200 × 200 × 16 base plates on the deck over the casing walls; 6 intermediate posts above the door-head girts",
          src="ZEN annexure · D-24", status="A", note="Member sizes to be confirmed by a structural check.")
    girts = [ibeam((sx * (xo - 70), -(yo - 120), zg + 150), (sx * (xo - 70), yo - 120, zg + 150), h=300, b=140, tw=7.5, tf=12.4) for sx in S]
    def chan_y(sx):      # ISMC 150 along Y, web on the wall plane, toes inward
        return merge(box(sx * (xo - 5.4), sx * xo, -yo, yo, zt - 150, zt), box(sx * (xo - 75), sx * xo, -yo, yo, zt - 9, zt),
                     box(sx * (xo - 75), sx * xo, -yo, yo, zt - 150, zt - 141))
    def chan_x(sy):
        return merge(box(-xo, xo, sy * (yo - 5.4), sy * yo, zt - 150, zt), box(-xo, xo, sy * (yo - 75), sy * yo, zt - 9, zt),
                     box(-xo, xo, sy * (yo - 75), sy * yo, zt - 150, zt - 141))
    R.add("ZEN-02 Door-head girts ISMB 300", compound(*girts), "enclosure", "zenframe", tag="ZEN-02", title="Door-head girts ISMB 300",
          spec=f"Both long sides at +{(zg)/1000:.3f}, spanning the corner posts (7.97 m) so the skimming openings are clear full length; carry the upper wall and the lateral duct",
          src="D-24", status="A", note="Deflection to be checked with the duct and wall loads.")
    R.add("ZEN-03 Top beams ISMC 150", compound(*[chan_y(sx) for sx in S], *[chan_x(sy) for sy in S]), "enclosure", "zenframe", tag="ZEN-03",
          title="Top ring beams ISMC 150", spec="Ring at +4.826 → +4.976; the end beams carry the roof-cover rails", src="ZEN annexure", status="A")
    # ---------------------------------------------------------------- sheeting and stiffeners
    upper = [box(sx * xo, sx * (xo + 3), -yo, yo, zg, zt) for sx in S]
    ends = []
    for sy in S:
        e = box(-(xo + 3), xo + 3, sy * yo, sy * (yo + 3), zb, zt)
        if sy > 0:
            for sx in S:
                e = e.cut(box(sx * 761, sx * 1261, yo - 10, yo + 20, 4126, 4826))
        ends.append(e)
    st = []
    for sx in S:
        for z in (3300, 4100):
            st += [box(sx * (xo + 3), sx * (xo + 53), -3980, 3980, z, z + 6), box(sx * (xo + 47), sx * (xo + 53), -3980, 3980, z - 50, z)]
    for sy in S:
        for z in (1100, 1900, 2700, 3500):
            st += [box(-(xo - 120), xo - 120, sy * (yo + 3), sy * (yo + 53), z, z + 6), box(-(xo - 120), xo - 120, sy * (yo + 47), sy * (yo + 53), z - 50, z)]
    R.add("ZEN-04 Wall sheeting", compound(*upper, *ends), "enclosure", "zen", tag="ZEN-04", title="Wall sheeting 3 mm MS",
          spec="End walls full height; long sides above the door head; sheet flush with the casing outer face; north wall cut for the two lateral ducts",
          src="ZEN annexure · D-24", status="C")
    R.add("ZEN-04a Sheet stiffeners", compound(*st), "enclosure", "zenframe", tag="ZEN-04a", title="Sheet stiffeners L 50 × 50 × 6",
          spec="Horizontal at ≈800 pitch on the outside faces", src="ZEN annexure", status="A")
    # ---------------------------------------------------------------- skimming doors (vertical lift, outside the wall plane)
    guides = []
    for sx in S:
        for sy in S:
            gd = box(sx * (xo + 3), sx * 1530, sy * 3995, sy * yo, 150, zt - 150)
            guides.append(gd.cut(box(sx * 1452, sx * 1518, sy * 3980, sy * 4050, 140, zt)))
    R.add("ZEN-06 Door guides", compound(*guides), "enclosure", "zenframe", tag="ZEN-06", title="Skimming-door guide channels",
          spec="On the corner posts, outside the wall plane, +0.150 → +4.826", src="D-24", status="D")
    zd0, zd1 = 200, zg + 50
    wins = [(yc, sill, sill + 600) for yc in (-3000, -1000, 1000, 3000)]
    for sx, nm in ((-1, "west"), (1, "east")):
        a0, a1 = sx * 1460, sx * 1510
        skin = merge(box(a0, sx * 1463, -4040, 4040, zd0, zd1), box(sx * 1507, a1, -4040, 4040, zd0, zd1))
        edge = _hollow(a0, a1, -4040, 4040, zd0, zd1, t=50, open_ends="xX")
        ribs = [box(sx * 1463, sx * 1507, y - 20, y + 20, zd0, zd1) for y in (-2000, 0, 2000)]
        rails = [box(sx * 1463, sx * 1507, -4040, 4040, z - 20, z + 20) for z in (sill - 60, sill + 660)]
        door = merge(skin, edge)
        for (yc, z0, z1) in wins:
            door = door.cut(box(a0 - 1, a1 + 1, yc - 300, yc + 300, z0, z1))
        frames = [box(sx * 1510, sx * 1525, yc - 350, yc + 350, z0 - 50, z1 + 50).cut(box(sx * 1505, sx * 1530, yc - 300, yc + 300, z0, z1)) for (yc, z0, z1) in wins]
        lugs = [box(sx * 1470, sx * 1500, y - 40, y + 40, zd1, zd1 + 80).cut(cyl((sx * 1460, y, zd1 + 45), (sx * 1510, y, zd1 + 45), 15)) for y in (-3000, 3000)]
        R.add(f"ZEN-07{'a' if sx < 0 else 'b'} Skimming door {nm}", compound(door, *ribs, *rails, *frames, *lugs), "enclosure", "zen",
              tag=f"ZEN-07{'a' if sx < 0 else 'b'}", title=f"Skimming door, {nm} side (vertical lift)",
              spec=f"7,970 × 2,306 × 50 framed panel, 3 mm skins; 4 × 600 × 600 toughened-glass windows in removable frames, sill +{sill/1000:.3f}; lift {lift:.0f} full, {B.v('enclosure.skim_stop'):.0f} skimming stop",
              src="ZEN annexure · D-24 · D-25", status="D", anim=f"door{'W' if sx < 0 else 'E'}")
        glass = compound(*[box(sx * 1482, sx * 1490, yc - 300, yc + 300, z0, z1) for (yc, z0, z1) in wins])
        R.add(f"ZEN-07{'a' if sx < 0 else 'b'}G Door windows {nm}", glass, "enclosure", "glass", tag=f"ZEN-07{'a' if sx < 0 else 'b'}G",
              title=f"Door windows, {nm} (4 × 600 × 600 toughened glass)", spec="8 mm toughened glass in removable frames", src="ZEN annexure", status="C",
              alpha=0.35, anim=f"door{'W' if sx < 0 else 'E'}")
        zh = zt - 176
        hb = []
        for y in (-3000, 3000):
            hb += [box(sx * (xo + 3), sx * 1600, y - 60, y + 60, zt - 40, zt), box(sx * 1400, sx * 1570, y - 120, y + 120, zh, zt - 40),
                   cyl((sx * 1485, y, zh - 60), (sx * 1485, y, zh), 30)]
        prox = [box(sx * 1530, sx * 1560, sy * 4020, sy * 4060, z, z + 40) for sy in (1,) for z in (zd0 + 20, zd0 + 20 + B.v("enclosure.skim_stop"), zd0 + 20 + lift)]
        R.add(f"ZEN-08{'a' if sx < 0 else 'b'} Door hoists {nm}", compound(*hb, *prox), "enclosure", "motor", tag=f"ZEN-08{'a' if sx < 0 else 'b'}",
              title=f"Door chain hoists, {nm} (2 × electric, synchronised)", spec="2 electric chain hoists at 8 m/min on brackets off the top beam; proximity limits closed / skimming stop / full lift",
              src="ZEN annexure", status="C")
        top_ch = zh - 60
        ch = compound(*[cyl((sx * 1485, y, zd1 + 45), (sx * 1485, y, top_ch), 8) for y in (-3000, 3000)])
        R.add(f"ZEN-08{'a' if sx < 0 else 'b'}C Hoist chains {nm}", ch, "enclosure", "chain", tag=f"ZEN-08{'a' if sx < 0 else 'b'}C",
              title=f"Hoist load chains, {nm}", spec="Shown at the closed position", src="ZEN annexure", status="C", anim=f"chain{'W' if sx < 0 else 'E'}:{top_ch:.0f}")
    # ---------------------------------------------------------------- roof covers (split on the centreline, slide outward)
    yr0, yr1 = yo - 75, yo - 40                      # rail on the end-beam top flange
    rails, outr = [], []
    for sy in S:
        rails += [box(-3000, 3000, sy * yr0, sy * yr1, zt, zt + 30), box(-3000, 3000, sy * (yo - 32), sy * (yo - 2), zt, zt + 40)]
        for sx in S:
            outr += [merge(box(sx * (xo + 3), sx * 3000, sy * (yo - 5.4), sy * yo, zt - 150, zt), box(sx * (xo + 3), sx * 3000, sy * (yo - 75), sy * yo, zt - 9, zt),
                           box(sx * (xo + 3), sx * 3000, sy * (yo - 75), sy * yo, zt - 150, zt - 141)),
                     cyl((sx * 1531, sy * (yo - 40), zt - 1000), (sx * 2500, sy * (yo - 40), zt - 151), 40)]
    lim = [box(sx * x - 30, sx * x + 30, sy * (yo + 5), sy * (yo + 45), zt - 60, zt) for sx in S for sy in (1,) for x in (1330, 2950)]
    R.add("ZEN-05 Cover rails and outriggers", compound(*rails, *outr), "enclosure", "zenframe", tag="ZEN-05", title="Roof-cover rails, racks and outriggers",
          spec=f"Rail 35 × 30 and m4 rack on both end beams, extended on ISMC 150 outriggers with Ø80 knee braces to X ±3.0 m; travel {travel:.0f} per cover",
          src="ZEN annexure · D-24", status="D")
    R.add("ZEN-05a Cover limit switches", compound(*lim), "enclosure", "yellow", tag="ZEN-05a", title="Roof-cover limit switches (2 per cover)",
          spec="Closed and open positions, on the north rail", src="ZEN annexure", status="C")
    zc0 = zt + 150
    for sx, nm in ((-1, "west"), (1, "east")):
        xa, xb = sx * slot / 2, sx * (xo + 100)
        fr = box(xa, xb, -(yo + 100), yo + 100, zc0, zc0 + 100).cut(box(sx * (slot / 2 + 50), sx * (xo + 50), -(yo + 50), yo + 50, zc0 - 1, zc0 + 101))
        cross = [box(xa, xb, y - 25, y + 25, zc0, zc0 + 100) for y in (-2700, -1350, 0, 1350, 2700)]
        sheet = box(xa, xb, -(yo + 100), yo + 100, zc0 + 100, zc0 + 103)
        seal = box(sx * slot / 2, sx * (slot / 2 + 25), -(yo + 100), yo + 100, zt + 60, zc0)
        carr, wh = [], []
        for sy in S:
            carr.append(box(sx * 250, sx * 1350, sy * (yo - 120), sy * (yo + 10), zt + 100, zc0))
            wh += [cyl((sx * x, sy * (yo - 77.5), zt + 80), (sx * x, sy * (yo - 37.5), zt + 80), 50) for x in (400, 1200)]
            wh.append(cyl((sx * 850, sy * (yo - 32), zt + 82), (sx * 850, sy * (yo - 2), zt + 82), 42))      # pinion on the rack
        shaft = cyl((sx * 850, -(yo - 2), zt + 82), (sx * 850, yo - 2, zt + 82), 25)
        pb = [box(sx * 800, sx * 900, y - 50, y + 50, zt + 60, zt + 100) for y in (-2700, 0, 2700)]
        motor = merge(box(sx * 760, sx * 940, yo + 10, yo + 260, zt + 30, zt + 230), cyl((sx * 850, yo - 2, zt + 82), (sx * 850, yo + 10, zt + 82), 25))
        R.add(f"ZEN-09{'a' if sx < 0 else 'b'} Roof cover {nm}", compound(fr, *cross, sheet, seal, *carr, *wh, shaft, *pb), "enclosure", "zen",
              tag=f"ZEN-09{'a' if sx < 0 else 'b'}", title=f"Sliding roof cover, {nm}",
              spec=f"{abs(xb - xa):,.0f} × {2 * (yo + 100):,.0f} ISMC 100 frame, 3 mm sheet; end carriages with 4 wheels; line shaft with pinions on both racks; brush seal on the {slot:.0f} mm rope slot",
              src="ZEN annexure · D-24", status="C", anim=f"roof{'W' if sx < 0 else 'E'}")
        R.add(f"ZEN-09{'a' if sx < 0 else 'b'}M Cover drive {nm}", motor, "enclosure", "motor", tag=f"ZEN-09{'a' if sx < 0 else 'b'}M",
              title=f"Roof-cover drive, {nm}: 0.5 HP geared motor, VFD", spec="On the north carriage, driving the line shaft", src="ZEN annexure", status="C",
              anim=f"roof{'W' if sx < 0 else 'E'}")
    # ---------------------------------------------------------------- lighting
    lamps, lens = [], []
    for sy in S:
        for x in (-500, 500):
            lamps += [box(x - 150, x + 150, sy * (yo - 200), sy * (yo - 60), zt - 760, zt - 540), box(x - 30, x + 30, sy * (yo - 60), sy * yo, zt - 680, zt - 620)]
            lens.append(box(x - 130, x + 130, sy * (yo - 206), sy * (yo - 200), zt - 740, zt - 560))
    R.add("ZEN-10 LED floods", compound(*lamps), "enclosure", "black", tag="ZEN-10", title="LED floodlights 4 × 200 W", spec="Two on each end wall, inside, aimed at the bath",
          src="ZEN annexure", status="C")
    R.add("ZEN-10a LED flood lenses", compound(*lens), "enclosure", "lamp", tag="ZEN-10a", title="LED flood lenses", spec="IP66", src="ZEN annexure", status="C")
    # ---------------------------------------------------------------- lateral suction ducts, header, outlet
    zd_a, zd_b = 4126, 4826
    lat = []
    for sx in S:
        d = _hollow(sx * 761, sx * 1261, -4050, yo + 3, zd_a, zd_b, open_ends="Y")
        for yc in range(-3500, 3501, 1000):
            d = d.cut(box(sx * 755, sx * 767, yc - 350, yc + 350, zd_a + 60, zd_a + 90))
        lat.append(d)
    R.add("ZEN-11 Lateral slot ducts", compound(*lat), "enclosure", "galv", tag="ZEN-11", title="Lateral slot plenums 500 × 700",
          spec="Inside both top edges, 3 mm MS; 8 slots 700 × 30 per side on the inner face (≈16.5 m/s) with sliding shutters; 10,000 m³/h per side, plenum 7.9 m/s at the north end (under half the slot velocity, C-15); cleaning doors",
          src="ZEN annexure · C-15", status="D")
    hdr = _hollow(-1261, 1261, yo + 3, yo + 603, zd_a, zd_b).cut(cyl((0, yo + 590, 4476), (0, yo + 610, 4476), 350))
    for sx in S:
        hdr = hdr.cut(box(sx * 764, sx * 1258, yo, yo + 8, zd_a + 3, zd_b - 3))
    yo2 = 5300
    zo = 4476
    out = pipe([(0, yo + 603, zo), (0, yo2, zo), (4600, yo2, zo)], 350).cut(pipe([(0, yo + 590, zo), (0, yo2, zo), (4620, yo2, zo)], 347))
    fl = tube((4600, yo2, zo), (4620, yo2, zo), 420, 347)
    col = merge(box(3925, 4075, yo2 - 75, yo2 + 75, 0, zo - 400), box(3800, 4200, yo2 - 400, yo2 + 400, zo - 400, zo - 350), box(3800, 4200, yo2 - 200, yo2 + 200, 0, 20))
    R.add("ZEN-12 Suction header", hdr, "enclosure", "galv", tag="ZEN-12", title="Suction header 600 × 700 outside the north end wall",
          spec="Joins both slot plenums; Ø700 outlet on the north face; 13.2 m/s", src="ZEN annexure · D-24", status="D")
    R.add("ZEN-13 Outlet duct Ø700", merge(out, fl), "enclosure", "galv", tag="ZEN-13", title="Outlet duct Ø700 to the zinc-fume bag filter",
          spec="20,000 m³/h, 14.4 m/s; north then east at +4.476 to a flanged stub at X +4.6 m", src="HDG · ZEN annexure", status="A",
          note="Bag-filter (ZFE) location and fan are open (O-16).")
    R.add("ZEN-13a Outlet duct support", col, "enclosure", "zenframe", tag="ZEN-13a", title="Outlet duct support column", spec="ISHB 150 with saddle", src="this design", status="D")


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
