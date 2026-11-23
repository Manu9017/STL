#!/usr/bin/env python3
"""Print the `files` maps for republishing site/ to its claude.ai artifact.

    python3 tools/artifact_files.py            # summary + batch files written to preview/artifact-batches/
    python3 tools/artifact_files.py --changed  # only files changed since the last publish (git diff against docs/artifact-published.txt)

One Artifact publish takes at most 255 supporting files and 64 MB, so the site goes up in batches, and one
artifact VERSION holds at most 511 files in all. The real site has more than that, so the artifact gets a
lighter preview build: assets/resp/ (the 480/960 px speed copies) is left out, and pages that use it are
rewritten into preview/artifact-build/ with those srcset candidates removed (the browser then uses the
THUMB/FULL originals) and the home page's 3D previews pointed at v/img/*.jpg. Production keeps everything.
index.html is the page itself (file_path), everything else is a supporting file. Files that are not
part of the public site (README.md, photos/, setup/, .nojekyll) are left out.
Each batch is written as JSON: {"published/path": "site/published/path", ...}
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
SITE = os.path.join(REPO, "site")
OUT = os.path.join(REPO, "preview", "artifact-batches")
EXCLUDE_TOP = {"README.md", ".nojekyll", "photos", "setup", "CNAME", "_redirects", "_headers", "robots.txt", "sitemap.xml", "404.html"}  # robots/sitemap: production only
EXCLUDE_PREFIX = ("assets/resp/", "assets/og/", "items/r-frp.html", "assets/config.js", "assets/track.js")
# config.js / track.js: the visitor log only works on the real domain (claude.ai cannot report visitors), so the
# preview leaves both out and artifact_source() switches off the loader in site.js and v/shivas-bar.js.
NO_TRACK = {"assets/site.js": "if (ME && !window.SHIVAS_TRACK) {", "v/shivas-bar.js": "if (!window.SHIVAS_TRACK) {"}   # resp: speed copies; r-frp: redirect stub for an old URL - both production only (artifact file limit)
BUILD = os.path.join(REPO, "preview", "artifact-build")
# Preview only (23 Nov 2026, 567 files against the 511 limit): photo thumbnails (*_THUMB.webp) that have a full-size
# copy are left out, and every page or script that names one is rewritten to the full-size file; the browser scales
# it. The home page keeps its own thumbnails, so the first page a visitor sees stays light. Production keeps them all.
THUMB_DIRS = ("assets/library", "assets/own")
KEEP_THUMBS_OF = "index.html"
_SWAP = None


def thumb_swaps():
    """THUMB files left out of the preview: every thumbnail with a FULL copy that the home page does not use."""
    global _SWAP
    if _SWAP is None:
        home = open(os.path.join(SITE, KEEP_THUMBS_OF), encoding="utf-8").read()
        _SWAP = set()
        for d in THUMB_DIRS:
            for f in os.listdir(os.path.join(SITE, d)):
                rel = d + "/" + f
                if f.endswith("_THUMB.webp") and rel not in home and os.path.exists(os.path.join(SITE, d, f.replace("_THUMB.webp", "_FULL.webp"))):
                    _SWAP.add(rel)
    return _SWAP


def swap_thumbs(text):
    sw = thumb_swaps()
    text = re.sub(r"((?:assets/(?:library|own))/[A-Za-z0-9_.-]+?)_THUMB\.webp", lambda m: m.group(1) + ("_FULL.webp" if m.group(1) + "_THUMB.webp" in sw else "_THUMB.webp"), text)

    def dedupe(m):   # a srcset that now names the same file twice keeps its largest width
        seen = {}
        for c in [c.strip() for c in m.group(1).split(",") if c.strip()]:
            parts = c.split()
            url, w = parts[0], (int(parts[1][:-1]) if len(parts) > 1 and parts[1].endswith("w") and parts[1][:-1].isdigit() else 0)
            if url not in seen or w > seen[url][0]:
                seen[url] = (w, c)
        return 'srcset="' + ", ".join(v[1] for v in seen.values()) + '"'
    return re.sub(r'srcset="([^"]*)"', dedupe, text)
MAX_ARTIFACT_FILES = 511
MAX_FILES, MAX_BYTES = 250, 60 * 1024 * 1024


def all_files():
    out = []
    for d, dirs, files in os.walk(SITE):
        rel_d = os.path.relpath(d, SITE)
        if rel_d != "." and rel_d.split(os.sep)[0] in EXCLUDE_TOP:
            continue
        for f in files:
            rel = os.path.normpath(os.path.join(rel_d, f)).replace(os.sep, "/")
            if rel.split("/")[0] in EXCLUDE_TOP or rel == "index.html" or rel.startswith(EXCLUDE_PREFIX) or rel in thumb_swaps():
                continue
            out.append(rel)
    return sorted(out)


MARK = os.path.join(REPO, "docs", "artifact-published.txt")  # commit whose site/ is live on the artifact


def changed_files():
    try:
        base = open(MARK).read().split()[0]
    except (OSError, IndexError):
        sys.exit(f"{os.path.relpath(MARK, REPO)} missing: publish everything once, then write the commit id into it")
    try:
        r = subprocess.run(["git", "diff", "--name-only", "--diff-filter=ACMR", base, "--", "site"],
                           cwd=REPO, capture_output=True, text=True, check=True)
    except subprocess.CalledProcessError:
        sys.exit(f"Commit {base} from {os.path.relpath(MARK, REPO)} not found (shallow clone? run: git fetch --unshallow)")
    rels = [p[len("site/"):] for p in r.stdout.split() if p.startswith("site/")]
    return sorted(p for p in rels if p.split("/")[0] not in EXCLUDE_TOP and p != "index.html" and not p.startswith(EXCLUDE_PREFIX))


def artifact_source(rel):
    """Path to publish for rel: the file itself, or a rewritten copy (no visitor log, no assets/resp/, no left-out thumbnails)."""
    src = os.path.join(SITE, rel)
    if not rel.endswith((".html", ".js", ".css")):
        return src
    text = orig = open(src, encoding="utf-8").read()
    if rel in NO_TRACK:
        assert text.count(NO_TRACK[rel]) == 1, f"{rel}: tracker loader not found"
        text = text.replace(NO_TRACK[rel], "if (false) {  /* artifact preview: no visitor log */")
    if rel.endswith(".html") and "assets/resp/" in text:
        def fix_set(m):
            cands = [c for c in m.group(1).split(",") if "assets/resp/" not in c]
            return ('srcset="' + ",".join(cands).strip() + '"') if cands else ""
        text = re.sub(r'srcset="([^"]*)"', fix_set, text)
        text = re.sub(r'((?:\.\./)*)assets/resp/v-([a-z0-9-]+)\.webp', r'\1v/img/\2.jpg', text)
    if "_THUMB.webp" in text:
        text = swap_thumbs(text)
    if text == orig:
        return src
    out = os.path.join(BUILD, rel)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, "w", encoding="utf-8").write(text)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--changed", action="store_true")
    ap.add_argument("--update", action="store_true", help="removals for the live artifact first, then every file that is new, changed or rewritten")
    a = ap.parse_args()
    removals = []
    shutil.rmtree(BUILD, ignore_errors=True)
    if a.update:
        # the live artifact holds what the marker commit's site/ gave under the same rules (thumbnails with a FULL
        # copy left out unless that commit's home page used them); send what is new or changed since, plus every
        # page or script that names a thumbnail that is now left out or kept where it was not before
        base = open(MARK).read().split()[0]
        r = subprocess.run(["git", "ls-tree", "-r", "--name-only", base, "--", "site"], cwd=REPO, capture_output=True, text=True, check=True)
        tree = {p[len("site/"):] for p in r.stdout.split() if p.startswith("site/")}
        home = subprocess.run(["git", "show", f"{base}:site/{KEEP_THUMBS_OF}"], cwd=REPO, capture_output=True, text=True, check=True).stdout
        swaps_then = {p for p in tree if p.startswith(THUMB_DIRS) and p.endswith("_THUMB.webp") and p not in home
                      and p.replace("_THUMB.webp", "_FULL.webp") in tree}
        live = {p for p in tree if p.split("/")[0] not in EXCLUDE_TOP and not p.startswith(EXCLUDE_PREFIX)} - swaps_then
        now = set(all_files()) | {"index.html"}
        removals = sorted(live - now)
        changed = set(changed_files())
        moved = swaps_then ^ thumb_swaps()
        def names_moved(p):
            if not p.endswith((".html", ".js", ".css")) or not moved:
                return False
            text = open(os.path.join(SITE, p), encoding="utf-8").read()
            return any(m in text for m in moved)
        files = [p for p in all_files() if p not in live or p in changed or names_moved(p)]
        print(f"live artifact (commit {base[:8]}): {len(live)} files; remove {len(removals)}; send {len(files)}; thumbnails moved in or out: {len(moved)}")
    else:
        files = changed_files() if a.changed else all_files()
    total = len(all_files()) + 1
    if total > MAX_ARTIFACT_FILES:
        sys.exit(f"The artifact would hold {total} files; the limit is {MAX_ARTIFACT_FILES}. Exclude more (EXCLUDE_PREFIX).")
    batches, cur, size = [], {}, 0
    for rel in removals:   # removals go first, so no intermediate version holds more than the limit
        if cur and len(cur) >= MAX_FILES:
            batches.append(cur)
            cur, size = {}, 0
        cur[rel] = None
    for rel in files:
        s = os.path.getsize(os.path.join(SITE, rel))
        if cur and (len(cur) >= MAX_FILES or size + s > MAX_BYTES):
            batches.append(cur)
            cur, size = {}, 0
        cur[rel] = os.path.relpath(artifact_source(rel), REPO)
        size += s
    if cur:
        batches.append(cur)
    os.makedirs(OUT, exist_ok=True)
    for old in os.listdir(OUT):
        os.remove(os.path.join(OUT, old))
    for i, b in enumerate(batches, 1):
        with open(os.path.join(OUT, f"batch-{i}.json"), "w") as fh:
            json.dump(b, fh, indent=0)
    page = os.path.relpath(artifact_source("index.html"), REPO)
    print(f"{len(files)} supporting files and {len(removals)} removals in {len(batches)} batch(es); page: {page}; artifact total {total} of {MAX_ARTIFACT_FILES}")
    for i, b in enumerate(batches, 1):
        print(f"  preview/artifact-batches/batch-{i}.json  {len(b)} files")


if __name__ == "__main__":
    main()
