"""Sheet definitions GA-001..GA-006 and rendering to DXF, PDF and SVG."""
from __future__ import annotations

import sys
import time

from ezdxf.addons.drawing import Frontend, RenderContext, config, layout
from ezdxf.addons.drawing.pymupdf import PyMuPdfBackend
from ezdxf.addons.drawing.svg import SVGBackend
from ezdxf.enums import TextEntityAlignment

from ..basis import B, G
from . import sheets as S
from .sheets import A1, OUT, Sheet

S.VIEWS["north"] = ((0, 1, 0), (-1, 0, 0))        # looking south, west to the right
S.VIEWS["top_rot"] = ((0, 0, 1), (0, 1, 0))       # plan with north to the right

LEVELS = [(G.rim, "+0.300 kettle rim"), (G.deck, "+0.256 deck"), (G.captop, "+0.250 cap beam"), (G.ctop, "+0.150 casing top / zinc"),
          (0, "±0.000 FFL"), (G.bZ, "−0.390 burner axis"), (G.k_out_bot, "−1.060 kettle bottom"), (G.f_top, "−1.315 hearth"),
          (G.cbase, "−1.575 casing base"), (G.pad_top, "−1.725 pad top"), (G.bpit_floor, "−1.750 burner pit floor"), (G.pad_bot, "−2.325 pad underside")]


def ga001():
    s = Sheet("SHV-FUR-6700-GA-001", "GENERAL ARRANGEMENT", "Furnace, dryer, heat-recovery loop and stack — plan and elevation")
    T = s.view("PLAN (TOP VIEW)", "top", (365, 333), 75, exclude=("load", "enclosure"))
    s.dim(T, 75, (-G.cXo, G.cYo), (G.cXo, G.cYo), 10)
    s.dim(T, 75, (G.cXo, -G.cYo), (G.cXo, G.cYo), 14, vertical=True)
    s.dim(T, 75, (G.dX0 - 350, G.dY + 350), (G.dX1 + 350, G.dY + 350), 12)
    s.dim(T, 75, (G.stack[0], G.stack[1]), (0, G.stack[1]), -8)
    s.dim(T, 75, (G.dX1 + 350, 0), (-G.cXo, 0), 30)
    for (u, v, txt, dx, dy) in [(0, 0, "KET-01 kettle 6,700 × 1,250 × 1,310 in HV furnace FUR-01", 30, 40), (-7500, 0, "DRY-01 4-position pit dryer", -40, 52),
                                (-2650, -7600, "HRL-05 mixing box S2", 30, -26), (-4775, -7600, "HRL-07 recirc. blower AEP-ZA-9.0", -45, -40),
                                (G.stack[0], G.stack[1], "STK-01 stack Ø400 × 12 m", -40, -8), (7600, -7600, "GAS-02 gas train A1–A11 (PNG in at A1)", 10, -25),
                                (3400, -5100, "AIR-02 combustion air blower MBI-4040", 20, 18), (2900, 5500, "VEN-PF-N pit fan", 25, 12),
                                (-2650, -2500, "HRL-03 junction", -8, 30), (-1800, -2500, "FLU-01 lined flue duct", 22, 24)]:
        s.callout(T, u, v, txt, dx, dy)
    # north arrow
    nx, ny = 530, 555
    s.msp.add_lwpolyline([(nx, ny), (nx - 4, ny - 12), (nx, ny - 9), (nx + 4, ny - 12)], close=True, dxfattribs={"layer": "FRAME"})
    s.text("N", (nx, ny + 2), 4, align=TextEntityAlignment.BOTTOM_CENTER)
    T2 = s.view("ELEVATION LOOKING NORTH", "south", (690, 330), 100, exclude=("load", "enclosure", "civil"))
    s.levels(T2, -12400, [(G.rim, "+0.300 rim"), (0, "±0.000 FFL"), (12000, "+12.000 stack top"), (4000, "+4.000 bleed duct")], 6, right=False)
    s.notes(["All dimensions in mm, levels in m from FFL ±0.000 at the kettle centre on plan.",
             "Plant coordinates: X east, Y north. Origin = kettle centre. Grid of the HDG plant model maps as X = 1000(x − 45.5), Y = −1000(z − 8.5).",
             "Layout of loop equipment follows the SHIVAS HDG plant model with the changes in the decision register (D-13, D-19, D-20).",
             "Gas: PID-02 Rev M. Header DN65 on sleepers at +0.140; mains DN50 into both burner pits.",
             "Heat-recovery trenches 1,000 deep clear (Hold H1 / O-01). Flue in a lined steel duct in a vented trench (D-10).",
             "This drawing is generated from the 3D model SHV-FUR-6700 Rev A; the STEP file is the master geometry."], x=560, y=95)
    return s


