import json, os, datetime, re
from p_main import main_page, mobile_page
from p_galv import galv_page
from p_wire import wire_page
from p_rest import furnace_page, about_page, contact_page

ROOT = "/mnt/user-data/outputs/artifacts/bd30008f-1f30-46e3-afd3-f262c4183b8d/project"
os.makedirs(ROOT, exist_ok=True)

pages = [
    ("Main.dc.html", "Home: choose a division", main_page),
    ("Galvanizing.dc.html", "Galvanizing division", galv_page),
    ("WireDrawing.dc.html", "Wire drawing division", wire_page),
    ("Furnace.dc.html", "Product page template: pulse-fired furnace", furnace_page),
    ("About.dc.html", "Company and group", about_page),
    ("Contact.dc.html", "Request a quote", contact_page),
    ("Mobile.dc.html", "Mobile home", mobile_page),
]

boards, order = {}, []
x = 0
for fn, title, fnc in pages:
    html, h = fnc()
    w = 390 if fn == "Mobile.dc.html" else 1440
    with open(os.path.join(ROOT, fn), "w") as f:
        f.write(html)
    boards[fn] = {"x": x, "y": 0, "w": w, "h": h, "title": title, "is_interactive": True}
    order.append(fn)
    print(fn, w, h, len(html))
    x += w + 80

total_w = x - 80
now = datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
sitemap = ("Sitemap\n\n"
           "Home: division gateway\n"
           "Wire drawing: straight line, OTO, line equipment, die calculator\n"
           "Galvanizing: process explorer, 12 systems, furnace, air and water, automation, knowledge\n"
           "Product pages: one per system, built from the furnace template\n"
           "Knowledge: guides feeding SEO\n"
           "Projects: case studies (to add)\n"
           "Company and group\n"
           "Request a quote: division-specific RFQ\n\n"
           "Text in [brackets] is a placeholder for real facts or photos.")
canvas = {
    "v": 3,
    "createdOnFiles": {"v": 1, "at": now},
    "title": "SHIVAS Technology Website",
    "launch": {"view": "canvas"},
    "pages": [],
    "boards": boards,
    "order": order,
    "notes": {
        "rowtitle": {"x": 0, "y": -320, "text": "shivastechnology.com redesign: desktop pages and mobile", "kind": "title1", "maxW": total_w},
        "sitemap": {"x": -520, "y": 0, "text": sitemap, "w": 420, "maxH": 700, "fill": "blue", "size": "m"},
    },
    "designSystems": [],
}
with open(os.path.join(ROOT, "canvas.json"), "w") as f:
    json.dump(canvas, f, indent=1)

# sanity: unbalanced holes and unclosed common tags
for fn, _, _ in pages:
    s = open(os.path.join(ROOT, fn)).read()
    holes = re.findall(r"\{\{[^}]*\}\}", s)
    stray = s.count("{{") - len(holes)
    for tag in ("div", "a", "span", "svg", "section", "button", "sc-for", "sc-if", "path", "rect", "p", "h2", "label", "select", "nav"):
        o = len(re.findall(rf"<{tag}[\s>]", s)); c = s.count(f"</{tag}>")
        if o != c:
            print("  MISMATCH", fn, tag, o, c)
    if stray:
        print("  stray braces", fn, stray)
