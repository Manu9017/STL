SHIVAS website visitor log: setup (about 10 minutes, once)

What you get
- A Google Sheet with every page view: page, device (phone / computer, model, browser), country, city,
  network or company name, time on page, where the visitor came from.
- A row and an email for every enquiry and every "Ask our engineer" request from the calculators,
  with what that visitor looked at before getting in touch.
- An email every morning at 8:00 (India time): yesterday's visits, companies, enquiries,
  WhatsApp / phone / email taps and calculators used.

What it cannot do
- Name a person who has not sent you their details. A name comes only from the enquiry form,
  the calculators or a WhatsApp message.
- Name the company of a visitor on home broadband or mobile data (Jio, Airtel ...). Companies are named
  only when people browse from an office network that is registered to the company.
- Record location or company for visitors who press "No thanks". Their page views are still counted.

Steps
1. Sign in to Google with the account that should own the data (for example shivastechnology@gmail.com).
2. Create a new Google Sheet. Name it "SHIVAS visitor log".
3. In the sheet: Extensions → Apps Script. Delete what is there, paste all of Code.gs, press Save.
4. In the function list at the top choose "setup" and press Run. Allow the permissions it asks for
   (the sheet, sending email, running every morning). The tabs Visits, Leads and Companies appear.
5. Deploy → New deployment → gear icon → Web app.
     Execute as: Me      Who has access: Anyone
   Press Deploy and copy the Web app URL (it ends in /exec).
6. In the website files, open assets/config.js and paste the URL between the quotes of sheetUrl:
     sheetUrl: 'https://script.google.com/macros/s/AKfy..../exec',
   Upload the site again (or ask Claude to republish it).
7. Test: open the website, press OK on the bar at the bottom, fill the enquiry form.
   A row appears in Visits and Leads within a few seconds and the enquiry email arrives.

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