def ga002():
    s = Sheet("SHV-FUR-6700-GA-002", "FURNACE — PLAN AT BURNER AXIS", "Section at −0.390, burner pits, alleys, corner shields")
    bb = ((-2500, 2600), (-6400, 6400), (-3000, 1800))
    T = s.view("SECTION AT −0.390 (BURNER AXIS), NORTH TO THE RIGHT", "top_rot", (420, 420), 25, cut=(2, G.bZ, "-"),
               bbox=bb, exclude=("load", "enclosure", "stack", "dryer"), clip=(-6400, 6400, -2500, 2500))
    # in top_rot: u = Y (north right), v = -X (west up)
    s.dim(T, 25, (-G.cYi, -G.cXi), (G.cYi, -G.cXi), -78)
    s.dim(T, 25, (-G.cYo, G.cXi), (-G.cYo, -G.cXi), -30, vertical=True)
    s.dim(T, 25, (-G.kLo / 2, G.kWo / 2), (G.kLo / 2, G.kWo / 2), 60)
    s.dim(T, 25, (0, -G.kWo / 2), (0, G.kWo / 2), 30, vertical=True)
    s.dim(T, 25, (1500, -G.kWo / 2), (1500, -G.lfX), 22, vertical=True)
    s.dim(T, 25, (1500, -G.lfX), (1500, -G.cXi), 22, vertical=True)
    s.dim(T, 25, (G.cYi, 0), (G.cYi, G.bX), -40, vertical=True)
    s.dim(T, 25, (G.cYo, -1500), (G.bpitY1, -1500), -40)
    s.dim(T, 25, (G.flueY - 500, G.cXo), (G.flueY + 500, G.cXo), 20)
    for (u, v, txt, dx, dy) in [(G.cYo + 600, G.bX, "BUR-01 burner 1 Bloom HV-400, fires south (left)", 20, 40), (-G.cYo - 600, -G.bX, "BUR-02 burner 2, fires north", -20, -40),
                                (3300, 700, "TOP-07 curved SS shield NW, 750 × 1,500 dev.", 30, 30), (-3300, -700, "TOP-07 SS shield SE", -30, -30),
                                (0, 0, "KET-01 kettle + zinc (cut)", 40, 12), (G.flueY, G.cXo + 400, "FLU-01 flue port 700 × 300 → lined duct 700 × 400", -30, 30),
                                (2000, 0, "Leak pit below (CIV-02)", 20, -30), (5000, 0, "Gas train B4 → B2 → B1 → B3", 25, -38)]:
        s.callout(T, u, v, txt, dx, dy)
    s.text("N →", (760, 520), 5)
    # detail: NW corner shield 1:10
    T2 = s.view("DETAIL 1 — NW CORNER SHIELD AT −0.390", "top_rot", (370, 115) , 10, cut=(2, G.bZ, "-"),
                bbox=((-1500, 0), (2000, 4300), (-1000, 0)), include=("kettle", "topclose", "lining", "casing", "burner"), clip=(2300, 4250, 100, 1450))
    s.dim(T2, 10, (G.kLo / 2, G.kWo / 2), (G.kLo / 2 + 56, G.kWo / 2), -12)
    s.notes(["Burners fire tangentially along the alleys from diagonally opposite end faces (Rev H): axis 946.5 off centre, 271.5 off the kettle plate; flame Ø197.",
             "Alley = 450 clear between the kettle and the 250 lining (SH-INS); flame edge 80 mm from the lining, 173 mm from the kettle.",
             "Corner shields (SH-INS-03 Rev B, 19 Nov): 725 straight + R350 quarter + 225 = 1,500 developed, 750 high (−0.695…+0.055), 50 off the kettle; 2 × 25 fibre behind.",
             "Wall lining D-05: 175 folded module 128 kg/m³ + 50 microporous + 25 CaSi, rebated 50 above the HD-board seat."], x=24, y=200, w=300)
    return s


