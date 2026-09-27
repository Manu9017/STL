# Brand layer applied on top of the generated artboards (see build.py):
# the real SHIVAS logo, the vibrant palette built on the logo red, a brand
# stripe, breadcrumbs with cross-division "Jump to" links, a "Keep exploring"
# row on every inner page, and a working mobile menu.
import re

LOGO = "/_blob/7e388a42bbaaacc40b2c9ce5143a1fdf"
LOGO_LIGHT = "/_blob/3dcd77c2428396d3e29bd9a804dd88f3"
RED, GOLD, BLUE = "#E3000F", "#FFB400", "#0070AD"
GALV_D = "#A85F00"  # galvanizing accent for text on light grounds
ALT = "Shivas: SHIVAS Technology Ltd"

PALETTE = {
 "#102638": "#0A1F4D", "#16324A": "#133078", "#28415A": "#2A4A8F", "#1B2B39": "#14213D",
 "#4A5B6A": "#475A78", "#A9B8C5": "#B9C8E8", "#E9EEF2": "#EEF3FF", "#0E7C86": BLUE,
 "#0A5C63": "#005A87", "#E3A23B": GOLD, "#8A5A12": "#A34700", "#E7ECEF": "#E6F6FA",
 "#F6F8F9": "#F5F8FF", "#2B4A62": "#1E4F91", "#8FA3B3": "#8EA6CC", "#7F97AB": "#7F9CCB",
 "#C4D1DB": "#C8D6F0", "#CFD8DE": "#D3DDEE", "#9AAAB6": "#9DB0D0", "#D5DDE3": "#D0E7EF",
 "#C9D3DA": "#C9D6EA", "#5E7A92": "#6F8FC9", "#E6F3F4": "#E3F2FB",
}

STRIPE = ('<div aria-hidden="true" style="height: 4px; flex-shrink: 0; display: flex">'
          f'<span style="flex-grow: 1; background: {RED}"></span><span style="flex-grow: 1; background: {GOLD}"></span>'
          f'<span style="flex-grow: 1; background: {BLUE}"></span></div>')

def crumbs(items, right):
    sep = '<span aria-hidden="true" style="color: #9DB0D0">›</span>'
    parts = []
    for label, href in items:
        parts.append(f'<a href="{href}" style="color: #475A78">{label}</a>' if href else
                     f'<span aria-current="page" style="color: #0A1F4D; font-weight: 600">{label}</span>')
    r = ''.join(f'<a href="{h}" style="display: inline-flex; align-items: center; gap: 8px; min-height: 44px; font-weight: 600; color: {c}">'
                f'<span style="width: 10px; height: 10px; border-radius: 5px; background: {c}"></span>{t}</a>' for t, h, c in right)
    return ('<nav aria-label="Breadcrumb" style="height: 56px; flex-shrink: 0; box-sizing: border-box; padding: 0 80px; display: flex; align-items: center; justify-content: space-between; background: #FFFFFF; border-bottom: 1px solid #D3DDEE; font-size: 15px">'
            f'<div style="display: flex; align-items: center; gap: 10px">{sep.join(parts)}</div>'
            f'<div style="display: flex; align-items: center; gap: 28px"><span style="color: #475A78">Jump to</span>{r}</div></nav>')

WD = ("Wire drawing", "WireDrawing.dc.html", BLUE)
GV = ("Galvanizing", "Galvanizing.dc.html", GALV_D)
CO = ("Company", "About.dc.html", "#0A1F4D")
QT = ("Request a quote", "Contact.dc.html", RED)
FU = ("Pulse-fired furnaces", "Furnace.dc.html", GALV_D)

def card(kicker, title, text, href, color):
    return (f'<a href="{href}" style="display: flex; flex-direction: column; gap: 12px; padding: 28px; background: #FFFFFF; border: 1px solid #D3DDEE; border-top: 6px solid {color}; color: #14213D">'
            f'<span style="font-size: 14px; font-weight: 700; color: {color}">{kicker}</span>'
            f'<span style="font-size: 24px; line-height: 1.2; font-weight: 800; font-stretch: 112%; color: #0A1F4D">{title}</span>'
            f'<span style="font-size: 16px; line-height: 1.55; color: #475A78">{text}</span>'
            f'<span style="margin-top: auto; font-size: 16px; font-weight: 600; color: {color}">Go there →</span></a>')

