#!/usr/bin/env python3
"""Put "From our engineers" (articles to read) at the bottom of every page that has none.

Owner, 23 Nov 2026: a reader should find articles at the foot of each page, not only through the menu.
Articles are chosen per page by the words they share with the page (title, h1, description), with a lift for
the page's own company (data-div) and topic family. Pages that already carry a hand-picked list (.rdl on product
pages, the article grid on articles, the calculator pages, the home page's article section) are left alone.
The block sits between <!--rel:start--> and <!--rel:end--> and is rewritten on every run.

    python3 tools/build_related.py          # write
    python3 tools/build_related.py --check  # exit 1 when a block is out of date (check_site.py runs this)
"""
import glob, html, math, os, re, sys
from collections import Counter

SITE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "site")
FAM = {"Wire drawing": "wire", "Wire lines": "wire", "Wire quality": "wire", "Effluent": "rein", "Fume control": "rein", "Tanks and FRP": "rein"}
STOP = set("""a an and are as at be by for from how in is it its of on or the to with what why when where your our you we this that
these those which who will can into than then their there they them out up not no all any each one two three more most over under
about after before also only very just plant plants shivas page product products machine machines line lines system systems use used
make made built build design designed""".split())
# general pages (no single subject): a balanced pick, two articles for each business
GENERAL = {"gallery.html", "3d-models.html", "about.html", "contact.html", "careers.html", "privacy.html", "items/index.html", "calculators.html"}
FEATURED = ["blog/galvanizing-defects-field-guide.html", "blog/sizing-a-galvanizing-kettle.html", "blog/planning-a-wire-drawing-line.html",
            "blog/straight-line-or-oto.html", "blog/zld-for-pickling-effluent.html", "blog/choosing-tank-materials.html"]
SKIP = {"index.html", "404.html", "blog/index.html", "items/r-frp.html"}


def read(rel):
    return open(os.path.join(SITE, rel), encoding="utf-8").read()


def words(t):
    t = html.unescape(re.sub(r"<[^>]+>", " ", t)).lower()
    out = []
    for w in re.findall(r"[a-z][a-z\-]{2,}", t):
        w = w.strip("-")
        if w.endswith("ies"): w = w[:-3] + "y"
        elif w.endswith("s") and not w.endswith("ss"): w = w[:-1]
        if w not in STOP and len(w) > 2: out.append(w)
    return out


def meta(s, name):
    m = re.search(r'<meta name="%s" content="([^"]*)"' % name, s)
    return html.unescape(m.group(1)) if m else ""


def articles():
    arts = []
    for p in sorted(glob.glob(os.path.join(SITE, "blog", "*.html"))):
        rel = os.path.relpath(p, SITE)
        if rel == "blog/index.html": continue
        s = read(rel)
        title = html.unescape(re.sub(r"<[^>]+>", "", re.search(r"<h1[^>]*>(.*?)</h1>", s, re.S).group(1))).strip()
        topic = (re.search(r'<header class="post-h"><span class="k">([^<]*)</span>', s) or [None, ""])[1]
        when = re.search(r'<span class="when">([^<]*)</span>', s)
        mins = re.search(r"(\d+) min read", when.group(1)) if when else None
        date = re.search(r'"datePublished":\s*"([\d-]+)"', s)
        arts.append({"rel": rel, "title": title, "topic": topic, "fam": FAM.get(topic, "hdg"),
                     "mins": mins.group(1) if mins else "", "date": date.group(1) if date else "",
                     "w": Counter(words(title) * 3 + words(meta(s, "description")) + words(topic) * 2)})
    df = Counter(w for a in arts for w in a["w"])
    n = len(arts)
    for a in arts:
        a["idf"] = {w: math.log(1 + n / df[w]) for w in a["w"]}
    return arts


def page_words(s):
    title = re.search(r"<title>(.*?)</title>", s, re.S)
    h1 = re.search(r"<h1[^>]*>(.*?)</h1>", s, re.S)
    ks = " ".join(re.findall(r'<span class="k">([^<]*)</span>', s)[:2])
    return Counter(words((title.group(1) if title else "") * 1) * 2 + words(h1.group(1) if h1 else "") * 3 + words(meta(s, "description")) + words(ks))


