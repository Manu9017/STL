---
name: publish-artifact
description: Republish the SHIVAS website from site/ to its claude.ai artifact (https://claude.ai/artifact/QbaMojD3TugfPsudMNCAXJ) so the shared link shows the latest version. Use only when the user asks to publish, republish, update the artifact or update the shared link.
---

# Publish site/ to the claude.ai artifact

Artifact: **https://claude.ai/artifact/QbaMojD3TugfPsudMNCAXJ** (`index.html` is the page; 508 supporting files as of 12 Nov 2026, version 58; robots.txt and sitemap.xml are production only).
Anyone with the link sees an update straight away, so **publish only when the user asks**, and only after the `site-check` skill reports 0 errors.

## Steps
1. **Read the artifact first.** A publish is refused unless this conversation has read it.
   Call `Artifact` with `action: "read"` and the URL. If the live version has changes that aren't in `site/` (someone edited it in chat), stop and tell the user. Merge those changes into `site/` before publishing, so they aren't overwritten.
2. **Mind the file limit.** One artifact version holds at most **511 files**, and the real site has more. So the artifact gets a lighter preview build:
   - `assets/resp/` (the speed copies of photos) is left out;
   - pages that reference it are rewritten into `preview/artifact-build/`, with those `srcset` candidates removed and the home page's 3D previews pointed at `v/img/*.jpg`.

   `tools/artifact_files.py` does all of this and prints `artifact total N of 511`. If a new feature pushes the total over, add another production-only prefix to `EXCLUDE_PREFIX` in that script, and give the pages a fallback that works without it.
3. **Make the batches:**
   ```bash
   python3 tools/artifact_files.py            # everything (first publish from a new session)
   python3 tools/artifact_files.py --changed  # only files changed since the last publish
   ```
   This writes `preview/artifact-batches/batch-N.json`. Each is a `files` map of `{"published/path": "site/published/path"}`, kept under the 255-file limit for one publish. `README.md`, `photos/`, `setup/` and `.nojekyll` are not published.
4. **Publish batch 1 with the page:** `Artifact` publish with:
   - `url`: the artifact URL;
   - `file_path`: the page the script prints (usually `preview/artifact-build/index.html`);
   - `files`: the contents of `batch-1.json`, with absolute paths. Give `.woff2` the contentType `font/woff2` and `.ico` the contentType `image/x-icon`. Leave out `icon`, since the artifact keeps its own.
5. **Publish each later batch** to the same `url` with the same `file_path` and the next batch's `files`. Files left out of a publish are kept, so the batches add up.
6. To remove a page from the artifact, publish with that path mapped to `null`.
7. **Record what was published** so the next `--changed` run knows. Git tags can't be pushed from cloud sessions, so the commit id goes in a file:
   ```bash
   git rev-parse HEAD > docs/artifact-published.txt   # the commit whose site/ you just published
   git commit -m "Record artifact publish" docs/artifact-published.txt && git push
   ```
8. Give the user the link and say what changed.

## Notes
- The service rewrites the page head when it stores `index.html`: it drops `<!DOCTYPE><html><head>` and moves the `<title>`, meta tags and `<style>` blocks. So the first publish in a session is refused with a diff that shows these moves. That's expected. Check the diff for **real content** that is on the live page and not in `site/index.html`. If there is any, merge it in. If there's none, publish again unchanged and it goes through.
- Example (10 Nov 2026): the live page still had `--m:"IBM Plex Mono"` where `site/` has `--m:"Noto Sans"`. Noto Sans is correct: it matches `assets/v39.css`, the newest layer, and the font the page loads.
- If the only change is in `index.html`, publish the page without `files`.
- Pages link with relative paths (`items/kettle.html`, `../assets/…`). Keep them relative so the same files work on the artifact, GitHub Pages and a custom domain.
