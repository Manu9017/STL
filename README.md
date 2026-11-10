# SHIVAS website

Website for the SHIVAS group, Ghaziabad, India: SHIVAS Technology Limited (hot-dip galvanizing plants, wire drawing machines), SHIVAS Reinplast Company of India (PP/FRP tanks, scrubbers, pickling, ETP/ZLD) and SHIVAS Products India (FRP profiles and resins).

- `site/`: **the live site**. Plain HTML/CSS/JS with no build step. Open `site/index.html`, or see `site/README.md` for GitHub Pages hosting.
- `CLAUDE.md`: how the site is organised and the rules for editing it. Start here.
- `tools/`: `check_site.py` (links, SEO, claims, counts), `a11y.cjs` (axe, light and dark), `lighthouse.sh` (speed), `screenshot.cjs` (screenshots), `fix_img_sizes.py`, `responsive_images.py`, `artifact_files.py`.
- `.claude/skills/`: Claude Code skills: `site-check`, `site-audit`, `site-preview`, `site-edit`, `viewer-3d`, `tracking-setup`, `publish-artifact`.
- `design/`, `assets/`, `docs/astro-rebuild-brief.md`: earlier design handoff for an Astro rebuild (on hold).

Shared preview: https://claude.ai/artifact/QbaMojD3TugfPsudMNCAXJ

```bash
python3 tools/check_site.py          # before every commit
node tools/screenshot.cjs            # desktop and phone screenshots of key pages
node tools/a11y.cjs                  # accessibility, every page, light and dark
tools/lighthouse.sh                  # Lighthouse scores (phone and desktop)
```