def pick(s, arts, k, div):
    pw = page_words(s)
    scored = []
    for a in arts:
        sc = sum(min(pw[w], 3) * a["w"][w] * a["idf"][w] for w in pw if w in a["w"])
        if div and a["fam"] == div: sc = sc * 1.4 + 2
        scored.append((sc, a["date"], a["rel"], a))
    scored.sort(key=lambda x: (-x[0], x[1] and -int(x[1].replace("-", "")) or 0, x[2]))
    top = scored[0][0] or 1
    keep = [x for x in scored[:k] if x[0] >= 0.25 * top]   # weak matches out, at least three stay
    return [x[3] for x in (keep if len(keep) >= 3 else scored[:3])]


def items_html(arts, pre):
    return "".join('<li><a href="%s%s"><b>%s</b><span>%s%s</span></a></li>' % (
        pre, a["rel"], html.escape(a["title"], quote=False), html.escape(a["topic"], quote=False),
        (" · %s min read" % a["mins"]) if a["mins"] else "") for a in arts)


def block(rel, s, arts):
    pre = "../" * rel.count("/")
    body = re.search(r"<body([^>]*)>", s).group(1)
    pt = (re.search(r'data-pt="(\w+)"', body) or [None, ""])[1]
    div = (re.search(r'data-div="(\w+)"', body) or [None, ""])[1]
    more = '<p class="rel-more"><a href="%sblog/index.html">All articles from our engineers →</a></p>' % pre
    if pt == "app":
        # one list per company page; the three copies stay identical
        lists = []
        for cls, d, label in (("tech-only pg-hdg", "hdg", "galvanizing"), ("pg-wire", "wire", "wire drawing"), ("rein-only", "rein", "Reinplast")):
            fake = "<title>%s</title>" % label   # the same for all three copies
            chosen = [a for a in arts if a["fam"] == d]
            fam = chosen
            chosen = pick(fake, fam, 6, d)
            chosen += [a for a in sorted(fam, key=lambda a: a["date"], reverse=True) if a not in chosen][:6 - len(chosen)]
            lists.append('<ul class="rdl %s">%s</ul>' % (cls, items_html(chosen, pre)))
        return ('<!--rel:start--><section class="sheet rel-arts" id="read" aria-labelledby="read-h"><div class="wrap">'
                '<span class="eyebrow">Read more</span><h2 id="read-h">From our engineers</h2>'
                '<p class="lede">Practical notes on the plants and machines on this page, written by the engineers who build them.</p>'
                + "".join(lists) + more + "</div></section><!--rel:end-->")
    k = 6 if pt in ("hub", "page") else 4
    if rel in GENERAL:
        by = {a["rel"]: a for a in arts}
        chosen = [by[r] for r in FEATURED]
    else:
        chosen = pick(s, arts, k, div)
    return ('<!--rel:start--><section class="sec rel-arts" id="read" aria-labelledby="read-h"><h2 id="read-h">From our engineers</h2>'
            '<p class="sub">Practical notes from the engineers who design and build these plants.</p><ul class="rdl">'
            + items_html(chosen, pre) + "</ul>" + more + "</section><!--rel:end-->")


def targets():
    for p in sorted(glob.glob(os.path.join(SITE, "*.html")) + glob.glob(os.path.join(SITE, "items", "*.html"))):
        rel = os.path.relpath(p, SITE).replace(os.sep, "/")
        if rel in SKIP: continue
        s = read(rel)
        if 'id="v39c"' not in s: continue                       # redirect stubs
        if "<!--rel:start-->" not in s and ('class="rdl"' in s or 'class="bgrid"' in s): continue   # hand-picked list already there
        yield rel, s


def place(rel, s, b):
    s = re.sub(r"<!--rel:start-->.*?<!--rel:end-->", "", s, flags=re.S)
    if 'data-pt="app"' in s:
        i = s.index('<section class="enquire" id="enquire">')
    elif 'data-pt="item"' in s and '<section class="ask"' in s:
        i = s.index('<section class="ask"')                     # before the quote band, after the FAQ
    else:
        i = s.index("</main>")
    return s[:i] + b + s[i:]


def main():
    arts = articles()
    stale = []
    for rel, s in targets():
        new = place(rel, s, block(rel, s, arts))
        if new != s:
            stale.append(rel)
            if "--check" not in sys.argv:
                open(os.path.join(SITE, rel), "w", encoding="utf-8").write(new)
    if "--check" in sys.argv:
        if stale:
            print("related articles out of date (run python3 tools/build_related.py): " + ", ".join(stale)); sys.exit(1)
        print("related articles up to date")
    else:
        print("wrote %d pages" % len(stale))


if __name__ == "__main__":
    main()
