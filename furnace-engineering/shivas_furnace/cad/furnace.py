"""Furnace: civil works under it, casing & structure, lining, kettle & support, top closure, burners, instruments."""
from __future__ import annotations

import math

from ..basis import B, G
from .lib import box, compound, cyl, frame, ibeam, merge, pipe, quarter_ring, rrect, rring, sph, tube

S = B.v  # shorthand


def build_civil_furnace(R):
    g = G
    # pad (D-15: 150 lower than Rev K to make room for the ventilated grillage)
    pad = box(-1500, 1500, -4250, 4250, g.pad_bot, g.pad_top)
    for yc in (-2000, 2000):  # leak-pit thickening
        pad = pad.union(box(-650, 650, yc - 650, yc + 650, g.pad_bot - 325, g.pad_bot))
        pad = pad.cut(box(-425, 425, yc - 425, yc + 425, g.pad_top - 600, g.pad_top + 1))
    R.add("CIV-01 Furnace foundation pad", pad, "civil", "concrete", tag="CIV-01", title="Furnace foundation pad",
          spec="RCC M30, 3,000 × 8,500 × 600, T16 @ 150 both ways; top −1.725, underside −2.325; thickened 1,300 sq. under each leak pit",
          material="RCC M30", src="Rev K · D-15 · D-07", status="D", note="Rev K pad kept, set 150 mm lower for the ventilated grillage.")
    # leak pits: castable liner 75 inside a 850 cut
    lp = None
    for yc in (-2000, 2000):
        liner = box(-425, 425, yc - 425, yc + 425, g.pad_top - 675, g.pad_top).cut(box(-350, 350, yc - 350, yc + 350, g.pad_top - 600, g.pad_top + 1))
        lp = merge(lp, liner)
    R.add("CIV-02 Zinc leak pits", lp, "civil", "castable", tag="CIV-02", title="Zinc leak pits (2)",
          spec="700 × 700 × 600 clear, 75 mm dense castable liner, at Y ±2,000 on the kettle centreline",
          src="Rev K (size) · D-07 (position)", status="D", qty="2",
          note="Reached from the hearth through 700 × 700 openings with a sacrificial 25 mm board and a steel chute through the grillage.")
    # furnace pit walls along the casing + burner pits
    t = g.pitw
    walls = merge(box(-1700, -1500, -4106, 4106, g.pad_bot, 0), box(1500, 1700, -4106, 4106, g.pad_bot, 0))
    slabs = None
    for s in (1, -1):
        y0, y1 = sorted((s * g.bpitY0, s * (g.bpitY1 + t)))
        slabs = merge(slabs, box(-1700, 1700, min(s * 4250, s * (g.bpitY1 + t)), max(s * 4250, s * (g.bpitY1 + t)), g.bpit_slab, g.bpit_floor))
        walls = walls.union(box(-1700, -1500, y0, y1, g.bpit_slab, 0)).union(box(1500, 1700, y0, y1, g.bpit_slab, 0))
        ye = s * g.bpitY1
        walls = walls.union(box(-1700, 1700, min(ye, ye + s * t), max(ye, ye + s * t), g.bpit_slab, 0))
    # flue duct sleeve through the west wall
    walls = walls.cut(box(-1701, -1499, g.flueY - 520, g.flueY + 520, -830, -70))
    R.add("CIV-03 Furnace and burner pit walls", walls, "civil", "rccpit", tag="CIV-03", title="Furnace pit and burner pit walls",
          spec="RCC 200, furnace pit 3,000 wide; burner pits 3,000 × 1,800 clear, floor −1.750", src="Rev K · HDG · D-08", status="D",
          note="119 mm ventilated gap between the casing and the pit walls; grating at FFL.")
    R.add("CIV-04 Burner pit floor slabs", slabs, "civil", "concrete2", tag="CIV-04", title="Burner pit floor slabs",
          spec="RCC 200, top −1.750, underside −1.950", src="Rev K · HDG", status="C")
    gr = merge(box(-1500, -g.cXo - 4, -4106, 4106, -40, 0), box(g.cXo + 4, 1500, -4106, 4106, -40, 0))
    gr = gr.cut(box(-1501, -g.cXo - 3, g.flueY - 520, g.flueY + 520, -41, 1))
    R.add("CIV-05 Gap gratings", gr, "civil", "grating", tag="CIV-05", title="Ventilated-gap gratings at FFL",
          spec="Serrated grating 115 × 40, both long sides of the casing", src="D-08", status="D")
    # grillage ISMB 150 @ 600 (D-15)
    beams = []
    y = -3900
    while y <= 3901:
        beams.append(ibeam((-g.cXo, y, g.pad_top + 75), (g.cXo, y, g.pad_top + 75)))
        y += 600
    R.add("STR-01 Ventilated grillage", compound(*beams), "casing", "steel2", tag="STR-01", title="Ventilated foundation grillage",
          spec=f"ISMB 150 transverse @ 600 c/c ({len(beams)} nos), 2,762 long, on the pad; air channels open to both pit gaps",
          material="IS 2062 E250", src="D-15", status="D", qty=str(len(beams)))
    chutes = compound(*[box(-356, 356, yc - 356, yc + 356, g.pad_top, g.cbase).cut(box(-350, 350, yc - 350, yc + 350, g.pad_top - 1, g.cbase + 1)) for yc in (-2000, 2000)])
    R.add("STR-02 Leak-pit chutes", chutes, "casing", "steel", tag="STR-02", title="Leak-pit chutes through the grillage",
          spec="6 mm plate, 712 × 712 × 150", src="D-07", status="D", qty="2")


