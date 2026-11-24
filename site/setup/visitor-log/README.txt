SHIVAS website visitor log (Version 4, 24 Nov 2026)

What you get
- A Google Sheet with every page view: page, device (phone / computer, model, browser), country, city,
  network or company name, time on page, where the visitor came from. The first page of each visit is
  marked "Start of visit" in the Detail column.
- A row and an email for every enquiry and every "Ask our engineer" request from the calculators, at once,
  with what that visitor looked at before getting in touch.
- Every Monday at 8:30 (India time) one report of the week before, built to act on:
    Follow up first: the enquiries, the companies (office networks) that looked at the site, the most
      interested visitors, and the WhatsApp, phone and email taps.
    What people looked at: products, calculators with what visitors entered, 3D models, articles.
    Where visitors came from: Google, LinkedIn, direct or an app, other sites; countries; phone or computer.
    Worth improving: pages that many people leave within a few seconds.
  Each number is compared with the week before. It goes to info@shivastechnology.com AND to the Google
  account you set this up with.
- Tabs in the Sheet: Visits (every page view), Pages (views per page), Daily (views per day),
  Viewers (each visitor who pressed OK), Companies (office networks) and Leads (enquiries).
- The 3D model pages are counted too. They do not show the bar (it would cover the model's buttons);
  a choice made on the main site applies there, otherwise only the plain page view is recorded.

Not sent any more (Version 4): an email every time someone opens the site, and the report every morning.
Both can be switched back on without changing the script (see Switches).

What it cannot do
- Report visits to the claude.ai preview link. The preview is built without the visitor log (claude.ai
  pages are not set up to send data to your Sheet). Only the real site (www.shivastechnology.com) sends.
- Name a person who has not sent you their details. A name comes only from the enquiry form,
  the calculators or a WhatsApp message.
- Name the company of a visitor on home broadband or mobile data (Jio, Airtel ...). Companies are named
  only when people browse from an office network that is registered to the company.
- Record location or company for visitors who press "No thanks". Their page views are still counted.

Your own visits
Open www.shivastechnology.com/?staff=1 once on each of your phones and computers (and in each browser you
use). A message confirms it, and from then on that browser is not counted, so the report shows customers,
not you. Enquiries you send from it still arrive. To count a browser again: open www.shivastechnology.com/?staff=0

Updating the script to a new version (the web app link stays the same)
Do this on a computer (the Apps Script editor does not work in the phone apps).
1. Open script.google.com, signed in to the Google account that owns the visitor log, and open the
   visitor log project: the one where Deploy > Manage deployments lists the web app whose link is in
   assets/config.js (for SHIVAS the deployment ID starts with AKfycbwtq). The SHIVAS project was made at
   script.google.com, not from the Sheet, so Extensions > Apps Script in the Sheet opens a different,
   empty project: do not use that one.
2. Click Code.gs on the left, select everything in it, delete it, paste the new Code.gs, press Save.
3. Deploy > Manage deployments > select that web app > the pencil (Edit) > Version: New version > Deploy.
   Do NOT choose "New deployment": that makes a new link the website does not use.
4. In the function list at the top choose sendTestWeekly, press Run: the report of the last 7 days
   arrives within a minute.

First setup (about 5 minutes, once; already done for SHIVAS)
1. Sign in to Google with the account that should own the data.
2. Create a new Google Sheet. Name it "SHIVAS visitor log".
3. In the sheet: Extensions > Apps Script. Delete what is there, paste all of Code.gs, press Save.
4. Deploy > New deployment > gear icon > Web app.
     Execute as: Me      Who has access: Anyone
   Press Deploy. Google asks for permissions (the sheet, sending email, running every week):
   choose your account > Advanced > Go to the project > Allow. Copy the Web app URL (it ends in /exec).
5. Open that URL once in the same browser. It finishes the setup by itself: the tabs Visits, Leads,
   Companies, Pages, Daily and Viewers appear, the Monday report is scheduled, and a "SHIVAS visitor
   log is switched on" email arrives. (Running "setup" from the function list does the same. Made the
   script at script.google.com instead of from the Sheet? That works too: setup then makes a Sheet called
   "SHIVAS visitor log".)
6. Put the /exec URL in assets/config.js between the quotes of sheetUrl:
     sheetUrl: 'https://script.google.com/macros/s/AKfy..../exec',
7. Test on the real site (not the claude.ai preview): open it, press OK on the bar at the bottom, fill
   the enquiry form. Rows appear in Visits and Leads within seconds and the enquiry email arrives.

Switches (Apps Script > Project settings (gear) > Script properties > Add script property)
- DAILY_REPORT = on     a report of yesterday every morning at 8:00, as well as the Monday report.
- VISIT_ALERTS = on     an email every time someone opens the site (at most 25 a day).
- REPORT_TO = a@x.com, b@y.com     more addresses for the reports, separated by commas.
Delete a property (or set it to off) to switch it off again. No new version is needed for these.
If you switch DAILY_REPORT or VISIT_ALERTS on, say so on privacy.html too ("Why, and who sees it").

Options (assets/config.js)
- ga4: a Google Analytics 4 measurement ID (G-...) for charts of countries, cities and devices.
- companyScript: the script address from a company-identification service (Dealfront / Leadfeeder,
  Snitcher, Albacross ...). These name more companies than the visitor log can, for a monthly fee.

Changing who gets the emails
- Top of Code.gs: ALERT_TECH, ALERT_REIN, DIGEST_TO. After changing Code.gs, make a new version
  (see "Updating the script" above; the URL stays the same).

Privacy
- The bar at the bottom of the website asks every visitor once. privacy.html explains what is recorded.
- Visit rows older than 24 months are deleted automatically (KEEP_DAYS in Code.gs). Enquiries are kept.
- If someone asks to see or delete their data, find their rows by name, phone, email or visitor number
  and delete them.
