# Shared pieces for the SHIVAS website artboards
INK = "#102638"      # navy steel (dark ground)
BLUE = "#1F4E79"     # SHIVAS blue
TEAL = "#0E7C86"     # wire division
TEAL_D = "#0A5C63"
AMBER = "#E3A23B"    # molten zinc / galvanizing division
AMBER_D = "#8A5A12"
ZINC = "#E7ECEF"     # zinc light ground
PAPER = "#F6F8F9"
RULE = "#CFD8DE"
TEXT = "#1B2B39"
MUTED = "#4A5B6A"
ON_DARK = "#E9EEF2"
ON_DARK_M = "#A9B8C5"

FONT = "'Archivo', 'Helvetica Neue', system-ui, sans-serif"

HELMET = """<helmet>
<link href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@62..125,100..900&amp;display=swap" rel="stylesheet">
<style>
body{margin:0;background:#F6F8F9}
a{color:#0E7C86;text-decoration:none}a:hover{color:#0A5C63}
a:focus-visible,button:focus-visible,input:focus-visible,select:focus-visible,textarea:focus-visible{outline:3px solid #E3A23B;outline-offset:3px}
.ln{fill:none;stroke-width:1.6;stroke-linecap:round;stroke-linejoin:round}
.lt{fill:none;stroke-width:1;stroke-linecap:round}
.lk{fill:none;stroke-width:3;stroke-linecap:round;stroke-linejoin:round}
.dsh{stroke-dasharray:5 5}
.s-steel{stroke:#2B4A62}.s-soft{stroke:#8FA3B3}.s-teal{stroke:#0E7C86}.s-amber{stroke:#E3A23B}.s-dk{stroke:#7F97AB}.s-dk2{stroke:#C4D1DB}
.f-teal{fill:#0E7C86}.f-amber{fill:#E3A23B}.f-steel{fill:#2B4A62}.f-zinc{fill:#E7ECEF}.f-white{fill:#FFFFFF}.f-ink{fill:#102638}.f-soft{fill:#C9D3DA}
.lbl{font-family:'Archivo',sans-serif;font-size:11px;font-weight:500;fill:#4A5B6A}
.lbl-d{font-family:'Archivo',sans-serif;font-size:11px;font-weight:500;fill:#A9B8C5}
.mid{text-anchor:middle}
@keyframes run{to{stroke-dashoffset:-40}}
.wire-run{stroke-dasharray:6 14;animation:run 1.4s linear infinite}
@keyframes pulse{0%,45%{opacity:.95}50%,100%{opacity:.12}}
.pulse{animation:pulse 2.4s steps(1,end) infinite}
@keyframes melt{0%,100%{opacity:.82}50%{opacity:1}}
.melt{animation:melt 4s ease-in-out infinite}
input,select,textarea{font-family:'Archivo',sans-serif}
@media (prefers-reduced-motion: reduce){.wire-run,.pulse,.melt{animation:none}}
</style>
</helmet>"""


def page(title, w, h, body, script="class Component extends DCLogic {\n  renderVals() { return {}; }\n}", bg=PAPER):
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{title}</title>
<script src="./support.js"></script>
</head>
<body>
<x-dc>
{HELMET}
<div style="width: {w}px; height: {h}px; overflow: hidden; display: flex; flex-direction: column; font-family: {FONT}; color: {TEXT}; background: {bg}">
{body}
</div>
</x-dc>
<script type="text/x-dc" data-dc-script data-props='{{"$preview":{{"width":{w},"height":{h}}}}}'>
{script}
</script>
</body>
</html>
"""


def sec(h, inner, bg=PAPER, pad="0 80px", extra="", sid=None):
    idattr = f' id="{sid}"' if sid else ""
    return f'<section{idattr} style="height: {h}px; flex-shrink: 0; box-sizing: border-box; overflow: hidden; padding: {pad}; background: {bg}; {extra}">\n{inner}\n</section>'


LOGO = f"""<svg viewBox="0 0 40 40" width="40" height="40" aria-hidden="true"><rect x="0" y="0" width="40" height="40" rx="3" fill="{BLUE}"></rect><path d="M4 14 H15 L23 18.6 V21.4 L15 26 H4 Z" fill="{AMBER}"></path><rect x="23" y="18.6" width="13" height="2.8" fill="{AMBER}"></rect><path d="M13 7 H22 V17 Z" fill="#FFFFFF"></path><path d="M13 33 H22 V23 Z" fill="#FFFFFF"></path></svg>"""


def header(active=""):
    def link(label, href, key):
        on = key == active
        style = f"font-size: 16px; font-weight: {600 if on else 500}; color: {TEXT}; padding: 10px 0; border-bottom: 2px solid {AMBER if on else 'transparent'}"
        return f'<a href="{href}" style="{style}">{label}</a>'
    nav = "".join([
        link("Wire drawing", "WireDrawing.dc.html", "wire"),
        link("Galvanizing", "Galvanizing.dc.html", "galv"),
        link("Knowledge", "Galvanizing.dc.html#knowledge", "know"),
        link("Company", "About.dc.html", "about"),
        link("Contact", "Contact.dc.html", "contact"),
    ])
    return f"""<header style="height: 88px; flex-shrink: 0; box-sizing: border-box; display: flex; align-items: center; justify-content: space-between; padding: 0 80px; background: #FFFFFF; border-bottom: 1px solid {RULE}">
