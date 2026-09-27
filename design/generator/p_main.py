from lib import *


def main_page():
    parts = [header()]
    # intro strip
    parts.append(sec(72, f"""<div style="height: 100%; display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid {RULE}">
<h1 style="margin: 0; font-size: 20px; font-weight: 600; color: {TEXT}">Wire drawing machinery and turnkey hot dip galvanizing plants, engineered and built in Ghaziabad, India.</h1>
<span style="font-size: 16px; color: {MUTED}">Choose a division</span></div>""", bg="#FFFFFF"))
    # split hero
    left = f"""<a href="WireDrawing.dc.html" style="flex: 1; display: flex; flex-direction: column; justify-content: space-between; box-sizing: border-box; padding: 72px 64px 48px 80px; background: {ZINC}; color: {TEXT}">
<div style="display: flex; flex-direction: column; gap: 22px">
<span style="font-size: 17px; font-weight: 600; color: {TEAL}">Wire drawing division</span>
<h2 style="margin: 0; font-size: 64px; line-height: 1.02; font-weight: 800; font-stretch: 125%; letter-spacing: -0.01em; color: {INK}">Machines that draw steel wire</h2>
<p style="margin: 0; max-width: 500px; font-size: 19px; line-height: 1.55; color: {MUTED}">Straight line and OTO type wire drawing machines, with the pay-offs, descalers, die boxes, coilers and spoolers that complete the line.</p>
<span style="align-self: flex-start; display: inline-flex; align-items: center; min-height: 52px; padding: 0 26px; font-size: 16px; font-weight: 600; background: {TEAL}; color: #FFFFFF; border-radius: 2px">Enter wire drawing</span>
</div>
<div style="margin-right: -64px">{svg_straight_line(640)}</div>
</a>"""
    right = f"""<a href="Galvanizing.dc.html" style="flex: 1; display: flex; flex-direction: column; justify-content: space-between; box-sizing: border-box; padding: 72px 80px 48px 64px; background: {INK}; color: {ON_DARK}">
<div style="display: flex; flex-direction: column; gap: 22px">
<span style="font-size: 17px; font-weight: 600; color: {AMBER}">Hot dip galvanizing division</span>
<h2 style="margin: 0; font-size: 64px; line-height: 1.02; font-weight: 800; font-stretch: 125%; letter-spacing: -0.01em; color: #FFFFFF">Plants that galvanize steel</h2>
<p style="margin: 0; max-width: 520px; font-size: 19px; line-height: 1.55; color: {ON_DARK_M}">Turnkey galvanizing plants: zinc kettles, high velocity pulse-fired furnaces, PP and FRP process tanks, enclosed rooms, fume extraction, and ETP and ZLD systems.</p>
<span style="align-self: flex-start; display: inline-flex; align-items: center; min-height: 52px; padding: 0 26px; font-size: 16px; font-weight: 600; background: {AMBER}; color: {INK}; border-radius: 2px">Enter galvanizing</span>
</div>
<div style="margin-left: -24px">{svg_kettle_scene(600)}</div>
</a>"""
    parts.append(f'<div style="height: 880px; flex-shrink: 0; display: flex">{left}{right}</div>')

    # one engineering house
    cols = [
        ("Engineered in-house", "Process design, plant layout, combustion engineering, mechanical design and PLC programming are done by our own engineers. The kettle, the furnace, the fume system and the controls are designed to work together."),
        ("Built at our works", "Fabrication, machining, PP and FRP work, panel building and assembly at our works in Ghaziabad, with quality checks at each stage of manufacture."),
        ("Commissioned on site", "Erection, start-up, operator training and after-sales support for single machines, complete lines and turnkey plants, in India and abroad."),
    ]
    cells = "".join(f'<div style="display: flex; flex-direction: column; gap: 14px; border-top: 3px solid {INK}; padding-top: 24px"><h3 style="margin: 0; font-size: 24px; font-weight: 700; color: {INK}">{h}</h3><p style="margin: 0; font-size: 17px; line-height: 1.6; color: {MUTED}">{b}</p></div>' for h, b in cols)
    parts.append(sec(540, f"""<div style="padding-top: 96px; display: flex; flex-direction: column; gap: 56px">
<h2 style="margin: 0; max-width: 900px; font-size: 44px; line-height: 1.1; font-weight: 800; font-stretch: 112%; color: {INK}">Process, mechanical, combustion and controls under one roof</h2>
<div style="display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 48px">{cells}</div></div>"""))

    # directory
    wire_items = [("Straight line wire drawing machines", "WireDrawing.dc.html#straight-line"), ("OTO type wire drawing machines", "WireDrawing.dc.html#oto"), ("Inverted vertical machines", "WireDrawing.dc.html#line"), ("Pay-offs and mechanical descalers", "WireDrawing.dc.html#line"), ("Rotating die boxes", "WireDrawing.dc.html#line"), ("Dead block coilers, spoolers and take-ups", "WireDrawing.dc.html#line"), ("Annealing furnaces", "WireDrawing.dc.html#line"), ("Drives and control panels", "WireDrawing.dc.html#line")]
    galv_items = [("Turnkey hot dip galvanizing plants", "Galvanizing.dc.html"), ("Zinc kettles", "Galvanizing.dc.html#systems"), ("High velocity pulse-fired furnaces", "Furnace.dc.html"), ("Kettle enclosures", "Galvanizing.dc.html#systems"), ("Enclosed pretreatment rooms", "Galvanizing.dc.html#systems"), ("PP and FRP process tanks", "Galvanizing.dc.html#systems"), ("Flux filtration and regeneration", "Galvanizing.dc.html#systems"), ("Zinc and acid fume extraction", "Galvanizing.dc.html#air-water"), ("ETP and ZLD systems", "Galvanizing.dc.html#air-water"), ("Automation and material handling", "Galvanizing.dc.html#automation")]
    def dl(title, items, color):
        rows = "".join(f'<a href="{h}" style="display: flex; justify-content: space-between; align-items: center; min-height: 52px; border-bottom: 1px solid {RULE}; font-size: 18px; font-weight: 500; color: {TEXT}"><span>{t}</span><svg viewBox="0 0 16 16" width="16" height="16" aria-hidden="true"><path d="M5 3 L10 8 L5 13" class="ln s-steel"></path></svg></a>' for t, h in items)
        return f'<div style="display: flex; flex-direction: column"><h3 style="margin: 0 0 12px; font-size: 22px; font-weight: 700; color: {color}">{title}</h3>{rows}</div>'
    parts.append(sec(760, f"""<div style="padding-top: 80px; display: flex; flex-direction: column; gap: 44px">
<h2 style="margin: 0; font-size: 44px; font-weight: 800; font-stretch: 112%; color: {INK}">Everything we build</h2>
<div style="display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 80px">{dl("Wire drawing", wire_items, TEAL_D)}{dl("Hot dip galvanizing", galv_items, AMBER_D)}</div></div>""", bg="#FFFFFF"))

    # proof
    tiles = "".join(f"""<div style="display: flex; flex-direction: column; gap: 14px">
<div style="height: 260px; background: {ZINC}; border: 1px dashed #9AAAB6; display: flex; align-items: center; justify-content: center; font-size: 15px; color: {MUTED}">[Site photo: {ph}]</div>
<div style="font-size: 20px; font-weight: 700; color: {INK}">{t}</div>
<div style="font-size: 16px; line-height: 1.5; color: {MUTED}">[Client name], [City, Country]<br>{d}</div></div>""" for t, ph, d in (
        ("Structural galvanizing plant", "kettle and crane in operation", "Kettle [L × W × D m], [tonnes per month]"),
        ("Crash barrier galvanizing line", "W-beam jigs at the kettle", "Kettle [L × W × D m], pulse-fired furnace"),
        ("Straight line drawing line", "machine running wire", "[Blocks] × Ø[block] mm, [inlet] to [outlet] mm")))
    parts.append(sec(640, f"""<div style="padding-top: 80px; display: flex; flex-direction: column; gap: 40px">
<div style="display: flex; justify-content: space-between; align-items: flex-end"><h2 style="margin: 0; font-size: 44px; font-weight: 800; font-stretch: 112%; color: {INK}">Where our equipment runs</h2>{btn("See all projects", "About.dc.html#projects", "ghost")}</div>
<div style="display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 32px">{tiles}</div></div>"""))

    # group
    group = [
        ("SHIVAS Reinplast", "Thermoplastic and FRP process equipment, fume scrubbers and air pollution control.", "https://shivasasia.com", "shivasasia.com"),
        ("PP tanks", "Polypropylene tanks built to DVS guidelines, with steel support structures.", "https://pptanks.com", "pptanks.com"),
        ("Pickling plants", "Pickling lines for wire, pipe, strip and structures.", "https://pickling-plants.com", "pickling-plants.com"),
        ("FRP blowers", "Corrosion-resistant FRP and PP blowers for fume extraction.", "https://frpblower.com", "frpblower.com"),
    ]
    gcells = "".join(f'<a href="{u}" style="display: flex; flex-direction: column; gap: 10px; padding: 28px; background: #16324A; color: {ON_DARK}"><span style="font-size: 20px; font-weight: 700; color: #FFFFFF">{n}</span><span style="font-size: 16px; line-height: 1.5; color: {ON_DARK_M}">{d}</span><span style="margin-top: auto; font-size: 15px; font-weight: 600; color: {AMBER}">{l}</span></a>' for n, d, u, l in group)
    parts.append(sec(520, f"""<div style="padding-top: 80px; display: flex; flex-direction: column; gap: 36px">
<div style="display: flex; flex-direction: column; gap: 12px"><h2 style="margin: 0; font-size: 44px; font-weight: 800; font-stretch: 112%; color: #FFFFFF">The SHIVAS group</h2>
<p style="margin: 0; max-width: 760px; font-size: 18px; line-height: 1.55; color: {ON_DARK_M}">Our sister company SHIVAS Reinplast builds the thermoplastic and FRP equipment that surrounds a galvanizing or wire plant. One group, one point of contact.</p></div>
<div style="display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 20px; height: 220px">{gcells}</div></div>""", bg=INK))

    # CTA
    parts.append(sec(300, f"""<div style="height: 100%; display: flex; align-items: center; justify-content: space-between; gap: 48px">
<div style="display: flex; flex-direction: column; gap: 12px"><h2 style="margin: 0; font-size: 44px; font-weight: 800; font-stretch: 112%; color: {INK}">Tell us what you need to draw or galvanize</h2>
<p style="margin: 0; font-size: 18px; color: {TEXT}">Send your wire sizes or job dimensions. An engineer replies, not a sales desk.</p></div>
<div style="display: flex; gap: 14px; flex-shrink: 0">{btn("Request a quote", "Contact.dc.html", "ghost")}{btn("WhatsApp us", "https://wa.me/919810280104", "ghost")}</div></div>""", bg=AMBER))
    parts.append(footer())
    h = 88 + 72 + 880 + 540 + 760 + 640 + 520 + 300 + FOOTER_H
    return page("SHIVAS Technology — choose a division", 1440, h, "\n".join(parts)), h