def ga003():
    s = Sheet("SHV-FUR-6700-GA-003", "FURNACE — CROSS SECTION A–A", "Section at Y = 250 (mid-bay between ribs) looking north; kettle support and top closure detail")
    bb = ((-2200, 2200), (-200, 4500), (-2700, 700))
    sc = 15
    T = s.view("SECTION A–A (Y = 250, MID-BAY BETWEEN RIBS) LOOKING NORTH", "south", (190, 385), sc, cut=(1, 250, "+"), bbox=bb,
               exclude=("load", "enclosure", "gas", "air"), clip=(-2000, 2000, -2700, 700))
    s.dim(T, sc, (-G.cXi, G.captop), (G.cXi, G.captop), 34)
    s.dim(T, sc, (-G.kWo / 2, G.rim), (G.kWo / 2, G.rim), 14)
    s.dim(T, sc, (G.kWo / 2, -700), (G.lfX, -700), 5)
    s.dim(T, sc, (G.lfX, -700), (G.cXi, -700), 5)
    s.dim(T, sc, (-1900, G.k_out_bot), (-1900, G.rim), -6, vertical=True)
    s.levels(T, 2000, LEVELS, 8)
    for (u, v, txt, dx, dy) in [(0, -400, "PRC-01 zinc, 1,160 deep", 25, 50), (-G.kWo / 2 - 25, -740, "TOP-06 band 305 × 50", -45, 10),
                                (-G.lfX - 100, -1000, "LIN-01..03 wall 175 module + 50 MPI + 25 CaSi", -30, -8), (-400, G.f_top - 100, "Hearth D-04: 25 HD + 3 × 50 + 25 MPI + 50 CaSi", -30, -55),
                                (500, G.pad_top + 75, "STR-01 ventilated grillage ISMB 150 @ 600", 40, -60), (-900, -2000, "CIV-01 pad M30, 600", -40, -30),
                                (-G.bX, G.bZ, "flame axis (burner 1, west alley)", -45, 25)]:
        s.callout(T, u, v, txt, dx, dy)
    # detail 1: west top closure at 1:5
    T2 = s.view("DETAIL 1 — KETTLE SUPPORT AND TOP CLOSURE (WEST SIDE, Y = 250)", "south", (775, 420), 5, cut=(1, 250, "+"),
                bbox=((-1500, -500), (-200, 4500), (-200, 450)), include=("kettle", "topclose", "lining", "casing"), clip=(-1420, -620, -120, 340))
    s.dim(T2, 5, (-G.kWo / 2, G.fl_bot), (-G.kWo / 2 - G.flw, G.fl_bot), -6)
    s.dim(T2, 5, (-G.kWo / 2, G.lip_top), (-G.lrX, G.lip_top), -14)
    s.dim(T2, 5, (-1400, G.lip_top), (-1400, G.fl_bot), -6, vertical=True)
    s.dim(T2, 5, (-1400, G.ctop), (-1400, G.captop), -6, vertical=True)
    for (u, v, txt, dx, dy) in [(-G.kWo / 2 - 60, G.rim - 20, "KET-02 rim flange 120 × 40", 40, 30), (-G.kWo / 2 - 70, G.strip_bot + 4, "SUP-01 graphite strip 8 × 100", 50, 18),
                                (-G.ring_out_X + 5, G.ring_top - 50, "SUP-02 bearing ring ISA 100 × 100 × 10", 60, 4), (-G.kWo / 2 - 25, G.lip_top - 6, "TOP-01 lip plate 50 × 12", 50, -14),
                                (-900, G.lip_top + 12, "TOP-02 HD board 25", 20, -36), (-900, 185, "TOP-03..05 blanket 3 × 50, 64 kg/m³", -60, -50),
                                (-1230, 200, "STR-10 cap beam 300 × 100 × 10", -30, 22), (-1000, G.deck - 3, "STR-11 deck 6 mm chequered", -10, 52),
                                (-1250, -60, "LIN-01..03 wall lining 175 + 50 + 25", -30, -20)]:
        s.callout(T2, u, v, txt, dx, dy)
    rows = [["Support load path", "flange → graphite strip → bearing ring → 36 ribs → cap beam → casing → grillage → pad (STL-EF)"],
            ["Suspended load", "≈795 kN incl. 5 % jig (C-12)"], ["Rib stress", "≈100 MPa vs 140 allowable at 250 °C (C-12)"],
            ["Kettle growth", "≈39 mm along its length; slides on the graphite strip"], ["Casing skin", "61–65 °C at 900–1,000 °C hot face (C-04)"],
            ["Pad top", "≈65 °C with the ventilated grillage (C-04, D-15)"]]
    s.table(420, 300, 2, rows, (60, 300), h=6, size=2.0, head=["Check", "Value (calc SHV-FUR-6700-CR)"])
    return s