<a href="Main.dc.html" aria-label="SHIVAS Technology home" style="display: flex; align-items: center; gap: 12px; color: {INK}">{LOGO}<span style="display: flex; flex-direction: column; gap: 3px"><span style="font-size: 25px; font-weight: 800; font-stretch: 125%; line-height: 1; letter-spacing: 0.02em">SHIVAS</span><span style="font-size: 13px; font-weight: 500; color: {MUTED}">Technology Limited</span></span></a>
<nav aria-label="Main" style="display: flex; align-items: center; gap: 36px">{nav}<a href="Contact.dc.html" style="font-size: 16px; font-weight: 600; color: {INK}; background: {AMBER}; padding: 14px 22px; border-radius: 2px">Request a quote</a></nav>
</header>"""


FOOTER_H = 400


def footer():
    col = lambda title, items: (
        f'<div style="display: flex; flex-direction: column; gap: 12px"><div style="font-size: 15px; font-weight: 700; color: {ON_DARK}; margin-bottom: 4px">{title}</div>'
        + "".join(f'<a href="{h}" style="font-size: 15px; color: {ON_DARK_M}">{t}</a>' for t, h in items)
        + "</div>")
    wire = [("Straight line machines", "WireDrawing.dc.html#straight-line"), ("OTO type machines", "WireDrawing.dc.html#oto"), ("Line equipment", "WireDrawing.dc.html#line"), ("Die sequence calculator", "WireDrawing.dc.html#calculator")]
    galv = [("Turnkey HDG plants", "Galvanizing.dc.html"), ("Pulse-fired furnaces", "Furnace.dc.html"), ("Zinc kettles", "Galvanizing.dc.html#systems"), ("Fume extraction", "Galvanizing.dc.html#air-water"), ("ETP and ZLD", "Galvanizing.dc.html#air-water")]
    group = [("SHIVAS Reinplast", "https://shivasasia.com"), ("PP tanks", "https://pptanks.com"), ("Pickling plants", "https://pickling-plants.com"), ("FRP blowers", "https://frpblower.com"), ("Company and group", "About.dc.html")]
    return f"""<footer style="height: {FOOTER_H}px; flex-shrink: 0; box-sizing: border-box; background: {INK}; padding: 64px 80px 32px; display: flex; flex-direction: column; justify-content: space-between">
