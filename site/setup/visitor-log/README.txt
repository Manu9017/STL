SHIVAS website visitor log: setup (about 10 minutes, once)

What you get
- A Google Sheet with every page view: page, device (phone / computer, model, browser), country, city,
  network or company name, time on page, where the visitor came from.
- A row and an email for every enquiry and every "Ask our engineer" request from the calculators,
  with what that visitor looked at before getting in touch.
- An email when someone opens the site (once per visit, at most 25 a day): the first page, device,
  where they came from, and city / company network for visitors who pressed OK. Same recipients as
  the morning report. To stop them, set VISIT_ALERTS to false at the top of the script.
- A report by email every morning at 8:00 (India time) for yesterday, and every Monday at 8:30 for
  the last 7 days: every page viewed (views, visitors, average time), the 3D models opened, each
  visitor who pressed OK with where they came from and the pages they looked at, companies,
  enquiries, WhatsApp / phone / email taps and calculators used, with a link to the Sheet.
  It goes to info@shivastechnology.com AND to the Google account you set this up with.
  To send it to more people: Apps Script → Project settings → Script properties → add REPORT_TO
  with the addresses, separated by commas.
- Tabs in the Sheet: Visits (every page view), Pages (views per page), Daily (views per day),
  Viewers (each visitor who pressed OK), Companies (office networks) and Leads (enquiries).
- The 3D model pages are counted too. They do not show the bar (it would cover the model's buttons);
  a choice made on the main site applies there, otherwise only the plain page view is recorded.

What it cannot do
- Report visits to the claude.ai preview link. The preview is built without the visitor log (claude.ai
  pages are not set up to send data to your Sheet). Alerts come from the real site
  (www.shivastechnology.com) once it is live.
- Name a person who has not sent you their details. A name comes only from the enquiry form,
  the calculators or a WhatsApp message.
- Name the company of a visitor on home broadband or mobile data (Jio, Airtel ...). Companies are named
  only when people browse from an office network that is registered to the company.
- Record location or company for visitors who press "No thanks". Their page views are still counted.

Steps (about 5 minutes; Claude Desktop can click through them for you while you approve)
1. Sign in to Google with the account that should own the data (for example shivastechnology@gmail.com).
2. Create a new Google Sheet. Name it "SHIVAS visitor log".
3. In the sheet: Extensions → Apps Script. Delete what is there, paste all of Code.gs, press Save.
4. Deploy → New deployment → gear icon → Web app.
     Execute as: Me      Who has access: Anyone
   Press Deploy. Google asks for permissions (the sheet, sending email, running every morning):
   choose your account → Advanced → Go to the project → Allow. Copy the Web app URL (it ends in /exec).
5. Open that URL once in the same browser. It finishes the setup by itself: the tabs Visits, Leads,
   Companies, Pages, Daily and Viewers appear, the morning and Monday reports are scheduled, and a
   "SHIVAS visitor log is switched on" email arrives. (Running "setup" from the function list does the
   same. Already set up before? Paste the new Code.gs, run setup again, then Deploy → Manage
   deployments → edit → New version: your data is kept. Made the script at script.google.com
   instead of from the Sheet? That works too: setup then makes a Sheet called "SHIVAS visitor log".)
6. Send the /exec URL to Claude. Claude puts it in assets/config.js and publishes the site. Or do it
   yourself: open assets/config.js and paste it between the quotes of sheetUrl:
     sheetUrl: 'https://script.google.com/macros/s/AKfy..../exec',
7. Test on the real site (not the claude.ai preview): open it, press OK on the bar at the bottom, fill
   the enquiry form. Rows appear in Visits and Leads within seconds, and the visit and enquiry
   emails arrive. "sendTestReport" in the function list sends today's report on demand.

Options (assets/config.js)
- ga4: a Google Analytics 4 measurement ID (G-...) for charts of countries, cities and devices.
- companyScript: the script address from a company-identification service (Dealfront / Leadfeeder,
  Snitcher, Albacross ...). These name more companies than the visitor log can, for a monthly fee.

Changing who gets the emails
- Top of Code.gs: ALERT_TECH, ALERT_REIN, DIGEST_TO. After changing Code.gs: Deploy → Manage deployments
  → edit → Version: New version → Deploy (the URL stays the same).

Privacy
- The bar at the bottom of the website asks every visitor once. privacy.html explains what is recorded.
- Visit rows older than 24 months are deleted automatically (KEEP_DAYS in Code.gs). Enquiries are kept.
- If someone asks to see or delete their data, find their rows by name, phone, email or visitor number
  and delete them.
