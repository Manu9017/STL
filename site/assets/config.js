/* SHIVAS website settings. Fill these in once; every page reads them.
   Leave a value empty ('') to switch that part off. With all three empty, the site records nothing.

   sheetUrl       Web app URL of the SHIVAS visitor log (Google Sheet + Apps Script, see setup/visitor-log/README.txt).
                  Every visit, calculator use and enquiry is written to the sheet; enquiries are emailed at once
                  and a summary of the day's visitors is emailed every morning.
   ga4            Google Analytics 4 measurement ID, e.g. 'G-XXXXXXXXXX' (optional: charts of countries, cities, devices).
   companyScript  Script address given by a company-identification service (Dealfront / Leadfeeder, Snitcher,
                  Albacross ...), optional: names more companies from their office networks than the visitor log can.

   Visitors are asked once (small bar at the bottom). Location, network and the visitor number are recorded
   only after they press OK; enquiries they send are always recorded. Details: privacy.html */
window.SHIVAS_CONFIG = {
  sheetUrl: '',
  ga4: '',
  companyScript: ''
};