def explore(cards):
    return ('<section aria-label="Keep exploring" style="height: 400px; flex-shrink: 0; box-sizing: border-box; overflow: hidden; padding: 72px 80px 0; background: #F5F8FF">'
            '<div style="display: flex; flex-direction: column; gap: 32px"><h2 style="margin: 0; font-size: 36px; font-weight: 800; font-stretch: 112%; color: #0A1F4D">Keep exploring SHIVAS</h2>'
            '<div style="display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 24px; height: 220px">'
            + ''.join(card(*c) for c in cards) + '</div></div></section>')

C_WD = ("Wire drawing division", "Machines that draw steel wire", "Straight line and OTO machines, line equipment and a die sequence calculator.", "WireDrawing.dc.html", BLUE)
C_GV = ("Galvanizing division", "Plants that galvanize steel", "Turnkey plants, zinc kettles, furnaces, fume and effluent systems.", "Galvanizing.dc.html", GALV_D)
C_FU = ("Galvanizing product", "Pulse-fired furnaces", "Even kettle heating, steady zinc temperature and flue heat recovery.", "Furnace.dc.html", GALV_D)
C_AW = ("Galvanizing systems", "Fume extraction, ETP and ZLD", "Clean air and zero liquid discharge for a compliant plant.", "Galvanizing.dc.html#air-water", GALV_D)
C_CO = ("Company and group", "One group, one point of contact", "Leadership, projects, standards and the SHIVAS group companies.", "About.dc.html", "#0A1F4D")
C_PR = ("Projects", "Where our equipment runs", "Galvanizing plants and drawing lines in India and abroad.", "About.dc.html#projects", "#0A1F4D")
C_QT = ("Request a quote", "Talk to an engineer", "Send your sizes or job mix. An engineer replies, not a sales desk.", "Contact.dc.html", RED)
C_CALC = ("Wire drawing tool", "Die sequence calculator", "Work out passes, reductions and speeds for your rod and finish sizes.", "WireDrawing.dc.html#calculator", BLUE)

PAGES = {
 "WireDrawing.dc.html": ([("Home", "Main.dc.html"), ("Wire drawing division", None)], [GV, CO, QT], [C_GV, C_PR, C_QT]),
 "Galvanizing.dc.html": ([("Home", "Main.dc.html"), ("Hot dip galvanizing division", None)], [WD, FU, QT], [C_WD, C_FU, C_QT]),
 "Furnace.dc.html": ([("Home", "Main.dc.html"), ("Galvanizing", "Galvanizing.dc.html"), ("Systems", "Galvanizing.dc.html#systems"), ("Pulse-fired furnaces", None)], [GV, WD, QT], [C_AW, C_WD, C_QT]),
 "About.dc.html": ([("Home", "Main.dc.html"), ("Company and group", None)], [WD, GV, QT], [C_WD, C_GV, C_QT]),
 "Contact.dc.html": ([("Home", "Main.dc.html"), ("Request a quote", None)], [WD, GV, CO], [C_WD, C_GV, C_CALC]),
}

HEADER_LOGO_RE = re.compile(r'<a href="Main\.dc\.html" aria-label="SHIVAS Technology home"[^>]*>.*?</a>', re.S)
FOOTER_LOGO_RE = re.compile(r'<div style="display: flex; align-items: center; gap: 12px"><svg\b.*?</svg><span[^>]*>SHIVAS</span></div>', re.S)

