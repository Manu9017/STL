from lib import *
import json

STAGES = [
    ("degrease", "Degreasing", 96, "#6E8FA8", "Removes oil, grease and drawing lubricants so the acid can reach the steel. Usually a heated alkaline or acid degreaser, warmed with heat recovered from the furnace flue.", ["PP-H or FRP tank with steel support structure", "Flue-gas heat exchanger or immersion heating", "Oil skimming and sludge removal"]),
    ("rinse1", "Rinse", 60, "#9FB6C7", "Stops degreaser carrying over and weakening the pickling acid.", ["PP-H rinse tank", "Cascade overflow to save water"]),
    ("pickle", "Pickling", 132, "#1F4E79", "Hydrochloric acid removes mill scale and rust. Several tanks at staged strengths let the plant use acid down to its useful limit before it goes to treatment.", ["Multiple PP-H or FRP pickling tanks", "Lateral extraction or a fully enclosed room", "Acid storage, dosing and transfer"]),
    ("rinse2", "Rinse", 60, "#9FB6C7", "Keeps acid and dissolved iron out of the flux. Iron carried into the flux ends up as dross and ash in the kettle.", ["PP-H rinse tanks, single or double", "Rinse water routed to the ETP"]),
    ("flux", "Fluxing", 96, "#0E7C86", "A heated zinc ammonium chloride flux cleans the last oxide and protects the steel until it reaches the zinc. Flux kept low in iron means less dross and lower zinc consumption.", ["Heated flux tank", "Continuous flux filtration and iron removal", "Density, pH and temperature monitoring"]),
    ("dry", "Drying", 76, "#B98A3E", "Hot air dries the flux film and preheats the work, so it enters the zinc dry and warm. Less splashing, less ash, faster dipping.", ["Drying pit or tunnel", "Hot air from furnace flue gas", "Temperature control"]),
    ("zinc", "Galvanizing", 150, "#E3A23B", "The steel is dipped in molten zinc at 440 to 460 °C. Zinc and iron react to form the alloy layers of the coating. Immersion and withdrawal speed decide coating thickness and finish.", ["Zinc kettle in a high velocity pulse-fired furnace", "Kettle enclosure with white fume extraction to a bag filter", "Dross grab, zinc skimming and ash handling"]),
    ("quench", "Quenching", 66, "#6E8FA8", "Cooling stops the zinc-iron reaction, fixes the coating and makes the work safe to handle.", ["Quench tank with cooling", "Water reuse through the ETP"]),
    ("passivate", "Passivation", 66, "#8499AB", "A chromium-free passivation film protects fresh zinc against white rust in storage and transport.", ["PP-H passivation tank", "Dosing and bath control"]),
]


