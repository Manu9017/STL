from lib import *
from p_wire import spec_rows


def furnace_page():
    parts = [header("galv")]
    crumbs = f'<nav aria-label="Breadcrumb" style="display: flex; gap: 10px; font-size: 15px; color: {ON_DARK_M}"><a href="Main.dc.html" style="color: {ON_DARK_M}">Home</a><span>/</span><a href="Galvanizing.dc.html" style="color: {ON_DARK_M}">Galvanizing</a><span>/</span><span style="color: #FFFFFF">Pulse-fired furnaces</span></nav>'
    parts.append(sec(720, f"""<div style="padding-top: 40px; display: flex; flex-direction: column; gap: 40px">{crumbs}
<div style="display: grid; grid-template-columns: 540px 1fr; gap: 56px; align-items: center">
<div style="display: flex; flex-direction: column; gap: 22px">
<h1 style="margin: 0; font-size: 56px; line-height: 1.04; font-weight: 800; font-stretch: 125%; color: #FFFFFF">High velocity pulse-fired galvanizing furnaces</h1>
<p style="margin: 0; font-size: 19px; line-height: 1.6; color: {ON_DARK_M}">Furnaces that heat the kettle evenly along its whole length, hold the zinc at a steady temperature, and send their flue heat back into the plant.</p>
<div style="display: flex; gap: 14px">{btn("Request a furnace offer", "Contact.dc.html")}{btn("Download datasheet", "Furnace.dc.html#spec", "ghost-dark")}</div></div>
<div>{svg_pulse_plan(680)}</div></div></div>""", bg=INK))

    # how pulse firing works
    rows = []
    for i in range(6):
        segs = ""
        for c in range(4):
            x = 90 + c * 150 + i * 25
            segs += f'<rect x="{x}" y="{16 + i*34}" width="72" height="18" class="f-amber"></rect>'
        rows.append(f'<text x="0" y="{29 + i*34}" class="lbl">Burner {i+1}</text><line x1="90" y1="{25 + i*34}" x2="700" y2="{25 + i*34}" class="lt s-soft"></line>{segs}')
    timing = f'<svg viewBox="0 0 700 250" width="700" role="img" aria-label="Pulse timing: each burner fires at full rate for a short time, staggered">' + "".join(rows) + '<text x="90" y="244" class="lbl">Time</text><path d="M130 240 H690 M684 236 L690 240 L684 244" class="lt s-steel"></path></svg>'
    points = [("Full-velocity jets", "Each burner fires only at its full rate, so the gas leaves at high velocity and stirs the whole chamber. Heat reaches the kettle wall by convection, evenly."), ("Heat by time, not flame size", "Demand is met by how long each burner fires, not by turning flames down. Low demand never means lazy flames and cold ends."), ("No hot spots", "Staggered firing around the kettle keeps the wall heat flux within the kettle maker's limits, which is what decides kettle life."), ("Steady zinc", "Thermocouples in the zinc and the chamber feed the PLC, which sets the pulse timing to hold the bath at your set point.")]
    pcells = "".join(f'<div style="display: flex; flex-direction: column; gap: 8px"><span style="font-size: 19px; font-weight: 700; color: {INK}">{t}</span><span style="font-size: 16px; line-height: 1.55; color: {MUTED}">{d}</span></div>' for t, d in points)
    parts.append(sec(760, f"""<div style="padding-top: 88px; display: grid; grid-template-columns: 1fr 700px; gap: 72px">
<div style="display: flex; flex-direction: column; gap: 28px">
<h2 style="margin: 0; font-size: 44px; line-height: 1.1; font-weight: 800; font-stretch: 112%; color: {INK}">How pulse firing works</h2>
<div style="display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 28px 32px">{pcells}</div></div>
<div style="display: flex; flex-direction: column; gap: 14px; padding-top: 8px"><div style="padding: 28px; background: #FFFFFF; border: 1px solid {RULE}">{timing}</div><span style="font-size: 14px; color: {MUTED}">Illustrative timing. Actual cycle times are set during commissioning.</span></div></div>"""))

    # spec
    specs = [("Kettle sizes", "To suit your job mix, [smallest] to [largest] m"), ("Zinc bath temperature", "440 to 460 °C typical, set per client"), ("Fuel", "Natural gas, LPG, or light oil"), ("Burners", "High velocity, pulse-fired, [make to client choice]"), ("Casing", "Steel casing with ceramic fibre or refractory lining"), ("Control", "PLC with HMI, zinc and chamber thermocouples"), ("Safety", "Flame supervision, gas train with safety shut-off, zinc overtemperature trip"), ("Heat recovery", "Flue gas to dryer, degreasing and flux tanks")]
    parts.append(sec(720, f"""<div style="padding-top: 88px; display: grid; grid-template-columns: 1fr 1fr; gap: 80px">
<div style="display: flex; flex-direction: column; gap: 18px">
<h2 style="margin: 0; font-size: 44px; line-height: 1.1; font-weight: 800; font-stretch: 112%; color: {INK}">Specification</h2>
<p style="margin: 0; font-size: 17px; line-height: 1.6; color: {MUTED}">Every furnace is designed for its kettle. Send us the kettle size, target throughput and fuel, and we will size the burners, firing rate and heat recovery.</p>
{btn("Download datasheet (PDF)", "Furnace.dc.html#spec", "ghost")}</div>
<div style="display: flex; flex-direction: column">{spec_rows(specs)}</div></div>""", bg="#FFFFFF", sid="spec"))

    # retrofit + faq
    faqs = [("Can you convert our existing furnace to pulse firing?", "Often, yes. We survey the casing, lining and kettle, then quote a burner and control retrofit where the furnace is sound."), ("Will it work with our current kettle?", "We check the kettle's condition and its maker's heat flux limit first, and set the firing pattern to suit."), ("What does heat recovery save?", "It depends on your pretreatment temperatures and throughput. We calculate it for your plant in the proposal.")]
    fcells = "".join(f'<div style="display: flex; flex-direction: column; gap: 10px; padding: 24px 0; border-top: 1px solid {RULE}"><span style="font-size: 19px; font-weight: 700; color: {INK}">{q}</span><span style="font-size: 16px; line-height: 1.55; color: {MUTED}">{a}</span></div>' for q, a in faqs)
    parts.append(sec(640, f"""<div style="padding-top: 88px; display: grid; grid-template-columns: 420px 1fr; gap: 80px">
<h2 style="margin: 0; font-size: 44px; line-height: 1.1; font-weight: 800; font-stretch: 112%; color: {INK}">Questions plant owners ask</h2>
<div style="display: flex; flex-direction: column">{fcells}</div></div>""", bg=ZINC))

    rel = [("Zinc kettles", "Galvanizing.dc.html#systems"), ("Kettle enclosures", "Galvanizing.dc.html#systems"), ("Dryers and heat recovery", "Galvanizing.dc.html#systems"), ("Automation and SCADA", "Galvanizing.dc.html#automation")]
    rcells = "".join(f'<a href="{h}" style="display: flex; align-items: center; min-height: 72px; padding: 0 24px; font-size: 18px; font-weight: 600; background: #FFFFFF; border: 1px solid {RULE}; color: {INK}">{t}</a>' for t, h in rel)
    parts.append(sec(300, f"""<div style="padding-top: 72px; display: flex; flex-direction: column; gap: 28px"><h2 style="margin: 0; font-size: 30px; font-weight: 800; font-stretch: 112%; color: {INK}">Works with</h2>
<div style="display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 16px">{rcells}</div></div>"""))
    parts.append(footer())
    h = 88 + 720 + 760 + 720 + 640 + 300 + FOOTER_H
    return page("SHIVAS — pulse-fired galvanizing furnaces", 1440, h, "\n".join(parts)), h


