---
name: write-article
description: Write and publish a new SHIVAS engineering article in site/blog/ - topic and outline, SHIVAS voice, correct standards, page head (title, description, canonical, Article JSON-LD), cards on blog/index.html, sitemap, related links and the home-page article count. Use when the user asks for a new article, blog post, technical note, guide or case explainer, or to turn notes into an article.
---

# New article

## Before writing
- **Pick a topic** buyers search for that the 25 existing articles don't cover. Check `blog/index.html` first, so you don't write a second "pickling" article.
  - If the `harborrank:content-brief` or `keyword-research` skills are available, use them for intent and questions.
  - Otherwise plan from the questions customers ask (`enquiry-reply`).
- **Collect the facts.**
  - Process numbers must be standard practice. Cite ISO 1461, ASTM A123, IS 2629 or IS 4759 for galvanizing. Never cite BS 729.
  - SHIVAS-specific numbers (projects, clients, sizes built) come only from the owner. Anything missing becomes `[bracketed]` and goes into `docs/content-checklist.md`.
  - Don't claim CE, ISO 9001 or EN 746.

## Writing
- **Voice:** short plain sentences, engineer to engineer. Concrete causes and fixes. No hype, no emoji. Write SHIVAS in capitals.
- **Length:** 900–1,600 words.
- **Shape:** what goes wrong → why → how to check it → how to fix or design it right. Include one table or checklist a reader can use on the shop floor. End with a short "Talk to us" pointing to the matching product page and calculator.

## Publishing (copy an existing article in the same category, e.g. `blog/pickling-right.html`)
1. **Head:**
   - `<title>… | SHIVAS Articles</title>`;
   - a unique meta description of 140–160 characters;
   - canonical `https://www.shivastechnology.com/blog/<slug>.html`;
   - `Article` JSON-LD (`headline`, `description`, `datePublished` YYYY-MM-DD, author "SHIVAS").
   - Keep the fonts block (`v52f`), the favicon links and `defer` on `site.js`.
2. **Pictures:**
   - Take them from `assets/library/`, filed under the right product (see "Choosing photos" in `site-edit`), or use `drawings.svg#<id>`.
   - Run `python3 tools/fix_img_sizes.py blog/<slug>.html`.
3. **Index:** add a `bcard` with the right `data-cat` to `blog/index.html`.
4. **Counts:** update "All N articles" on `index.html` and the proof strip number. `check_site.py` warns if you forget.
5. **Links:** add the page to `sitemap.xml`. Link to it from 1–3 related product pages or articles.
6. **Check:**
   - `python3 tools/check_site.py` shows 0/0.
   - `node tools/a11y.cjs blog/<slug>.html` is clean.
   - Screenshot it on desktop and phone.
7. **Share it (optional):** a LinkedIn or WhatsApp post with the link, tagged `utm_source=linkedin&utm_medium=social&utm_campaign=<slug>` (see `analytics-tracking`).
