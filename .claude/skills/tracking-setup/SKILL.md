---
name: tracking-setup
description: Turn on, change or check the SHIVAS website visitor log (Google Sheet + Apps Script), Google Analytics 4 or company identification - assets/config.js, track.js, setup/visitor-log/Code.gs and the privacy page. Use when the user sends an Apps Script /exec URL or a G- measurement ID, asks to turn tracking on or off, or asks who visited the site.
---

# Visitor tracking

Everything is **off** until `site/assets/config.js` has values. With all three empty, the site records nothing.

```js
window.SHIVAS_CONFIG = { sheetUrl: '', ga4: '', companyScript: '' };
```

## What only the owner can do
These steps run in the owner's Google account. Claude can't do them from here, so send the user these steps (from `site/setup/visitor-log/README.txt`):
1. Create a Google Sheet called "SHIVAS visitor log". Go to Extensions → Apps Script and paste all of `site/setup/visitor-log/Code.gs`.
2. Run `setup` and allow the permissions it asks for.
3. Deploy → New deployment → Web app, with "Execute as" set to Me and "Who has access" set to Anyone. Copy the URL that ends in `/exec`.
4. Optional: create a GA4 property and copy its measurement ID (`G-…`).

## What Claude does once the URL or ID arrives
1. **Check the values.**
   - `sheetUrl` must match `^https://script\.google\.com/macros/s/[A-Za-z0-9_-]+/exec$`.
   - `ga4` must match `^G-[A-Z0-9]{6,12}$`.
   - Reject anything else and ask again. A web-app URL is not a secret: it is in every visitor's browser anyway.
2. **Fill them into `site/assets/config.js`.** Don't touch `companyScript` unless the user names a service and gives its script address.
3. **Check where the emails go.** At the top of `Code.gs`:
   - `ALERT_TECH` goes to info@shivastechnology.com, cc shivastechnology@gmail.com;
   - `ALERT_REIN` goes to info@shivasasia.com, cc shivasasia@gmail.com;
   - `DIGEST_TO` goes to info@shivastechnology.com.

   Leads must go to SHIVAS addresses only, never to a third party.
4. **Check the consent bar and privacy page.**
   - The bar comes from `track.js`. Location, network and the visitor number are recorded only after the visitor presses OK.
   - `privacy.html` must describe what is now on (Sheet log, GA4 if set, retention of 24 months for visits). It already covers the Sheet log. Add GA4 if you turned it on: what it collects, that it is Google Analytics, and how to opt out.
   - Keep the page compliant with India's DPDP Act 2023.
5. **Test.**
   - Run `node tools/screenshot.cjs index.html` and check the consent bar appears and doesn't cover the phone dock. Press OK in a Playwright session and check that no console errors appear.
   - Requests to `script.google.com` may be blocked from this sandbox. If so, say so; don't change the network settings for it.
   - Ask the user to open the live site, press OK, send a test enquiry, and confirm a row appears in Visits and Leads and that the alert email arrives.
6. **Ship it.** Commit, push, and republish the artifact if the user wants the shared link updated (`publish-artifact` skill).

## Notes
- The 3D viewers (`v/`) don't load `site.js` or `track.js`, so viewer visits aren't logged. Logging them would need `track.js` added to each viewer, and its consent bar may cover viewer controls. Ask first.
- To turn tracking off, empty the values in `config.js`. Data already in the Sheet stays there. The owner deletes it in the Sheet if needed.
- If the Google Sheets connector is connected in this session, Claude can read the Visits and Leads tabs to answer "who visited" questions. Treat the rows as personal data: summarise, don't paste raw rows into other services.
