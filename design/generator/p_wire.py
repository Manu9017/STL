from lib import *


def spec_rows(rows, dark=False):
    c1 = ON_DARK_M if dark else MUTED
    c2 = "#FFFFFF" if dark else TEXT
    rl = "#28415A" if dark else RULE
    return "".join(f'<div style="display: grid; grid-template-columns: 220px 1fr; gap: 16px; padding: 13px 0; border-bottom: 1px solid {rl}; font-size: 16px"><span style="color: {c1}">{k}</span><span style="color: {c2}; font-weight: 500; font-variant-numeric: tabular-nums">{v}</span></div>' for k, v in rows)


def wire_page():
    parts = [header("wire")]
    # hero
    parts.append(sec(740, f"""<div style="height: 100%; display: grid; grid-template-columns: 520px 1fr; gap: 40px; align-items: center">
<div style="display: flex; flex-direction: column; gap: 24px">
<span style="font-size: 17px; font-weight: 600; color: {TEAL}">Wire drawing division</span>
<h1 style="margin: 0; font-size: 62px; line-height: 1.03; font-weight: 800; font-stretch: 125%; letter-spacing: -0.01em; color: {INK}">Wire drawing machines and complete lines</h1>
<p style="margin: 0; font-size: 19px; line-height: 1.6; color: {MUTED}">Straight line and OTO type machines for low and high carbon steel wire, and every machine from rod pay-off to finished coil or spool.</p>
<div style="display: flex; gap: 14px">{btn("Request a machine quote", "Contact.dc.html", "teal")}{btn("Try the die calculator", "#calculator", "ghost")}</div>
</div>
<div style="display: flex; justify-content: flex-end">{svg_straight_line(800)}</div></div>""", bg=ZINC))

    # straight line
    sl_specs = [("Model series", "SLM series, e.g. SLM-600"), ("Block diameter", "[400 to 1200] mm"), ("Number of blocks", "[2 to 12], to your pass schedule"), ("Inlet rod", "Up to [Ø14] mm"), ("Finishing speed", "Up to [xx] m/s, by wire grade"), ("Drives", "AC vector drive per block, PLC synchronised"), ("Cooling", "Water-cooled capstans and die boxes")]
    parts.append(sec(760, f"""<div style="height: 100%; display: grid; grid-template-columns: 1fr 1fr; gap: 80px; align-items: center">
<div style="display: flex; flex-direction: column; gap: 20px">
<h2 style="margin: 0; font-size: 48px; line-height: 1.06; font-weight: 800; font-stretch: 118%; color: {INK}">Straight line wire drawing machines</h2>
<p style="margin: 0; font-size: 18px; line-height: 1.6; color: {MUTED}">Wire runs straight from one block to the next with no twist and no loops between passes. Each block has its own drive, and tension between blocks is held by dancer arms or load control, so the line runs fast and the wire stays straight. Suited to high carbon, spring, PC strand and bead wire as well as low carbon wire.</p>
<div style="display: flex; flex-direction: column">{spec_rows(sl_specs)}</div></div>
<div style="display: flex; flex-direction: column; gap: 16px">
<div style="height: 420px; background: {ZINC}; border: 1px dashed #9AAAB6; display: flex; align-items: center; justify-content: center; font-size: 15px; color: {MUTED}">[Photo: SLM line in the works, three-quarter view]</div>
<span style="font-size: 15px; color: {MUTED}">Specifications in brackets are to be confirmed per model.</span></div></div>""", bg="#FFFFFF", sid="straight-line"))

    # OTO
    oto_specs = [("Configuration", "Over-the-top pulley between blocks"), ("Block diameter", "[400 to 900] mm"), ("Number of blocks", "[2 to 10]"), ("Wire", "Low carbon: binding, nail, mesh, fencing, GI base wire"), ("Drives", "AC drives with PLC speed matching")]
    parts.append(sec(720, f"""<div style="height: 100%; display: grid; grid-template-columns: 1fr 1fr; gap: 80px; align-items: center">
<div style="display: flex; flex-direction: column; gap: 16px">{svg_oto(600)}</div>
<div style="display: flex; flex-direction: column; gap: 20px">
<h2 style="margin: 0; font-size: 48px; line-height: 1.06; font-weight: 800; font-stretch: 118%; color: {INK}">OTO type wire drawing machines</h2>
<p style="margin: 0; font-size: 18px; line-height: 1.6; color: {MUTED}">Wire leaves each block over an overhead pulley and enters the next die. Wire can store on each block, so small speed differences between passes are absorbed. Simple, forgiving and economical for low carbon wire.</p>
<div style="display: flex; flex-direction: column">{spec_rows(oto_specs)}</div></div></div>""", sid="oto"))

    # line equipment grid
    ic = icons_wire()
    eq = [
        ("payoff", "Pay-offs", "Static and rotating rod pay-offs, overhead and horizontal, with brakes to hold back-tension."),
        ("descaler", "Mechanical descalers", "Reverse-bending rollers and brushes that crack and strip scale before the first die."),
        ("butt", "Pointing and butt welding", "Rod pointers and butt welders to join coils and keep the line running."),
        ("diebox", "Die boxes", "Fixed and rotating die boxes with soap stirrers and water-cooled die holders."),
        ("deadblock", "Dead block coilers", "Coil drawn wire onto a stationary block into compact, stackable coils."),
        ("spooler", "Spoolers", "Spoolers with automatic traverse for evenly wound, tight spools."),
        ("takeup", "Take-ups", "Horizontal take-ups for galvanizing and strand pickling lines."),
        ("invvert", "Inverted vertical machines", "Drawing and coiling in one machine, producing heavy coils for large diameters."),
        ("anneal", "Annealing furnaces", "Furnaces for annealing low carbon wire after drawing."),
        ("pickle", "Pickling for wire", "Batch, tunnel and fumeless pickling, built by our sister company SHIVAS Reinplast."),
        ("giwire", "Galvanized wire lines", "Hot dip galvanizing lines for wire, from our galvanizing division."),
        ("panel", "Drives and control panels", "AC drive panels, PLC and HMI built in-house for every machine we supply."),
    ]
    cards = "".join(f"""<div style="display: flex; flex-direction: column; gap: 12px; padding: 24px 24px 28px; background: #FFFFFF; border: 1px solid {RULE}">
<div style="background: {PAPER}; padding: 10px 0">{ic[k]}</div>
<span style="font-size: 20px; font-weight: 700; color: {INK}">{t}</span>
<span style="font-size: 16px; line-height: 1.55; color: {MUTED}">{d}</span></div>""" for k, t, d in eq)
    parts.append(sec(1440, f"""<div style="padding-top: 96px; display: flex; flex-direction: column; gap: 40px">
<div style="display: flex; justify-content: space-between; align-items: flex-end; gap: 48px"><h2 style="margin: 0; max-width: 720px; font-size: 44px; line-height: 1.1; font-weight: 800; font-stretch: 112%; color: {INK}">Everything from rod coil to finished wire</h2>
<p style="margin: 0; max-width: 420px; font-size: 17px; line-height: 1.55; color: {MUTED}">Buy a single machine or a complete line with one set of controls.</p></div>
<div style="display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 20px">{cards}</div></div>""", bg=ZINC, sid="line"))

    # calculator
    def field(label, key, hint):
        return f"""<div style="display: flex; flex-direction: column; gap: 8px">
<label for="{key}" style="font-size: 15px; font-weight: 600; color: {ON_DARK}">{label}</label>
<input id="{key}" type="number" value="{{{{{key}}}}}" onChange="{{{{set_{key}}}}}" step="any" style="height: 52px; box-sizing: border-box; padding: 0 14px; font-size: 20px; font-weight: 600; font-variant-numeric: tabular-nums; color: #FFFFFF; background: #16324A; border: 1.5px solid #5E7A92; border-radius: 2px">
<span style="font-size: 13px; color: {ON_DARK_M}">{hint}</span></div>"""
    res = lambda lab, key: f'<div style="display: flex; flex-direction: column; gap: 6px; padding: 18px 20px; background: #16324A"><span style="font-size: 14px; color: {ON_DARK_M}">{lab}</span><span style="font-size: 30px; font-weight: 800; font-stretch: 112%; color: {AMBER}; font-variant-numeric: tabular-nums">{{{{{key}}}}}</span></div>'
    table = f"""<div style="display: flex; flex-direction: column">
<div style="display: grid; grid-template-columns: 80px 1fr 1fr 1fr; padding: 10px 0; border-bottom: 1px solid #5E7A92; font-size: 14px; font-weight: 600; color: {ON_DARK_M}"><span>Die</span><span>Wire Ø mm</span><span>Reduction %</span><span>Block speed m/s</span></div>
<sc-for list="{{{{dies}}}}" as="d" hint-placeholder-count="8"><div style="display: grid; grid-template-columns: 80px 1fr 1fr 1fr; padding: 9px 0; border-bottom: 1px solid #28415A; font-size: 16px; color: #FFFFFF; font-variant-numeric: tabular-nums"><span style="color: {ON_DARK_M}">{{{{d.no}}}}</span><span style="font-weight: 600">{{{{d.dia}}}}</span><span>{{{{d.red}}}}</span><span>{{{{d.v}}}}</span></div></sc-for>
</div>"""
    parts.append(sec(1000, f"""<div style="padding-top: 88px; display: grid; grid-template-columns: 440px 1fr; gap: 72px">
<div style="display: flex; flex-direction: column; gap: 22px">
<h2 style="margin: 0; font-size: 44px; line-height: 1.08; font-weight: 800; font-stretch: 112%; color: #FFFFFF">Die sequence calculator</h2>
<p style="margin: 0; font-size: 17px; line-height: 1.6; color: {ON_DARK_M}">Enter your rod and finished sizes. The calculator spreads the reduction evenly across the dies and shows the speed each block must run at.</p>
<div style="display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 18px">
{field("Inlet rod Ø (mm)", "D", "e.g. 5.5")}{field("Finished wire Ø (mm)", "d", "e.g. 2.0")}{field("Number of dies", "n", "1 to 16")}{field("Finishing speed (m/s)", "v", "Last block")}
</div>
<sc-if value="{{{{bad}}}}" hint-placeholder-val="{{{{false}}}}"><div style="padding: 14px 16px; background: #3A2A12; color: {AMBER}; font-size: 15px; line-height: 1.5">Finished size must be smaller than the rod, with 1 to 16 dies and a speed above zero.</div></sc-if>
<p style="margin: 0; font-size: 14px; line-height: 1.55; color: {ON_DARK_M}">Typical area reduction per pass for steel wire is roughly 15 to 25 percent, depending on grade and lubrication. Send us your schedule and our engineers will check it against the machine.</p>
</div>
<div style="display: flex; flex-direction: column; gap: 24px">
<div style="display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 14px">{res("Total area reduction", "total")}{res("Reduction per pass", "per")}{res("Elongation ratio", "elong")}</div>
{table}</div></div>""", bg=INK, sid="calculator"))

    # drives & wires
    wires = ["Low carbon wire", "High carbon wire", "Spring wire", "PC wire and strand", "Bead wire", "Binding wire", "Nail wire", "Fencing and mesh wire", "GI base wire", "ACSR core wire"]
    wtags = "".join(f'<span style="display: inline-flex; align-items: center; min-height: 44px; padding: 0 18px; font-size: 16px; font-weight: 500; color: {INK}; background: #FFFFFF; border: 1px solid {RULE}">{w}</span>' for w in wires)
    ctrl = [("Drives", "An AC vector drive on every block, with regenerative options on larger lines."), ("Control", "PLC speed cascade, dancer or load-cell tension control, one HMI for the line."), ("Safety", "Guarding, interlocked doors, emergency stops along the line and wire-break detection."), ("Support", "Remote access to the PLC for diagnostics, and spares from Ghaziabad.")]
    ccells = "".join(f'<div style="display: flex; flex-direction: column; gap: 8px; border-top: 2px solid {TEAL}; padding-top: 18px"><span style="font-size: 19px; font-weight: 700; color: {INK}">{t}</span><span style="font-size: 16px; line-height: 1.55; color: {MUTED}">{d}</span></div>' for t, d in ctrl)
    parts.append(sec(760, f"""<div style="padding-top: 88px; display: flex; flex-direction: column; gap: 64px">
<div style="display: flex; flex-direction: column; gap: 28px"><h2 style="margin: 0; font-size: 44px; font-weight: 800; font-stretch: 112%; color: {INK}">Drives, controls and safety</h2>
<div style="display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 32px">{ccells}</div></div>
<div style="display: flex; flex-direction: column; gap: 20px"><h3 style="margin: 0; font-size: 26px; font-weight: 700; color: {INK}">Wire our machines draw</h3>
<div style="display: flex; flex-wrap: wrap; gap: 10px">{wtags}</div></div></div>""", bg="#FFFFFF"))

    # in-house mill
    parts.append(sec(440, f"""<div style="height: 100%; display: grid; grid-template-columns: 1fr 1fr; gap: 64px; align-items: center">
<div style="height: 300px; background: #D5DDE3; border: 1px dashed #9AAAB6; display: flex; align-items: center; justify-content: center; font-size: 15px; color: {MUTED}">[Photo: drawing line at Kay Jay Steels]</div>
<div style="display: flex; flex-direction: column; gap: 18px">
<h2 style="margin: 0; font-size: 40px; line-height: 1.1; font-weight: 800; font-stretch: 112%; color: {INK}">Built by people who draw wire every day</h2>
<p style="margin: 0; font-size: 18px; line-height: 1.6; color: {MUTED}">Our group runs its own wire drawing plant, Kay Jay Steels in Ghaziabad. [Confirm: SHIVAS machines in daily production there.] What we learn on that shop floor goes back into the next machine.</p>
{btn("About the group", "About.dc.html", "ghost")}</div></div>""", bg=ZINC))

    parts.append(sec(300, f"""<div style="height: 100%; display: flex; align-items: center; justify-content: space-between; gap: 48px">
<div style="display: flex; flex-direction: column; gap: 12px"><h2 style="margin: 0; font-size: 44px; font-weight: 800; font-stretch: 112%; color: #FFFFFF">Send us your rod and finished sizes</h2>
<p style="margin: 0; font-size: 18px; color: #E6F3F4">We reply with a machine configuration, pass schedule and offer.</p></div>
<a href="Contact.dc.html" style="display: inline-flex; align-items: center; min-height: 52px; padding: 0 26px; font-size: 16px; font-weight: 600; background: #FFFFFF; color: {TEAL_D}; border-radius: 2px">Request a machine quote</a></div>""", bg=TEAL))
    parts.append(footer())
    h = 88 + 740 + 760 + 720 + 1440 + 1000 + 760 + 440 + 300 + FOOTER_H

    script = """class Component extends DCLogic {
  constructor(...a) { super(...a); this.state = { D: '5.5', d: '2.0', n: '8', v: '15' }; }
  renderVals() {
    const st = this.state || {};
    const Ds = st.D ?? '5.5', ds = st.d ?? '2.0', ns = st.n ?? '8', vs = st.v ?? '15';
    const D = parseFloat(Ds), d = parseFloat(ds), n = parseInt(ns, 10), v = parseFloat(vs);
    const ok = D > 0 && d > 0 && d < D && n >= 1 && n <= 16 && v > 0;
    const set = (k) => (e) => this.setState({ [k]: e.target.value });
    let dies = [], total = '–', per = '–', elong = '–';
    if (ok) {
      const ratio = d / D;
      const r = 1 - Math.pow(ratio, 2 / n);
      total = ((1 - ratio * ratio) * 100).toFixed(1) + '%';
      per = (r * 100).toFixed(1) + '%';
      elong = (1 / (ratio * ratio)).toFixed(2);
      for (let i = 1; i <= n; i++) {
        const di = D * Math.pow(ratio, i / n);
        dies.push({ no: i, dia: di.toFixed(3), red: (r * 100).toFixed(1), v: (v * Math.pow(d / di, 2)).toFixed(2) });
      }
    }
    return { D: Ds, d: ds, n: ns, v: vs, set_D: set('D'), set_d: set('d'), set_n: set('n'), set_v: set('v'),
      bad: !ok, dies, total, per, elong };
  }
}"""
    return page("SHIVAS — wire drawing machines", 1440, h, "\n".join(parts), script), h
