#!/usr/bin/env python3
"""Write site/calculators/<page>.html: one page for each calculator in site/assets/calcs.js.

Each page carries the calculator itself (a <div class="cx-one" data-calc="..."> that calcs.js fills), and, as plain
text for readers and search engines, what you enter, what it works out and how, taken from the calculator's own
inputs, results and note, so the page always says what the calculator does. Header, menu and footer come from
site/calculators.html. Titles, descriptions, products and articles are set below.

    python3 tools/build_calc_pages.py           # write the pages (needs node)
    python3 tools/build_calc_pages.py --check   # exit 1 when a page no longer matches calcs.js or this file

Run it after changing a calculator's inputs, results or note in calcs.js, or the header or footer of
calculators.html; tools/check_site.py runs the check. New pages also go in site/sitemap.xml.
"""
import html
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.join(os.path.dirname(HERE), "site")
OUT = os.path.join(SITE, "calculators")
BASE_URL = "https://www.shivastechnology.com/"

# id: (h1, <title>, meta description, products, articles). Products are items/*.html (or a page in site/),
# the same pages that carry the calculator; articles are blog/*.html.
PAGES = {
    "wire": ("Wire drawing calculator", "Wire drawing calculator: passes, dies, speed and kW | SHIVAS",
             "Free wire drawing calculator: from rod to finished size, the dies you need, the diameter after each die, block speeds, power per block and output a day.",
             ["slm", "oto", "wet", "ivcoiler", "bull", "wdline", "mig", "diebox"],
             ["planning-a-wire-drawing-line", "die-angle-and-reduction", "straight-line-or-oto", "wire-breaks-causes-and-cures", "wire-heat-and-strain-ageing", "drawing-die-care"]),
    "burner": ("Burner kW calculator for galvanizing furnaces", "Galvanizing furnace burner kW calculator | SHIVAS",
               "Free burner kW calculator for galvanizing: the kettle your largest article needs, furnace firing rate, high-velocity burners, wall heat flux and fuel an hour.",
               ["furnace", "burner", "gastrain", "kettle", "turnkey"],
               ["burners-and-kettle-life", "choosing-furnace-fuel", "sizing-a-galvanizing-kettle", "kettle-wall-checks", "installing-a-new-kettle"]),
    "zld": ("ETP and ZLD plant calculator", "ETP and ZLD plant calculator: RO, MEE or MVR, ATFD | SHIVAS",
            "Free ETP and ZLD calculator for pickling and galvanizing effluent: neutraliser and sludge, RO, a multiple-effect or MVR evaporator, the ATFD, steam and power.",
            ["r-zld", "r-etp", "env"],
            ["zld-for-pickling-effluent", "effluent-to-zld", "mee-or-mvr", "where-the-atfd-fits", "ro-before-the-evaporator", "lime-or-caustic-for-zld", "etp-sludge-and-filter-press"]),
    "coating": ("Galvanized coating thickness check", "Galvanized coating thickness check, ISO 1461 | SHIVAS",
                "Check a hot-dip galvanized coating against the ISO 1461 minimums: mean and local thickness, coating mass in g/m² and the zinc it puts on a tonne of steel.",
                ["kettle", "turnkey", "spin"],
                ["measuring-coating-thickness", "how-long-galvanizing-lasts", "silicon-and-the-sandelin-effect", "where-your-zinc-goes", "spin-galvanizing-fasteners", "dull-thick-and-flaking-coatings"]),
    "wireweight": ("Wire weight and length calculator", "Wire weight calculator: kg per km and metres per coil | SHIVAS",
                   "Free wire weight calculator: kg per metre and per km, metres in a coil or spool and how long it takes to fill, output a day and zinc on galvanized wire.",
                   ["wdline", "mig", "hdgwire", "wirezinc", "dbc", "spooler", "vcoiler", "egline"],
                   ["galvanized-wire-line", "testing-zinc-coating-on-wire", "planning-a-wire-drawing-line", "wire-diameter-and-ovality"]),
    "scrubber": ("Fume scrubber and blower calculator", "Fume scrubber and blower calculator | SHIVAS",
                 "Size a packed-bed fume scrubber from your pickling tanks: extraction air, tower diameter, packing height, recirculation pump and the blower motor in kW and HP.",
                 ["r-scrub", "r-msscrub", "r-apc", "r-hood", "afe", "acidroom"],
                 ["acid-fume-scrubbers", "scrubber-troubleshooting", "fumeless-pickling-for-wire"]),
    "acid": ("Pickling acid calculator", "Pickling acid calculator: HCl use and spent acid | SHIVAS",
             "Free pickling acid calculator: the hydrochloric acid your pickling uses, the spent acid to dispose of or regenerate each month, and what one tank charge holds.",
             ["r-pick", "r-wirepick", "r-pipepick", "r-strip", "pretreat", "line-fpl", "r-acid"],
             ["pickling-right", "spent-acid-options", "fumeless-pickling-for-wire", "counterflow-rinsing"]),
    "neutralise": ("Spent acid neutralisation calculator", "Spent acid neutralisation calculator: lime and sludge | SHIVAS",
                   "Neutralise spent hydrochloric pickling acid with lime: the lime a month, iron hydroxide sludge and filter cake, and the calcium chloride left in the water.",
                   ["r-etp", "r-acid"],
                   ["spent-acid-options", "etp-sludge-and-filter-press", "lime-or-caustic-for-zld", "effluent-to-zld"]),
    "bagfilter": ("Bag filter calculator", "Bag filter calculator: cloth area, bags and fan | SHIVAS",
                  "Size a pulse-jet bag filter from the air flow and the dust: cloth area, number of bags, housing, can velocity, bag material for the temperature and fan power.",
                  ["zfe", "enclosure", "r-apc"],
                  ["zinc-fume-extraction", "flux-and-your-zinc-bill"]),
    "fan": ("Fan and blower motor calculator", "Fan and blower motor calculator: kW and HP | SHIVAS",
            "Any fan or blower: from the air flow and the total pressure, the air power, the shaft power and the motor to install, in kW and HP.",
            ["r-blower", "r-duct"],
            ["acid-fume-scrubbers", "zinc-fume-extraction"]),
    "rectifier": ("Electro-galvanizing rectifier calculator", "Electro-galvanizing rectifier calculator | SHIVAS",
                  "Electro-galvanizing rectifier calculator: plating current, current density on the wire, rectifier rating and zinc used, from wire size, strands and line speed.",
                  ["egline", "line-egl"],
                  ["electro-galvanizing-wire", "testing-zinc-coating-on-wire"]),
    "frp": ("FRP profile weight and deflection calculator", "FRP profile weight and deflection calculator | SHIVAS",
            "Pultruded FRP profile calculator: weight per metre, the same section in steel, and how far it bends as a simply supported beam under your load, beside steel.",
            ["../pultrusion", "r-frpfab"],
            ["designing-with-frp-profiles", "frp-profile-quality-checks"]),
}
COMPANY = {"hdg": "SHIVAS Technology", "wire": "SHIVAS Technology", "rein": "SHIVAS Reinplast", "frp": "SHIVAS Products India"}
OG = {"hdg": "og-galvanizing.jpg", "wire": "og-wire-drawing.jpg", "rein": "og-reinplast.jpg", "frp": "og-default.jpg"}
MG_NOTE = ("Each size it picks (a motor, burner, rectifier or fan) is the next standard size above the calculated need. "
           "Choose an extra margin of 10, 20 or 30 % and it is added to the need before the size is picked; nothing else is added.")