def ga004():
    s = Sheet("SHV-FUR-6700-GA-004", "FURNACE — LONG SECTION B–B AND BURNER PIT", "Section through the west alley on the burner-1 axis; north burner pit elevation")
    bb = ((-1500, 2500), (-6500, 6500), (-2800, 1600))
    T = s.view("SECTION B–B (X = −946.5, BURNER 1 AXIS) LOOKING EAST", "west", (420, 455), 25, cut=(0, -G.bX, "+"), bbox=bb,
               exclude=("load", "enclosure", "stack", "dryer", "loop"), clip=(-6500, 6500, -2700, 1600))
    # 'west' view: u = -Y, v = Z
    s.dim(T, 25, (-G.cYi, G.cbase), (G.cYi, G.cbase), -40)
    s.dim(T, 25, (-G.kLo / 2, G.rim + 400), (G.kLo / 2, G.rim + 400), 10)
    s.dim(T, 25, (-G.cYo, -1500), (-G.bpitY1, -1500), -22)
    s.levels(T, 6500, LEVELS, 8)
    for (u, v, txt, dx, dy) in [(-G.cYo - 300, G.bZ, "BUR-01 burner 1 Bloom HV-400", -10, 45), (-G.cYi + 500, G.bZ, "flame axis −0.390, Ø197, fires south", 30, 30),
                                (-G.lfY + 150, G.bZ, "LIN-05 burner block 400 × 400", 10, -40), (2500, -450, "flue port 700 × 300 (west face)", 20, 35),
                                (-5000, G.bpit_floor + 300, "VEN-PF-N extract at −1.450", -10, -18), (2000, G.pad_top - 300, "CIV-02 leak pit 700 × 700 × 600", 20, -18)]:
        s.callout(T, u, v, txt, dx, dy)
    T2 = s.view("NORTH BURNER PIT — ELEVATION LOOKING SOUTH (CUT AT Y = +5.000)", "north", (215, 200), 15, cut=(1, 5000, "-"),
                bbox=((-1800, 1800), (3000, 5100), (-2000, 1500)), exclude=("load", "enclosure", "civil"), clip=(-1750, 1750, -1950, 1300))
    for (u, v, txt, dx, dy) in [(-G.bX, G.bZ, "BUR-01", 20, 30), (0, G.bZ - 550, "GAS-11 B4 · B2 VAS240 · B1 GIK40 · B3 GEH40", 40, -10),
                                (-G.bX, 300, "AIR-11 4\" branch + D2", -30, 16), (900, -700, "BMS-N BCU 370 + TZI8", 30, 12)]:
        s.callout(T2, u, v, txt, dx, dy)
    s.notes(["Burner pits 3,000 × 1,800 clear, floor −1.750 (Rev K). Handrails 1,000 / 500 / toe board; cat ladder each pit.",
             "Pit fans D-09: one 3 HP fan per pit, extracting 300 above the pit floor (LPG is heavier than air), ≥ 189 m³/h each.",
             "Burner train on the face per SH-PID-02 Rev M; BCU 370 proves air, purges, sparks direct (no pilot), proves UV.",
             "Burner body drawn as an envelope; replace with the Bloom HV-400 GA before fabrication (O-03)."], x=400, y=110)
    return s


