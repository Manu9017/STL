# CLAUDE.md — shivastechnology.com rebuild

Read this first. It is the brief for building the production site from the approved design.

## Goal
Replace the 2019 site at shivastechnology.com with a fast, static, SEO-strong site.
- Positioning: closest to Assomac (wire drawing) and Arvind Corrotech (turnkey HDG).
- Visitors land on a gateway and choose one of two divisions: **Wire drawing** or **Hot dip galvanizing**.
- The company name is always written **SHIVAS** in capitals.

## Source of truth
- `design/artboards/*.dc.html` — approved page designs, with all copy, layout, colours and inline SVG.
  - They use a design-canvas format: `{{hole}}` bindings, `<sc-for>` loops, `<sc-if>` branches, a `class Component extends DCLogic` script and `<helmet>`. Treat these as specs. Do **not** ship them as they are.
  - Links point to `X.dc.html`. Map them to the real routes in the table below.
- `design/generator/*.py` — the Python that generated the artboards. It holds all copy, stage data, spec tables and SVG functions in structured form, which is easier to port than the HTML.
- `assets/illustrations/*.svg` — every illustration exported as a standalone SVG. Use these; don't redraw them.
- `docs/` — the redirect map, the due-diligence list and the content checklist.

## Stack (recommended)
- **Astro** (static output), TypeScript, plain CSS with custom properties. No UI framework unless an island needs one.
- Two interactive islands, in vanilla TS or Preact:
  1. The galvanizing process explorer: 9 stages, crane follows the selection, prev/next buttons.
  2. The wire die sequence calculator: inputs D, d, n and v. Per-pass reduction r = 1 − (d/D)^(2/n). Die i diameter = D·(d/D)^(i/n). Block speed = v·(d/dᵢ)².
- Content lives in Markdown/MDX with content collections: `products`, `knowledge`, `projects`.
- Deploy to Cloudflare Pages, Netlify or Vercel. Handle redirects at the host (`public/_redirects`).

## Design tokens
| Token | Value | Use |
|---|---|---|
| ink | #102638 | dark grounds, galvanizing hero |
| blue | #1F4E79 | SHIVAS brand, logo |
| teal | #0E7C86 / dark #0A5C63 | wire division accent |
| amber | #E3A23B / dark #8A5A12 for text on light | galvanizing accent, primary CTA |
| zinc | #E7ECEF | light section ground |
| paper | #F6F8F9 | page ground |
| rule | #CFD8DE | borders |
| text / muted | #1B2B39 / #4A5B6A | on light |
| on-dark / muted | #E9EEF2 / #A9B8C5 | on dark |

- Font: **Archivo** variable (Google Fonts, `wdth 62..125`, `wght 100..900`). Self-host it.
  - Headings: `font-stretch: 112–125%`, weight 800.
  - Body: 100%, 400–500.
- Buttons have a 2px radius. Sections are left-aligned on a 1280px content width with 80px side margins.
- Motion is limited to the running wire and the pulsing burner flames. Respect `prefers-reduced-motion`.
- Keep the look as designed. No gradient washes, emoji, all-caps labels or card shadows.

## Routes
| Artboard | Route |
|---|---|
| Main.dc.html | `/` |
| WireDrawing.dc.html | `/wire-drawing/` (sections: `#straight-line`, `#oto`, `#line`, `#calculator`) |
| Galvanizing.dc.html | `/galvanizing/` (sections: `#process`, `#systems`, `#air-water`, `#automation`, `#knowledge`) |
| Furnace.dc.html | `/galvanizing/pulse-fired-furnaces/`. This is the **template for every product page.** |
| About.dc.html | `/company/` |
| Contact.dc.html | `/contact/` |
| Mobile.dc.html | Reference for the responsive layout below 768px |

Product pages to build from the furnace template:
- Galvanizing: zinc-kettles, kettle-enclosures, enclosed-process-rooms, pp-frp-process-tanks, flux-filtration-regeneration, zinc-fume-extraction, acid-fume-extraction, etp-zld, dryers-heat-recovery, cranes-material-handling, automation-scada.
- Wire drawing: straight-line-machines, oto-machines, pay-offs, descalers, pointing-butt-welding, die-boxes, dead-block-coilers, spoolers, take-ups, inverted-vertical-machines, annealing-furnaces, galvanized-wire-lines, drives-control-panels.

Also create:
- `/knowledge/` hub, with the 6 article stubs listed on the galvanizing page.
- `/projects/` (case studies).
- `/privacy/`, `/terms/` and a 404 page.

## Must-dos
1. **Enquiry form.** Post to our own endpoint (Formspree, Web3Forms or a serverless function) and deliver to info@shivastechnology.com only. The old site copied every lead to clquery@indianbusinesshub.com. Do not reproduce that.
2. **Redirects.** Apply every row in `docs/redirects.csv` as a 301 redirect.
3. **SEO:**
   - Unique title and description on every page.
   - `Organization` + `LocalBusiness` JSON-LD sitewide, `Product` on product pages, `BreadcrumbList`.
   - `sitemap.xml`, `robots.txt` and canonical URLs.
   - Open Graph images.
4. **Performance.** Target Lighthouse 95+. Inline SVG where it is animated. Serve photos as AVIF/WebP with explicit width and height.
5. **Accessibility.** Real buttons, links and labels (already in the design), visible focus rings, AA contrast.
6. **Placeholders.** Every `[bracketed]` string is a fact still to be supplied. Collect them into `docs/content-checklist.md` and never invent numbers, clients or certificates.
7. **Contact actions.** WhatsApp click-to-chat: `https://wa.me/919810280104`. Phone: `tel:+919810280104`.
8. **Footer.** Include CIN and GSTIN, links to the group sites (shivasasia.com, pptanks.com, pickling-plants.com, frpblower.com) and a privacy policy compliant with India's DPDP Act 2023.

## Don't
- Don't copy any competitor's text or images.
- Don't claim CE, ISO 9001 or EN 746 until the certificates are confirmed.
- Don't cite BS 729. Use ISO 1461, ASTM A123, IS 2629 and IS 4759.