DUMP = r"""
global.window = {}; global.document = { getElementById: function () { return null; }, querySelector: function () { return null; } };
global.localStorage = { getItem: function () { return null; }, setItem: function () {} };
eval(require('fs').readFileSync(process.argv[1], 'utf8'));
var out = { pages: window.SHIVAS_CALC_PAGES, calcs: window.SHIVAS_CALCS.map(function (c) {
  var v = {}; c.inputs.forEach(function (f) { v[f.k] = f.v; }); var r = c.run(v);
  return { id: c.id, div: c.div, t: c.t, s: c.s, lead: c.lead, mg: !!c.mg, note: r.note || '',
    key: (r.key || []).map(function (k) { return k[0]; }), rows: (r.rows || []).map(function (x) { return x[0]; }),
    table: r.table ? (r.table.title || 'Step by step') : '', svg: !!r.svg,
    inputs: c.inputs.map(function (f) {
      var sel = f.type === 'sel';
      return { l: f.l, u: f.u || '', adv: !!f.adv, sel: sel, v: sel ? (f.opts.filter(function (o) { return o[0] === f.v; })[0] || ['', ''])[1] : f.v,
        opts: sel ? f.opts.map(function (o) { return o[1]; }) : null, hint: f.hint || '', auto: (!f.v && f.hint && f.hint.indexOf('0 =') === 0) ? (f.auto || (f.k === 'nb' ? 'auto' : 'from the article')) : '' };
    }) };
}) };
process.stdout.write(JSON.stringify(out));
"""


