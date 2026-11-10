---
name: site-audit
description: Measure and fix speed (Lighthouse) and accessibility (axe, light and dark mode) on the SHIVAS website in site/. Use when the user asks about speed, Lighthouse, Core Web Vitals, SEO score, accessibility, contrast or WCAG, after changing CSS, fonts, images or page structure, and before a publish that touched many pages.
---

# Speed and accessibility audit

Two tools, both run from the repo root. Both serve `site/` themselves.

```bash
tools/lighthouse.sh                                   # home, galvanizing, items/kettle; phone + desktop
tools/lighthouse.sh items/slm.html blog/index.html    # any pages
node tools/a11y.cjs                                   # axe on every page (not v/), light + dark, phone width (~3 min)
node tools/a11y.cjs index.html items/kettle.html      # a few pages
```

- `lighthouse.sh` installs Lighthouse once into `~/.cache/shivas-lighthouse` (axe-core comes with it). It serves the site with gzip, as GitHub Pages and Cloudflare do, so the scores match production. It prints a score row per page and form factor, then any failing binary audits. The JSON reports go to `preview/lighthouse/`, which is git-ignored.
- `a11y.cjs` prints one line per rule and selector, with the number of pages and the theme(s) affected.

## Baseline (10 Nov 2026)
| Page | Phone perf / a11y / best / SEO | Desktop |
|---|---|---|
| index.html | 96 / 100 / 100 / 100 | 100 across |
| items/kettle.html, items/slm.html | 98 / 100 / 100 / 100 | 100 across |
| blog/pickling-right.html | 100 / 100 / 100 / 100 | 100 across |
| galvanizing.html | about 82 / 99 / 100 / 100 | 100 / 99 |

The galvanizing, wire-drawing and Reinplast pages are each an 800 KB single-page app (8,700 DOM nodes), and that is what holds their phone score back. Don't refactor them for it unless asked.

axe on all 118 pages × 2 themes: **4 known issues, 12 instances**, all inside the galvanizing and Reinplast apps:
- `#stName` heading order;
- two `hall-card` buttons that contain links (`nested-interactive`);
- `.totop` outside a landmark.

Anything else is new. Fix it.

## How the site is kept fast (don't undo these)
- **Font:** Noto Sans latin only, `assets/fonts/noto-sans-latin.woff2` (36 KB). It is preloaded, and the `@font-face` is inline in each page's `<style id="v52f">`. Never add Google Fonts back to the pages. The 3D viewers load their own fonts, and that's fine.
- **Photos:**
  - Every `<img>` has width/height. Run `python3 tools/fix_img_sizes.py <page>` for new pages.
  - Large photos get 480/960 px copies in `assets/resp/` plus `srcset`. Run `python3 tools/responsive_images.py`. It is idempotent and never touches `assets/library/`.
  - The hero image gets `fetchpriority="high"`. Images below the fold get `loading="lazy" decoding="async"`.
- **Scripts:** `site.js` is `defer`. Don't add render-blocking scripts in `<head>`.

## How contrast is kept at AA
- The fixes live in the **A11Y LAYER** at the end of `assets/v39.css`. It changes **text tones only**. Brand colours stay for fills, borders and icons.
- Light-mode rules are scoped `:root:not([data-theme="dark"])`. Dark-mode rules are scoped `:root[data-theme="dark"]`.
- Text colours that pass: amber text on white `#945400`; teal text `#0a6e78`; WhatsApp green fill `#15803d` with white text; amber on navy `#ffc35a`; dim grey `#5f7389`.
- In dark mode the accent `--acc` is `#5b9bd5`, so fills that use it carry dark text (`#0b1622`).
- When axe flags a new colour pair, add a narrowly scoped rule to that layer. Don't change the brand variables globally, because the same variable is often used as a fill.
- Footer headings are `<h4 aria-level="2">`. `v39.css` forces every `h2` to the large title style, so don't switch them to `<h2>`.