def ga005():
    s = Sheet("SHV-FUR-6700-GA-005", "DRYER AND HEAT-RECOVERY LOOP", "Section C–C through the dryer and plan of the trenches at −0.200")
    T = s.view("SECTION C–C (Y = 0) LOOKING NORTH", "south", (370, 440), 40, cut=(1, 0, "+"),
               bbox=((-12500, -1000), (-500, 5000), (-2200, 1800)), exclude=("enclosure",), clip=(-12500, -1500, -2100, 1600))
    s.dim(T, 40, (G.dX0, -1600), (G.dX1, -1600), -15)
    s.dim(T, 40, (G.dX0 - 400, G.d_floor), (G.dX0 - 400, 0), -14, vertical=True)
    for x in G.dP:
        s.callout(T, x, 650, f"P{G.dP.index(x) + 1}", 0, 12)
    for (u, v, txt, dx, dy) in [(G.dX0 + 175, -700, "DRY-04 supply box 1,300 × 350, centre fed", -20, -35), (G.dX1 - 175, -700, "DRY-05 extraction box", 20, -35),
                                (-7500, 125, "DRY-11 deck + fixed cover", 25, 30), (-5250, 430, "DRY-03 door P4", 30, 22)]:
        s.callout(T, u, v, txt, dx, dy)
    T2 = s.view("LOOP PLAN — SECTION AT −0.200", "top", (430, 245), 75, cut=(2, -200, "-"),
                bbox=((-12500, 1000), (-9500, 4500), (-1500, 2000)), exclude=("load", "enclosure"), clip=(-12500, 500, -9200, 4300))
    for (u, v, txt, dx, dy) in [(-3175, 0, "HRL-02 return 900 × 1,000 · 100 °C", 25, 20), (-2650, -2500, "HRL-03 junction", 30, 8),
                                (-2650, -5000, "HRL-04 suction 1,000 × 1,000", 30, 0), (-2650, -7600, "HRL-05 mixing box S2", 30, -12),
                                (-8000, -8100, "HRL-08 discharge 1,100 × 1,000 · 120 °C", -10, -18), (-11400, -3000, "HRL-08", -20, 0),
                                (-1800, -2500, "FLU-01 flue 800 °C", 25, 18)]:
        s.callout(T2, u, v, txt, dx, dy)
    rows = [["Recirculation blower", "AEP-ZA-9.0 · 48,000 m³/h at 120 °C · 72 mmWC · 30 HP"], ["Mixing", "flue + return + fresh → ≈124 °C (C-08)"],
            ["Dryer duty", "≈209 kW across the loads (C-08)"], ["Bleed", "4,729 Nm³/h → Ø400 × 12 m stack, ≈150 kW to the HX"],
            ["Perforated faces", "Ø15 @ 37 staggered, 14.9 % open, ≈5,900 holes each (D-12)"], ["Loop pressure", "≈74 mmWC hot (C-09) — confirm fan rating basis (O-07)"]]
    s.table(560, 250, 2, rows, (60, 200), h=6, size=2.0, head=["Item", "Value"])
    return s