def calc_data():
    r = subprocess.run(["node", "-e", DUMP, os.path.join(SITE, "assets", "calcs.js")], capture_output=True, text=True, check=True)
    return json.loads(r.stdout)


def read(rel):
    return open(os.path.join(SITE, rel), encoding="utf-8").read()


def up(text):
    """calculators.html markup, for a page one folder down: every site-relative href or src gets ../ in front."""
    def fix(m):
        attr, q, url = m.group(1), m.group(2), m.group(3)
        if re.match(r"^([a-z]+:|#|/|\.\./|data:)", url):
            return m.group(0)
        url = "../" + (url[2:] if url.startswith("./") else url)
        return f'{attr}={q}{url}{q}'
    return re.sub(r'\b(href|src)=(["\'])([^"\']*)\2', fix, text)


def first(pattern, text, what):
    m = re.search(pattern, text, flags=re.S)
    if not m:
        sys.exit(f"build_calc_pages: {what} not found in calculators.html")
    return m.group(0)


def page_info(rel):
    """name and one-line description of a product page or article, from its own h1 and description."""
    s = read(rel)
    h1 = re.search(r"<h1[^>]*>(.*?)</h1>", s, flags=re.S).group(1)
    d = re.search(r'<meta name="description" content="([^"]*)"', s).group(1)
    return html.unescape(re.sub(r"<[^>]+>", "", h1).strip()), html.unescape(d)


def esc(t):
    return html.escape(t, quote=False)


def fmt(v):
    if isinstance(v, float) and v.is_integer():
        v = int(v)
    return f"{v:,}" if isinstance(v, int) and abs(v) >= 10000 else str(v)


def entered(c):
    main, adv = [], []
    for f in c["inputs"]:
        u = "" if f["u"] in ("", "no.") else f["u"]
        if f["sel"]:
            main.append(f"<li><b>{esc(f['l'])}</b>, one of: {esc('; '.join(f['opts']))}</li>")
            continue
        if f["adv"]:
            val = esc(f["auto"]) if f["auto"] else esc(fmt(f["v"])) + ("\u00a0" + esc(u) if u else "")
            name = re.sub(r", if (you already have one|you know it|your supplier gives one)$", "", re.sub(r" [(].*[)]$", "", f["l"]))
            adv.append(f"{esc(name)} {val}")
        elif not f["v"] and f["hint"]:
            main.append(f"<li><b>{esc(f['l'])}</b> ({esc(f['hint'])})</li>")
        else:
            main.append(f"<li><b>{esc(f['l'])}</b>, typical {esc(fmt(f['v']))}{chr(160) + esc(u) if u else ''}</li>")
    out = '<ul class="cxin">' + "".join(main) + "</ul>"
    if adv:
        out += f'<p class="sub">Under <b>Advanced</b>, {len(adv)} more inputs for a closer answer, each set to a typical value until you change it: {"; ".join(adv)}.</p>'
    return out