def build_casing(R):
    g = G
    outer = box(-g.cXo, g.cXo, -g.cYo, g.cYo, g.cbase, g.ctop)
    inner = box(-g.cXi, g.cXi, -g.cYi, g.cYi, g.cbase + g.cfp, g.ctop + 1)
    cas = outer.cut(inner)
    # flue cut-out (west face) and burner holes (end faces)
    cas = cas.cut(box(-g.cXo - 1, -g.cXi + 1, g.flueY - 500, g.flueY + 500, -750, -150))
    for x, s in ((-g.bX, 1), (g.bX, -1)):
        cas = cas.cut(cyl((x, s * (g.cYi - 1), g.bZ), (x, s * (g.cYo + 1), g.bZ), 125))
    for yc in (-2000, 2000):
        cas = cas.cut(box(-350, 350, yc - 350, yc + 350, g.cbase - 1, g.cbase + g.cfp + 1))
    R.add("CAS-01 Casing shell", cas, "casing", "steel", tag="CAS-01", title="Furnace casing shell",
          spec="8,200 × 2,750 inside, 6 mm walls, 10 mm floor; base −1.575, top +0.150; flue cut-out 1,000 × 600; burner holes Ø250",
          material="IS 2062 E250 BR, continuously welded, gas-tight", src="Rev K · STL-EF · D-17", status="C")
    st = []
    zt = g.ctop
    y = -3600
    while y <= 3601:
        if abs(y - g.flueY) > 600:
            st.append(box(-g.cXo - 100, -g.cXo, y - 5, y + 5, g.cbase, zt))
        st.append(box(g.cXo, g.cXo + 100, y - 5, y + 5, g.cbase, zt))
        y += 800
    for x in (-1100, 0, 1100):
        if abs(abs(x) - g.bX) > 400:
            for s in (1, -1):
                st.append(box(x - 5, x + 5, s * g.cYo, s * (g.cYo + 100), g.cbase, zt))
    zb = g.cbase + 0.55 * (g.ctop - g.cbase)
    belts = [box(g.cXo, g.cXo + 50, -g.cYo, g.cYo, zb - 5, zb + 5),
             box(-g.cXo - 50, -g.cXo, -g.cYo, g.flueY - 520, zb - 5, zb + 5),
             box(-g.cXo - 50, -g.cXo, g.flueY + 520, g.cYo, zb - 5, zb + 5)]
    R.add("CAS-02 Stiffeners and belts", compound(*st, *belts), "casing", "steel2", tag="CAS-02", title="Casing stiffeners and belts",
          spec="Vertical MS flat 100 × 10 @ 800 c/c; horizontal belt MS flat 50 × 10 at 0.55 H", material="IS 2062 E250",
          src="STL-EF · HDG", status="C")
    cap = frame(-g.cXo, g.cXo, -g.cYo, g.cYo, -g.cap_in_X, g.cap_in_X, -g.cap_in_Y, g.cap_in_Y, g.ctop, g.captop)
    cap = cap.cut(frame(-g.cXo + 10, g.cXo - 10, -g.cYo + 10, g.cYo - 10, -g.cap_in_X - 10, g.cap_in_X + 10, -g.cap_in_Y - 10, g.cap_in_Y + 10, g.ctop + 10, g.captop - 10))
    R.add("STR-10 Cap beam", cap, "casing", "steel", tag="STR-10", title="Cap beam (perimeter)",
          spec="Fabricated box 300 × 100 × 10 on the casing top, +0.150 → +0.250", material="IS 2062 E250", src="D-03 (after STL-EF SHS 300 × 150)", status="D")
    # sectional chequered deck: cap outer to flange outer, split in panels
    fx, fy = g.kWo / 2 + g.flw, g.kLo / 2 + g.flw
    deck = rrect(2 * g.cYo, 2 * g.cXo, 0, g.captop, g.deck).cut(rrect(2 * fy + 6, 2 * fx + 6, g.kro + g.flw + 3, g.captop - 1, g.deck + 1))
    for yc in range(-3000, 3001, 1000):
        deck = deck.cut(box(-g.cXo - 1, g.cXo + 1, yc - 2, yc + 2, g.captop - 1, g.deck + 1))
    R.add("STR-11 Chequered deck", deck, "casing", "deck", tag="STR-11", title="Sectional chequered deck plate",
          spec="6 mm chequered, bolted panels ≈1,000 long, +0.250 → +0.256; rim stands 44 mm proud", src="STL-EF · D-03", status="D")


