---
name: viewer-3d
description: Work on the SHIVAS 3D plant viewers in site/v/ - add a new 3D model, change one, fix its SHIVAS button position, title or share image, and list it on the 3D models page and home page. Use whenever a task mentions the 3D viewers, 3D models, v/*.html or shivas-bar.js.
---

# 3D viewers (`site/v/`)

There are eleven self-contained three.js apps. Each is 0.07–2.4 MB of HTML with the model data inline, and they load three.js r128 from cdnjs. They were built in Claude chat. Treat each as its own app: make **small, surgical edits** (string replacement in the head, or one tag before `</body>`). Never reformat or regenerate a viewer.

| File | Name | Product page |
|---|---|---|
| hdg-plant | Hot-dip galvanizing plant, single line | items/turnkey |
| spin-galvanizing | Spin galvanizing plant for fasteners (SG500) | items/spin |
| zinc-ash-plant / -hoist / -hydraulic | Zinc ash recovery plant / compact, hoist tilt / compact, hydraulic tilt | items/ash |
| dross-grab | Pneumatic dross grab · SH-DG-400 | items/dross |
| electric-furnace | Electric kettle furnace | items/efurnace |
| acid-room-2line | Enclosed acid room, two lines | items/acidroom |
| etp-zld-compact / -spread | Effluent treatment and ZLD, 90 m³/day, space-restricted / open site | items/r-zld / items/r-etp |
| arp-10 | Acid regeneration plant, ARP-10 | items/r-acid |

The README says it, and the site must say it too: these are **indicative general arrangements**, with client names and commercial data removed.

## What every viewer carries
- **Head:**
  - `<title>{Name} · 3D model | SHIVAS</title>`;
  - a meta description (the text from its card on `3d-models.html`);
  - canonical `https://www.shivastechnology.com/v/{file}.html`;
  - Open Graph tags with the image `v/img/{file}.jpg` (800×500);
  - `../favicon.ico` and `../apple-touch-icon.png`.
- **Before `</body>`:**
  `<script defer src="shivas-bar.js" data-name="{Name}" data-item="{item id}" data-d="{desktop position}" data-p="{phone position}"></script>`
- **Sitemap:** an entry in `sitemap.xml`.

`shivas-bar.js` adds one round SHIVAS button. It opens a menu with these links:
- Ask about this plant (WhatsApp, pre-filled with the name)
- Call
- Details and photos (`items/{item}.html`)
- All 3D models
- SHIVAS home

Keys and clicks inside the menu don't reach the viewer.

## Placing the button (each viewer's UI is different)
`data-d` applies at 760 px and wider; `data-p` applies below 760 px. Both are CSS for a `position:fixed` box, for example `top:70px;right:12px`. `left:50%` centres the button.

To choose a position:
1. Screenshot the viewer at 1440×900 and on an iPhone 13. Use a Playwright context with `--use-gl=swiftshader --enable-unsafe-swiftshader` so WebGL renders.
2. Check two states: with its intro panel open, and after dismissing the intro. Some viewers (hdg, spin) open an intro card. Close it with a scripted click on the "Explore on my own" element; Playwright's own click can wait forever, because some viewers rewrite `location.hash` themselves (ETP writes `#mee`).
3. Pick a corner that is free in both states, set it, and re-shoot.
4. Test the menu with `page.touchscreen.tap(x, y)` on the phone, then tap outside the menu to check it closes.

## Adding a new viewer
1. Put it in `site/v/{file}.html` and its 800×500 preview at `site/v/img/{file}.jpg`.
2. Add the head tags and the script tag above, plus the sitemap entry.
3. Add a card to `3d-models.html`, copying an existing card's markup.
4. If it's a headline plant, consider it for the home page's `#models3d` section. Previews there are WebP copies in `assets/resp/v-{file}.webp`:
   `python3 -c "from PIL import Image; Image.open('site/v/img/X.jpg').convert('RGB').save('site/assets/resp/v-X.webp','WEBP',quality=78,method=6)"`
5. Link to it from its product page. The other product pages use `../v/{file}.html`.
6. The home page shows "11 3D models" and "All 11 3D models". `tools/check_site.py` warns when that count no longer matches, so update both numbers.
7. Run `python3 tools/check_site.py` and take the screenshots above.

## Claims
The viewers' spec tables cite standards. EN 746-2 in `arp-10`, `spin-galvanizing` and `zinc-ash-plant` was reviewed and kept by the owner, and it is allow-listed in the checker. Don't add new certificate claims (CE, ISO 9001, EN 746) to any viewer, and don't cite BS 729.