def build_page(c, D, tpl):
    h1, title, desc, prods, arts = PAGES[c["id"]]
    slug = D["pages"][c["id"]]
    rel = f"calculators/{slug}.html"
    url = BASE_URL + rel
    brand = "rein" if c["div"] == "rein" else "tech"
    others = ['<li><a href="../calculator.html"><b>Galvanizing plant calculator</b><span>Kettle, furnace, zinc, fuel and cost per tonne from your steel and tonnage.</span></a></li>']
    for o in D["calcs"]:
        if o["id"] != c["id"]:
            others.append(f'<li><a href="{D["pages"][o["id"]]}.html"><b>{esc(o["t"])}</b><span>{esc(o["s"])}</span></a></li>')
    plinks = []
    for p in prods:
        prel = (p[3:] + ".html") if p.startswith("../") else f"items/{p}.html"
        name, d = page_info(prel)
        plinks.append(f'<li><a href="../{prel}"><b>{esc(name)}</b><span>{esc(d)}</span></a></li>')
    alinks = []
    for a in arts:
        name, d = page_info(f"blog/{a}.html")
        alinks.append(f'<li><a href="../blog/{a}.html"><b>{esc(name)}</b><span>{esc(d)}</span></a></li>')
    results = [f"<li>{esc(k)}</li>" for k in c["key"]] + [f"<li>{esc(r)}</li>" for r in c["rows"]]
    if c["table"]:
        results.append(f"<li>{esc(c['table'])}, as a table</li>")
    if c["svg"]:
        results.append("<li>A process flow diagram of the plant you set</li>")
    how = f'<p>{c["note"]}</p>' + (f"<p>{MG_NOTE}</p>" if c["mg"] else "") + \
        '<p>The answer is a first sizing from typical values, and every input can be changed. Press <b>Ask our engineer to check this</b> under the results and SHIVAS replies with a checked sizing and a proposal.</p>'
    ld = [
        {"@context": "https://schema.org", "@type": "WebApplication", "name": h1, "description": desc, "url": url,
         "applicationCategory": "BusinessApplication", "operatingSystem": "Any", "browserRequirements": "Requires JavaScript",
         "isAccessibleForFree": True, "offers": {"@type": "Offer", "price": "0", "priceCurrency": "INR"},
         "provider": {"@type": "Organization", "name": {"rein": "SHIVAS Reinplast Company of India", "frp": "SHIVAS Products India"}.get(c["div"], "SHIVAS Technology Limited"), "url": BASE_URL}},
        {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "SHIVAS", "item": BASE_URL},
            {"@type": "ListItem", "position": 2, "name": "Engineering calculators", "item": BASE_URL + "calculators.html"},
            {"@type": "ListItem", "position": 3, "name": h1, "item": url}]},
    ]
    head = (f'<!DOCTYPE html>\n<html lang="en" data-brand="{brand}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">'
            f'<meta name="theme-color" content="#1f4e79"><link rel="icon" href="../favicon.ico" sizes="48x48"><link rel="apple-touch-icon" href="../apple-touch-icon.png">\n'
            f'<title>{esc(title)}</title><meta name="description" content="{html.escape(desc)}">\n'
            f'<link rel="canonical" href="{url}"><meta property="og:type" content="website"><meta property="og:url" content="{url}">'
            f'<meta property="og:title" content="{html.escape(title)}"><meta property="og:description" content="{html.escape(desc)}">'
            f'<meta property="og:image" content="{BASE_URL}assets/og/{OG[c["div"]]}"><meta name="twitter:card" content="summary_large_image">\n'
            + tpl["theme"] + "\n" + up(tpl["css"]) + tpl["v36"] + up(tpl["v39"]) + up(tpl["fonts"]) + up(tpl["v52f"]).replace("url(assets/", "url(../assets/") + "\n"
            + "".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in ld)
            + '</head><body data-item="" data-calcs="1">\n')
    main = (f'<main id="main" class="wrap cxpg"><nav class="crumbs" aria-label="You are here"><a href="../">SHIVAS</a><span>›</span><a href="../calculators.html">Engineering calculators</a><span>›</span><b>{esc(h1)}</b></nav>\n'
            f'<section class="hero hero-s"><div class="hero-t"><span class="k">{COMPANY[c["div"]]} · calculator</span><h1>{esc(h1)}</h1>\n<p class="d">{esc(c["lead"])}</p></div></section>\n'
            f'<div class="cx-one" data-calc="{c["id"]}" data-h="0" data-div="{c["div"]}"><noscript><p class="sub">This calculator works in your browser and needs JavaScript. Call or WhatsApp +91 98109 20468 and our engineers will work it out with you.</p></noscript></div>\n'
            f'<section class="sec" aria-labelledby="in-h"><h2 id="in-h">What you enter</h2>{entered(c)}</section>\n'
            f'<section class="sec" aria-labelledby="out-h"><h2 id="out-h">What it works out</h2><ul class="cxin">{"".join(results)}</ul></section>\n'
            f'<section class="sec" aria-labelledby="hw-h"><h2 id="hw-h">How it works</h2>{how}</section>\n'
            f'<section class="sec" aria-labelledby="pr-h"><h2 id="pr-h">The equipment it sizes</h2><p class="sub">The same calculator is on each of these pages.</p><ul class="cxl">{"".join(plinks)}</ul></section>\n'
            f'<section class="sec" aria-labelledby="ar-h"><h2 id="ar-h">From our engineers</h2><ul class="cxl">{"".join(alinks)}</ul></section>\n'
            f'<section class="sec" aria-labelledby="oc-h"><h2 id="oc-h">Other calculators</h2><ul class="cxl">{"".join(others)}</ul><p class="sub"><a href="../calculators.html">All calculators on one page →</a></p></section>\n'
            '</main>\n')
    body = up(tpl["skip"]) + "\n" + up(tpl["header"]) + up(tpl["menu"]) + "\n" + main + up(tpl["footer"]) + "\n" + \
        '<script src="../assets/item.js" defer></script><script src="../assets/calcs.js" defer></script>\n</body></html>\n'
    return rel, head + body