def about_page():
    parts = [header("about")]
    parts.append(sec(560, f"""<div style="height: 100%; display: grid; grid-template-columns: 1fr 1fr; gap: 72px; align-items: center">
<div style="display: flex; flex-direction: column; gap: 22px">
<h1 style="margin: 0; font-size: 56px; line-height: 1.04; font-weight: 800; font-stretch: 125%; color: {INK}">An engineering company from Ghaziabad</h1>
<p style="margin: 0; font-size: 19px; line-height: 1.6; color: {MUTED}">SHIVAS Technology Limited designs and builds wire drawing machinery and hot dip galvanizing plants. The company is run by engineers and led by Krishan Verma, B.Sc. Engg. and M.S. from BITS Pilani. [Year founded], [number of employees], [plants and machines supplied].</p></div>
<div style="height: 400px; background: {ZINC}; border: 1px dashed #9AAAB6; display: flex; align-items: center; justify-content: center; font-size: 15px; color: {MUTED}">[Photo: works in Ghaziabad, aerial or shop floor]</div></div>""", bg="#FFFFFF"))

    team = [("Krishan Verma", "Managing Director [confirm title]", "B.Sc. Engg., M.S., BITS Pilani"), ("Jayant Singh Verma", "Director", "Combustion, process metallurgy and automation"), ("[Name]", "[Head of design]", "[Background]"), ("[Name]", "[Head of projects]", "[Background]")]
    tcells = "".join(f'<div style="display: flex; flex-direction: column; gap: 12px"><div style="height: 220px; background: {ZINC}; border: 1px dashed #9AAAB6; display: flex; align-items: center; justify-content: center; font-size: 14px; color: {MUTED}">[Portrait]</div><span style="font-size: 20px; font-weight: 700; color: {INK}">{n}</span><span style="font-size: 16px; color: {TEXT}">{r}</span><span style="font-size: 15px; color: {MUTED}">{b}</span></div>' for n, r, b in team)
    parts.append(sec(620, f"""<div style="padding-top: 88px; display: flex; flex-direction: column; gap: 36px"><h2 style="margin: 0; font-size: 44px; font-weight: 800; font-stretch: 112%; color: {INK}">Leadership</h2>
<div style="display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 24px">{tcells}</div></div>"""))

    caps = [("Design office", "Process, mechanical, combustion and electrical engineering, 2D and 3D design."), ("Fabrication", "Kettles, furnace casings, machine frames and steel structures."), ("Thermoplastics and FRP", "PP-H tanks, ducting and scrubbers, with SHIVAS Reinplast."), ("Machining and assembly", "Capstans, gearboxes and die boxes, assembled and aligned in-house."), ("Panel shop", "Drive panels, PLC panels and burner management panels."), ("Site teams", "Erection, commissioning and service engineers.")]
    ccells = "".join(f'<div style="display: flex; flex-direction: column; gap: 8px; border-top: 2px solid {AMBER}; padding-top: 18px"><span style="font-size: 19px; font-weight: 700; color: #FFFFFF">{t}</span><span style="font-size: 16px; line-height: 1.55; color: {ON_DARK_M}">{d}</span></div>' for t, d in caps)
    parts.append(sec(560, f"""<div style="padding-top: 88px; display: flex; flex-direction: column; gap: 40px"><h2 style="margin: 0; font-size: 44px; font-weight: 800; font-stretch: 112%; color: #FFFFFF">What happens under our roof</h2>
<div style="display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 40px 48px">{ccells}</div></div>""", bg=INK))

    group = [("SHIVAS Technology Limited", "Wire drawing machinery and hot dip galvanizing plants.", "shivastechnology.com", "Main.dc.html", True),
             ("SHIVAS Reinplast", "PP and FRP process equipment, fume scrubbers, pickling plants and blowers.", "shivasasia.com", "https://shivasasia.com", False),
             ("PP tanks", "Polypropylene tanks and pickling tanks.", "pptanks.com", "https://pptanks.com", False),
             ("Pickling plants", "Pickling for wire, pipe, strip and structures.", "pickling-plants.com", "https://pickling-plants.com", False),
             ("FRP blowers", "FRP and PP centrifugal blowers.", "frpblower.com", "https://frpblower.com", False),
             ("Kay Jay Steels", "Wire drawing plant, Ghaziabad.", "[website]", "About.dc.html", False)]
    gcells = "".join(f'<a href="{h}" style="display: flex; flex-direction: column; gap: 10px; padding: 26px; min-height: 170px; box-sizing: border-box; background: {INK if me else "#FFFFFF"}; border: 1px solid {INK if me else RULE}"><span style="font-size: 20px; font-weight: 700; color: {"#FFFFFF" if me else INK}">{n}</span><span style="font-size: 16px; line-height: 1.5; color: {ON_DARK_M if me else MUTED}">{d}</span><span style="margin-top: auto; font-size: 15px; font-weight: 600; color: {AMBER if me else TEAL_D}">{l}</span></a>' for n, d, l, h, me in group)
    parts.append(sec(720, f"""<div style="padding-top: 88px; display: flex; flex-direction: column; gap: 36px"><div style="display: flex; flex-direction: column; gap: 12px"><h2 style="margin: 0; font-size: 44px; font-weight: 800; font-stretch: 112%; color: {INK}">The SHIVAS group</h2>
<p style="margin: 0; max-width: 760px; font-size: 18px; line-height: 1.55; color: {MUTED}">Each company has its own specialism and its own site. Together they cover a galvanizing or wire plant end to end.</p></div>
<div style="display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 20px">{gcells}</div></div>""", bg=ZINC))

    stds = [("Galvanized coatings", "IS 2629, IS 4759, ISO 1461, ASTM A123"), ("Thermoplastic tanks", "DVS 2205 design, DVS 2207 welding"), ("Furnaces and burners", "[Standards followed, e.g. EN 746-2]"), ("Machinery", "[CE marking for export machines, if held]"), ("Quality system", "[ISO 9001 certificate number, if held]")]
    parts.append(sec(560, f"""<div style="padding-top: 88px; display: grid; grid-template-columns: 420px 1fr; gap: 80px" id="projects">
<div style="display: flex; flex-direction: column; gap: 16px"><h2 style="margin: 0; font-size: 44px; line-height: 1.1; font-weight: 800; font-stretch: 112%; color: {INK}">Standards we design to</h2>
<p style="margin: 0; font-size: 17px; line-height: 1.6; color: {MUTED}">Items in brackets are shown only once certificates are confirmed.</p></div>
<div style="display: flex; flex-direction: column">{spec_rows(stds)}</div></div>""", bg="#FFFFFF"))
    parts.append(footer())
    h = 88 + 560 + 620 + 560 + 720 + 560 + FOOTER_H
    return page("SHIVAS — company and group", 1440, h, "\n".join(parts)), h


