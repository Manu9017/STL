#!/usr/bin/env python3
"""SHIVAS site checker. Standard library only.

    python3 tools/check_site.py            # check site/
    python3 tools/check_site.py --root site --quiet

Checks every HTML page under the site root for:
  errors   broken internal links and images, missing <title>, missing meta description,
           invalid JSON-LD, lead e-mails copied to a third party, sitemap entries with no file
  warnings duplicate titles/descriptions, missing or wrong canonical, pages missing from the
           sitemap, <img> without alt or width/height, standards/certificates we must not
           claim, [bracketed] placeholders, division pages drifting apart
Exit code 1 when there are errors.
"""
import argparse
import json
import os
import re
import sys
from collections import Counter, defaultdict
from html.parser import HTMLParser
from urllib.parse import unquote, urlsplit

BASE_URL = "https://www.shivastechnology.com/"
# The 3D viewers in v/ are self-contained apps; we only check their links and claims.
VIEWER_DIR = "v/"
# Pages that should not be in the sitemap.
NOINDEX_OK = {"items/r-frp.html"}
# Claims the brief says not to make until certificates are confirmed, and a withdrawn standard.
CLAIMS = [
    (re.compile(r"\bCE[- ](?:mark|marked|certified|certification|compliant)\b", re.I), "CE claim (confirm certificate first)"),
    (re.compile(r"\bISO\s*9001\b"), "ISO 9001 claim (confirm certificate first)"),
    (re.compile(r"\bEN\s*746\b"), "EN 746 reference (do not claim until confirmed)"),
    (re.compile(r"\bBS\s*729\b"), "BS 729 is withdrawn: cite ISO 1461 / ASTM A123 / IS 2629 / IS 4759"),
]
# EN 746-2 in these 3D viewers' spec tables was reviewed and kept by the owner (10 Nov 2026).
EN746_KEPT = {"v/arp-10.html", "v/spin-galvanizing.html", "v/zinc-ash-plant.html"}
THIRD_PARTY_MAIL = re.compile(r"indianbusinesshub|clquery", re.I)
PLACEHOLDER = re.compile(r"\[(?:[A-Z][^\[\]<>{}\n]{2,70})\]")
DIVISION_PAGES = ["galvanizing.html", "wire-drawing.html", "reinplast.html"]


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title = None
        self._in_title = False
        self.description = None
        self.canonical = None
        self.noindex = False
        self.refresh = False
        self.links = []          # (attr, value, line)
        self.ids = set()
        self.imgs = []           # (attrs, line)
        self.jsonld = []         # (text, line)
        self._in_jsonld = None
        self._skip = 0           # inside script/style
        self.text = []           # (text, line)

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        line = self.getpos()[0]
        if a.get("id"):
            self.ids.add(a["id"])
        if tag == "a" and a.get("name"):
            self.ids.add(a["name"])
        if tag == "title":
            self._in_title = True
            self.title = ""
        elif tag == "meta":
            n = (a.get("name") or "").lower()
            if n == "description":
                self.description = a.get("content") or ""
            elif n == "robots" and "noindex" in (a.get("content") or ""):
                self.noindex = True
            if (a.get("http-equiv") or "").lower() == "refresh":
                self.refresh = True
        elif tag == "link" and "canonical" in (a.get("rel") or "").split():
            self.canonical = a.get("href")
        elif tag == "img":
            self.imgs.append((a, line))
        if tag == "script":
            if (a.get("type") or "") == "application/ld+json":
                self._in_jsonld = ["", line]
            else:
                self._skip += 1
        elif tag == "style":
            self._skip += 1
        for k in ("href", "src"):
            if a.get(k) is not None and tag in ("a", "img", "link", "script", "source", "iframe"):
                if tag == "link" and "preconnect" in (a.get("rel") or ""):
                    continue
                self.links.append((k, a[k], line))
        if a.get("srcset"):
            for part in a["srcset"].split(","):
                u = part.strip().split(" ")[0]
                if u:
                    self.links.append(("srcset", u, line))

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False
        elif tag == "script":
            if self._in_jsonld is not None:
                self.jsonld.append(tuple(self._in_jsonld))
                self._in_jsonld = None
            elif self._skip:
                self._skip -= 1
        elif tag == "style" and self._skip:
            self._skip -= 1

    def handle_data(self, data):
        if self._in_title:
            self.title += data
        if self._in_jsonld is not None:
            self._in_jsonld[0] += data
        elif not self._skip and data.strip():
            self.text.append((data, self.getpos()[0]))


