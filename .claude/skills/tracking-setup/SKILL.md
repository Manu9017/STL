---
name: tracking-setup
description: Turn on, change or check the SHIVAS website visitor log (Google Sheet + Apps Script), Google Analytics 4 or company identification - assets/config.js, track.js, setup/visitor-log/Code.gs and the privacy page. Use when the user sends an Apps Script /exec URL or a G- measurement ID, asks to turn tracking on or off, or asks who visited the site.
---

# Visitor tracking

**Status (23 Nov 2026): the visitor log is on.** `sheetUrl` in `site/assets/config.js` is the live Apps Script web app (Version 3, final link); GA4 and `companyScript` are empty. `site/setup/visitor-log/Code.gs` is Version 5 (24 Nov 2026; WhatsApp to the owner's +91 98186 10744 through the official Cloud API, set up in Meta by the owner, README.txt "WhatsApp"; never an unofficial relay, since leads go to SHIVAS only; the token is a script property, never in Code.gs or a chat), which the owner pastes in and deploys as a new version of the same deployment (Deploy > Manage deployments > Edit > New version; never New deployment, which changes the link). The live project is standalone at script.google.com (deployment ID starts `AKfycbwtq`), not bound to the Sheet, so Extensions > Apps Script in the Sheet opens the wrong project. Emails whose footer says "morning report" or "set VISIT_ALERTS to false" come from Version 3: the new version is not deployed yet. When the owner says the emails are noise or asks what the data is good for: the per-visit alert and the daily report stay off, the Monday report is the summary to act on, and their own browsers are left out with `?staff=1` (see `site/setup/visitor-log/README.txt`). With all three values empty the site records nothing.

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
- **Emails (Version 4, 24 Nov 2026: each enquiry at once, plus the Monday report; the per-visit alert and the daily report are off unless the script properties `VISIT_ALERTS` or `DAILY_REPORT` are set to on). The lines below describe each email:**
  - Each lead, straight away, to ALERT_TECH or ALERT_REIN.
  - A visit alert (`visitAlert_`, added 22 Nov 2026): one email per visit, on its first page (track.js sends `landing: 1`, a yes/no flag kept in the tab), at most `VISIT_ALERTS_PER_DAY` (25) a day; `VISIT_ALERTS = false` turns it off. It never names a person; city and company appear only for visitors who pressed OK.
  - `dailyDigest` at 08:00 IST (yesterday) and `weeklyDigest` on Mondays at 08:30 (last 7 days). Both contain every page viewed, the 3D models opened, each consented visitor with the pages they viewed, companies, taps, calculators and a link to the Sheet.
- **Report recipients** (`recipients_()`): DIGEST_TO, plus the Google account that runs the script (`Session.getEffectiveUser()`), plus the script property `REPORT_TO` (comma-separated). Never write a personal address into `Code.gs`: it is served publicly under `site/setup/`.
- **Test run:** `sendTestReport()` sends today's report so far.
- **3D viewers:** `v/shivas-bar.js` loads `config.js` and `track.js` with `window.SHIVAS_NOBAR = true`. There is no consent bar there (it would cover the viewer's controls). A visitor's earlier choice applies; without one, only the plain page view is sent.

## The claude.ai preview never records visits
`tools/artifact_files.py` leaves `assets/config.js` and `assets/track.js` out of the artifact and switches off their loader in the preview copies of `site.js` and `v/shivas-bar.js`. Visit alerts and reports come only from the real site once it is live on the domain. Say so when the owner asks why opening the artifact link sends no email.

## Testing it here
- `track.js` stays silent for automation (`navigator.webdriver`, and a user agent containing "Headless"). To test it, give the Playwright context a normal Chrome `userAgent`, serve `site/` over http (routes do not see `file://` pages), set `navigator.sendBeacon = undefined` in an init script so the fallback `fetch` is routable, and:
  - launch Chromium with `--disable-blink-features=AutomationControlled` and override `navigator.webdriver` in an init script;
  - route `assets/config.js` to a test `sheetUrl`, and route `script.google.com` to capture the POST bodies.
- Time on page is sent with `sendBeacon` when the page is hidden or left, and a test cannot catch a beacon sent while the page unloads. Wrap `Blob` and replace `sendBeacon` in an init script with a stub that hands the text to an exposed binding, then fire `visibilitychange` with `document.visibilityState` set to `hidden` while the page is still open (23 Nov 2026: view, update, time, click, calc and lead all matched the script, the time message carried its view's `pv`). Answer `script.google.com` and the IP lookups locally so no test row reaches the live Sheet.
- `Code.gs` can be run in Node against small stand-ins for SpreadsheetApp, MailApp, Utilities, Session, PropertiesService and ScriptApp, to check the formulas, recipients and email HTML before the owner pastes it in. `node tools/test_visitor_log.cjs` does this (visit alerts, the daily cap, a failing MailApp, enquiries); last run 22 Nov 2026.

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
