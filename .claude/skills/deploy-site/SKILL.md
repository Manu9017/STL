---
name: deploy-site
description: Put the SHIVAS website from site/ live on www.shivastechnology.com (Cloudflare Pages recommended, or Netlify, or GitHub Pages), connect the domain, apply the 301 redirects from the 2019 site, and check it after launch. Use when the user asks to go live, deploy, host, launch, connect the domain, move off the old site, or asks why old links or Google results land on missing pages.
---

# Deploy the SHIVAS site

`site/` is the whole website: static files, no build step. Production gets everything, including `assets/resp/` and `_redirects`. The claude.ai artifact is only a preview (see `publish-artifact`).

## Pick the host
| Host | 301 redirects | Compression | Notes |
|---|---|---|---|
| **Cloudflare Pages (recommended)** | yes, reads `site/_redirects` | Brotli and gzip | Free. Fast in India. DNS can stay at the registrar or move to Cloudflare. |
| Netlify | yes, same `_redirects` format | yes | Free tier is enough. |
| GitHub Pages | **no** | gzip | Old URLs would 404. Only use it with HTML refresh stubs for each old path, and say that this costs some of the old pages' Google ranking. |

## Steps (Cloudflare Pages)
The owner does the account and DNS steps in their browser. Claude can't log in to Cloudflare or the domain registrar.
1. **Create the project.** Cloudflare dashboard → Workers & Pages → Create → Pages → connect GitHub repo `manu9017/stl` and choose the production branch.
   - Build command: *(none)*.
   - Build output directory: `site`.
2. **Connect the domain.** Custom domains → add `www.shivastechnology.com` and `shivastechnology.com`. Follow the DNS records Cloudflare shows (a CNAME for `www`). Set the bare domain to redirect to `www`.
3. **Check before switching DNS.** Use the `*.pages.dev` preview URL:
   ```bash
   for p in / /galvanizing.html /items/kettle.html /v/hdg-plant.html /profile.html /galvanizing-kettle.html /enquiry.php; do
     curl -s -o /dev/null -w "%{http_code} %{redirect_url}  $p\n" "https://<project>.pages.dev$p"; done
   ```
   Every page must return 200. Every old path must return a 301 to its `docs/redirects.csv` `site_path`.
4. **After DNS switches:**
   - Google Search Console: add the property, submit `https://www.shivastechnology.com/sitemap.xml`, and inspect a few URLs.
   - Run `tools/lighthouse.sh` against the live site. Pass the URLs to Lighthouse directly, since the script serves `site/` locally; the baselines are in `site-audit`.

## Upload by hand (a zip, 23 Nov 2026)
The upload zip is `site/` with the files at its root (no `site/` folder inside): `git archive --format=zip -9 -o <zip> HEAD:site`. It carries `assets/config.js` with the visitor log switched on, `assets/track.js`, `_redirects`, `_headers` and `.htaccess`. Never upload the artifact preview build (`preview/artifact-build/`): it has the visitor log switched off.
- **Cloudflare Pages:** Workers & Pages → Create → Pages → Upload assets (Direct Upload) → name the project → drop the zip → Deploy. Then Custom domains as in step 2 below. A new upload later: the project → Create deployment → drop the new zip.
- **cPanel or other Apache hosting:** File Manager → `public_html` → back up or remove the old site's files → Upload the zip → Extract into `public_html` → check that `index.html` sits directly in `public_html` and that `.htaccess` is there (Settings → Show hidden files). `.htaccess` gives the same 301 redirects, 404 page and headers as `_redirects` and `_headers`, and compression (every block sits inside `IfModule`). Its HTTPS AND WWW block is commented out: switch it on once https://www.shivastechnology.com/ has a valid certificate, or use cPanel > Domains > Force HTTPS Redirect instead. It could not be run in a real Apache here (installing Apache in the session was refused), so check the site right after upload and rename `.htaccess` if pages answer 500.

## Redirects
- **Source of truth:** `docs/redirects.csv` (`old_path,new_path,site_path`). `new_path` belongs to the on-hold Astro plan; `site_path` is what the current site uses.
- **To regenerate `site/_redirects`:** edit the CSV, then rebuild the file (format `/old /new 301`, one per line), and the `Redirect 301 /old /new` lines in `site/.htaccess`. `python3 tools/check_site.py` fails if a target page is missing.
- **When a page is renamed or removed:** add a row for it. Never leave an old URL that Google knows about pointing at a 404.

## Before every production deploy
Run `python3 tools/check_site.py`. It must show 0 errors and 0 warnings. If CSS, fonts or layout changed, also run the `site-audit` checks. Tracking stays off until `assets/config.js` is filled in (see `tracking-setup`).

## Production-only files (14 Nov 2026)
These deploy with `site/` but are left out of the artifact preview (see `tools/artifact_files.py`):
- `_headers`: Cloudflare Pages security headers and cache lifetimes. Long immutable cache only on fonts/library/resp; `assets/config.js` is 5 minutes so tracking can be switched quickly.
- `404.html`: the not-found page. All its links and assets use absolute paths (`/...`), because it is served at any missing URL. It is `noindex` and not in the sitemap.
- `assets/og/`: 1200×630 JPG link-preview images (`og:image`). `og-default.jpg` is the branded card; items use their own photo (`items-<id>.jpg`). Regenerate an item's card by deleting it and re-running the og script in the repo history, or any 1200×630 JPG works.
After go-live, paste a page URL into a WhatsApp chat and the preview card should appear; metatags.io also shows all the cards.