def site_files(root):
    out = []
    for d, _, files in os.walk(root):
        for f in files:
            out.append(os.path.relpath(os.path.join(d, f), root).replace(os.sep, "/"))
    return set(out)


def resolve(page_rel, url, files):
    """Return (target_rel, fragment) for an internal URL, or None for external/special URLs."""
    if not url or url.startswith(("http://", "https://", "//", "mailto:", "tel:", "data:", "javascript:", "blob:", "{", "$")):
        if url.startswith(BASE_URL):
            url = "/" + url[len(BASE_URL):]
        else:
            return None
    parts = urlsplit(url)
    path, frag = unquote(parts.path), parts.fragment
    if not path:
        return page_rel, frag
    if path.startswith("/"):
        target = path.lstrip("/")
    else:
        target = os.path.normpath(os.path.join(os.path.dirname(page_rel), path)).replace(os.sep, "/")
    if target in (".", ""):
        target = "index.html"
    if target.endswith("/") or (target not in files and target + "/index.html" in files):
        target = target.rstrip("/") + "/index.html"
    return target, frag


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "site"))
    ap.add_argument("--quiet", action="store_true", help="print totals and errors only")
    ap.add_argument("--anchors", action="store_true", help="also warn about #anchors not found in the target page")
    args = ap.parse_args()
    root = os.path.abspath(args.root)
    files = site_files(root)
    pages = sorted(f for f in files if f.endswith(".html"))
    errors, warnings = [], []
    parsed = {}

    for rel in pages:
        with open(os.path.join(root, rel), encoding="utf-8", errors="replace") as fh:
            src = fh.read()
        p = Page()
        try:
            p.feed(src)
        except Exception as e:  # malformed markup should not stop the run
            errors.append(f"{rel}: HTML parse failed ({e})")
            continue
        p.src = src
        parsed[rel] = p

    titles, descs = defaultdict(list), defaultdict(list)
    for rel, p in parsed.items():
        viewer = rel.startswith(VIEWER_DIR)
        stub = p.refresh or p.noindex
        if not viewer:
            if not (p.title or "").strip():
                errors.append(f"{rel}: no <title>")
            else:
                titles[p.title.strip()].append(rel)
            if not stub:
                if not (p.description or "").strip():
                    errors.append(f"{rel}: no meta description")
                else:
                    descs[p.description.strip()].append(rel)
                want = BASE_URL + ("" if rel == "index.html" else rel)
                if not p.canonical:
                    warnings.append(f"{rel}: no canonical link")
                elif p.canonical not in (want, want.replace("/index.html", "/")):
                    warnings.append(f"{rel}: canonical is {p.canonical}, expected {want}")
            for text, line in p.jsonld:
                try:
                    json.loads(text)
                except ValueError as e:
                    errors.append(f"{rel}:{line}: invalid JSON-LD ({e})")
            nosize = 0
            for a, line in p.imgs:
                if "alt" not in a:
                    warnings.append(f"{rel}:{line}: <img> without alt ({a.get('src', '')[:60]})")
                # no src = a slot that script fills (gallery viewer, lightbox); data: = inline
                if a.get("src") and not (a.get("width") and a.get("height")) and not a["src"].startswith("data:"):
                    nosize += 1
            if nosize:
                # explicit sizes stop layout shift (Lighthouse CLS)
                warnings.append(f"{rel}: {nosize} <img> without width/height")
            for text, line in p.text:
                for m in PLACEHOLDER.finditer(text):
                    warnings.append(f"{rel}:{line}: placeholder {m.group(0)}")

        for kind, url, line in p.links:
            r = resolve(rel, url.strip(), files)
            if r is None:
                if kind == "href" and url.startswith("mailto:") and THIRD_PARTY_MAIL.search(url):
                    errors.append(f"{rel}:{line}: enquiry copied to a third party ({url[:80]})")
                continue
            target, frag = r
            if target not in files:
                errors.append(f"{rel}:{line}: broken {kind} -> {url}")
            elif args.anchors and frag and target.endswith(".html") and target in parsed:
                if frag not in parsed[target].ids and not frag.startswith(("/", "!")):
                    warnings.append(f"{rel}:{line}: #{frag} not found in {target} (may be made by script)")

        for i, ln in enumerate(p.src.splitlines(), 1):
            for rx, why in CLAIMS:
                if rx.search(ln) and not (why.startswith("EN 746") and rel in EN746_KEPT):
                    warnings.append(f"{rel}:{i}: {why}")
            if THIRD_PARTY_MAIL.search(ln) and "mailto:" not in ln:
                errors.append(f"{rel}:{i}: third-party lead address in page source")

    for t, rels in titles.items():
        if len(rels) > 1:
            warnings.append(f"duplicate title '{t[:70]}' on: {', '.join(rels)}")
    for d, rels in descs.items():
        if len(rels) > 1:
            warnings.append(f"duplicate description on: {', '.join(rels)}")

    # sitemap
    sm_path = os.path.join(root, "sitemap.xml")
    if os.path.exists(sm_path):
        with open(sm_path, encoding="utf-8") as fh:
            locs = re.findall(r"<loc>\s*([^<]+?)\s*</loc>", fh.read())
        in_map = set()
        for loc in locs:
            if not loc.startswith(BASE_URL):
                errors.append(f"sitemap.xml: {loc} is not on {BASE_URL}")
                continue
            rel = loc[len(BASE_URL):] or "index.html"
            if rel.endswith("/"):
                rel += "index.html"
            in_map.add(rel)
            if rel not in files:
                errors.append(f"sitemap.xml: {loc} has no file")
        for rel, p in parsed.items():
            if rel.startswith(VIEWER_DIR) or p.refresh or p.noindex or rel in NOINDEX_OK:
                continue
            if rel not in in_map:
                warnings.append(f"sitemap.xml: {rel} is not listed")
    else:
        errors.append("sitemap.xml missing")
    if "robots.txt" not in files:
        errors.append("robots.txt missing")

    # division pages share one code base; large drift usually means an edit reached only one of them
    # Natural difference (Nov 2026, after adding canonicals): 71 lines (wire-drawing), 103 (reinplast).
    srcs = {d: Counter(parsed[d].src.splitlines()) for d in DIVISION_PAGES if d in parsed}
    drift = []
    if len(srcs) == 3:
        base = srcs[DIVISION_PAGES[0]]
        for other in DIVISION_PAGES[1:]:
            o = srcs[other]
            diff = sum((base - o).values()) + sum((o - base).values())
            drift.append(f"{other} {diff}")
            if diff > 150:
                warnings.append(f"{other} differs from {DIVISION_PAGES[0]} on {diff} lines (about 71 and 103 is normal): did a shared edit reach all three division pages?")

    # numbers quoted on the home page must match the site (they go stale when pages are added)
    if "index.html" in parsed:
        home = parsed["index.html"].src
        actual = {
            "products": len(set(re.findall(r'<a class="mini[^"]*" href="([a-z0-9-]+)\.html"', parsed["items/index.html"].src))) if "items/index.html" in parsed else None,
            "3D models": len([f for f in files if f.startswith(VIEWER_DIR) and f.endswith(".html")]),
            "articles": len([f for f in files if f.startswith("blog/") and f.endswith(".html") and f != "blog/index.html"]),
            "photos": int((re.findall(r'data-div="" aria-pressed="true">All <i>(\d+)</i>', parsed["gallery.html"].src) or [0])[0]) if "gallery.html" in parsed else None,
        }
        for label, n in actual.items():
            for m in re.finditer(r'<b>(\d+)</b><span>' + re.escape(label) + r'</span>', home):
                if n is not None and int(m.group(1)) != n:
                    warnings.append(f"index.html: proof strip says {m.group(1)} {label}, the site has {n}")
        for pat, label in [(r'All (\d+) articles', "articles"), (r'See all (\d+) photos', "photos"), (r'All (\d+) 3D models', "3D models")]:
            for m in re.finditer(pat, home):
                if actual[label] is not None and int(m.group(1)) != actual[label]:
                    warnings.append(f"index.html: '{m.group(0)}' but the site has {actual[label]} {label}")

    # tracking state
    cfg = os.path.join(root, "assets", "config.js")
    if os.path.exists(cfg):
        with open(cfg, encoding="utf-8") as fh:
            c = fh.read()
        on = [k for k in ("sheetUrl", "ga4", "companyScript") if re.search(k + r"\s*:\s*'[^']+'", c)]
        tracking = ", ".join(on) if on else "off (config.js is empty)"
    else:
        tracking = "config.js missing"

    print(f"SHIVAS site check: {len(pages)} HTML pages, {len(files)} files in {os.path.relpath(root)}")
    print(f"Visitor tracking: {tracking}")
    if drift:
        print("Division pages vs galvanizing.html, differing lines: " + ", ".join(drift))
    print(f"{len(errors)} errors, {len(warnings)} warnings\n")
    if errors:
        print("ERRORS")
        for e in errors:
            print("  " + e)
        print()
    if warnings and not args.quiet:
        print("WARNINGS")
        for w in warnings:
            print("  " + w)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