def contact_page():
    parts = [header("contact")]

    def inp(label, key, typ="text", auto=""):
        a = f' autocomplete="{auto}"' if auto else ""
        return f'<div style="display: flex; flex-direction: column; gap: 8px"><label for="{key}" style="font-size: 15px; font-weight: 600; color: {TEXT}">{label}</label><input id="{key}" type="{typ}"{a} style="height: 52px; box-sizing: border-box; padding: 0 14px; font-size: 17px; color: {TEXT}; background: #FFFFFF; border: 1.5px solid #8FA3B3; border-radius: 2px"></div>'

    def sel(label, key, opts):
        o = "".join(f"<option>{x}</option>" for x in opts)
        return f'<div style="display: flex; flex-direction: column; gap: 8px"><label for="{key}" style="font-size: 15px; font-weight: 600; color: {TEXT}">{label}</label><select id="{key}" style="height: 52px; box-sizing: border-box; padding: 0 12px; font-size: 17px; color: {TEXT}; background: #FFFFFF; border: 1.5px solid #8FA3B3; border-radius: 2px">{o}</select></div>'

    galv_fields = f"""<div style="display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 20px">
{sel("What will you galvanize?", "g-mat", ["Structures and towers", "Pipes and tubes", "Crash barriers", "Fasteners and small parts", "Wire", "Mixed jobbing work"])}
{sel("What do you need?", "g-scope", ["Complete turnkey plant", "Kettle and furnace", "Pretreatment line or enclosed room", "Fume extraction", "ETP or ZLD", "Upgrade of an existing plant"])}
{inp("Largest job, L × W × H (m)", "g-size")}
{inp("Throughput (tonnes per month)", "g-tpm", "number")}
{sel("Fuel available", "g-fuel", ["Natural gas", "LPG", "Light oil", "Not decided"])}
{inp("Site location", "g-site")}</div>"""
    wire_fields = f"""<div style="display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 20px">
{sel("Machine type", "w-type", ["Straight line", "OTO type", "Inverted vertical", "Complete line", "Not sure, advise me"])}
{sel("Wire grade", "w-grade", ["Low carbon", "High carbon", "Spring or PC wire", "Stainless", "Other"])}
{inp("Inlet rod Ø (mm)", "w-in", "number")}
{inp("Finished wire Ø (mm)", "w-out", "number")}
{inp("Output needed (tonnes per day)", "w-tpd", "number")}
{sel("Take-up", "w-take", ["Dead block coiler", "Spooler", "Inverted vertical coil", "Not sure"])}</div>"""

    tab = lambda label, key, on: f'<button type="button" onClick="{{{{{key}}}}}" aria-pressed="{{{{{on}}}}}" style="min-height: 52px; padding: 0 24px; border: 0; font-family: {FONT}; font-size: 16px; font-weight: 600; cursor: pointer; background: {{{{{on}Bg}}}}; color: {{{{{on}Fg}}}}">{label}</button>'
    form = f"""<div style="display: flex; flex-direction: column; gap: 28px">
<sc-if value="{{{{sent}}}}" hint-placeholder-val="{{{{false}}}}"><div role="status" style="padding: 28px; background: {INK}; color: #FFFFFF; display: flex; flex-direction: column; gap: 8px"><span style="font-size: 24px; font-weight: 700">Enquiry sent</span><span style="font-size: 17px; color: {ON_DARK_M}">An engineer from the {{{{divName}}}} division will reply within [one working day]. A copy has gone to your email.</span></div></sc-if>
<div style="display: flex; gap: 0; box-shadow: inset 0 0 0 1.5px {INK}; align-self: flex-start">{tab("Hot dip galvanizing", "pickG", "g")}{tab("Wire drawing", "pickW", "w")}</div>
<sc-if value="{{{{isG}}}}" hint-placeholder-val="{{{{true}}}}">{galv_fields}</sc-if>
<sc-if value="{{{{isW}}}}" hint-placeholder-val="{{{{false}}}}">{wire_fields}</sc-if>
<div style="height: 1px; background: {RULE}"></div>
<div style="display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 20px">
{inp("Your name", "c-name", "text", "name")}{inp("Company", "c-co", "text", "organization")}
{inp("Email", "c-mail", "email", "email")}{inp("Phone or WhatsApp", "c-tel", "tel", "tel")}
{inp("Country", "c-country", "text", "country-name")}
<div style="display: flex; flex-direction: column; gap: 8px"><label for="c-file" style="font-size: 15px; font-weight: 600; color: {TEXT}">Drawings or layout (optional)</label><input id="c-file" type="file" style="height: 52px; box-sizing: border-box; padding: 12px; font-size: 15px; color: {TEXT}; background: #FFFFFF; border: 1.5px dashed #8FA3B3"></div></div>
<div style="display: flex; flex-direction: column; gap: 8px"><label for="c-msg" style="font-size: 15px; font-weight: 600; color: {TEXT}">Anything else we should know</label><textarea id="c-msg" rows="4" style="box-sizing: border-box; padding: 14px; font-size: 17px; color: {TEXT}; background: #FFFFFF; border: 1.5px solid #8FA3B3; border-radius: 2px; resize: vertical"></textarea></div>
<div style="display: flex; align-items: center; gap: 20px"><button type="button" onClick="{{{{send}}}}" style="min-height: 56px; padding: 0 32px; border: 0; border-radius: 2px; background: {AMBER}; color: {INK}; font-family: {FONT}; font-size: 17px; font-weight: 700; cursor: pointer">Send enquiry</button><span style="font-size: 14px; color: {MUTED}">We use your details only to answer this enquiry. See our privacy policy.</span></div>
</div>"""
    side = f"""<div style="display: flex; flex-direction: column; gap: 28px; padding: 36px; background: {INK}; color: {ON_DARK}">
<span style="font-size: 24px; font-weight: 700; color: #FFFFFF">Talk to an engineer</span>
<div style="display: flex; flex-direction: column; gap: 6px"><span style="font-size: 14px; color: {ON_DARK_M}">Phone and WhatsApp</span><a href="tel:+919810280104" style="font-size: 22px; font-weight: 700; color: #FFFFFF">+91 98102 80104</a></div>
<div style="display: flex; flex-direction: column; gap: 6px"><span style="font-size: 14px; color: {ON_DARK_M}">Email</span><a href="mailto:info@shivastechnology.com" style="font-size: 18px; font-weight: 600; color: {AMBER}">info@shivastechnology.com</a></div>
<div style="display: flex; flex-direction: column; gap: 6px"><span style="font-size: 14px; color: {ON_DARK_M}">Works and office</span><span style="font-size: 17px; line-height: 1.55">A-1/270, Swadeshi Compound<br>Kavi Nagar Industrial Area<br>Ghaziabad, Uttar Pradesh 201002<br>India</span></div>
<div style="display: flex; flex-direction: column; gap: 6px"><span style="font-size: 14px; color: {ON_DARK_M}">Hours</span><span style="font-size: 17px">[Monday to Saturday, 9:30 to 18:30 IST]</span></div>
<a href="https://wa.me/919810280104" style="display: flex; align-items: center; justify-content: center; min-height: 52px; font-size: 16px; font-weight: 600; background: {AMBER}; color: {INK}; border-radius: 2px">Message us on WhatsApp</a>
<div style="height: 200px; background: #16324A; display: flex; align-items: center; justify-content: center; font-size: 14px; color: {ON_DARK_M}">[Map: Kavi Nagar Industrial Area]</div></div>"""
    parts.append(sec(1340, f"""<div style="padding-top: 72px; display: flex; flex-direction: column; gap: 40px">
<div style="display: flex; flex-direction: column; gap: 12px"><h1 style="margin: 0; font-size: 56px; font-weight: 800; font-stretch: 125%; color: {INK}">Request a quote</h1>
<p style="margin: 0; max-width: 760px; font-size: 19px; line-height: 1.55; color: {MUTED}">The more you tell us, the more exact our first offer. Choose a division and fill in what you know.</p></div>
<div style="display: grid; grid-template-columns: 1fr 440px; gap: 64px; align-items: start">{form}{side}</div></div>"""))
    parts.append(footer())
    h = 88 + 1340 + FOOTER_H
    script = """class Component extends DCLogic {
  constructor(...a) { super(...a); this.state = { div: 'g', sent: false }; }
  renderVals() {
    const st = this.state || {};
    const g = (st.div ?? 'g') === 'g';
    return {
      isG: g, isW: !g,
      g: g ? 'true' : 'false', w: g ? 'false' : 'true',
      gBg: g ? '#102638' : 'transparent', gFg: g ? '#FFFFFF' : '#102638',
      wBg: g ? 'transparent' : '#102638', wFg: g ? '#102638' : '#FFFFFF',
      pickG: () => this.setState({ div: 'g', sent: false }),
      pickW: () => this.setState({ div: 'w', sent: false }),
      sent: !!st.sent,
      divName: g ? 'galvanizing' : 'wire drawing',
      send: () => this.setState({ sent: true })
    };
  }
}"""
    return page("SHIVAS — request a quote", 1440, h, "\n".join(parts), script), h
