SHIVAS website visitor log (Version 6, 24 Nov 2026)

What you get
- A Google Sheet with every page view: page, device (phone / computer, model, browser), country, city,
  network or company name, time on page, where the visitor came from. The first page of each visit is
  marked "Start of visit" in the Detail column.
- ONE email a week, every Monday at 8:30 (India time), about the week before:
    In the email: what to follow up first (enquiries, companies, the most interested visitors, WhatsApp,
      phone and email taps), what people looked at (products, calculators with what they entered,
      3D models, articles), where they came from, countries, devices, and pages people leave quickly.
      Every number is compared with the week before.
    Attached: ONE Excel file with everything the log has for that week, tab by tab: Summary, Enquiries,
      Companies, Visitors who pressed OK, Pages, Calculators, Taps, Came from, Countries, Devices, Days,
      Every visit. IP addresses are left out of the file (they stay only in the Sheet).
  It goes to info@shivastechnology.com AND to the Google account you set this up with.
- An email for each enquiry as it arrives (the enquiry form and "Ask our engineer" in the calculators),
  with what that visitor looked at first. To have these only in the weekly email instead, add the script
  property ENQUIRY_EMAILS = off (see Switches).
- Nothing else: no email per visit, no daily email, no WhatsApp.
- Tabs in the Sheet: Visits (every page view), Pages (views per page), Daily (views per day),
  Viewers (each visitor who pressed OK), Companies (office networks) and Leads (enquiries).
- The 3D model pages are counted too. They do not show the bar (it would cover the model's buttons);
  a choice made on the main site applies there, otherwise only the plain page view is recorded.

Finding out who a potential client is, the fair way
- Enquiries: name, phone, email and company, because the person typed them in.
- Companies: when a visitor who pressed OK browses from an office network, the network names its company.
  The weekly email and the Companies tab give a Google and a LinkedIn search link for each company, so you
  can see who it is and reach it through its own public channels. The links search the company, never a person.
- Interest score (Companies and Visitors tabs): page views + minutes + 5 for each calculator use + 5 for
  each WhatsApp, phone or email tap + 10 for an enquiry + 3 for a return visit.
- What it never does: name a person who did not send their details, look up phone numbers, or follow
  people across other websites. Visitors who press "No thanks" are counted, never located or named.

What it cannot do
- Report visits to the claude.ai preview link. The preview is built without the visitor log. Only the
  real site (www.shivastechnology.com) sends.
- Name the company of a visitor on home broadband or mobile data (Jio, Airtel ...).

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
3. Choose setupWeekly in the function list at the top, press Run, allow if asked: one trigger remains,
   every Monday at 8:30.
4. Choose sendTestWeekly, press Run: the email for the last 7 days arrives, with the Excel file.
5. Deploy > Manage deployments > select that web app > the pencil (Edit) > Version: New version > Deploy.
   Do NOT choose "New deployment": that makes a new link the website does not use.

First setup (about 5 minutes, once; already done for SHIVAS)
1. Sign in to Google with the account that should own the data.
2. Create a new Google Sheet. Name it "SHIVAS visitor log".
3. In the sheet: Extensions > Apps Script. Delete what is there, paste all of Code.gs, press Save.
4. Deploy > New deployment > gear icon > Web app.
     Execute as: Me      Who has access: Anyone
   Press Deploy and allow the permissions Google asks for (the sheet, sending email, running every week).
   Copy the Web app URL (it ends in /exec).
5. Open that URL once in the same browser. It finishes the setup by itself: the tabs appear, the Monday
   email is scheduled, and a "SHIVAS visitor log is switched on" email arrives.
6. Put the /exec URL in assets/config.js between the quotes of sheetUrl.
7. Test on the real site (not the claude.ai preview): open it, press OK on the bar at the bottom, fill
   the enquiry form. Rows appear in Visits and Leads within seconds.

Switches (Apps Script > Project settings (gear) > Script properties > Add script property)
- REPORT_TO = a@x.com, b@y.com     more addresses for the weekly email, separated by commas.
- ENQUIRY_EMAILS = off              no email for each enquiry; they are then only in the weekly email
                                    and the Leads tab. Delete the property to have them again.

Changing who gets the emails
- Top of Code.gs: ALERT_TECH, ALERT_REIN (enquiry emails), DIGEST_TO (the weekly email). After changing
  Code.gs, make a new version (see "Updating the script"; the link stays the same).

Privacy
- The bar at the bottom of the website asks every visitor once. privacy.html explains what is recorded.
- Visit rows older than 24 months are deleted automatically (KEEP_DAYS in Code.gs). Enquiries are kept.
- If someone asks to see or delete their data, find their rows by name, phone, email or visitor number
  and delete them.
