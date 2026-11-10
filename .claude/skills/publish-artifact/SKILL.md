---
name: publish-artifact
description: Republish the SHIVAS website from site/ to its claude.ai artifact (https://claude.ai/artifact/QbaMojD3TugfPsudMNCAXJ) so the shared link shows the latest version. Use only when the user asks to publish, republish, update the artifact or update the shared link.
---

# Publish site/ to the claude.ai artifact

Artifact: **https://claude.ai/artifact/QbaMojD3TugfPsudMNCAXJ** (`index.html` is the page; 498 supporting files at import).
Anyone with the link sees an update straight away, so **publish only when the user asks**, and only after the `site-check` skill reports 0 errors.

## Steps
1. **Read the artifact first.** A publish is refused unless this conversation has read it.
   Call `Artifact` with `action: "read"` and the URL. If the live version has changes that aren't in `site/` (someone edited it in chat), stop and tell the user. Merge those changes into `site/` before publishing, so they aren't overwritten.
2. **Make the batches:**
   ```bash
   python3 tools/artifact_files.py            # everything (first publish from a new session)
   python3 tools/artifact_files.py --changed  # only files changed since the last publish
   ```
   This writes `preview/artifact-batches/batch-N.json`. Each is a `files` map of `{"published/path": "site/published/path"}`, kept under the 255-file limit for one publish. `README.md`, `photos/`, `setup/` and `.nojekyll` are not published.
3. **Publish batch 1 with the page:** `Artifact` publish with `url` = the artifact URL, `file_path` = `site/index.html`, and `files` = the contents of `batch-1.json`. Leave out `icon`, since the artifact keeps its own.
4. **Publish each later batch** to the same `url` with the same `file_path` and the next batch's `files`. Files left out of a publish are kept, so the batches add up.
5. To remove a page from the artifact, publish with that path mapped to `null`.
6. **Tag the commit** so the next `--changed` run knows what was published:
   ```bash
   git tag -f artifact-published && git push -f origin artifact-published
   ```
7. Give the user the link and say what changed.

## Notes
- If the only change is in `index.html`, publish the page without `files`.
- Pages link with relative paths (`items/kettle.html`, `../assets/…`). Keep them relative so the same files work on the artifact, GitHub Pages and a custom domain.
