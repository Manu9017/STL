---
name: site-check
description: Check the SHIVAS website in site/ for broken links and images, missing or duplicate titles and descriptions, canonical links, invalid JSON-LD, sitemap gaps, banned certificate/standard claims, [bracketed] placeholders, third-party lead e-mails, home-page counts that no longer match the site, and drift between the three division pages. Use before every commit to site/, after any edit, or when the user asks for an SEO / link / quality check.
---

# Site check

Run from the repo root:

```bash
python3 tools/check_site.py            # full report
python3 tools/check_site.py --quiet    # totals and errors only
python3 tools/check_site.py --anchors  # also flag #anchors not found in the target page (many are made by script, so these are hints only)
```

The exit code is 1 when there are errors.

## Reading the report
**Errors must be fixed before committing:**
- `broken href/src`: a link or image points at a file that doesn't exist. Fix the path. Item and blog pages link with `../`.
- `no <title>` / `no meta description`: every indexable page needs both, and they must be unique.
- `invalid JSON-LD`: the `<script type="application/ld+json">` block won't parse. Check for a trailing comma or an unescaped quote.
- `enquiry copied to a third party`: remove it. Leads go to SHIVAS only.
- `sitemap.xml: … has no file`: remove the entry, or restore the page.

**Warnings: compare with the baseline.** On 10 Nov 2026 (after the image-size, canonical and sitemap fixes) the site had **0 errors and 0 warnings**. The EN 746-2 references in three 3D viewers were kept by the owner and are allow-listed in `EN746_KEPT`. Any other EN 746 mention still warns.

Home-page counts: the proof strip and the "All N …" links on `index.html` must match the site (products in `items/index.html`, pages in `v/` and `blog/`, the gallery's "All" count). A warning names the number to update.

Any `<img> without width/height` on a new or edited page: run `python3 tools/fix_img_sizes.py <page>`. It adds the real pixel size. Then screenshot the page.

Any warning that is **new** compared with the baseline was probably caused by your edit, so fix it. If a known warning is fixed, update the baseline numbers in this file.

The header line `Division pages vs galvanizing.html, differing lines` should stay near 71 (wire-drawing) and 103 (reinplast). A jump means a shared edit reached only one of the three division pages.

For speed and accessibility, use the `site-audit` skill (Lighthouse and axe).

## After the check
Tell the user the totals. If you fixed anything, say what. Don't silently change copy to clear a claim or placeholder warning: those are facts the user has to confirm.