def build_lining(R):
    g = G
    z0, z1 = g.f_plate_top, g.ctop
    layers = [("LIN-03", "Calcium silicate backing 25", "casi", 0, 25, "Calcium silicate board 245 kg/m³, 25 mm"),
              ("LIN-02", "Microporous 50", "mpi", 25, 75, "Microporous board 320 kg/m³, 2 × 25 mm"),
              ("LIN-01", "Folded module hot face 175", "module", 75, 250, "Folded ceramic-fibre module 128 kg/m³, 1430 grade, 175 mm, Z-anchored SS310")]
    for tag, title, col, a, b, spec in layers:
        xo, yo, xi, yi = g.cXi - a, g.cYi - a, g.cXi - b, g.cYi - b
        w = frame(-xo, xo, -yo, yo, -xi, xi, -yi, yi, z0, z1)
        if tag == "LIN-01":   # 50 mm rebate above the HD-board seat (SH-INS)
            w = w.cut(frame(-g.lrX, g.lrX, -g.lrY, g.lrY, -g.lfX - 1, g.lfX + 1, -g.lfY - 1, g.lfY + 1, g.lip_top, z1 + 1))
        w = w.cut(box(-g.cXi - 1, -g.lfX + 1, g.flueY - 500, g.flueY + 500, -750, -150))
        for x, s in ((-g.bX, 1), (g.bX, -1)):
            w = w.cut(box(x - 200, x + 200, s * g.lfY - s * 1, s * g.cYi + s * 1, g.bZ - 200, g.bZ + 200))
        R.add(f"{tag} {title}", w, "lining", col, tag=tag, title=title, spec=spec + "; walls −1.565 → +0.150",
              src="D-05 (Rev K 128 kg/m³ hot face; SH-INS 250 mm)", status="D")
    # burner blocks and flue port block
    bb = []
    for x, s in ((-g.bX, 1), (g.bX, -1)):
        blk = box(x - 200, x + 200, min(s * g.lfY, s * g.cYi), max(s * g.lfY, s * g.cYi), g.bZ - 200, g.bZ + 200)
        bb.append(blk.cut(cyl((x, s * (g.lfY - 5), g.bZ), (x, s * (g.cYi + 5), g.bZ), 100)))
    R.add("LIN-05 Burner blocks", compound(*bb), "burner", "castable", tag="LIN-05", title="Burner blocks (quarls)",
          spec="Dense castable 1600 °C, 400 × 400 × 250 with Ø200 port", src="D-05", status="D", qty="2")
    fp = box(-g.cXi, -g.lfX, g.flueY - 500, g.flueY + 500, -750, -150).cut(box(-g.cXi - 1, -g.lfX + 1, g.flueY - 350, g.flueY + 350, -600, -300))
    R.add("LIN-06 Flue port block", fp, "flue", "castable", tag="LIN-06", title="Flue port block",
          spec="Dense castable frame 1,000 × 600 × 250, passage 700 × 300 = 0.21 m²", src="Rev H", status="C")
    # hearth (inside the lining): CaSi 50, microporous 25, blanket 3 x 50 A-B-A strips, HD board tiles
    hx, hy = g.lfX, g.lfY
    lpcut = lambda w, za, zb: w.cut(box(-350, 350, -2350, -1650, za - 1, zb + 1)).cut(box(-350, 350, 1650, 2350, za - 1, zb + 1))
    R.add("LIN-10 Hearth calcium silicate", lpcut(box(-hx, hx, -hy, hy, g.f_plate_top, g.f_casi_top), g.f_plate_top, g.f_casi_top),
          "lining", "casi", tag="LIN-10", title="Hearth calcium silicate 2 × 25", spec="245 kg/m³, 7,700 × 2,250", src="D-04", status="D")
    R.add("LIN-11 Hearth microporous", lpcut(box(-hx, hx, -hy, hy, g.f_casi_top, g.f_mpi_top), g.f_casi_top, g.f_mpi_top),
          "lining", "mpi", tag="LIN-11", title="Hearth microporous 25", spec="320 kg/m³", src="D-04", status="D")
    for i, (col, off) in enumerate((("B1", 0), ("B2", 305), ("B3", 0))):
        za, zb = g.f_mpi_top + 50 * i, g.f_mpi_top + 50 * (i + 1)
        strips, x = [], -hx - off
        while x < hx:
            a, b = max(x, -hx), min(x + 610, hx)
            if b - a > 5:
                strips.append(lpcut(box(a + 3, b - 3, -hy, hy, za, zb), za, zb))
            x += 610
        R.add(f"LIN-1{2 + i} Hearth blanket layer {i + 1}", compound(*strips), "lining", col, tag=f"LIN-1{2 + i}",
              title=f"Hearth blanket layer {i + 1} (layout {'ABA'[i]})",
              spec="64 kg/m³ 1260 grade, 50 mm, strips 610 × 7,725 (7,700 + 25 compression); layer 2 shifted 305 so no joint runs through",
              src="SH-INS-01 Rev B (B3 case) · D-04", status="D")
    tiles = []
    for xa in (-hx, -hx + 500, -hx + 1000, -hx + 1500, -hx + 2000):
        for ya in range(int(-hy), int(hy), 1000):
            a, b = xa, min(xa + 500, hx)
            c, d = ya, min(ya + 1000, hy)
            if b - a > 5 and d - c > 5:
                tiles.append(box(a + 2, b - 2, c + 2, d - 2, g.f_blk_top, g.f_top))
    hdb = lpcut(compound(*tiles), g.f_blk_top, g.f_top)
    R.add("LIN-15 Hearth HD board wear face", hdb, "lining", "hdb", tag="LIN-15", title="Hearth HD board wear face",
          spec="HD board 500 × 1,000 × 25; hearth surface −1.315; 255 mm under the kettle", src="D-04", status="D")
    covers = compound(*[box(-350, 350, yc - 350, yc + 350, g.f_blk_top, g.f_top) for yc in (-2000, 2000)])
    R.add("LIN-16 Leak-pit sacrificial covers", covers, "lining", "panel", tag="LIN-16", title="Leak-pit sacrificial covers",
          spec="25 mm board over the 700 × 700 hearth openings; molten zinc breaks through", src="D-07", status="D", qty="2")