def mobile_page():
    w = 390
    hdr = f"""<header style="height: 64px; flex-shrink: 0; display: flex; align-items: center; justify-content: space-between; padding: 0 20px; background: #FFFFFF; border-bottom: 1px solid {RULE}">
<a href="Main.dc.html" aria-label="SHIVAS Technology home" style="display: flex; align-items: center; gap: 10px; color: {INK}">{LOGO}<span style="font-size: 21px; font-weight: 800; font-stretch: 125%; letter-spacing: 0.02em">SHIVAS</span></a>
<button type="button" aria-label="Open menu" style="width: 48px; height: 48px; border: 0; background: transparent; display: flex; align-items: center; justify-content: center"><svg viewBox="0 0 24 24" width="24" height="24" aria-hidden="true"><path d="M3 7 H21 M3 12 H21 M3 17 H21" class="ln s-steel"></path></svg></button></header>"""
    intro = f'<div style="padding: 24px 20px 20px; flex-shrink: 0"><h1 style="margin: 0; font-size: 18px; line-height: 1.45; font-weight: 600; color: {TEXT}">Wire drawing machinery and turnkey hot dip galvanizing plants, engineered in Ghaziabad, India.</h1></div>'
    wire = f"""<a href="WireDrawing.dc.html" style="flex-shrink: 0; display: flex; flex-direction: column; gap: 14px; padding: 32px 20px 20px; background: {ZINC}; color: {TEXT}">
<span style="font-size: 15px; font-weight: 600; color: {TEAL}">Wire drawing division</span>
<span style="font-size: 36px; line-height: 1.04; font-weight: 800; font-stretch: 118%; color: {INK}">Machines that draw steel wire</span>
<span style="font-size: 16px; line-height: 1.5; color: {MUTED}">Straight line and OTO machines and complete drawing lines.</span>
{svg_straight_line(350)}
<span style="display: flex; align-items: center; justify-content: center; min-height: 52px; font-size: 16px; font-weight: 600; background: {TEAL}; color: #FFFFFF; border-radius: 2px">Enter wire drawing</span></a>"""
    galv = f"""<a href="Galvanizing.dc.html" style="flex-shrink: 0; display: flex; flex-direction: column; gap: 14px; padding: 32px 20px 20px; background: {INK}; color: {ON_DARK}">
<span style="font-size: 15px; font-weight: 600; color: {AMBER}">Hot dip galvanizing division</span>
<span style="font-size: 36px; line-height: 1.04; font-weight: 800; font-stretch: 118%; color: #FFFFFF">Plants that galvanize steel</span>
<span style="font-size: 16px; line-height: 1.5; color: {ON_DARK_M}">Turnkey plants, kettles, pulse-fired furnaces, fume and effluent systems.</span>
{svg_kettle_scene(350)}
<span style="display: flex; align-items: center; justify-content: center; min-height: 52px; font-size: 16px; font-weight: 600; background: {AMBER}; color: {INK}; border-radius: 2px">Enter galvanizing</span></a>"""
    quick = f"""<div style="flex-shrink: 0; padding: 28px 20px; display: flex; flex-direction: column; gap: 12px; background: #FFFFFF">
<span style="font-size: 20px; font-weight: 700; color: {INK}">Talk to an engineer</span>
<div style="display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 10px">
<a href="tel:+919810280104" style="display: flex; align-items: center; justify-content: center; min-height: 52px; font-weight: 600; color: {INK}; box-shadow: inset 0 0 0 1.5px {INK}">Call</a>
<a href="https://wa.me/919810280104" style="display: flex; align-items: center; justify-content: center; min-height: 52px; font-weight: 600; color: {INK}; box-shadow: inset 0 0 0 1.5px {INK}">WhatsApp</a>
<a href="Contact.dc.html" style="display: flex; align-items: center; justify-content: center; min-height: 52px; font-weight: 600; color: {INK}; background: {AMBER}">Quote</a></div></div>"""
    body = "\n".join([hdr, intro, wire, galv, quick])
    h = 1320
    return page("SHIVAS — mobile home", w, h, body, bg="#FFFFFF"), h
