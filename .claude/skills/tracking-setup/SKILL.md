---
name: tracking-setup
description: Turn on, change or check the SHIVAS website visitor log (Google Sheet + Apps Script), Google Analytics 4 or company identification - assets/config.js, track.js, setup/visitor-log/Code.gs and the privacy page. Use when the user sends an Apps Script /exec URL or a G- measurement ID, asks to turn tracking on or off, or asks who visited the site.
---

# Visitor tracking

Everything is **off** until `site/assets/config.js` has values. With all three empty, the site records nothing.

```js
window.SHIVAS_CONFIG = { sheetUrl: '', ga4: '', companyScript: '' };
```

## What the visitor log does once it is on
- **Sheet tabs:**
  - Visits: one row per page view, click, calculation or lead;
  - Pages: views per page, average time, last view;
  - Daily: views per day;
  - Viewers: each visitor who pressed OK, with network, city and device;
  - Companies: office networks;
  - Leads: enquiries.

  Pages, Daily, Viewers and Companies are `QUERY` formulas over Visits, written by `setup()`.
- **Emails:**
  - Each lead, straight away, to ALERT_TECH or ALERT_REIN.
  - `dailyDigest` at 08:00 IST (yesterday) and `weeklyDigest` on Mondays at 08:30 (last 7 days). Both contain every page viewed, the 3D models opened, each consented visitor with the pages they viewed, companies, taps, calculators and a link to the Sheet.
- **Report recipients** (`recipients_()`): DIGEST_TO, plus the Google account that runs the script (`Session.getEffectiveUser()`), plus the script property `REPORT_TO` (comma-separated). Never write a personal address into `Code.gs`: it is served publicly under `site/setup/`.
- **Test run:** `sendTestReport()` sends today's report so far.
- **3D viewers:** `v/shivas-bar.js` loads `config.js` and `track.js` with `window.SHIVAS_NOBAR = true`. There is no consent bar there (it would cover the viewer's controls). A visitor's earlier choice applies; without one, only the plain page view is sent.

## Testing it here
- `track.js` stays silent for automation (`navigator.webdriver`). To test it:
  - launch Chromium with `--disable-blink-features=AutomationControlled` and override `navigator.webdriver` in an init script;
  - route `assets/config.js` to a test `sheetUrl`, and route `script.google.com` to capture the POST bodies.
- `Code.gs` can be run in Node against small stand-ins for SpreadsheetApp, MailApp, Utilities, Session, PropertiesService and ScriptApp, to check the formulas, recipients and email HTML before the owner pastes it in. A run like this was last done in Nov 2026.

## What only the owner can do
These steps run in the owner's Google account. Claude can't do them from here, so send the user these steps (from `site/setup/visitor-log/README.txt`):
1. Create a Google Sheet called "SHIVAS visitor log". Go to Extensions → Apps Script and paste all of `site/setup/visitor-log/Code.gs`.
2. Run `setup` and allow the permissions it asks for.
3. Deploy → New deployment → Web app, with "Execute as" set to Me and "Who has access" set to Anyone. Copy the URL that ends in `/exec`.
4. Run `sendTestReport` once to check the email arrives.
5. Optional: create a GA4 property and copy its measurement ID (`G-…`).

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
