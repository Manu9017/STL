#!/usr/bin/env python3
"""Add width/height (the image's real pixel size) to <img> tags that lack them.

    python3 tools/fix_img_sizes.py              # all pages in site/ except the 3D viewers
    python3 tools/fix_img_sizes.py items/new.html blog/new-article.html
    python3 tools/fix_img_sizes.py --dry-run

Explicit sizes let the browser reserve space before the picture loads, so the page doesn't jump
(Lighthouse CLS). On this site every image's height is set by CSS (height:auto / 100%), so the
attributes only give the aspect ratio and never change the layout. This was checked on all pages, desktop and
phone, in Nov 2026. On a NEW page whose CSS leaves an image's height alone, the attribute decides
the height: screenshot the page after running this.
Line drawings (drawings.svg#id) are 120x72. Needs Pillow for webp/jpg/png.
"""
import os
import re
import sys

from PIL import Image

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "site")
IMG = re.compile(r"<img\b[^>]*>", re.I)
SRC = re.compile(r'\ssrc\s*=\s*"([^"]*)"', re.I)
SVG_VIEW = (120, 72)  # every <view> in assets/library/drawings.svg
_cache = {}


def size_of(path):
    if path not in _cache:
        if path.endswith(".svg"):
            m = re.search(r'viewBox="[\d.\s-]+?\s([\d.]+)\s([\d.]+)"', open(path, encoding="utf-8").read(2000))
            _cache[path] = (round(float(m.group(1))), round(float(m.group(2)))) if m else None
        else:
            with Image.open(path) as im:
                _cache[path] = im.size
    return _cache[path]


def fix(rel, dry):
    p = os.path.join(ROOT, rel)
    src = open(p, encoding="utf-8").read()
    added, skipped = 0, []

    def repl(m):
        nonlocal added
        tag = m.group(0)
        has_w = re.search(r"\swidth\s*=", tag, re.I)
        has_h = re.search(r"\sheight\s*=", tag, re.I)
        if has_w and has_h:
            return tag
        s = SRC.search(tag)
        if not s or s.group(1).startswith(("data:", "http", "//")) or "'" in s.group(1) or "+" in s.group(1):
            return tag
        url = s.group(1).split("?")[0]
        file, _, frag = url.partition("#")
        f = os.path.normpath(os.path.join(os.path.dirname(p), file))
        if not os.path.isfile(f):
            skipped.append(url)
            return tag
        wh = SVG_VIEW if (frag and f.endswith("drawings.svg")) else size_of(f)
        if not wh:
            skipped.append(url)
            return tag
        if has_w or has_h:  # one given: leave it, it may be a deliberate display size
            skipped.append(url + " (only one of width/height)")
            return tag
        added += 1
        return tag[:4] + f' width="{wh[0]}" height="{wh[1]}"' + tag[4:]

    out = IMG.sub(repl, src)
    if added and not dry:
        open(p, "w", encoding="utf-8").write(out)
    return added, skipped


def main():
    dry = "--dry-run" in sys.argv
    pages = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not pages:
        for d, _, files in os.walk(ROOT):
            rel_d = os.path.relpath(d, ROOT)
            if rel_d.split(os.sep)[0] in ("v", "setup", "photos"):
                continue
            pages += [os.path.normpath(os.path.join(rel_d, f)) for f in files if f.endswith(".html")]
    total = 0
    for rel in sorted(pages):
        added, skipped = fix(rel, dry)
        total += added
        if added or skipped:
            print(f"{rel}: +{added}" + (f"  skipped: {', '.join(skipped)}" if skipped else ""))
    print(f"{'Would add' if dry else 'Added'} sizes to {total} images.")


if __name__ == "__main__":
    main()