def build_kettle(R):
    g = G
    L, W, r = g.kLo, g.kWo, g.kro
    shell = rrect(L, W, r, g.k_out_bot, g.rim).cut(rrect(g.kLi, g.kWi, g.kri, g.k_in_bot, g.rim + 1))
    R.add("KET-01 Kettle", shell, "kettle", "kettle", tag="KET-01", title="Zinc kettle",
          spec="6,700 × 1,250 × 1,310 inside, 50 mm plate, corners R250 inside; rim +0.300, outer bottom −1.060",
          material="Kettle-grade low-Si killed plate, Si ≤ 0.03 %, P ≤ 0.02 %, UT + RT", src="Rev K · STL-EF · D-06", status="C")
    fl = rring(L, W, r, 0, g.flw, g.fl_bot, g.rim)
    R.add("KET-02 Rim flange", fl, "kettle", "kettle", tag="KET-02", title="Kettle rim flange",
          spec="120 wide × 40 thick, continuous; the load path: flange → graphite strip → bearing ring → ribs → cap beam",
          src="STL-EF Rev D · D-02", status="D")
    zinc = rrect(g.kLi - 4, g.kWi - 4, g.kri - 2, g.k_in_bot + 1, g.zinc)
    R.add("PRC-01 Molten zinc", zinc, "kettle", "zinc", tag="PRC-01", title="Molten zinc bath",
          spec="9.72 m³ × 6.62 t/m³ = 64.3 t at 445–455 °C; surface +0.150 (1,160 deep)", src="Rev K", status="C")
    strip = rring(L, W, r, 20, 120, g.strip_bot, g.strip_top)
    R.add("SUP-01 Graphite bearing strip", strip, "kettle", "graphite", tag="SUP-01", title="Graphite bearing strip",
          spec="8 × 100, 500 mm segments; lets the kettle grow ≈39 mm along its length", src="STL-EF", status="C")
    ring = merge(rring(L, W, r, 20, 120, g.ring_top - 10, g.ring_top), rring(L, W, r, 110, 120, g.ring_top - 100, g.ring_top - 10))
    R.add("SUP-02 Bearing ring", ring, "kettle", "support", tag="SUP-02", title="Bearing ring",
          spec="ISA 100 × 100 × 10, mitred and welded, perimeter only", material="IS 2062 E250", src="STL-EF", status="C")
    ribs = []
    pitch = B.v("support.rib_pitch")
    for y in range(-3500, 3501, int(pitch)):
        for s in (1, -1):
            ribs.append(box(s * g.ring_out_X, s * g.cap_in_X, y - 6, y + 6, g.rib_bot, g.rib_top))
    for x in (-500, 0, 500):
        for s in (1, -1):
            ribs.append(box(x - 6, x + 6, s * g.ring_out_Y, s * g.cap_in_Y, g.rib_bot, g.rib_top))
    R.add("SUP-03 Radial ribs", compound(*ribs), "kettle", "support", tag="SUP-03", title="Radial support ribs",
          spec=f"12 × 200 @ 500 c/c, {len(ribs)} nos, cantilevered from the cap beam; σ ≈ 100 MPa vs 140 allowable (C-12)",
          material="IS 2062 E250", src="STL-EF · C-12", status="C", qty=str(len(ribs)))
    lip = rring(L, W, r, 0, g.lipw, g.lip_top - g.lipt, g.lip_top)
    R.add("TOP-01 Lip plate", lip, "topclose", "lip", tag="TOP-01", title="Lip plate (HD-board seat)",
          spec="50 wide × 12, welded round the kettle; top 200 below the flange underside (+0.060)", src="SH-INS-01 Rev B", status="C")


