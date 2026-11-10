#!/usr/bin/env python3
"""Print the `files` maps for republishing site/ to its claude.ai artifact.

    python3 tools/artifact_files.py            # summary + batch files written to preview/artifact-batches/
    python3 tools/artifact_files.py --changed  # only files changed since the last publish (git diff against the tag)

One Artifact publish takes at most 255 supporting files and 64 MB, so the site goes up in batches.
index.html is the page itself (file_path), everything else is a supporting file. Files that are not
part of the public site (README.md, photos/, setup/, .nojekyll) are left out.
Each batch is written as JSON: {"published/path": "site/published/path", ...}
"""
import argparse
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
SITE = os.path.join(REPO, "site")
OUT = os.path.join(REPO, "preview", "artifact-batches")
EXCLUDE_TOP = {"README.md", ".nojekyll", "photos", "setup", "CNAME"}
MAX_FILES, MAX_BYTES = 250, 60 * 1024 * 1024
TAG = "artifact-published"


def all_files():
    out = []
    for d, dirs, files in os.walk(SITE):
        rel_d = os.path.relpath(d, SITE)
        if rel_d != "." and rel_d.split(os.sep)[0] in EXCLUDE_TOP:
            continue
        for f in files:
            rel = os.path.normpath(os.path.join(rel_d, f)).replace(os.sep, "/")
            if rel.split("/")[0] in EXCLUDE_TOP or rel == "index.html":
                continue
            out.append(rel)
    return sorted(out)


def changed_files():
    try:
        r = subprocess.run(["git", "diff", "--name-only", "--diff-filter=ACMR", TAG, "--", "site"],
                           cwd=REPO, capture_output=True, text=True, check=True)
    except subprocess.CalledProcessError:
        sys.exit(f"No git tag '{TAG}' yet: publish everything once, then run: git tag -f {TAG}")
    rels = [p[len("site/"):] for p in r.stdout.split() if p.startswith("site/")]
    return sorted(p for p in rels if p.split("/")[0] not in EXCLUDE_TOP and p != "index.html")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--changed", action="store_true")
    a = ap.parse_args()
    files = changed_files() if a.changed else all_files()
    batches, cur, size = [], {}, 0
    for rel in files:
        s = os.path.getsize(os.path.join(SITE, rel))
        if cur and (len(cur) >= MAX_FILES or size + s > MAX_BYTES):
            batches.append(cur)
            cur, size = {}, 0
        cur[rel] = "site/" + rel
        size += s
    if cur:
        batches.append(cur)
    os.makedirs(OUT, exist_ok=True)
    for old in os.listdir(OUT):
        os.remove(os.path.join(OUT, old))
    for i, b in enumerate(batches, 1):
        with open(os.path.join(OUT, f"batch-{i}.json"), "w") as fh:
            json.dump(b, fh, indent=0)
    print(f"{len(files)} supporting files in {len(batches)} batch(es); page: site/index.html")
    for i, b in enumerate(batches, 1):
        print(f"  preview/artifact-batches/batch-{i}.json  {len(b)} files")


if __name__ == "__main__":
    main()