<div style="display: grid; grid-template-columns: 1.4fr 1fr 1fr 1fr; gap: 48px">
<div style="display: flex; flex-direction: column; gap: 14px">
<div style="display: flex; align-items: center; gap: 12px">{LOGO}<span style="font-size: 22px; font-weight: 800; font-stretch: 125%; color: #FFFFFF; letter-spacing: 0.02em">SHIVAS</span></div>
<p style="margin: 0; font-size: 15px; line-height: 1.6; color: {ON_DARK_M}">SHIVAS Technology Limited<br>A-1/270, Swadeshi Compound, Kavi Nagar Industrial Area<br>Ghaziabad, Uttar Pradesh 201002, India</p>
<a href="tel:+919810280104" style="font-size: 17px; font-weight: 600; color: #FFFFFF">+91 98102 80104</a>
<a href="mailto:info@shivastechnology.com" style="font-size: 15px; color: {AMBER}">info@shivastechnology.com</a>
</div>
{col("Wire drawing", wire)}
{col("Galvanizing", galv)}
{col("Group", group)}
</div>
<div style="display: flex; justify-content: space-between; align-items: center; border-top: 1px solid #28415A; padding-top: 20px; font-size: 13px; color: {ON_DARK_M}">
<span>© 2026 SHIVAS Technology Limited. CIN [CIN]. GSTIN [GSTIN].</span>
<span style="display: flex; gap: 24px"><a href="About.dc.html" style="color: {ON_DARK_M}">Privacy policy</a><a href="About.dc.html" style="color: {ON_DARK_M}">Terms</a><a href="Contact.dc.html" style="color: {ON_DARK_M}">Careers</a></span>
</div>
</footer>"""


def btn(label, href, kind="amber"):
    if kind == "amber":
        s = f"background: {AMBER}; color: {INK}"
    elif kind == "teal":
        s = f"background: {TEAL}; color: #FFFFFF"
    elif kind == "ghost-dark":
        s = f"background: transparent; color: #FFFFFF; box-shadow: inset 0 0 0 1.5px #5E7A92"
    else:
        s = f"background: transparent; color: {INK}; box-shadow: inset 0 0 0 1.5px {INK}"
    return f'<a href="{href}" style="display: inline-flex; align-items: center; min-height: 52px; box-sizing: border-box; padding: 0 26px; font-size: 16px; font-weight: 600; border-radius: 2px; {s}">{label}</a>'


# ---------------------------------------------------------------- big SVGs

def svg_straight_line(w=640, dark=False):
    """Straight-line wire drawing machine, side elevation."""
    st = "s-dk" if dark else "s-steel"
    soft = "s-dk" if dark else "s-soft"
    lbl = "lbl-d" if dark else "lbl"
    p = [f'<svg viewBox="0 0 680 300" width="{w}" role="img" aria-label="Straight line wire drawing machine, side view">']
    p.append(f'<line x1="0" y1="272" x2="680" y2="272" class="ln {soft}"></line>')
    # pay-off coil
    p.append(f'<rect x="18" y="180" width="60" height="92" rx="2" class="ln {st}"></rect>')
    for cy in (132, 142, 152, 162, 172):
        p.append(f'<ellipse cx="48" cy="{cy}" rx="30" ry="8" class="ln {st}"></ellipse>')
    wire = ["M78 126"]
    for i in range(6):
        x = 120 + i * 88
        p.append(f'<rect x="{x}" y="160" width="72" height="112" rx="3" class="ln {st}"></rect>')
        p.append(f'<line x1="{x+10}" y1="186" x2="{x+62}" y2="186" class="lt {soft}"></line>')
        p.append(f'<circle cx="{x+36}" cy="228" r="16" class="lt {soft}"></circle>')
        p.append(f'<ellipse cx="{x+36}" cy="92" rx="32" ry="9" class="ln {st}"></ellipse>')
        p.append(f'<line x1="{x+4}" y1="92" x2="{x+4}" y2="150" class="ln {st}"></line>')
        p.append(f'<line x1="{x+68}" y1="92" x2="{x+68}" y2="150" class="ln {st}"></line>')
        p.append(f'<path d="M{x+4} 150 A32 9 0 0 0 {x+68} 150" class="ln {st}"></path>')
        p.append(f'<ellipse cx="{x+36}" cy="154" rx="36" ry="9" class="lt {soft}"></ellipse>')
        for y in (112, 121, 130, 139):
            p.append(f'<path d="M{x+4} {y} A32 9 0 0 0 {x+68} {y}" class="ln s-teal"></path>')
        # die box before block
        p.append(f'<rect x="{x-15}" y="118" width="12" height="24" rx="1" class="ln {st}"></rect>')
        wire.append(f"L{x-9} 130 L{x+4} 139")
        wire.append(f"M{x+68} 112")
    wire.append("L676 112")
    d = " ".join(wire)
    p.append(f'<path d="{d}" class="lk s-teal"></path>')
    p.append(f'<path d="{d}" class="ln s-dk2 wire-run"></path>')
    p.append(f'<text x="48" y="292" class="{lbl} mid">Pay-off</text>')
    p.append(f'<text x="376" y="292" class="{lbl} mid">Six drawing blocks with die boxes</text>')
    p.append("</svg>")
    return "".join(p)


def svg_oto(w=560, dark=False):
    st = "s-dk" if dark else "s-steel"
    soft = "s-dk" if dark else "s-soft"
    p = [f'<svg viewBox="0 0 600 280" width="{w}" role="img" aria-label="OTO type wire drawing machine, side view">']
    p.append(f'<line x1="0" y1="262" x2="600" y2="262" class="ln {soft}"></line>')
    path = ["M10 150"]
    for i in range(5):
        x = 60 + i * 104
        p.append(f'<rect x="{x}" y="170" width="74" height="92" rx="3" class="ln {st}"></rect>')
        p.append(f'<ellipse cx="{x+37}" cy="120" rx="33" ry="9" class="ln {st}"></ellipse>')
        p.append(f'<line x1="{x+4}" y1="120" x2="{x+4}" y2="162" class="ln {st}"></line>')
        p.append(f'<line x1="{x+70}" y1="120" x2="{x+70}" y2="162" class="ln {st}"></line>')
        p.append(f'<path d="M{x+4} 162 A33 9 0 0 0 {x+70} 162" class="ln {st}"></path>')
        for y in (134, 142, 150, 158):
            p.append(f'<path d="M{x+4} {y} A33 9 0 0 0 {x+70} {y}" class="ln s-teal"></path>')
        # overhead pulley and arm
        px = x + 88
        p.append(f'<line x1="{x+37}" y1="111" x2="{x+37}" y2="46" class="ln {st}"></line>')
        p.append(f'<line x1="{x+37}" y1="46" x2="{px}" y2="46" class="ln {st}"></line>')
        p.append(f'<circle cx="{px}" cy="46" r="12" class="ln {st}"></circle>')
        p.append(f'<rect x="{x-14}" y="140" width="12" height="22" rx="1" class="ln {st}"></rect>')
        path.append(f"L{x-8} 151 L{x+4} 158 M{x+70} 134 L{px+12} 46")
        if i < 4:
            path.append(f"M{px-12} 46 L{x+96} 151")
    d = " ".join(path)
    p.append(f'<path d="{d}" class="lk s-teal"></path>')
    p.append(f'<path d="{d}" class="ln s-dk2 wire-run"></path>')
    p.append("</svg>")
    return "".join(p)


def svg_kettle_scene(w=640):
    """Galvanizing scene on dark ground: crane, job, enclosure, kettle, pulse-fired furnace, bag filter."""
    p = [f'<svg viewBox="0 0 680 350" width="{w}" role="img" aria-label="Zinc kettle in a pulse-fired furnace with fume enclosure and crane">']
    p.append('<line x1="0" y1="330" x2="680" y2="330" class="ln s-dk"></line>')
    # crane girder + trolley + hook
    p.append('<rect x="60" y="14" width="500" height="10" class="ln s-dk"></rect>')
    p.append('<rect x="318" y="24" width="44" height="14" class="ln s-dk"></rect>')
    p.append('<line x1="340" y1="38" x2="340" y2="104" class="ln s-dk2"></line>')
    p.append('<rect x="270" y="104" width="140" height="7" class="ln s-dk2"></rect>')
    p.append('<line x1="284" y1="111" x2="296" y2="150" class="ln s-dk2"></line><line x1="396" y1="111" x2="384" y2="150" class="ln s-dk2"></line>')
    # job: I-beam
    p.append('<rect x="262" y="150" width="156" height="4" class="f-soft"></rect><rect x="262" y="164" width="156" height="4" class="f-soft"></rect><rect x="262" y="154" width="156" height="10" class="ln s-dk2"></rect>')
    # enclosure
    p.append('<path d="M176 180 V62 H250 M430 62 H504 V180" class="ln s-dk dsh"></path>')
    p.append('<path d="M504 90 H600 V60" class="ln s-dk"></path>')
    # bag filter
    p.append('<rect x="572" y="60" width="72" height="120" rx="2" class="ln s-dk"></rect>')
    for bx in (586, 604, 622):
        p.append(f'<line x1="{bx}" y1="72" x2="{bx}" y2="150" class="lt s-dk2"></line>')
    p.append('<path d="M586 180 L608 206 L630 180" class="ln s-dk"></path>')
    p.append('<line x1="608" y1="206" x2="608" y2="330" class="ln s-dk"></line>')
    # furnace casing, refractory, kettle
    p.append('<rect x="150" y="186" width="380" height="144" class="ln s-dk"></rect>')
    p.append('<rect x="166" y="198" width="348" height="132" class="lt s-dk dsh"></rect>')
    p.append('<rect x="204" y="206" width="272" height="96" class="f-amber melt"></rect>')
    p.append('<path d="M200 186 V305 H480 V186" class="lk s-dk2"></path>')
    p.append('<line x1="204" y1="206" x2="476" y2="206" class="ln s-amber"></line>')
    # burners + pulse flames
    delays = ["0s", "1.2s", "0.6s", "1.8s"]
    k = 0
    for side, bx, fx in (("L", 128, 150), ("R", 530, 530)):
        for by in (220, 272):
            p.append(f'<rect x="{bx}" y="{by-7}" width="22" height="14" rx="1" class="ln s-dk"></rect>')
            if side == "L":
                fl = f"M{fx} {by-5} Q{fx+26} {by-3} {fx+46} {by} Q{fx+26} {by+3} {fx} {by+5} Z"
            else:
                fl = f"M{fx} {by-5} Q{fx-26} {by-3} {fx-46} {by} Q{fx-26} {by+3} {fx} {by+5} Z"
            p.append(f'<path d="{fl}" class="f-amber pulse" style="animation-delay: {delays[k]}"></path>')
            k += 1
    # flue
    p.append('<path d="M500 186 V150 H540 V110" class="ln s-dk"></path>')
    # labels
    p.append('<line x1="176" y1="120" x2="120" y2="120" class="lt s-dk"></line><text x="114" y="124" class="lbl-d" style="text-anchor: end">Kettle enclosure</text>')
    p.append('<line x1="150" y1="272" x2="112" y2="300" class="lt s-dk"></line><text x="106" y="312" class="lbl-d" style="text-anchor: end">Pulse-fired burners</text>')
    p.append('<text x="340" y="262" class="lbl mid" style="fill: #102638; font-weight: 700">Zinc 440–460 °C</text>')
    p.append('<text x="608" y="52" class="lbl-d mid">Bag filter</text>')
    p.append('</svg>')
    return "".join(p)


def svg_acid_fume(w=620):
    p = [f'<svg viewBox="0 0 640 270" width="{w}" role="img" aria-label="Acid fume extraction: enclosed room, duct, packed-bed scrubber, FRP blower and stack">']
    p.append('<line x1="0" y1="252" x2="640" y2="252" class="ln s-soft"></line>')
    # room
    p.append('<path d="M10 252 V110 L120 80 L230 110 V252" class="ln s-steel"></path>')
    for tx in (28, 92, 156):
        p.append(f'<rect x="{tx}" y="200" width="54" height="52" class="ln s-steel"></rect><line x1="{tx}" y1="214" x2="{tx+54}" y2="214" class="lt s-teal"></line>')
    p.append('<path d="M120 80 V40 H330 V70" class="lk s-steel"></path>')
    for ax in (170, 230, 290):
        p.append(f'<path d="M{ax} 34 l10 6 l-10 6" class="ln s-teal"></path>')
    # scrubber
    p.append('<rect x="300" y="70" width="64" height="150" rx="3" class="ln s-steel"></rect>')
    p.append('<rect x="306" y="120" width="52" height="46" class="lt s-soft"></rect>')
    for yy in range(126, 166, 8):
        p.append(f'<line x1="310" y1="{yy}" x2="354" y2="{yy+6}" class="lt s-soft"></line>')
    p.append('<line x1="308" y1="100" x2="356" y2="100" class="ln s-teal"></line>')
    for sx in (316, 332, 348):
        p.append(f'<path d="M{sx} 100 v8" class="lt s-teal"></path>')
    p.append('<rect x="290" y="220" width="84" height="32" class="ln s-steel"></rect>')
    p.append('<path d="M374 236 H400 V100 H356" class="ln s-teal"></path>')
    # blower
    p.append('<path d="M332 70 V50 H440 V150" class="lk s-steel"></path>')
    p.append('<circle cx="460" cy="178" r="30" class="ln s-steel"></circle><circle cx="460" cy="178" r="8" class="ln s-steel"></circle>')
    p.append('<path d="M440 150 H452 M490 178 H520" class="lk s-steel"></path>')
    p.append('<rect x="436" y="208" width="48" height="44" class="ln s-steel"></rect>')
    # stack
    p.append('<path d="M520 178 H560 V10 H584 V252" class="lk s-steel"></path>')
    p.append('<path d="M566 4 q6 -8 12 0" class="ln s-soft"></path>')
    for x, y, t in ((120, 266, "Enclosed pretreatment room"), (332, 64, "Scrubber"), (460, 266, "FRP blower"), (572, 266, "Stack")):
        p.append(f'<text x="{x}" y="{y}" class="lbl mid">{t}</text>')
    p.append('</svg>')
    return "".join(p)


def svg_pulse_plan(w=620):
    """Plan view: kettle in furnace with staggered HV burners."""
    p = [f'<svg viewBox="0 0 640 300" width="{w}" role="img" aria-label="Plan view of kettle with staggered high velocity burners">']
    p.append('<rect x="40" y="50" width="560" height="200" class="ln s-dk"></rect>')
    p.append('<rect x="60" y="68" width="520" height="164" class="lt s-dk dsh"></rect>')
    p.append('<rect x="100" y="100" width="440" height="100" class="f-amber melt"></rect>')
    p.append('<rect x="96" y="96" width="448" height="108" class="lk s-dk2"></rect>')
    top = [130, 290, 450]
    bot = [190, 350, 510]
    delays = ["0s", "0.8s", "1.6s", "0.4s", "1.2s", "2.0s"]
    k = 0
    for bx in top:
        p.append(f'<rect x="{bx-8}" y="30" width="16" height="20" class="ln s-dk"></rect>')
        p.append(f'<path d="M{bx-5} 52 Q{bx+30} 70 {bx+110} 82 Q{bx+30} 76 {bx+5} 52 Z" class="f-amber pulse" style="animation-delay: {delays[k]}"></path>')
        k += 1
    for bx in bot:
        p.append(f'<rect x="{bx-8}" y="250" width="16" height="20" class="ln s-dk"></rect>')
        p.append(f'<path d="M{bx+5} 248 Q{bx-30} 230 {bx-110} 218 Q{bx-30} 224 {bx-5} 248 Z" class="f-amber pulse" style="animation-delay: {delays[k]}"></path>')
        k += 1
    p.append('<rect x="600" y="140" width="30" height="20" class="ln s-dk"></rect>')
    p.append('<text x="320" y="154" class="lbl mid" style="fill: #102638; font-weight: 700">Kettle</text>')
    p.append('<text x="615" y="182" class="lbl-d mid">Flue</text>')
    p.append('<text x="40" y="20" class="lbl-d">Burners fire tangentially along the wall, staggered on both sides</text>')
    p.append('<text x="40" y="292" class="lbl-d">Plan view</text>')
    p.append('</svg>')
    return "".join(p)


def svg_room(w=560):
    p = [f'<svg viewBox="0 0 600 300" width="{w}" role="img" aria-label="Enclosed pretreatment room with internal crane and extraction">']
    p.append('<line x1="0" y1="282" x2="600" y2="282" class="ln s-dk"></line>')
    p.append('<path d="M20 282 V90 L300 40 L580 90 V282" class="ln s-dk"></path>')
    p.append('<line x1="40" y1="118" x2="560" y2="118" class="ln s-dk"></line>')
    p.append('<rect x="250" y="122" width="40" height="12" class="ln s-dk"></rect><line x1="270" y1="134" x2="270" y2="190" class="ln s-dk2"></line><rect x="220" y="190" width="100" height="6" class="ln s-dk2"></rect>')
    xs = [40, 118, 196, 274, 352, 430, 508]
    for i, x in enumerate(xs):
        p.append(f'<rect x="{x}" y="226" width="62" height="56" class="ln s-dk"></rect>')
        p.append(f'<line x1="{x}" y1="238" x2="{x+62}" y2="238" class="lt s-amber"></line>')
    p.append('<path d="M300 40 V12 H560" class="lk s-dk"></path>')
    for ax in (380, 450, 520):
        p.append(f'<path d="M{ax} 6 l10 6 l-10 6" class="ln s-amber"></path>')
    p.append('<rect x="560" y="210" width="20" height="72" class="ln s-amber"></rect>')
    p.append('<text x="300" y="298" class="lbl-d mid">Tanks, crane and extraction inside one sealed room</text>')
    p.append('</svg>')
    return "".join(p)


# ---------------------------------------------------------------- small icons (200 x 110)

def icon(body, label, dark=False):
    return f'<svg viewBox="0 0 200 110" width="100%" height="110" role="img" aria-label="{label}">{body}</svg>'


def icons_galv():
    s, t, a = "ln s-steel", "ln s-teal", "ln s-amber"
    return {
        "kettle": icon(f'<path d="M40 20 V88 H160 V20" class="lk s-steel"></path><rect x="44" y="40" width="112" height="44" class="f-amber"></rect><path d="M40 100 H160 M40 96 v8 M160 96 v8" class="lt s-soft"></path><path d="M176 20 V88 M172 20 h8 M172 88 h8" class="lt s-soft"></path>', "Zinc kettle"),
        "furnace": icon(f'<rect x="20" y="16" width="160" height="84" class="{s}"></rect><path d="M50 24 V88 H150 V24" class="lk s-steel"></path><rect x="53" y="44" width="94" height="41" class="f-amber"></rect><path d="M22 40 Q34 42 46 44 Q34 46 22 48 Z" class="f-amber pulse"></path><path d="M178 70 Q166 72 154 74 Q166 76 178 78 Z" class="f-amber pulse" style="animation-delay: 1.2s"></path>', "High velocity pulse-fired furnace"),
        "enclosure": icon(f'<path d="M36 100 V30 H164 V100" class="{s} dsh"></path><path d="M100 30 V8 H180" class="lk s-steel"></path><path d="M60 100 V70 H140 V100" class="lk s-steel"></path><rect x="63" y="80" width="74" height="18" class="f-amber"></rect><path d="M84 52 q4 -8 8 0 q4 8 8 0" class="lt s-soft"></path>', "Kettle enclosure"),
        "room": icon(f'<path d="M14 104 V40 L100 12 L186 40 V104" class="{s}"></path>' + "".join(f'<rect x="{x}" y="76" width="30" height="28" class="{s}"></rect>' for x in (26, 62, 98, 134)) + '<line x1="24" y1="52" x2="176" y2="52" class="ln s-steel"></line>', "Enclosed process room"),
        "tanks": icon("".join(f'<rect x="{x}" y="30" width="52" height="66" class="{s}"></rect><line x1="{x}" y1="46" x2="{x+52}" y2="46" class="{t}"></line><line x1="{x+17}" y1="30" x2="{x+17}" y2="96" class="lt s-soft"></line><line x1="{x+35}" y1="30" x2="{x+35}" y2="96" class="lt s-soft"></line>' for x in (16, 74, 132)) + '<line x1="8" y1="100" x2="192" y2="100" class="lt s-soft"></line>', "PP and FRP process tanks"),
        "flux": icon(f'<rect x="12" y="40" width="60" height="56" class="{s}"></rect><line x1="12" y1="52" x2="72" y2="52" class="{t}"></line>' + "".join(f'<rect x="{x}" y="36" width="7" height="50" class="{s}"></rect>' for x in range(110, 176, 11)) + f'<path d="M72 70 H104 M180 60 V20 H42 V40" class="{t}"></path><path d="M36 34 l6 6 l6 -6" class="{t}"></path>', "Flux filtration and regeneration"),
        "whitefume": icon(f'<path d="M20 100 V60 H80 V100" class="lk s-steel"></path><rect x="24" y="80" width="52" height="18" class="f-amber"></rect><path d="M50 60 V20 H120" class="lk s-steel"></path><rect x="120" y="12" width="44" height="70" class="{s}"></rect>' + "".join(f'<line x1="{x}" y1="20" x2="{x}" y2="70" class="lt s-soft"></line>' for x in (130, 142, 154)) + f'<path d="M142 82 V100 H186" class="{s}"></path>', "Zinc white fume extraction"),
        "scrubber": icon(f'<rect x="40" y="14" width="36" height="86" rx="2" class="{s}"></rect>' + "".join(f'<line x1="44" y1="{y}" x2="72" y2="{y+5}" class="lt s-soft"></line>' for y in range(44, 70, 6)) + f'<path d="M8 60 H40 M58 14 V6 H108 V52" class="lk s-steel"></path><circle cx="118" cy="68" r="16" class="{s}"></circle><path d="M134 68 H156 V100 M156 100 V4 H170 V100" class="lk s-steel"></path>', "Acid fume scrubber, blower and stack"),
        "etp": icon(f'<path d="M14 30 H74 L56 70 H32 Z" class="{s}"></path><line x1="44" y1="70" x2="44" y2="100" class="{s}"></line><rect x="92" y="30" width="30" height="66" class="{s}"></rect><rect x="134" y="30" width="30" height="66" class="{s}"></rect><path d="M74 50 H92 M122 50 H134 M164 50 H190" class="{t}"></path><path d="M100 22 q4 -8 8 0 M142 22 q4 -8 8 0" class="lt s-soft"></path>', "ETP and ZLD"),
        "dryer": icon(f'<rect x="30" y="20" width="140" height="76" class="{s}"></rect>' + "".join(f'<path d="M{x} 86 q6 -12 0 -24 q-6 -12 0 -24" class="{a}"></path>' for x in (70, 100, 130)) + '<line x1="20" y1="100" x2="180" y2="100" class="lt s-soft"></line>', "Hot air dryer"),
        "crane": icon(f'<rect x="10" y="14" width="180" height="8" class="{s}"></rect><rect x="84" y="22" width="32" height="10" class="{s}"></rect><line x1="100" y1="32" x2="100" y2="62" class="{s}"></line><rect x="66" y="62" width="68" height="6" class="{s}"></rect><rect x="30" y="86" width="140" height="10" class="{s}"></rect><circle cx="50" cy="100" r="4" class="{s}"></circle><circle cx="150" cy="100" r="4" class="{s}"></circle>', "Cranes and transfer cars"),
        "plc": icon(f'<rect x="30" y="12" width="140" height="80" rx="3" class="{s}"></rect><path d="M44 72 L70 56 L92 62 L118 36 L156 44" class="{t}"></path><line x1="44" y1="30" x2="96" y2="30" class="lt s-soft"></line><line x1="80" y1="92" x2="80" y2="104" class="{s}"></line><line x1="120" y1="92" x2="120" y2="104" class="{s}"></line><line x1="60" y1="104" x2="140" y2="104" class="{s}"></line>', "PLC and SCADA automation"),
    }


def icons_wire():
    s, t = "ln s-steel", "ln s-teal"
    return {
        "payoff": icon(f'<rect x="70" y="70" width="60" height="30" class="{s}"></rect>' + "".join(f'<ellipse cx="100" cy="{y}" rx="40" ry="9" class="{s}"></ellipse>' for y in (28, 38, 48, 58)) + f'<path d="M140 30 Q170 20 190 24" class="{t}"></path>', "Pay-off stand"),
        "descaler": icon("".join(f'<circle cx="{x}" cy="{y}" r="12" class="{s}"></circle>' for x, y in ((50, 40), (80, 70), (110, 40), (140, 70))) + f'<path d="M10 58 L50 52 L80 58 L110 52 L140 58 L190 56" class="lk s-teal"></path>', "Mechanical descaler"),
        "butt": icon(f'<rect x="30" y="30" width="54" height="50" class="{s}"></rect><rect x="116" y="30" width="54" height="50" class="{s}"></rect><path d="M10 55 H96 M104 55 H190" class="lk s-teal"></path><path d="M96 46 L100 55 L96 64 M104 46 L100 55 L104 64" class="ln s-amber"></path>', "Pointing and butt welding"),
        "diebox": icon(f'<rect x="54" y="20" width="92" height="70" rx="3" class="{s}"></rect><path d="M84 36 L112 50 V60 L84 74 Z" class="{s}"></path><path d="M10 55 H96 M112 55 H190" class="lk s-teal"></path><path d="M130 28 a16 16 0 0 1 0 54" class="lt s-soft"></path>', "Rotating die box"),
        "deadblock": icon(f'<rect x="70" y="14" width="60" height="30" class="{s}"></rect><path d="M76 44 V96 M124 44 V96" class="{s}"></path>' + "".join(f'<ellipse cx="100" cy="{y}" rx="46" ry="8" class="{t}"></ellipse>' for y in (60, 70, 80, 90)) + '<line x1="30" y1="104" x2="170" y2="104" class="lt s-soft"></line>', "Dead block coiler"),
        "spooler": icon(f'<rect x="60" y="20" width="80" height="80" class="{s}"></rect><rect x="74" y="34" width="52" height="52" class="{s}"></rect>' + "".join(f'<line x1="{x}" y1="34" x2="{x}" y2="86" class="lt s-teal"></line>' for x in range(80, 124, 6)) + f'<path d="M10 30 H100" class="lk s-teal"></path><path d="M150 30 H190" class="lt s-soft"></path>', "Spooler"),
        "takeup": icon("".join(f'<ellipse cx="{x}" cy="56" rx="10" ry="34" class="{s}"></ellipse>' for x in (50, 100, 150)) + f'<path d="M10 22 H190" class="{t}"></path><line x1="20" y1="100" x2="180" y2="100" class="lt s-soft"></line>', "Horizontal take-up"),
        "invvert": icon(f'<rect x="70" y="10" width="60" height="22" class="{s}"></rect><path d="M74 32 V64 M126 32 V64" class="{s}"></path>' + "".join(f'<path d="M74 {y} A26 7 0 0 0 126 {y}" class="{t}"></path>' for y in (42, 50, 58)) + "".join(f'<ellipse cx="100" cy="{y}" rx="40" ry="7" class="{t}"></ellipse>' for y in (80, 88, 96)) + '<line x1="30" y1="104" x2="170" y2="104" class="lt s-soft"></line>', "Inverted vertical drawing machine"),
        "anneal": icon(f'<path d="M50 100 V40 Q100 10 150 40 V100" class="{s}"></path><rect x="70" y="60" width="60" height="40" class="{s}"></rect><path d="M86 56 q4 -8 0 -16 M100 56 q4 -8 0 -16 M114 56 q4 -8 0 -16" class="ln s-amber"></path>', "Annealing furnace"),
        "pickle": icon("".join(f'<rect x="{x}" y="40" width="40" height="56" class="{s}"></rect><line x1="{x}" y1="52" x2="{x+40}" y2="52" class="{t}"></line>' for x in (14, 60, 106, 152)) + f'<path d="M20 20 H180" class="{s}"></path>', "Pickling line"),
        "giwire": icon(f'<path d="M60 40 V90 H140 V40" class="lk s-steel"></path><rect x="63" y="56" width="74" height="31" class="f-amber"></rect><path d="M10 30 L80 70 H120 L190 30" class="lk s-teal"></path>', "Galvanized wire line"),
        "panel": icon(f'<rect x="50" y="10" width="100" height="92" class="{s}"></rect><line x1="100" y1="10" x2="100" y2="102" class="lt s-soft"></line><rect x="60" y="22" width="30" height="20" class="{t}"></rect>' + "".join(f'<circle cx="{x}" cy="60" r="4" class="{s}"></circle>' for x in (66, 78, 90)) + "".join(f'<line x1="110" y1="{y}" x2="140" y2="{y}" class="lt s-soft"></line>' for y in (26, 36, 46, 56, 66)), "Drives and control panels"),
    }