def _rib_cut(w, za, zb):
    g = G
    for y in range(-3500, 3501, 500):
        w = w.cut(box(-1400, -g.ring_out_X + 1, y - 8, y + 8, za - 1, zb + 1)).cut(box(g.ring_out_X - 1, 1400, y - 8, y + 8, za - 1, zb + 1))
    for x in (-500, 0, 500):
        w = w.cut(box(x - 8, x + 8, -4200, -g.ring_out_Y + 1, za - 1, zb + 1)).cut(box(x - 8, x + 8, g.ring_out_Y - 1, 4200, za - 1, zb + 1))
    return w


def build_topclose(R):
    g = G
    L, W, r = g.kLo, g.kWo, g.kro
    outer = box(-g.lrX, g.lrX, -g.lrY, g.lrY, 0, 1)
    def annulus(za, zb, inner_off=0):
        o = box(-g.lrX, g.lrX, -g.lrY, g.lrY, za, zb)
        return o.cut(rrect(L + 2 * inner_off, W + 2 * inner_off, r + inner_off, za - 1, zb + 1))
    hdb = _rib_cut(annulus(g.lip_top, g.hdb_top), g.lip_top, g.hdb_top)
    R.add("TOP-02 HD boards", hdb, "topclose", "hdb", tag="TOP-02", title="HD boards, top closure",
          spec="500 × 1,000 × 25, cut to 488 between ribs; bear 50 on the lip and 50 on the lining rebate", src="SH-INS-01 Rev B", status="C")
    ringzone = rrect(L + 2 * 121, W + 2 * 121, r + 121, g.ring_top - 101, g.ring_top + 1)
    for i, col in enumerate(("T1", "T2", "T3")):
        za, zb = g.hdb_top + 50 * i, g.hdb_top + 50 * (i + 1)
        w = _rib_cut(annulus(za, zb), za, zb).cut(ringzone.cut(rrect(L + 2 * 109, W + 2 * 109, r + 109, g.ring_top - 102, g.ring_top + 2)))
        R.add(f"TOP-0{3 + i} Top blanket layer {i + 1}", w, "topclose", col, tag=f"TOP-0{3 + i}", title=f"Top closure blanket layer {i + 1}",
              spec="64 kg/m³, 50 mm, compressed 610 → 500 and tucked flat (no upturn); 25 mm clear under the deck", src="SH-INS-01 Rev B", status="C")
    band = rring(L, W, r, 0, 50, -890, -585)
    R.add("TOP-06 Bottom band", band, "topclose", "band", tag="TOP-06", title="Bottom band 305 × 50",
          spec="64 kg/m³ blanket ripped 2 × 8,300 × 305, compressed butt joints at mid-length of the long sides; −0.890 → −0.585",
          src="SH-INS (1 roll per kettle) · D-04", status="D")
    # corner shields: NW (burner 1) and SE (burner 2)
    zs0, zs1 = B.v("lining.shield_z")
    for name, sx, sy in (("north-west, beside burner 1", -1, 1), ("south-east, beside burner 2", 1, -1)):
        cx, cy = sx * (W / 2 - r), sy * (L / 2 - r)
        def path(o_in, o_out, za, zb):
            straight_long = box(sx * (W / 2 + o_in), sx * (W / 2 + o_out), cy, cy - sy * 725, za, zb)
            arc = quarter_ring(cx, cy, r + o_in, r + o_out, za, zb, (sx, sy))
            straight_end = box(cx, cx - sx * 225, sy * (L / 2 + o_in), sy * (L / 2 + o_out), za, zb)
            return straight_long.union(arc).union(straight_end)
        plate = path(50, 56, zs0, zs1)
        fibre = path(0, 50, -570, 40)
        key = "NW" if sx < 0 else "SE"
        R.add(f"TOP-07 Corner shield {key}", plate, "topclose", "ss", tag="TOP-07", title=f"Curved SS corner shield, {name}",
              spec="750 high × 1,500 developed (725 + R350 quarter + 225); 50 mm off the kettle; −0.695 → +0.055",
              material="SS 310S 6 mm (assumed, O-10)", src="SH-INS-03 Rev B (19 Nov) · D-06", status="C")
        R.add(f"TOP-08 Shield fibre {key}", fibre, "topclose", "shf", tag="TOP-08", title=f"Shield backing fibre, {name}",
              spec="2 × 25 mm blanket 4,200 × 610, one roll per shield, no joints; −0.570 → +0.040", src="SH-INS-03 Rev B", status="C")


