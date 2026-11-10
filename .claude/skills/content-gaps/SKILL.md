---
name: content-gaps
description: Work through the facts and photos still missing from the SHIVAS site - list the [bracketed] placeholders and the open items in docs/content-checklist.md, turn them into a short question list for the owner, and apply the answers everywhere they belong. Use when the user asks what's missing, what to fill in, wants to give facts, photos, certificates, clients or numbers, or asks to finish the content checklist.
---

# Content gaps

## Find them
```bash
python3 tools/check_site.py | grep -i placeholder      # [bracketed] strings in pages
sed -n '1,200p' docs/content-checklist.md               # the checklist, including photos still needed
```

## Ask the owner
Group the open items into one short message, at most about 10 questions, with the most valuable first:
1. **Photos:**
   - the SHIVAS Products India pultrusion line and its profiles;
   - own photos of a complete galvanizing plant and of a wire drawing line.

   Photos go through the image library tools: originals go in `originals/supplied/<item-id>/`, then the owner runs `tools/pipeline.py` and approves them. Don't edit `assets/library.js` by hand.
2. **Company facts:** CIN and GSTIN for the footer, year-by-year milestones, and team or plant size if they want them shown.
3. **References** the owner is happy to publish: project names, places, sizes. Only with permission.
4. **Certificates:** whether CE, ISO 9001 or EN 746 are actually held. Until confirmed, none are claimed (except the EN 746-2 references the owner kept in three 3D viewers).

## Apply the answers
- **Replace the placeholders.** Change every copy at once: shared division pages, the home page, footers and JSON-LD. Then tick the item off in `docs/content-checklist.md`, noting the date and that the owner gave the fact.
- **New counts:** if the change adds products or articles, the home-page counts must follow. `check_site.py` warns when they don't.
- **Check and commit:** `python3 tools/check_site.py` must show 0/0. Commit with a message naming what the owner supplied.
