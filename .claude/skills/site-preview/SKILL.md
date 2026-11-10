---
name: site-preview
description: Serve the SHIVAS website from site/ and take desktop and phone screenshots with Playwright, reporting console errors and failed requests. Use after changing a page's layout, CSS or scripts, when the user asks to see or screenshot the site, or to confirm a change works in a real browser.
---

# Site preview

The script serves `site/` itself on a free local port. No other server is needed.

```bash
# default set: home, galvanizing, wire drawing, items/kettle, one article
node tools/screenshot.cjs --out <scratchpad>/shots

# specific pages, full length
node tools/screenshot.cjs items/slm.html blog/index.html --full --out <scratchpad>/shots

# just serve for manual browsing (runs until stopped, so start it in the background)
node tools/screenshot.cjs --serve --port 8080
```

- Pass page paths relative to `site/`. Anchors aren't supported in the filename; open the page and scroll if needed.
- Desktop is 1440×900 at scale 1 (add `--scale 2` for a screenshot the user will see). Phone is an emulated iPhone 13.
- Write screenshots to the session scratchpad, or to `preview/shots/` (git-ignored). Never commit them.
- The run ends with `No console errors or failed local requests.` or lists each problem (`script error`, `404`, `failed`). Treat any problem on a page you changed as something to fix.
- Google Fonts and cdnjs (three.js for the 3D viewers) load from the internet. If the network blocks them, fonts fall back and the viewers stay blank. That isn't a site bug.

## Checking a change
1. Take screenshots before and after the edit, on desktop and phone.
2. Read the PNGs and compare them. Check the header, the mobile dock at the bottom, and the dark mode if you touched colours (click `#thm`, or set `localStorage['shivas.mode']='dark'`).
3. If you changed shared division-page content, screenshot all three: `galvanizing.html`, `wire-drawing.html` and `reinplast.html`.
4. Send the user the screenshots that show the change.