def build_burners(R):
    g = G
    for i, (x, s) in enumerate(((-g.bX, 1), (g.bX, -1)), start=1):
        face = s * g.cYo
        y = lambda d: face + s * d
        mp = box(x - 300, x + 300, min(y(0), y(12)), max(y(0), y(12)), g.bZ - 300, g.bZ + 300)
        body = cyl((x, y(12), g.bZ), (x, y(532), g.bZ), 190)
        plen = cyl((x, y(532), g.bZ), (x, y(702), g.bZ), 230)
        air_in = cyl((x, y(617), g.bZ + 200), (x, y(617), g.bZ + 330), 57)
        gas_in = cyl((x, y(702), g.bZ), (x, y(794), g.bZ), 30)                       # axial 2" gas inlet (H1)
        flange_bolts = [cyl((x + 255 * math.cos(a), y(12), g.bZ + 255 * math.sin(a)), (x + 255 * math.cos(a), y(30), g.bZ + 255 * math.sin(a)), 9)
                        for a in [k * math.pi / 4 for k in range(8)]]
        R.add(f"BUR-0{i} Burner {i}", merge(body, plen, air_in, gas_in), "burner", "burner", tag=f"BUR-0{i}",
              title=f"Burner {i}: Bloom HV-400, {'north face, fires south along the west alley' if s > 0 else 'south face, fires north along the east alley'}",
              spec="Bloom HV-400 high-velocity, cold air, gas only, 586 kW (gas 59 Nm³/h, air 566 Nm³/h); axis −0.390, 946.5 off centre (271.5 off the kettle plate); flame Ø197; single 2\" gas inlet at the rear (H1)",
              src="SH-PID-02A Rev U · Rev H · Rev K", status="C", note="Body is an envelope (O-03): replace with the Bloom GA before fabrication.", pid=f"BURNER {i}", pidgroup=f"Burner {i}")
        R.add(f"BUR-1{i} Burner {i} mounting", compound(mp, *flange_bolts), "burner", "steel2", tag=f"BUR-1{i}", title=f"Burner {i} mounting plate",
              spec="600 × 600 × 12 on the casing end plate, 8 × M16", src="HDG", status="C")


