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
| `blog/*.html` | 59 articles plus `blog/index.html` (filters by topic; the featured card is the newest flagship article, and the filter script hides it unless its own topic is chosen). |
| `v/*.html` | 12 3D model viewers (three.js from cdnjs), opened from `3d-models.html`, listed most important first. Eleven are self-contained (0.07 to 2.4 MB each, so edit them surgically). `v/hv-furnace.html` (high-velocity furnace, 6.7 m kettle, 22 Nov 2026) loads its model from three base64 text files in `v/hv-furnace/` (about 24 MB, each under the 25 MiB Cloudflare file limit) with its own loader and `data-hint="0"`; its parts list was cleaned of client and commercial data. Each loads `v/shivas-bar.js` (zoom, full screen, a controls hint, and the SHIVAS button with the enquiry menu and a switch-model list). See the `viewer-3d` skill. |
| `calculator.html`, `calculators.html` | Plant calculator (`assets/calc.js`) and 12 more in `assets/calcs.js`, ordered by importance by the `ORDER` list (the plant calculator leads the list): wire drawing, burner kW, the flagship ETP and ZLD plant (neutraliser, sludge, RO, MEE or MVR, crystallizer, ATFD, with a stream table and a process flow SVG), ISO 1461 coating check, wire weight, scrubber, pickling acid, spent acid neutralisation, bag filter, fan, EG rectifier, FRP profile weight and deflection. Each needs a `<span class="cx-a" id="...">` anchor in `calculators.html`. Every formula was checked by hand; keep it that way when you change one. |
| `about`, `contact`, `careers`, `gallery`, `pultrusion`, `privacy`, `3d-models` `.html` | Other pages. |
| `assets/library.js`, `assets/library/` | The image library: every approved picture (PREVIEW / THUMB / FULL webp) and `drawings.svg`. `library.js` is **generated** by the SHIVAS image-library tools, which are not in this repo, so don't hand-edit it. See `site/photos/README.md`. Photos the owner sent after that (22 Nov 2026) are in `assets/own/` and enter the library through `assets/library-extra.js`, loaded right after `library.js` on product and division pages; the originals are in `docs/own-photos/`. Remove the supplement once the image-library tools include them. |
| `assets/site.js` | Site-wide helpers on every page (scroll-to-top, back-to-top, auto rails). It loads `config.js` and `track.js`. |
| `assets/config.js`, `assets/track.js`, `setup/visitor-log/` | Visitor log (Google Sheet + Apps Script), GA4 and company identification. **Currently all off**: `config.js` is empty. When on, it emails each enquiry, an alert when someone opens the site (once per visit, at most 25 a day), and a report every day and every week (to info@ and to the Google account that set it up), and fills the tabs Visits, Pages, Daily, Viewers, Companies and Leads. The claude.ai artifact preview is built without it, so opening the artifact link never sends an alert; alerts come from the real site once it is live. The 3D viewers are counted too, without the consent bar. See the `tracking-setup` skill. |
| `assets/v39.css`, `assets/v39.js` and inline `<style id="v3x">` blocks | Layered design revisions from the chat sessions. Later layers override earlier ones. Prefer editing the latest layer. |
| `assets/fonts/` | Noto Sans latin woff2 (self-hosted; `@font-face` inline in each page as `<style id="v52f">`). |
| `assets/resp/` | 480/960 px copies of large photos and WebP 3D previews, made by `tools/responsive_images.py`. |
| `favicon.ico`, `apple-touch-icon.png` | Cut from the logo's S. |
| `404.html`, `_redirects`, `_headers`, `assets/og/` | Production only, not on the artifact: the not-found page (absolute links, noindex), Cloudflare redirects and headers, and the 1200×630 link-preview images. Every page carries og/twitter tags; items and blog pages carry BreadcrumbList JSON-LD; every page has a theme-color meta. |
| `sitemap.xml`, `robots.txt` | Base URL `https://www.shivastechnology.com/`. Add every new indexable page, viewers included, to the sitemap. |

Each page carries its own `<title>`, meta description, canonical link and JSON-LD (`Organization`, `Product`, `FAQPage`, `Article`). Keep them unique and valid.

