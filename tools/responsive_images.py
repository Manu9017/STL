#!/usr/bin/env python3
"""Give large photos a srcset so phones download a picture sized for the screen.

    python3 tools/responsive_images.py            # all pages except the 3D viewers
    python3 tools/responsive_images.py --dry-run

For every <img src="..._FULL.webp"> (no srcset yet) whose file is 960 px wide or more, and every existing
srcset whose FULL candidate is 1100 px or more (adds the copies to it), this writes
480 px and 960 px copies to site/assets/resp/ (same crop, WebP q80) and adds
    srcset="resp/x-480.webp 480w, resp/x-960.webp 960w, library/x_FULL.webp <W>w"
    sizes="(max-width: 900px) calc(100vw - 40px), 560px"
The sizes value fits how this site lays photos out (full width on phones, about 560 px on desktop).
Measured on 10 Nov 2026. If an image is shown much smaller, give it its own sizes by hand.
assets/library/ is not touched: it belongs to the image-library tools.
"""
import os
import re
import sys

from PIL import Image

SITE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "site")
RESP = os.path.join(SITE, "assets", "resp")
WIDTHS = (480, 960)
SIZES = "(max-width: 900px) calc(100vw - 40px), 560px"
IMG = re.compile(r"<img\b[^>]*>")


def variants(full):
    """Make the smaller copies once; return [(relpath_from_site, width)] including the original."""
    im = Image.open(full)
    w, h = im.size
    base = os.path.basename(full).replace("_FULL.webp", "")
    out = []
    for tw in WIDTHS:
        if tw >= w:
            continue
        dst = os.path.join(RESP, f"{base}-{tw}.webp")
        if not os.path.exists(dst):
            os.makedirs(RESP, exist_ok=True)
            im.convert("RGB").resize((tw, round(h * tw / w)), Image.LANCZOS).save(dst, "WEBP", quality=80, method=6)
        out.append((os.path.relpath(dst, SITE).replace(os.sep, "/"), tw))
    out.append((os.path.relpath(full, SITE).replace(os.sep, "/"), w))
    return out


def main():
    dry = "--dry-run" in sys.argv
    changed = 0
    for d, _, files in os.walk(SITE):
        rel_d = os.path.relpath(d, SITE)
        if rel_d.split(os.sep)[0] in ("v", "setup", "photos"):
            continue
        for fn in files:
            if not fn.endswith(".html"):
                continue
            page = os.path.join(d, fn)
            up = "../" * (0 if rel_d == "." else rel_d.count(os.sep) + 1)
            src = open(page, encoding="utf-8").read()
            n = 0

            def fix(m):
                nonlocal n
                tag = m.group(0)
                if "srcset=" in tag:
                    return widen(tag)
                s = re.search(r'\ssrc="([^"]+_FULL\.webp)"', tag)
                if not s:
                    return tag
                full = os.path.normpath(os.path.join(d, s.group(1)))
                if not os.path.isfile(full) or Image.open(full).size[0] < 960:
                    return tag
                if dry:
                    n += 1
                    return tag
                set_ = ", ".join(f"{up}{p} {w}w" for p, w in variants(full))
                n += 1
                return tag[:4] + f' srcset="{set_}" sizes="{SIZES}"' + tag[4:]

            def widen(tag):
                # existing srcset (e.g. THUMB 720w + FULL 1600w): add 480/960 copies of the FULL so phones get ~1000 px
                nonlocal n
                m2 = re.search(r'srcset="([^"]*)"', tag)
                if not m2 or "assets/resp/" in m2.group(1):
                    return tag
                f = re.search(r'([^\s,"]+_FULL\.webp) \d+w', m2.group(1))
                if not f:
                    return tag
                full = os.path.normpath(os.path.join(d, f.group(1)))
                if not os.path.isfile(full) or Image.open(full).size[0] < 1100:
                    return tag
                if dry:
                    n += 1
                    return tag
                extra = ", ".join(f"{up}{p} {w}w" for p, w in variants(full)[:-1])
                n += 1
                return tag.replace(m2.group(0), 'srcset="' + extra + ", " + m2.group(1) + '"')

            new = IMG.sub(fix, src)
            if n:
                changed += n
                print(f"{os.path.relpath(page, SITE)}: {n}")
                if not dry:
                    open(page, "w", encoding="utf-8").write(new)
    print(("Would update " if dry else "Updated ") + f"{changed} images")


if __name__ == "__main__":
    main()