def recolor_cta_band(s):
    # the gold call-to-action bands become brand red with white text
    def fix(m):
        sec = m.group(0).replace(f"background: {GOLD}; \">", f"background: {RED}; \">", 1)
        sec = sec.replace("color: #0A1F4D\">", "color: #FFFFFF\">").replace("color: #14213D\">", "color: #FFFFFF\">")
        sec = sec.replace("color: #0A1F4D; box-shadow: inset 0 0 0 1.5px #0A1F4D", "color: #FFFFFF; box-shadow: inset 0 0 0 1.5px #FFFFFF")
        return sec
    return re.sub(r'<section style="height: 300px;[^"]*background: ' + GOLD + r'; ">.*?</section>', fix, s, flags=re.S)

def _transform(name, s):
    delta = 0
    # 1. logo
    if name == "Mobile.dc.html":
        s = HEADER_LOGO_RE.sub(f'<a href="Main.dc.html" aria-label="SHIVAS Technology home" style="display: flex; align-items: center"><img src="{LOGO}" alt="{ALT}" style="height: 34px; width: auto; display: block"></a>', s, 1)
    else:
        s = HEADER_LOGO_RE.sub(f'<a href="Main.dc.html" aria-label="SHIVAS Technology home" style="display: flex; align-items: center"><img src="{LOGO}" alt="{ALT}" style="height: 48px; width: auto; display: block"></a>', s, 1)
    s = FOOTER_LOGO_RE.sub(f'<div style="display: flex; align-items: center"><img src="{LOGO_LIGHT}" alt="{ALT}" style="height: 44px; width: auto; display: block"></div>', s)
    # 2. palette
    for a, b in PALETTE.items():
        s = re.sub(re.escape(a), b, s, flags=re.I)
    # primary quote button in the nav -> brand red
    s = s.replace(f"color: #0A1F4D; background: {GOLD}; padding: 14px 22px", f"color: #FFFFFF; background: {RED}; padding: 14px 22px")
    # active nav item underline -> red
    s = s.replace(f"border-bottom: 2px solid {GOLD}", f"border-bottom: 2px solid {RED}")
    s = recolor_cta_band(s)
    # 3. brand stripe under the header
    s = s.replace("</header>", "</header>\n" + STRIPE, 1); delta += 4
    # 4. breadcrumbs + explore
    if name in PAGES:
        items, right, cards = PAGES[name]
        if name == "Furnace.dc.html":
            s, n = re.subn(r'<nav aria-label="Breadcrumb".*?</nav>\n?', '', s, count=1, flags=re.S)
            assert n == 1
            s = s.replace('<div style="padding-top: 40px; display: flex; flex-direction: column; gap: 40px">', '<div style="padding-top: 72px; display: flex; flex-direction: column; gap: 40px">', 1)
        s = s.replace(STRIPE, STRIPE + "\n" + crumbs(items, right), 1); delta += 56
        s = s.replace("<footer", explore(cards) + "\n<footer", 1); delta += 400
    # 5. footer: add a Home link to the Group column
    s = s.replace('<a href="About.dc.html" style="font-size: 15px; color: #B9C8E8">Company and group</a></div>',
                  '<a href="About.dc.html" style="font-size: 15px; color: #B9C8E8">Company and group</a><a href="Main.dc.html" style="font-size: 15px; color: #B9C8E8">Home</a></div>')
    # 6. root height and preview
    m = re.search(r'<div style="width: (\d+)px; height: (\d+)px;', s)
    w, h = int(m.group(1)), int(m.group(2))
    nh = h + delta
    s = s.replace(m.group(0), f'<div style="width: {w}px; height: {nh}px;', 1)
    s = s.replace(f'"$preview":{{"width":{w},"height":{h}}}', f'"$preview":{{"width":{w},"height":{nh}}}')
    if name == "Mobile.dc.html":
        s = _mobile_menu(s)
    return s, nh