def galv_page():
    parts = [header("galv")]
    # hero
    parts.append(sec(760, f"""<div style="height: 100%; display: grid; grid-template-columns: 540px 1fr; gap: 40px; align-items: center">
<div style="display: flex; flex-direction: column; gap: 24px">
<span style="font-size: 17px; font-weight: 600; color: {AMBER}">Hot dip galvanizing division</span>
<h1 style="margin: 0; font-size: 62px; line-height: 1.03; font-weight: 800; font-stretch: 125%; letter-spacing: -0.01em; color: #FFFFFF">Turnkey hot dip galvanizing plants</h1>
<p style="margin: 0; font-size: 19px; line-height: 1.6; color: {ON_DARK_M}">We design, build and commission complete galvanizing plants, and supply any part of one. Zinc kettles, pulse-fired furnaces, PP and FRP process lines, enclosed rooms, fume extraction, effluent treatment and the automation that runs it all.</p>
<div style="display: flex; gap: 14px">{btn("Request a plant proposal", "Contact.dc.html")}{btn("Explore the process", "#process", "ghost-dark")}</div>
</div>
<div style="display: flex; justify-content: flex-end">{svg_kettle_scene(760)}</div></div>""", bg=INK))

    # delivery sequence
    steps = ["Feasibility and layout", "Process design", "Detail engineering", "Manufacturing", "Erection", "Commissioning and training", "Service and spares"]
    stepcells = "".join(f'<div style="display: flex; flex-direction: column; gap: 10px; padding-top: 18px; border-top: 2px solid {AMBER if i == 0 else "#5E7A92"}"><span style="font-size: 14px; font-weight: 600; color: {AMBER}; font-variant-numeric: tabular-nums">{i+1:02d}</span><span style="font-size: 17px; font-weight: 600; line-height: 1.3; color: #FFFFFF">{s}</span></div>' for i, s in enumerate(steps))
    parts.append(sec(230, f"""<div style="padding-top: 40px; display: flex; flex-direction: column; gap: 22px">
<h2 style="margin: 0; font-size: 22px; font-weight: 700; color: {ON_DARK}">One contract from layout to first dip</h2>
<div style="display: grid; grid-template-columns: repeat(7, minmax(0, 1fr)); gap: 20px">{stepcells}</div></div>""", bg="#16324A"))

    # process explorer
    tankrow = f"""<div style="display: flex; align-items: flex-end; gap: 8px; height: 200px; border-bottom: 3px solid {INK}; padding-bottom: 0">
<sc-for list="{{{{stages}}}}" as="s" hint-placeholder-count="9">
<button type="button" onClick="{{{{s.pick}}}}" aria-pressed="{{{{s.on}}}}" style="flex: {{{{s.flex}}}}; height: {{{{s.h}}}}px; border: 0; border-radius: 2px 2px 0 0; background: {{{{s.bg}}}}; box-shadow: {{{{s.ring}}}}; color: #FFFFFF; font-family: {FONT}; font-size: 14px; font-weight: 600; cursor: pointer; display: flex; align-items: flex-end; justify-content: center; padding: 0 4px 12px; opacity: {{{{s.op}}}}">{{{{s.label}}}}</button>
</sc-for></div>"""
    panel = f"""<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 56px; padding-top: 36px">
<div style="display: flex; flex-direction: column; gap: 14px">
<span style="font-size: 15px; font-weight: 600; color: {MUTED}; font-variant-numeric: tabular-nums">Stage {{{{cur.no}}}} of 9</span>
<h3 style="margin: 0; font-size: 36px; font-weight: 800; font-stretch: 112%; color: {INK}">{{{{cur.label}}}}</h3>
<p style="margin: 0; font-size: 18px; line-height: 1.6; color: {TEXT}">{{{{cur.text}}}}</p>
<div style="display: flex; gap: 12px; margin-top: 8px"><button type="button" onClick="{{{{prev}}}}" style="min-height: 48px; padding: 0 20px; border: 0; box-shadow: inset 0 0 0 1.5px {INK}; background: transparent; font-family: {FONT}; font-size: 15px; font-weight: 600; color: {INK}; cursor: pointer">Previous stage</button><button type="button" onClick="{{{{next}}}}" style="min-height: 48px; padding: 0 20px; border: 0; background: {INK}; font-family: {FONT}; font-size: 15px; font-weight: 600; color: #FFFFFF; cursor: pointer">Next stage</button></div>
</div>
<div style="display: flex; flex-direction: column; gap: 12px; padding: 28px 32px; background: #FFFFFF; border: 1px solid {RULE}">
<span style="font-size: 17px; font-weight: 700; color: {INK}">What SHIVAS supplies for this stage</span>
<sc-for list="{{{{cur.items}}}}" as="it" hint-placeholder-count="3"><div style="display: flex; gap: 12px; align-items: baseline; font-size: 17px; line-height: 1.5; color: {TEXT}"><span style="width: 8px; height: 8px; flex-shrink: 0; background: {AMBER}; transform: translateY(-2px)"></span><span>{{{{it}}}}</span></div></sc-for>
</div></div>"""
    parts.append(sec(820, f"""<div style="padding-top: 88px; display: flex; flex-direction: column; gap: 16px">
<h2 style="margin: 0; font-size: 44px; font-weight: 800; font-stretch: 112%; color: {INK}">Walk the line, tank by tank</h2>
<p style="margin: 0 0 32px; max-width: 760px; font-size: 18px; line-height: 1.55; color: {MUTED}">Select a stage to see what it does and what we build for it. The same crane carries the work from degreasing to passivation.</p>
<svg viewBox="0 0 1280 30" width="1280" height="30" aria-hidden="true"><rect x="0" y="4" width="1280" height="6" class="f-steel"></rect><rect x="{{{{craneX}}}}" y="0" width="60" height="14" class="f-amber"></rect><line x1="{{{{craneC}}}}" y1="14" x2="{{{{craneC}}}}" y2="30" class="ln s-steel"></line></svg>
{tankrow}{panel}</div>""", sid="process"))

    # systems grid
    ic = icons_galv()
    systems = [
        ("kettle", "Zinc kettles", "Kettles fabricated from low-carbon, low-silicon kettle steel, sized to your longest and deepest job with room for dross and handling.", "Galvanizing.dc.html#systems"),
        ("furnace", "High velocity pulse-fired furnaces", "Burners fire at full velocity and pulse on and off, spreading heat evenly along the kettle wall. Gas or oil fired.", "Furnace.dc.html"),
        ("enclosure", "Kettle enclosures", "Fixed or moving enclosures around the kettle that contain white fume at the source and keep the working area clear.", "Galvanizing.dc.html#air-water"),
        ("room", "Enclosed process rooms", "The whole pretreatment line inside one sealed, extracted room, so acid fume never reaches the rest of the plant or the crane.", "Galvanizing.dc.html#air-water"),
        ("tanks", "PP and FRP process tanks", "PP-H and FRP tanks for degreasing, pickling, rinsing, fluxing and passivation, with steel support structures, designed to DVS guidelines.", "https://pptanks.com"),
        ("flux", "Flux filtration and regeneration", "Continuous removal of iron from the flux bath through oxidation, precipitation and filtration. Clean flux means less dross and ash.", "Galvanizing.dc.html#systems"),
        ("whitefume", "Zinc white fume extraction", "Captures the fume released when fluxed steel enters the zinc, and collects it in a pulse-jet bag filter before the stack.", "Galvanizing.dc.html#air-water"),
        ("scrubber", "Acid fume extraction", "Hoods or room extraction, PP and FRP ducting, a packed-bed wet scrubber, FRP blower and chimney, sized as one system.", "Galvanizing.dc.html#air-water"),
        ("etp", "ETP and ZLD systems", "Treatment of spent acid and rinse water through neutralisation, clarification and filtration, with RO and evaporation for zero liquid discharge.", "Galvanizing.dc.html#air-water"),
        ("dryer", "Dryers and heat recovery", "Drying pits and tunnels heated by furnace flue gas, which also warms the degreasing and flux tanks.", "Furnace.dc.html"),
        ("crane", "Cranes and material handling", "EOT cranes, transfer cars, jigs and handling equipment laid out for your job mix and throughput.", "Galvanizing.dc.html#automation"),
        ("plc", "Automation and SCADA", "PLC control of furnace, tanks and cranes, with recipes, alarms, energy and zinc reporting on one SCADA screen.", "Galvanizing.dc.html#automation"),
    ]
    cards = "".join(f"""<a href="{href}" style="display: flex; flex-direction: column; gap: 12px; padding: 24px 24px 28px; background: #FFFFFF; border: 1px solid {RULE}; color: {TEXT}">
<div style="background: {PAPER}; padding: 10px 0">{ic[k]}</div>
<span style="font-size: 20px; font-weight: 700; color: {INK}">{t}</span>
<span style="font-size: 16px; line-height: 1.55; color: {MUTED}">{d}</span></a>""" for k, t, d, href in systems)
    parts.append(sec(1560, f"""<div style="padding-top: 96px; display: flex; flex-direction: column; gap: 40px">
<div style="display: flex; justify-content: space-between; align-items: flex-end; gap: 48px"><h2 style="margin: 0; max-width: 760px; font-size: 44px; line-height: 1.1; font-weight: 800; font-stretch: 112%; color: {INK}">Every system in the plant, from one supplier</h2>
<p style="margin: 0; max-width: 420px; font-size: 17px; line-height: 1.55; color: {MUTED}">Buy the complete plant, or one system to upgrade an existing line.</p></div>
<div style="display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 20px">{cards}</div></div>""", bg=ZINC, sid="systems"))

    # furnace spotlight
    parts.append(sec(720, f"""<div style="height: 100%; display: grid; grid-template-columns: 1fr 620px; gap: 64px; align-items: center">
<div style="display: flex; flex-direction: column; gap: 22px">
<span style="font-size: 17px; font-weight: 600; color: {AMBER}">Where the energy goes</span>
<h2 style="margin: 0; font-size: 48px; line-height: 1.06; font-weight: 800; font-stretch: 118%; color: #FFFFFF">The furnace decides your fuel bill and your kettle life</h2>
<p style="margin: 0; font-size: 18px; line-height: 1.6; color: {ON_DARK_M}">Most of a galvanizing plant's energy is burned around the kettle. Our high velocity burners fire in timed pulses, so heat is spread along the wall instead of concentrated in hot spots. That protects the kettle, holds the zinc temperature steady, and sends usable flue heat to the dryer and pretreatment tanks.</p>
<div style="display: flex; gap: 14px">{btn("How pulse firing works", "Furnace.dc.html")}</div></div>
<div>{svg_pulse_plan(620)}</div></div>""", bg=INK))

    # air and water
    flow = ["Spent acid and rinse water", "Neutralisation", "Clarifier", "Filter press", "Two-stage RO", "Evaporator (MEE or MVR)", "Water back to process"]
    arrow = '<svg viewBox="0 0 24 24" width="24" height="24" aria-hidden="true"><path d="M4 12 H19 M14 7 L19 12 L14 17" class="ln s-teal"></path></svg>'
    flowcells = arrow.join(f'<div style="flex: 1; min-height: 88px; display: flex; align-items: center; justify-content: center; text-align: center; padding: 0 10px; font-size: 16px; font-weight: 600; line-height: 1.3; background: {"#FFFFFF" if i not in (0, 6) else INK}; color: {INK if i not in (0, 6) else "#FFFFFF"}; border: 1px solid {RULE}">{s}</div>' for i, s in enumerate(flow))
    parts.append(sec(940, f"""<div style="padding-top: 96px; display: flex; flex-direction: column; gap: 56px">
<div style="display: grid; grid-template-columns: 480px 1fr; gap: 64px; align-items: center">
<div style="display: flex; flex-direction: column; gap: 18px">
<h2 style="margin: 0; font-size: 44px; line-height: 1.1; font-weight: 800; font-stretch: 112%; color: {INK}">Clean air and water, designed in from the start</h2>
<p style="margin: 0; font-size: 18px; line-height: 1.6; color: {MUTED}">Acid fume is drawn from the pretreatment room through PP and FRP ducting to a packed-bed scrubber, then out through an FRP blower and stack. Zinc white fume from the kettle goes to a pulse-jet bag filter. Both are sized with the plant, not added later.</p>
</div>
<div style="display: flex; justify-content: flex-end">{svg_acid_fume(700)}</div></div>
<div style="display: flex; flex-direction: column; gap: 18px">
<h3 style="margin: 0; font-size: 26px; font-weight: 700; color: {INK}">Effluent treatment through to zero liquid discharge</h3>
<div style="display: flex; align-items: center; gap: 8px">{flowcells}</div>
<p style="margin: 0; font-size: 16px; line-height: 1.55; color: {MUTED}">Configured to your effluent volumes and your pollution control board's conditions. We supply the ETP alone or the complete ZLD system.</p></div></div>""", sid="air-water"))

    # automation
    feats = [("Recipe dipping", "Immersion and withdrawal times per job type, run by the crane control."), ("Bath control", "Temperature, level and concentration for every tank, with alarms."), ("Furnace control", "Zinc and chamber temperature, burner pulse timing and flue monitoring."), ("Plant reporting", "Zinc, fuel and acid use per tonne, shift by shift.")]
    fcells = "".join(f'<div style="display: flex; flex-direction: column; gap: 10px; border-top: 2px solid {TEAL}; padding-top: 20px"><span style="font-size: 20px; font-weight: 700; color: {INK}">{t}</span><span style="font-size: 16px; line-height: 1.55; color: {MUTED}">{d}</span></div>' for t, d in feats)
    parts.append(sec(560, f"""<div style="padding-top: 88px; display: flex; flex-direction: column; gap: 40px">
<div style="display: flex; flex-direction: column; gap: 14px"><h2 style="margin: 0; font-size: 44px; font-weight: 800; font-stretch: 112%; color: {INK}">Fully automatic, if you want it</h2>
<p style="margin: 0; max-width: 780px; font-size: 18px; line-height: 1.55; color: {MUTED}">From manual lines with PLC-controlled furnaces to plants where cranes, tanks and kettle run on programmed cycles. Every level is built on the same controls, so a plant can grow into full automation.</p></div>
<div style="display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 32px">{fcells}</div></div>""", bg="#FFFFFF", sid="automation"))

    # knowledge
    arts = [("How pulse firing protects a zinc kettle", "Furnace"), ("Why iron in flux raises your zinc consumption", "Flux"), ("Coating too thick? Where the extra zinc comes from", "Coating"), ("Sizing a kettle from your job mix", "Kettles"), ("Enclosed rooms versus open pickling lines", "Pretreatment"), ("What ZLD means for a galvanizer", "Effluent")]
    acells = "".join(f'<a href="Galvanizing.dc.html#knowledge" style="display: flex; flex-direction: column; justify-content: space-between; gap: 18px; min-height: 150px; padding: 24px; background: #16324A; color: #FFFFFF"><span style="font-size: 14px; font-weight: 600; color: {AMBER}">{c}</span><span style="font-size: 20px; line-height: 1.3; font-weight: 700">{t}</span></a>' for t, c in arts)
    parts.append(sec(640, f"""<div style="padding-top: 88px; display: flex; flex-direction: column; gap: 36px">
<div style="display: flex; justify-content: space-between; align-items: flex-end"><div style="display: flex; flex-direction: column; gap: 12px"><h2 style="margin: 0; font-size: 44px; font-weight: 800; font-stretch: 112%; color: #FFFFFF">Galvanizing knowledge</h2>
<p style="margin: 0; max-width: 700px; font-size: 18px; line-height: 1.55; color: {ON_DARK_M}">Practical guides from the engineers who design these plants. Written for plant owners and operators.</p></div>{btn("All guides", "Galvanizing.dc.html#knowledge", "ghost-dark")}</div>
<div style="display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 20px">{acells}</div></div>""", bg=INK, sid="knowledge"))

    # CTA
    parts.append(sec(300, f"""<div style="height: 100%; display: flex; align-items: center; justify-content: space-between; gap: 48px">
<div style="display: flex; flex-direction: column; gap: 12px"><h2 style="margin: 0; font-size: 44px; font-weight: 800; font-stretch: 112%; color: {INK}">Planning a new plant or an upgrade?</h2>
<p style="margin: 0; font-size: 18px; color: {TEXT}">Send your largest job size and monthly tonnage. We reply with a layout and a budgetary offer.</p></div>
{btn("Request a plant proposal", "Contact.dc.html", "ghost")}</div>""", bg=AMBER))
    parts.append(footer())

    h = 88 + 760 + 230 + 820 + 1560 + 720 + 940 + 560 + 640 + 300 + FOOTER_H

    stages_js = json.dumps([{"id": s[0], "label": s[1], "w": s[2], "bg": s[3], "text": s[4], "items": s[5]} for s in STAGES])
    script = f"""class Component extends DCLogic {{
  constructor(...a) {{ super(...a); this.state = {{ sel: 6 }}; }}
  renderVals() {{
    const S = {stages_js};
    const sel = (this.state && this.state.sel != null) ? this.state.sel : 6;
    const total = S.reduce((t, s) => t + s.w, 0);
    let acc = 0, cx = 0;
    const stages = S.map((s, i) => {{
      const mid = (acc + s.w / 2) / total * 1280; acc += s.w;
      if (i === sel) cx = mid;
      return {{
        label: s.label, flex: s.w, bg: s.bg,
        h: i === sel ? 190 : 150,
        on: i === sel ? 'true' : 'false',
        op: i === sel ? 1 : 0.78,
        ring: i === sel ? 'inset 0 0 0 3px #102638' : 'none',
        pick: () => this.setState({{ sel: i }})
      }};
    }});
    const c = S[sel];
    return {{
      stages,
      cur: {{ no: sel + 1, label: c.label, text: c.text, items: c.items }},
      craneX: Math.max(0, Math.min(1220, cx - 30)),
      craneC: cx,
      prev: () => this.setState({{ sel: (sel + 8) % 9 }}),
      next: () => this.setState({{ sel: (sel + 1) % 9 }})
    }};
  }}
}}"""
    return page("SHIVAS — hot dip galvanizing plants", 1440, h, "\n".join(parts), script), h