def build_instruments(R):
    g = G
    tcs = []
    for yc, hot in zip(B.v("kettle.tc_positions_Y"), (600, 800, 1100)):
        x = g.kWi / 2 - 70
        tcs.append(cyl((x, yc, g.zinc - hot), (x, yc, g.rim + 250), 16))
        tcs.append(box(x - 60, x + 60, yc - 60, yc + 60, g.rim + 250, g.rim + 370))
        tcs.append(box(x - 10, x + 300, yc - 15, yc + 15, g.rim + 10, g.rim + 30))      # clamp arm to the flange
        coil = None
        for k in range(10):
            a0, a1 = k * math.pi / 5, (k + 1) * math.pi / 5
            p0 = (x + 150 + 150 * math.cos(a0), yc + 150 * math.sin(a0), g.rim + 450 + 6 * k)
            p1 = (x + 150 + 150 * math.cos(a1), yc + 150 * math.sin(a1), g.rim + 450 + 6 * (k + 1))
            coil = merge(coil, cyl(p0, p1, 5))
        tcs.append(coil)
    R.add("INS-01 Bath thermocouples", compound(*tcs), "instr", "galv", tag="INS-01", title="Bath thermocouples (3)",
          spec="Duplex Type K in Ti Gr.2 tubes, hot parts 600 / 800 / 1,100 mm, Ø300 expansion coil; east inner edge at Y −2,400 / 0 / +2,400",
          src="Rev K thermocouple schedule", status="C", qty="3")
    ftc = []
    for s, yc in ((-1, 2000), (1, -2000)):
        ftc.append(cyl((s * g.cXo, yc, -400), (s * (g.cXo - 450), yc, -400), 10))
        ftc.append(box(s * g.cXo, s * (g.cXo + 90), yc - 45, yc + 45, -445, -355))
    R.add("INS-02 Chamber thermocouples", compound(*ftc), "instr", "galv", tag="INS-02", title="Chamber thermocouples (2)",
          spec="Type N, Inconel 600 MI Ø8, U = 450, through the long walls at −0.400 (west Y +2,000, east Y −2,000)",
          src="Rev K (type) · this design (positions)", status="D", qty="2")


def build(R):
    build_civil_furnace(R)
    build_casing(R)
    build_lining(R)
    build_kettle(R)
    build_topclose(R)
    build_burners(R)
    build_instruments(R)