def _mobile_menu(s):
    s = s.replace('<div style="width: 390px; height: 1324px; overflow: hidden; display: flex;',
                  '<div style="width: 390px; height: 1324px; overflow: hidden; position: relative; display: flex;', 1)
    old = re.search(r'<button type="button" aria-label="Open menu".*?</button>', s, re.S).group(0)
    btn = ('<button type="button" onClick="{{toggle}}" aria-label="{{menuLabel}}" aria-expanded="{{open}}" aria-controls="m-menu" style="width: 48px; height: 48px; border: 0; background: transparent; display: flex; align-items: center; justify-content: center; cursor: pointer">'
           '<sc-if value="{{open}}" hint-placeholder-val="{{false}}"><svg viewBox="0 0 24 24" width="24" height="24" aria-hidden="true"><path d="M5 5 L19 19 M19 5 L5 19" class="ln s-steel"></path></svg></sc-if>'
           '<sc-if value="{{closed}}" hint-placeholder-val="{{true}}"><svg viewBox="0 0 24 24" width="24" height="24" aria-hidden="true"><path d="M3 7 H21 M3 12 H21 M3 17 H21" class="ln s-steel"></path></svg></sc-if></button>')
    s = s.replace(old, btn, 1)

    def item(label, href, color, sub):
        return (f'<a href="{href}" style="display: flex; align-items: center; gap: 14px; min-height: 60px; padding: 0 20px; border-bottom: 1px solid #D3DDEE; color: #0A1F4D">'
                f'<span style="width: 10px; height: 10px; border-radius: 5px; flex-shrink: 0; background: {color}"></span>'
                f'<span style="display: flex; flex-direction: column; gap: 2px"><span style="font-size: 18px; font-weight: 700">{label}</span><span style="font-size: 14px; color: #475A78">{sub}</span></span></a>')
    menu = ('<sc-if value="{{open}}" hint-placeholder-val="{{false}}"><nav id="m-menu" aria-label="Main" style="position: absolute; top: 68px; left: 0; width: 390px; bottom: 0; z-index: 5; background: #FFFFFF; display: flex; flex-direction: column">'
            + item("Home", "Main.dc.html", "#0A1F4D", "Choose a division")
            + item("Wire drawing", "WireDrawing.dc.html", BLUE, "Straight line, OTO, line equipment")
            + item("Die sequence calculator", "WireDrawing.dc.html#calculator", BLUE, "Passes, reductions and speeds")
            + item("Hot dip galvanizing", "Galvanizing.dc.html", GALV_D, "Turnkey plants and 12 systems")
            + item("Pulse-fired furnaces", "Furnace.dc.html", GALV_D, "Galvanizing product page")
            + item("Knowledge", "Galvanizing.dc.html#knowledge", GALV_D, "Guides for galvanizers")
            + item("Company and group", "About.dc.html", "#0A1F4D", "Leadership, projects, group sites")
            + f'<div style="padding: 20px; display: flex; flex-direction: column; gap: 10px"><a href="Contact.dc.html" style="display: flex; align-items: center; justify-content: center; min-height: 52px; font-size: 16px; font-weight: 600; background: {RED}; color: #FFFFFF; border-radius: 2px">Request a quote</a>'
            + '<a href="https://wa.me/919810280104" style="display: flex; align-items: center; justify-content: center; min-height: 52px; font-size: 16px; font-weight: 600; color: #0A1F4D; box-shadow: inset 0 0 0 1.5px #0A1F4D; border-radius: 2px">WhatsApp +91 98102 80104</a></div>'
            + '</nav></sc-if>')
    i = s.index(STRIPE) + len(STRIPE)
    s = s[:i] + "\n" + menu + s[i:]
    s = s.replace(f'font-weight: 600; color: #0A1F4D; background: {GOLD}">Quote</a>', f'font-weight: 600; color: #FFFFFF; background: {RED}">Quote</a>')
    s = s.replace("renderVals() { return {}; }", """state = { open: false };
  renderVals() {
    const open = this.state.open;
    return {
      open, closed: !open,
      menuLabel: open ? 'Close menu' : 'Open menu',
      toggle: () => this.setState({ open: !open }),
    };
  }""")
    return s


def apply(name, html):
    """Return (html, height) for one generated artboard with the brand layer applied."""
    return _transform(name, html)


def recolor_svg(svg):
    """Apply the vibrant palette to a standalone illustration."""
    for a, b in PALETTE.items():
        svg = re.sub(re.escape(a), b, svg, flags=re.I)
    return svg