def template():
    s = read("calculators.html")
    t = {
        "theme": first(r"<script>\(function\(\)\{var t=null;.*?</script>", s, "theme script"),
        "css": first(r'<link rel="stylesheet" href="assets/item\.css"><script defer src="assets/site\.js"></script>', s, "item.css and site.js"),
        "v36": first(r'<style id="v36">.*?</style>', s, "v36 style"),
        "v39": first(r'<link id="v39c"[^>]*><script id="v39j"[^>]*></script>', s, "v39 links"),
        "fonts": "".join(re.findall(r'<link rel="preload"[^>]*>', s)),
        "v52f": first(r'<style id="v52f">.*?</style>', s, "font faces"),
        "skip": first(r'<a class="skip"[^>]*>.*?</a>', s, "skip link"),
        "header": first(r'<header class="top">.*?</header>', s, "header"),
        "menu": first(r'<div class="menu v42m v42sub" id="v42menu" hidden>.*?</div></div>', s, "menu"),
        "footer": first(r'<footer class="foot v31f">.*?</footer>', s, "footer"),
    }
    t["menu"] = t["menu"].replace('<a href="">Home</a>', '<a href="./">Home</a>')
    return t


def main():
    D = calc_data()
    tpl = template()
    want = {}
    for c in D["calcs"]:
        if c["id"] not in PAGES:
            sys.exit(f"build_calc_pages: no PAGES entry for calculator '{c['id']}'")
        rel, text = build_page(c, D, tpl)
        want[rel] = text
    if "--check" in sys.argv:
        stale = [r for r, t in want.items() if not os.path.exists(os.path.join(SITE, r)) or read(r) != t]
        if stale:
            print("calculator pages out of date (run python3 tools/build_calc_pages.py): " + ", ".join(stale))
            sys.exit(1)
        print(f"{len(want)} calculator pages up to date")
        return
    os.makedirs(OUT, exist_ok=True)
    for rel, text in want.items():
        open(os.path.join(SITE, rel), "w", encoding="utf-8").write(text)
    print(f"wrote {len(want)} pages in site/calculators/")
    for rel in want:
        print("  " + BASE_URL + rel)


if __name__ == "__main__":
    main()