def ga006():
    s = Sheet("SHV-FUR-6700-GA-006", "SCHEDULES — LEVELS, DESIGN DATA, BILL OF MATERIALS", "Generated from the design basis and the 3D model")
    R = S.registry()
    rows = [[p.tag, p.title, p.qty, p.spec, p.status] for p in sorted([p for p in R.parts if p.layer != "flow"], key=lambda p: p.tag)]
    half = (len(rows) + 1) // 2
    w = (20, 70, 9, 160, 6)
    head = ["Tag", "Item", "Qty", "Specification", "St"]
    s.text("BILL OF MATERIALS  (St: C confirmed · D decided here · A assumed · O open)", (24, 577), 3.0)
    s.table(24, 572, 5, rows[:half], w, h=3.75, size=1.5, head=head)
    s.table(24 + sum(w) + 4, 572, 5, rows[half:], w, h=3.75, size=1.5, head=head)
    x2 = 24 + 2 * sum(w) + 12
    s.text("LEVELS SCHEDULE", (x2, 577), 3.0)
    lv = [[lab.split(" ", 1)[0], lab.split(" ", 1)[1]] for _z, lab in LEVELS] + [["−1.000", "loop trench clear floor (Hold H1)"], ["−1.100", "mixing box floor"],
          ["−1.400", "dryer clear floor"], ["+0.500", "air ring centreline"], ["+4.000", "bleed duct centreline"], ["+12.000", "stack top"]]
    y = s.table(x2, 572, 2, lv, (24, 72), h=4.6, size=1.9, head=["Level m", "Description"])
    s.text("DESIGN DATA", (x2, y - 8), 3.0)
    dd = [["Kettle", "6,700 × 1,250 × 1,310 in, 50 plate"], ["Zinc", "64.3 t, 445–455 °C"], ["Burners", "2 × Bloom HV-400"],
          ["Installed", "1,172 kW (118 Nm³/h)"], ["At 6.0 t/h", "≈761 kW, 12.8 Nm³/t"], ["Capacity", "6.0–6.7 t/h at 25 kW/m²"],
          ["Comb. air", "MBI-4040 1,400 m³/h · 725 mmWC"], ["Dryer", "4 pos. 6.0 × 7.5 × 1.4 m, 209 kW"],
          ["Recirc.", "AEP-ZA-9.0 48,000 m³/h"], ["Stack", "Ø400 × 12 m, 15 m/s"]]
    s.table(x2, y - 12, 2, dd, (24, 72), h=4.6, size=1.9, head=["Item", "Value"])
    return s


def render(sheets):
    import pymupdf
    for name, sh in sheets:
        sh.save(name)
        cfg = config.Configuration(background_policy=config.BackgroundPolicy.WHITE, color_policy=config.ColorPolicy.COLOR,
                                   lineweight_scaling=0.6, min_lineweight=0.08)
        page = layout.Page(A1[0], A1[1], layout.Units.mm, margins=layout.Margins.all(0))
        bsvg = SVGBackend()
        Frontend(RenderContext(sh.doc), bsvg, config=cfg).draw_layout(sh.msp)
        (OUT / f"{name}.svg").write_text(bsvg.get_string(page, settings=layout.Settings(fit_page=False, scale=1)))
        bpdf = PyMuPdfBackend()
        Frontend(RenderContext(sh.doc), bpdf, config=cfg).draw_layout(sh.msp)
        pdf = bpdf.get_pdf_bytes(page, settings=layout.Settings(fit_page=False, scale=1))
        (OUT / f"{name}.pdf").write_bytes(pdf)
        one = pymupdf.open("pdf", pdf)
        one[0].get_pixmap(dpi=110).save(str(OUT / f"{name}.png"))
        print("rendered", name)
    allpdf = pymupdf.open()
    for f in sorted(OUT.glob("SHV-FUR-6700-GA-00?.pdf")):
        allpdf.insert_pdf(pymupdf.open(str(f)))
    allpdf.save(str(OUT / "SHV-FUR-6700-GA-set.pdf"))


def build(which=None):
    t = time.time()
    defs = [("SHV-FUR-6700-GA-001", ga001), ("SHV-FUR-6700-GA-002", ga002), ("SHV-FUR-6700-GA-003", ga003),
            ("SHV-FUR-6700-GA-004", ga004), ("SHV-FUR-6700-GA-005", ga005), ("SHV-FUR-6700-GA-006", ga006)]
    sheets = []
    for name, fn in defs:
        if which and name[-3:] not in which:
            continue
        t0 = time.time()
        sheets.append((name, fn()))
        print(name, f"{time.time() - t0:.1f}s")
    render(sheets)
    print(f"total {time.time() - t:.1f}s")


if __name__ == "__main__":
    build(sys.argv[1:] or None)