## Look
The home page opens with a slideshow (`.hbn` in `<style id="v60home">`, script at the end of `index.html`): the owner's banner (`assets/brand/shivas-banner-2000.webp`; its tiles link to the product pages), then six HD pictures (`assets/brand/slide-*.webp`, phone copies in `assets/resp/`). It moves right on its own every 3 s and visitors can swipe, use the trackpad or drag it with the mouse; no buttons (owner's choice, 12 Nov 2026); on phones it pans across the banner first. It waits while the pointer is over it. Below it, the hero is a mosaic of four SHIVAS own photos, a proof strip of counts taken from the site, and a 3D models section (`index.html`, `<style id="v60home">`).
Current tokens (in each page's inline `:root`): navy `#1f4e79`, teal `#0e7c86` (Reinplast), amber `#e8a317` (primary buttons), ink `#13202c`, muted `#4f6275`, line `#dde5ee`, bg `#f6f8fb`. There is a dark mode under `[data-theme="dark"]`; since 14 Nov 2026 a first-time visitor gets their system theme (the inline theme script in every page head), and a stored choice wins. The home page has a last style layer, `<style id="v70polish">` right after the v39.css link (22 Nov 2026): amber section labels with an accent bar, the "How we work" navy band with numbered steps joined by a line, calculator tiles with navy number badges and an "Open" cue, card lift on hover, bolder proof numbers. Below-the-fold cards fade up once on scroll (MOTION LAYER at the end of `assets/v39.css`, driven by `site.js`; off for reduced motion and on the three division apps).
**Fonts:** headings use Archivo 600–800 and body text uses Noto Sans. Both are self-hosted in `assets/fonts/`, preloaded, with an inline `@font-face` in `<style id="v52f">`. Headings are set in the TYPE LAYER of `assets/v39.css`.
**Navigation:** inner pages share one site nav (`<nav class="snav">`): Home, Products, 3D models, Calculators, Photos, Articles, About, Contact, with `aria-current` on the current section. The home header shows Products, 3D models, Calculators, Articles, About, Contact. Division pages show their section links as a second row (NAV LAYER). The quote button always says **Get a quote**.
**Order:** animations (the explorer tabs), 3D models, product lists and calculators run most important first (owner, 22 Nov 2026), set by the `ord(...)` lists in the division app, the `MODELS` list in `v/shivas-bar.js` and `ORDER` in `assets/calcs.js`.
**Hero photos:** the division pages use `.v61-hm` (one main photo and two linked tiles). Only use a photo for the product it is filed under; see the `site-edit` skill.
Text contrast is WCAG AA in both themes, through the **A11Y LAYER** at the end of `assets/v39.css` (text tones only, scoped per theme). New text colours must pass too; check with `node tools/a11y.cjs`.
The logo-red palette in `docs/astro-rebuild-brief.md` belongs to the on-hold rebuild, not to this site.

## Facts and claims (always)
- No em dashes anywhere on the site (owner, 22 Nov 2026): use a colon, a comma or brackets. `tools/check_site.py` warns about any.
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
- `deploy-site`: go live on www.shivastechnology.com (Cloudflare Pages recommended), domain, 301 redirects from the 2019 site (`site/_redirects`, from `docs/redirects.csv`).
- `enquiry-reply`: draft replies to enquiries as **Gmail drafts** (Gmail and Calendar are connected). Never send without the owner, and never quote prices.
- `write-article`: a new engineering article, from topic to sitemap.
- `content-gaps`: the missing facts and photos, as questions for the owner, applied everywhere.
- `ui-ux-pro-max` (design intelligence: searchable styles, palettes, font pairings, UX guidelines) and `banner-design`: adapted from nextlevelbuilder/ui-ux-pro-max-skill (MIT), with SHIVAS notes on top. The brand palette and the facts rules always win.
- `page-cro`, `form-cro`, `analytics-tracking`, `lead-research-assistant`, `social-content` (draft-only LinkedIn and WhatsApp posts) and `schema-markup` (JSON-LD, with no invented prices or ratings): adapted from davila7/claude-code-templates (MIT), with SHIVAS notes on top.
- **Agents** (`.claude/agents/`, from the same repository with SHIVAS notes): `seo-specialist` and `search-ai-optimization-expert` (audits and advice only, never invented rankings), and `sales-engineer` (technical offers and plant briefs; it pauses for owner sign-off on prices, guarantees and certificates).
- **Installed plugins** (Sales, Marketing, Design, Copywriting, HarborRank, B2B Sales Enablement and others) add generic skills. Where they overlap, these project skills and the facts rules above take priority.

## Workflow
1. Edit under `site/`.
2. Run `python3 tools/check_site.py`. There must be 0 errors and 0 warnings. After style or layout work, also run `node tools/a11y.cjs` and `tools/lighthouse.sh`.
3. Screenshot the pages you changed (desktop and phone) and look at them.
4. Commit on the working branch and push.
5. Republish the artifact only when the user asks. The link is public.
