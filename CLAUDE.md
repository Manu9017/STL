# CLAUDE.md: SHIVAS website

Read this first.

## What this repo is
The website for the SHIVAS group, Ghaziabad, India:
- **SHIVAS Technology Limited** (since 2019): hot-dip galvanizing plants and wire drawing machines.
- **SHIVAS Reinplast Company of India** (since 1991): PP/FRP tanks, fume scrubbers, pickling, ETP and ZLD.
- **SHIVAS Products India** (since 2002): FRP pultruded profiles and resins.

The company name is always written **SHIVAS** in capitals.

| Path | What it is |
|---|---|
| `site/` | **The live website and the source of truth.** Plain HTML, CSS and JS. No build step. It was built in Claude chat, published as the artifact https://claude.ai/artifact/QbaMojD3TugfPsudMNCAXJ and imported here on 10 Nov 2026. |
| `tools/` | `check_site.py` (links, SEO, claims, counts), `a11y.cjs` (axe), `lighthouse.sh`, `screenshot.cjs` (screenshots and a gzip server), `fix_img_sizes.py`, `responsive_images.py`, `artifact_files.py`. |
| `.claude/skills/` | Project skills for working on the site. |
| `design/`, `assets/`, `preview/build.py` | The earlier design handoff for an Astro rebuild. **On hold.** Its brief is kept in `docs/astro-rebuild-brief.md`. Do not build from it unless the user asks. |
| `docs/` | Redirect map, due-diligence list, content checklist, the old brief. |

## How `site/` is put together
| Path | Notes |
|---|---|
| `index.html` | Home page (gateway to the companies, calculators, photos, articles, enquiry form). |
| `galvanizing.html`, `wire-drawing.html`, `reinplast.html` | **One shared app, three copies.** Each is about 800 KB with `<div id="app" data-page="hdg / wire / …">`. They differ only in the title, meta, `data-page` and a few self-links. **Any change to shared content must go into all three.** `tools/check_site.py` reports how far they have drifted. |
| `items/*.html` | One page per product, line or plant (about 85). `items/index.html` lists them all. Shared styles in `assets/item.css`, script in `assets/item.js`. `items/r-frp.html` is a redirect stub. |
| `blog/*.html` | 25 articles plus `blog/index.html`. |
| `v/*.html` | 11 self-contained 3D model viewers (three.js from cdnjs), opened from `3d-models.html`. They are 0.07–2.4 MB each, so edit them surgically. Each loads `v/shivas-bar.js` (the SHIVAS button with the enquiry menu). See the `viewer-3d` skill. |
| `calculator.html`, `calculators.html` | Plant calculator (`assets/calc.js`) and the other calculators (`assets/calcs.js`). |
| `about`, `contact`, `careers`, `gallery`, `pultrusion`, `privacy`, `3d-models` `.html` | Other pages. |
| `assets/library.js`, `assets/library/` | The image library: every approved picture (PREVIEW / THUMB / FULL webp) and `drawings.svg`. `library.js` is **generated** by the SHIVAS image-library tools, which are not in this repo, so don't hand-edit it. See `site/photos/README.md`. |
| `assets/site.js` | Site-wide helpers on every page (scroll-to-top, back-to-top, auto rails). It loads `config.js` and `track.js`. |
| `assets/config.js`, `assets/track.js`, `setup/visitor-log/` | Visitor log (Google Sheet + Apps Script), GA4 and company identification. **Currently all off**: `config.js` is empty. Turning it on is a privacy decision, so ask the user first and keep `privacy.html` in step. |
| `assets/v39.css`, `assets/v39.js` and inline `<style id="v3x">` blocks | Layered design revisions from the chat sessions. Later layers override earlier ones. Prefer editing the latest layer. |
| `assets/fonts/` | Noto Sans latin woff2 (self-hosted; `@font-face` inline in each page as `<style id="v52f">`). |
| `assets/resp/` | 480/960 px copies of large photos and WebP 3D previews, made by `tools/responsive_images.py`. |
| `favicon.ico`, `apple-touch-icon.png` | Cut from the logo's S. |
| `sitemap.xml`, `robots.txt` | Base URL `https://www.shivastechnology.com/`. Add every new indexable page, viewers included, to the sitemap. |

Each page carries its own `<title>`, meta description, canonical link and JSON-LD (`Organization`, `Product`, `FAQPage`, `Article`). Keep them unique and valid.

## Look
The home page hero is a mosaic of four SHIVAS own photos, a proof strip of counts taken from the site, and a 3D models section (`index.html`, `<style id="v60home">`).
Current tokens (in each page's inline `:root`): navy `#1f4e79`, teal `#0e7c86` (Reinplast), amber `#e8a317` (primary buttons), ink `#13202c`, muted `#4f6275`, line `#dde5ee`, bg `#f6f8fb`. There is a dark mode under `[data-theme="dark"]`. Font: Noto Sans, self-hosted.
Text contrast is WCAG AA in both themes, through the **A11Y LAYER** at the end of `assets/v39.css` (text tones only, scoped per theme). New text colours must pass too; check with `node tools/a11y.cjs`.
The logo-red palette in `docs/astro-rebuild-brief.md` belongs to the on-hold rebuild, not to this site.

## Facts and claims (always)
- Never invent numbers, clients, projects, certificates or photos. If a fact is missing, write `[bracketed]` and add it to `docs/content-checklist.md`.
- Don't claim CE, ISO 9001 or EN 746 until the certificates are confirmed. Exception: the EN 746-2 references in the spec tables of the 3D viewers `v/arp-10.html`, `v/spin-galvanizing.html` and `v/zinc-ash-plant.html` were reviewed and kept by the owner on 10 Nov 2026. Don't add EN 746 anywhere else.
- Don't cite BS 729. Use ISO 1461, ASTM A123, IS 2629 and IS 4759.
- Don't copy any competitor's text or images.
- Enquiries go to SHIVAS only. Never copy leads to a third party (the 2019 site copied them to clquery@indianbusinesshub.com).
- Contacts in the site (all confirmed valid, 10 Nov 2026): enquiry desk and WhatsApp +91 98109 20468; sales +91 98102 80104 and +91 98186 10744; info@shivastechnology.com. Change them everywhere at once (header, mobile menu, dock, enquiry section, footer, JSON-LD).

## Skills (in `.claude/skills/`)
- `site-check`: run `python3 tools/check_site.py`. It checks links, SEO tags, JSON-LD, sitemap, claims, placeholders and division-page drift. **Run it before every commit.**
- `site-preview`: serve and screenshot pages on desktop and phone with `node tools/screenshot.cjs`.
- `site-edit`: how to change copy, add a product page or an article, and keep the shared pages in step.
- `site-audit`: Lighthouse and axe, with baselines (home 96–100, product pages 98–100 on phone; axe 4 known issues).
- `viewer-3d`: the 3D viewers, the SHIVAS button positions, and adding a model.
- `tracking-setup`: turning on the visitor log or GA4 once the owner sends the Apps Script URL or the `G-` ID.
- `publish-artifact`: republish `site/` to the claude.ai artifact so the shared link shows the latest version.

## Workflow
1. Edit under `site/`.
2. Run `python3 tools/check_site.py`. There must be 0 errors and 0 warnings. After style or layout work, also run `node tools/a11y.cjs` and `tools/lighthouse.sh`.
3. Screenshot the pages you changed (desktop and phone) and look at them.
4. Commit on the working branch and push.
5. Republish the artifact only when the user asks. The link is public.
