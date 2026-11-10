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
EXCLUDE_TOP = {"README.md", ".nojekyll", "photos", "setup", "CNAME", "_redirects"}
EXCLUDE_PREFIX = ("assets/resp/",)          # speed copies: production only (artifact file limit)
BUILD = os.path.join(REPO, "preview", "artifact-build")
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
            if rel.split("/")[0] in EXCLUDE_TOP or rel == "index.html" or rel.startswith(EXCLUDE_PREFIX):
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
    """Path to publish for rel: the file itself, or a rewritten copy without assets/resp/ references."""
    src = os.path.join(SITE, rel)
    if not rel.endswith(".html"):
        return src
    text = open(src, encoding="utf-8").read()
    if "assets/resp/" not in text:
        return src

    def fix_set(m):
        cands = [c for c in m.group(1).split(",") if "assets/resp/" not in c]
        return ('srcset="' + ",".join(cands).strip() + '"') if cands else ""
    text = re.sub(r'srcset="([^"]*)"', fix_set, text)
    text = re.sub(r'((?:\.\./)*)assets/resp/v-([a-z0-9-]+)\.webp', r'\1v/img/\2.jpg', text)
    out = os.path.join(BUILD, rel)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, "w", encoding="utf-8").write(text)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--changed", action="store_true")
    a = ap.parse_args()
    files = changed_files() if a.changed else all_files()
    shutil.rmtree(BUILD, ignore_errors=True)
    total = len(all_files()) + 1
    if total > MAX_ARTIFACT_FILES:
        sys.exit(f"The artifact would hold {total} files; the limit is {MAX_ARTIFACT_FILES}. Exclude more (EXCLUDE_PREFIX).")
    batches, cur, size = [], {}, 0
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
    print(f"{len(files)} supporting files in {len(batches)} batch(es); page: {page}; artifact total {total} of {MAX_ARTIFACT_FILES}")
    for i, b in enumerate(batches, 1):
        print(f"  preview/artifact-batches/batch-{i}.json  {len(b)} files")


if __name__ == "__main__":
    main()
