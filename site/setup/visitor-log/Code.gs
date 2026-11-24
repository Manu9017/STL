/**
 * SHIVAS website visitor log: Google Apps Script for a Google Sheet. Version 5 (24 Nov 2026).
 * Receives what the website sends (assets/track.js) and writes it to two tabs:
 *   Visits: one row per page view (page, device, browser, country, city, network or company, time on page ...)
 *   Leads: every enquiry form and "ask our engineer" request, with what that visitor looked at before.
 * Emails: every enquiry at once, and every Monday at 8:30 (India time) a report of the week before: what to follow up,
 * what people looked at, the calculators they used and where they came from. It goes to DIGEST_TO and to the Google
 * account that set this up. An email for every visit and a report every morning are switched off; to switch them on,
 * add VISIT_ALERTS = on or DAILY_REPORT = on in Project settings > Script properties (no new version needed).
 * WhatsApp (once set up, README.txt "WhatsApp"): every enquiry with the name and number, a company network looking
 * at the site, a short summary every morning at 8:00 and every Monday, all to the owner's own WhatsApp (WA_TO).
 * Tabs Pages, Daily, Viewers and Companies summarise the Visits tab.
 * Set up: see README.txt in this folder. Run setup() once, then Deploy > New deployment > Web app.
 * Update: paste this file over the old one, Save, then Deploy > Manage deployments > edit (pencil) >
 * Version: New version > Deploy. The web app link stays the same.
 */

// ---------------- settings ----------------
var ALERT_TECH = { to: 'info@shivastechnology.com', cc: 'shivastechnology@gmail.com' };   // galvanizing and wire drawing
var ALERT_REIN = { to: 'info@shivasasia.com', cc: 'shivasasia@gmail.com' };               // SHIVAS Reinplast
var DIGEST_TO = 'info@shivastechnology.com';                                              // the Monday report
var KEEP_DAYS = 730;                                                                      // visit rows older than this are deleted (privacy notice says 24 months)
var VISIT_ALERTS = false;                                                                  // an email every time someone opens the site (owner, 24 Nov 2026: off)
var VISIT_ALERTS_PER_DAY = 25;                                                             // if switched on: at most this many a day
var DAILY_REPORT = false;                                                                  // a report of yesterday every morning at 8:00 (off; the Monday report covers the week)
var SITE = 'https://www.shivastechnology.com/';

// a script property (Project settings > Script properties) overrides a switch above: on or off
function on_(name, fallback) {
  var v = null; try { v = PropertiesService.getScriptProperties().getProperty(name); } catch (e) {}
  return v === null || v === '' ? fallback : /^(on|yes|true|1)$/i.test(String(v).trim());
}

// ---------------- columns ----------------
var VISIT_COLS = [
  ['at', 'Time'], ['type', 'Type'], ['page', 'Page'], ['title', 'Title'], ['visitor', 'Visitor'], ['visit', 'Visit no.'], ['first', 'First seen'],
  ['device', 'Device'], ['model', 'Model'], ['os', 'OS'], ['browser', 'Browser'], ['screen', 'Screen'], ['lang', 'Language'], ['tz', 'Time zone'],
  ['ref', 'Came from'], ['utm', 'Campaign'], ['country', 'Country'], ['region', 'Region'], ['city', 'City'], ['org', 'Network / company'],
  ['nettype', 'Network type'], ['ip', 'IP address'], ['secs', 'Seconds on page'], ['scroll', 'Scrolled %'], ['detail', 'Detail'], ['pv', 'pv']
];
var LEAD_COLS = [
  ['at', 'Time'], ['source', 'Source'], ['name', 'Name'], ['company', 'Company'], ['contact', 'Phone / email'], ['email', 'Email'], ['place', 'Place given'],
  ['product', 'Product'], ['message', 'Message'], ['to', 'Sent to'], ['page', 'Page'], ['visitor', 'Visitor'], ['org', 'Network / company'],
  ['city', 'City'], ['country', 'Country'], ['device', 'Device'], ['seen', 'Pages seen before']
];

// ---------------- network type from the IP owner's name ----------------
var CLOUD = /\b(google|amazon|aws|microsoft|azure|cloudflare|akamai|fastly|digitalocean|ovh|hetzner|linode|vultr|oracle cloud|alibaba|tencent|contabo|leaseweb|m247|datacamp|nordvpn|expressvpn|proton|zscaler)\b/i;
var ISP = /\b(jio|reliance jio|airtel|bharti|vodafone|idea|bsnl|mtnl|act fibernet|atria convergence|beam telecom|hathway|tata (teleservices|play|sky)|you broadband|excitel|spectra|tikona|alliance broadband|gtpl|den networks|asianet|railtel|sify|netplus|fastway|siti broadband|ortel|broadband|internet service|telecom|tata communications|comcast|charter|spectrum|verizon|at&t|t-mobile|sprint|cox|virgin media|british telecom|sky uk|orange|telefonica|deutsche telekom|vodafone|etisalat|emirates integrated|omantel|ooredoo|saudi telecom|stc|zain|mobily|batelco|ptcl|grameenphone|robi|telstra|optus|singtel|starhub|maxis|telkom|turk telekom)\b/i;
function netType(org) {
  if (!org) return '';
  if (CLOUD.test(org)) return 'Cloud / VPN';
  if (ISP.test(org)) return 'Home / mobile';
  return 'Company network';
}

// ---------------- web app ----------------
// Opening the web app link once (as the owner, after Deploy) finishes the setup by itself and emails a confirmation,
// so nobody has to run setup() by hand. Later visits only say it is running.
function doGet() {
  if (!PropertiesService.getScriptProperties().getProperty('SHEET')) {
    try {
      setup();
      MailApp.sendEmail({ to: recipients_(), subject: 'SHIVAS visitor log is switched on', name: 'SHIVAS website',
        htmlBody: '<div style="font:14px/1.5 Arial,sans-serif;color:#13202c"><p><b>The SHIVAS visitor log is set up.</b></p>' +
          '<p>From now on you get an email for every enquiry, and every Monday at 8:30 a report of the week. Everything is also in the Google Sheet: ' +
          '<a href="' + book_().getUrl() + '">open the visitor log</a>.</p>' +
          '<p style="color:#566778">Last step: send the web app link (it ends in /exec) to Claude, so the website starts sending visits.</p></div>' });
      return ContentService.createTextOutput('SHIVAS visitor log is set up. A confirmation email is on its way. Copy this page\'s address (it ends in /exec) and send it to Claude.');
    } catch (err) {
      return ContentService.createTextOutput('Setup did not finish: ' + err.message + '. Open Extensions > Apps Script in the Sheet and run setup once.');
    }
  }
  return ContentService.createTextOutput('SHIVAS visitor log is running.');
}

function doPost(e) {
  var lock = LockService.getScriptLock(), later = [];
  try { lock.waitLock(10000); } catch (err) { /* write anyway */ }
  try {
    var d = JSON.parse((e && e.postData && e.postData.contents) || '{}');
    if (!d || !d.type || String(d.type).length > 20) return reply('bad');
    var cache = CacheService.getScriptCache(), n = +(cache.get('rate') || 0);          // flood guard: 300 rows a minute at most
    if (n > 300) return reply('busy');
    cache.put('rate', String(n + 1), 60);
    clean(d);
    d.nettype = netType(d.org);
    var book = book_(), visits = book.getSheetByName('Visits');
    if (d.type === 'time' || d.type === 'update') { update_(visits, d); if (d.type === 'update') later.push(function () { waCompany_(d); }); return reply('ok'); }
    if (d.type === 'lead') {
      d.seen = history_(visits, d.visitor);
      book.getSheetByName('Leads').appendRow(row_(LEAD_COLS, d));
      d.detail = d.source + ': ' + [d.name, d.company, d.contact].filter(Boolean).join(' · ');
      alert_(d);
      later.push(function () { waLead_(d); });
    }
    var landing = d.type === 'view' && +d.landing === 1;
    if (landing && !d.detail) d.detail = 'Start of visit';                               // the first page of each visit, so the report can count visits
    visits.appendRow(row_(VISIT_COLS, d));
    if (landing) { visitAlert_(d); later.push(function () { waVisit_(d); }); }
    if (d.type === 'view') later.push(function () { waCompany_(d); });
    return reply('ok');
  } finally {
    try { lock.releaseLock(); } catch (err) {}
    later.forEach(function (f) { try { f(); } catch (err) { waNote_(err.message); } });
  }
}
function reply(t) { return ContentService.createTextOutput(t); }
function clean(d) {
  for (var k in d) {
    if (typeof d[k] === 'string') d[k] = d[k].slice(0, k === 'message' || k === 'detail' || k === 'seen' ? 3000 : 300);
  }
  var t = new Date(d.at); d.at = isNaN(t) ? new Date() : t;
}
function book_() {
  var id = PropertiesService.getScriptProperties().getProperty('SHEET');
  var b = id ? SpreadsheetApp.openById(id) : (SpreadsheetApp.getActiveSpreadsheet() || SpreadsheetApp.create('SHIVAS visitor log')); if (!id) PropertiesService.getScriptProperties().setProperty('SHEET', b.getId()); return b;
}
function row_(cols, d) {   // text from the web is never run as a formula (+91... stays text too)
  return cols.map(function (c) { var v = d[c[0]]; if (v === undefined || v === null) return ''; return typeof v === 'string' && /^[=+\-@]/.test(v) ? "'" + v : v; });
}
function col_(cols, key) { for (var i = 0; i < cols.length; i++) if (cols[i][0] === key) return i + 1; return 0; }

// time on page and the visitor's OK arrive after the page view: fill them into that row
function update_(sh, d) {
  var last = sh.getLastRow(); if (last < 2 || !d.pv) return;
  var from = Math.max(2, last - 799), pvCol = col_(VISIT_COLS, 'pv');
  var pvs = sh.getRange(from, pvCol, last - from + 1, 1).getValues();
  for (var i = pvs.length - 1; i >= 0; i--) {
    if (String(pvs[i][0]) !== String(d.pv)) continue;
    var r = from + i, keys = d.type === 'time' ? ['secs', 'scroll'] : ['visitor', 'visit', 'first', 'country', 'region', 'city', 'org', 'nettype', 'ip'];
    keys.forEach(function (k) { if (d[k] !== undefined && d[k] !== '') sh.getRange(r, col_(VISIT_COLS, k)).setValue(d[k]); });
    return;
  }
}

// pages a visitor looked at before getting in touch
function history_(sh, visitor) {
  if (!visitor) return '';
  var last = sh.getLastRow(); if (last < 2) return '';
  var from = Math.max(2, last - 4999), v = sh.getRange(from, 1, last - from + 1, VISIT_COLS.length).getValues();
  var cV = col_(VISIT_COLS, 'visitor') - 1, cT = col_(VISIT_COLS, 'title') - 1, cA = 0, cY = col_(VISIT_COLS, 'type') - 1, cD = col_(VISIT_COLS, 'detail') - 1, out = [];
  v.forEach(function (r) {
    if (String(r[cV]) !== String(visitor)) return;
    var when = Utilities.formatDate(new Date(r[cA]), 'Asia/Kolkata', 'd MMM HH:mm');
    if (r[cY] === 'view') out.push(when + '  ' + r[cT]);
    else if (r[cY] === 'calc' || r[cY] === 'click') out.push(when + '  ' + (r[cY] === 'calc' ? 'Calculator: ' : 'Clicked ') + String(r[cD]).split('\n')[0]);
  });
  return out.slice(-40).join('\n');
}

// an email for every lead
function alert_(d) {
  var who = (d.div === 'rein' || /reinplast/i.test(d.product || '')) ? ALERT_REIN : ALERT_TECH;
  var line = function (k, v) { return v ? '<tr><td style="padding:3px 12px 3px 0;color:#566778">' + k + '</td><td style="padding:3px 0"><b>' + esc(v) + '</b></td></tr>' : ''; };
  var html = '<div style="font:14px/1.5 Arial,sans-serif;color:#13202c">' +
    '<p style="font-size:16px"><b>New website enquiry</b> · ' + esc(d.source) + '</p><table>' +
    line('Name', d.name) + line('Company', d.company) + line('Phone / email', d.contact) + line('Email', d.email) + line('Place given', d.place) +
    line('Product', d.product) + line('Sent to', d.to) + line('Network / company', d.org ? d.org + ' (' + d.nettype + ')' : '') +
    line('Location', [d.city, d.region, d.country].filter(Boolean).join(', ')) + line('Device', [d.device, d.model, d.os, d.browser].filter(Boolean).join(' · ')) + '</table>' +
    (d.message ? '<p><b>Message / calculation</b></p><pre style="white-space:pre-wrap;font:13px/1.45 monospace;background:#f3f5f7;padding:10px">' + esc(d.message) + '</pre>' : '') +
    (d.seen ? '<p><b>What this visitor looked at</b></p><pre style="white-space:pre-wrap;font:13px/1.45 monospace">' + esc(d.seen) + '</pre>' : '') +
    '<p style="color:#566778">Reply directly to the customer. All enquiries are in the Leads tab of the visitor log.</p></div>';
  MailApp.sendEmail({ to: who.to, cc: who.cc, subject: 'Website enquiry: ' + [d.name, d.company].filter(Boolean).join(' · ') + ' (' + (d.product || d.source) + ')', htmlBody: html, name: 'SHIVAS website' });
}
// if VISIT_ALERTS is on: an email when someone opens the site, the first page of each visit, at most VISIT_ALERTS_PER_DAY
// a day. Without the visitor's OK it can only say the page, device, language and where they came from. It never names a person.
function visitAlert_(d) {
  if (!on_('VISIT_ALERTS', VISIT_ALERTS)) return;
  try {
    var props = PropertiesService.getScriptProperties(), key = 'VA_' + day_(0), n = +(props.getProperty(key) || 0);
    if (n >= VISIT_ALERTS_PER_DAY) return;
    props.setProperty(key, String(n + 1));
    var y = 'VA_' + day_(-2); if (props.getProperty(y) !== null) props.deleteProperty(y);   // tidy old counters
    var line = function (k, v) { return v ? '<tr><td style="padding:3px 12px 3px 0;color:#566778">' + k + '</td><td style="padding:3px 0"><b>' + esc(v) + '</b></td></tr>' : ''; };
    var where = [d.city, d.region, d.country].filter(Boolean).join(', ');
    var html = '<div style="font:14px/1.5 Arial,sans-serif;color:#13202c">' +
      '<p style="font-size:16px"><b>Someone opened the SHIVAS website</b></p><table>' +
      line('First page', (d.title || '') + (d.page ? ' (' + d.page + ')' : '')) + line('Came from', d.ref || 'Typed the address or a saved link') + line('Campaign', d.utm) +
      line('Device', [d.device, d.model, d.os, d.browser].filter(Boolean).join(' · ')) + line('Language / time zone', [d.lang, d.tz].filter(Boolean).join(' · ')) +
      line('Location', where) + line('Network / company', d.org ? d.org + ' (' + d.nettype + ')' : '') + line('Visit no.', d.visit ? String(d.visit) : '') + '</table>' +
      '<p style="color:#566778">' + (where ? '' : 'Location and company network show only for visitors who pressed OK on the privacy bar. ') +
      'Alert ' + (n + 1) + ' of ' + VISIT_ALERTS_PER_DAY + ' today; every visit is in the Visits tab and in the Monday report. ' +
      'To stop these emails, delete the script property VISIT_ALERTS.</p></div>';
    MailApp.sendEmail({ to: recipients_(), subject: 'SHIVAS website: someone opened ' + (d.title || d.page || 'the site') + (where ? ' · ' + where : ''), htmlBody: html, name: 'SHIVAS website' });
  } catch (err) { /* an alert must never stop the visit being logged */ }
}
function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }

// ---------------- reports ----------------
// Who gets them: DIGEST_TO, the Google account that set this script up (so the owner always gets the report, without
// putting a personal address in this public file) and any extra addresses in the script property REPORT_TO
// (Apps Script: Project settings > Script properties > REPORT_TO, comma-separated).
function recipients_() {
  var list = [DIGEST_TO];
  try { var me = Session.getEffectiveUser().getEmail(); if (me) list.push(me); } catch (e) {}
  var extra = PropertiesService.getScriptProperties().getProperty('REPORT_TO');
  if (extra) list = list.concat(extra.split(/[,;\s]+/));
  var seen = {};
  return list.map(function (x) { return String(x || '').trim(); }).filter(function (x) {
    var k = x.toLowerCase(); if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(k) || seen[k]) return false; seen[k] = 1; return true;
  }).join(',');
}

// country for visitors who did not press OK, from their device's time zone (approximate; the report says so)
var TZC = {
  'Asia/Kolkata': 'India', 'Asia/Calcutta': 'India', 'Asia/Dhaka': 'Bangladesh', 'Asia/Kathmandu': 'Nepal', 'Asia/Katmandu': 'Nepal', 'Asia/Thimphu': 'Bhutan',
  'Asia/Colombo': 'Sri Lanka', 'Indian/Maldives': 'Maldives', 'Asia/Karachi': 'Pakistan', 'Asia/Kabul': 'Afghanistan', 'Asia/Yangon': 'Myanmar', 'Asia/Rangoon': 'Myanmar',
  'Asia/Dubai': 'United Arab Emirates', 'Asia/Muscat': 'Oman', 'Asia/Riyadh': 'Saudi Arabia', 'Asia/Qatar': 'Qatar', 'Asia/Bahrain': 'Bahrain', 'Asia/Kuwait': 'Kuwait',
  'Asia/Baghdad': 'Iraq', 'Asia/Tehran': 'Iran', 'Asia/Amman': 'Jordan', 'Asia/Beirut': 'Lebanon', 'Asia/Jerusalem': 'Israel', 'Europe/Istanbul': 'Turkey',
  'Asia/Tashkent': 'Uzbekistan', 'Asia/Almaty': 'Kazakhstan', 'Asia/Baku': 'Azerbaijan', 'Asia/Tbilisi': 'Georgia', 'Asia/Yerevan': 'Armenia',
  'Africa/Cairo': 'Egypt', 'Africa/Nairobi': 'Kenya', 'Africa/Dar_es_Salaam': 'Tanzania', 'Africa/Kampala': 'Uganda', 'Africa/Addis_Ababa': 'Ethiopia', 'Africa/Kigali': 'Rwanda',
  'Africa/Lagos': 'Nigeria', 'Africa/Accra': 'Ghana', 'Africa/Abidjan': "Cote d'Ivoire", 'Africa/Dakar': 'Senegal', 'Africa/Johannesburg': 'South Africa', 'Africa/Lusaka': 'Zambia',
  'Africa/Harare': 'Zimbabwe', 'Africa/Maputo': 'Mozambique', 'Africa/Casablanca': 'Morocco', 'Africa/Algiers': 'Algeria', 'Africa/Tunis': 'Tunisia', 'Africa/Khartoum': 'Sudan',
  'Indian/Mauritius': 'Mauritius', 'Asia/Singapore': 'Singapore', 'Asia/Kuala_Lumpur': 'Malaysia', 'Asia/Jakarta': 'Indonesia', 'Asia/Bangkok': 'Thailand',
  'Asia/Ho_Chi_Minh': 'Vietnam', 'Asia/Saigon': 'Vietnam', 'Asia/Manila': 'Philippines', 'Asia/Shanghai': 'China', 'Asia/Hong_Kong': 'Hong Kong', 'Asia/Taipei': 'Taiwan',
  'Asia/Tokyo': 'Japan', 'Asia/Seoul': 'South Korea', 'Australia/Sydney': 'Australia', 'Australia/Melbourne': 'Australia', 'Australia/Brisbane': 'Australia',
  'Australia/Perth': 'Australia', 'Australia/Adelaide': 'Australia', 'Pacific/Auckland': 'New Zealand', 'Europe/London': 'United Kingdom', 'Europe/Dublin': 'Ireland',
  'Europe/Paris': 'France', 'Europe/Berlin': 'Germany', 'Europe/Rome': 'Italy', 'Europe/Madrid': 'Spain', 'Europe/Amsterdam': 'Netherlands', 'Europe/Brussels': 'Belgium',
  'Europe/Zurich': 'Switzerland', 'Europe/Vienna': 'Austria', 'Europe/Warsaw': 'Poland', 'Europe/Prague': 'Czechia', 'Europe/Stockholm': 'Sweden', 'Europe/Oslo': 'Norway',
  'Europe/Copenhagen': 'Denmark', 'Europe/Helsinki': 'Finland', 'Europe/Lisbon': 'Portugal', 'Europe/Athens': 'Greece', 'Europe/Bucharest': 'Romania', 'Europe/Kiev': 'Ukraine',
  'Europe/Kyiv': 'Ukraine', 'Europe/Moscow': 'Russia', 'America/New_York': 'United States', 'America/Chicago': 'United States', 'America/Denver': 'United States',
  'America/Phoenix': 'United States', 'America/Los_Angeles': 'United States', 'America/Anchorage': 'United States', 'Pacific/Honolulu': 'United States',
  'America/Toronto': 'Canada', 'America/Vancouver': 'Canada', 'America/Edmonton': 'Canada', 'America/Winnipeg': 'Canada', 'America/Halifax': 'Canada',
  'America/Mexico_City': 'Mexico', 'America/Sao_Paulo': 'Brazil', 'America/Argentina/Buenos_Aires': 'Argentina', 'America/Santiago': 'Chile', 'America/Bogota': 'Colombia',
  'America/Lima': 'Peru'
};
function country_(r, c) {
  if (r[c.country]) return String(r[c.country]);
  var tz = String(r[c.tz] || ''); if (TZC[tz]) return TZC[tz];
  return tz ? 'Other (' + tz.split('/').pop().replace(/_/g, ' ') + ' time zone)' : 'Unknown';
}
// where a visit came from, from the referrer the browser gave on its first page
function source_(ref, utm) {
  var r = String(ref || ''), u = String(utm || '');
  if (/chatgpt|openai|perplexity|copilot|gemini|claude\.ai/i.test(u + ' ' + r)) return 'AI assistants (ChatGPT and others)';
  if (u) return 'Campaign: ' + u.split(' / ')[0];
  if (!r) return 'Direct or an app (WhatsApp, email)';
  var app = /^android-app:\/\/([^/]+)/.exec(r), h = (app ? app[1] : r.replace(/^[a-z]+:\/\//i, '').split(/[\/ ?#]/)[0].replace(/^www\./, '')).toLowerCase();
  if (h === 'com.google.android.gm') return 'Gmail';
  if (/^com\.google\.android\.googlequicksearchbox|(^|\.)google\./.test(h)) return 'Google search';
  if (/bing\.com|duckduckgo|yahoo\.|yandex|ecosia|baidu|(^|\.)search\./.test(h)) return 'Other search engines';
  if (/linkedin|lnkd\.in/.test(h)) return 'LinkedIn';
  if (/facebook|(^|\.)fb\.com|instagram/.test(h)) return 'Facebook or Instagram';
  if (/whatsapp|(^|\.)wa\.me/.test(h)) return 'WhatsApp';
  if (/youtube|youtu\.be/.test(h)) return 'YouTube';
  if (/indiamart/.test(h)) return 'IndiaMART';
  if (/tradeindia/.test(h)) return 'TradeIndia';
  if (/(^|\.)(t\.co|x\.com|twitter\.com)$/.test(h)) return 'X (Twitter)';
  return h || 'Other sites';
}
// a calculator row's text: its name, then what the visitor entered and the main results
function calcLine_(detail) {
  var ls = String(detail || '').split('\n').map(function (x) { return x.trim(); }).filter(function (x) { return x && x !== 'Results' && !/^Link:/.test(x); });
  var name = (ls.shift() || 'Calculator').replace(/ enquiry from the SHIVAS calculator$/, '');
  return { name: name, text: ls.slice(0, 6).join(' · ').slice(0, 300) };
}
function inc_(o, k) { o[k] = (o[k] || 0) + 1; }
function txt_(v) { return String(v === null || v === undefined ? '' : v).replace(/^'/, ''); }   // a cell kept as text by its leading '
function count_(n, one, many) { return n + ' ' + (n === 1 ? one : many); }
function ist_(ymd) { return new Date(ymd + 'T00:00:00+05:30'); }
function nice_(ymd) { return Utilities.formatDate(new Date(ymd + 'T12:00:00+05:30'), 'Asia/Kolkata', 'd MMM'); }

// the Visits and Leads rows from day 'from' (yyyy-MM-dd, India time) on. Each page view gets r.entry: true on the
// first page of a visit (rows marked 'Start of visit'; older rows: a new referrer, or 30 minutes without a page).
function load_(from) {
  var book = book_(), out = { visits: [], leads: [], c: {}, lc: {} }, cut = ist_(from);
  VISIT_COLS.forEach(function (x, i) { out.c[x[0]] = i; }); LEAD_COLS.forEach(function (x, i) { out.lc[x[0]] = i; });
  var read = function (name, width, max) {
    var sh = book.getSheetByName(name), last = sh ? sh.getLastRow() : 0; if (last < 2) return [];
    var start = Math.max(2, last - max + 1), t = sh.getRange(start, 1, last - start + 1, 1).getValues(), i = 0;
    while (i < t.length && !(new Date(t[i][0]) >= cut)) i++;
    return i < t.length ? sh.getRange(start + i, 1, last - start - i + 1, width).getValues() : [];
  };
  var c = out.c, rows = out.visits = read('Visits', VISIT_COLS.length, 60000), mark = -1, seen = {};
  out.leads = read('Leads', LEAD_COLS.length, 5000);
  for (var i = 0; i < rows.length; i++) if (rows[i][c.type] === 'view' && rows[i][c.detail] === 'Start of visit') { mark = i; break; }
  rows.forEach(function (r, i) {
    if (r[c.type] !== 'view') return;
    if (mark >= 0 && i >= mark) { r.entry = r[c.detail] === 'Start of visit'; return; }
    var sig = String(r[c.visitor] || [r[c.device], r[c.os], r[c.browser], r[c.screen], r[c.lang], r[c.tz], r[c.city]].join('|')), t = +new Date(r[c.at]);
    r.entry = !!r[c.ref] || !seen[sig] || t - seen[sig] > 30 * 60000; seen[sig] = t;
  });
  return out;
}

// everything between two days (yyyy-MM-dd, India time; 'from' included, 'to' not)
function summary_(data, from, to) {
  var t0 = ist_(from), t1 = ist_(to), c = data.c, lc = data.lc;
  var s = { views: 0, visits: 0, ok: {}, sources: {}, countries: {}, devices: {}, pages: {}, firms: {}, visitors: {}, calcs: [], calcN: {}, taps: [], tapN: {}, leads: [] };
  data.visits.forEach(function (r) {
    var t = new Date(r[c.at]); if (!(t >= t0 && t < t1)) return;
    var type = r[c.type], title = String(r[c.title] || r[c.page] || ''), page = String(r[c.page] || '').split('#')[0] || 'index.html', vid = String(r[c.visitor] || '');
    var where = [r[c.city], r[c.country]].filter(Boolean).join(', ');
    if (type === 'view') {
      s.views++;
      if (r.entry) { s.visits++; inc_(s.sources, source_(r[c.ref], r[c.utm])); inc_(s.countries, country_(r, c)); inc_(s.devices, r[c.device] || 'Unknown'); }
      var pg = s.pages[page] = s.pages[page] || { title: title, page: page, n: 0, secs: 0, timed: 0 };
      pg.n++; if (+r[c.secs]) { pg.secs += +r[c.secs]; pg.timed++; }
      if (vid) {
        s.ok[vid] = 1;
        var v = s.visitors[vid] = s.visitors[vid] || { id: vid, n: 0, secs: 0, pages: [], where: where, org: String(r[c.org] || ''), net: String(r[c.nettype] || ''), visit: 0, ref: '' };
        v.n++; v.secs += +r[c.secs] || 0; v.visit = Math.max(v.visit, +r[c.visit] || 1);
        if (v.pages.indexOf(title) < 0) v.pages.push(title); if (!v.ref && r.entry) v.ref = source_(r[c.ref], r[c.utm]);
      }
      if (r[c.nettype] === 'Company network' && r[c.org]) {
        var f = s.firms[r[c.org]] = s.firms[r[c.org]] || { n: 0, secs: 0, where: where, pages: [] };
        f.n++; f.secs += +r[c.secs] || 0; if (f.pages.indexOf(title) < 0) f.pages.push(title);
      }
    } else if (type === 'calc') {
      var cl = calcLine_(r[c.detail]); inc_(s.calcN, cl.name);
      s.calcs.push({ name: cl.name, text: cl.text, where: [r[c.org], where].filter(Boolean).join(' · ') });
    } else if (type === 'click') {
      var kind = String(r[c.detail] || '').split(':')[0];
      if (/^(WhatsApp|Phone|Email)$/.test(kind)) { inc_(s.tapN, kind); s.taps.push({ kind: kind, page: title }); }
    }
  });
  data.leads.forEach(function (r) {
    var t = new Date(r[lc.at]); if (!(t >= t0 && t < t1)) return;
    s.leads.push({ at: t, source: txt_(r[lc.source]), name: txt_(r[lc.name]), company: txt_(r[lc.company]), contact: txt_(r[lc.contact]), email: txt_(r[lc.email]), product: txt_(r[lc.product]),
      place: txt_(r[lc.place]), message: txt_(r[lc.message]), where: [r[lc.city], r[lc.country]].filter(Boolean).join(', '), org: txt_(r[lc.org]) });
  });
  return s;
}

// the report: what to follow up first, then what people looked at, then where they came from. p is the period before.
function report_(s, p, label, kind) {
  var navy = '#1f4e79', amber = '#e8a317', ink = '#13202c', mut = '#566778', line = '#dde5ee', soft = '#eef3f8';
  var grey = function (t) { return '<span style="color:' + mut + ';font-size:12px">' + t + '</span>'; };
  var none = function (t) { return '<p style="color:' + mut + ';margin:4px 0">' + t + '</p>'; }, per = kind === 'day' ? 'that day' : 'this week';
  var h2 = function (t, sub) { return '<h2 style="font:700 17px/1.3 Arial,sans-serif;margin:30px 0 4px;color:' + navy + '">' + t + '</h2>' + (sub ? '<p style="margin:0 0 10px;color:' + mut + ';font-size:13px">' + sub + '</p>' : ''); };
  var mins = function (secs) { secs = Math.round(secs || 0); return !secs ? '' : secs < 90 ? secs + ' s' : Math.round(secs / 60) + ' min'; };
  var keys = function (o) { return Object.keys(o).sort(function (a, b) { return o[b] - o[a] || (a < b ? -1 : 1); }); };
  var short = function (t) { t = String(t || ''); return t.length > 72 ? t.slice(0, 70) + '...' : t; };
  var bars = function (o, n) {
    var ks = keys(o).slice(0, n); if (!ks.length) return none('None ' + per + '.');
    var max = o[ks[0]];
    return '<table role="presentation" style="border-collapse:collapse;width:100%;font-size:14px">' + ks.map(function (k) {
      return '<tr><td style="padding:4px 10px 4px 0">' + esc(k) + '</td><td style="padding:4px 0;width:34%"><div style="background:' + soft + ';border-radius:4px"><div style="background:' + navy + ';height:10px;border-radius:4px;width:' + Math.max(4, Math.round(100 * o[k] / max)) + '%"></div></div></td>' +
        '<td style="padding:4px 0 4px 10px;text-align:right;white-space:nowrap"><b>' + o[k] + '</b></td></tr>';
    }).join('') + '</table>';
  };
  var pageTable = function (list, n) {
    if (!list.length) return none('None ' + per + '.');
    var cell = 'padding:6px 0;border-top:1px solid ' + line;
    return '<table role="presentation" style="border-collapse:collapse;width:100%;font-size:14px"><tr>' +
      '<td style="padding:0 0 4px;color:' + mut + ';font-size:12px">Page</td><td style="padding:0 0 4px 10px;color:' + mut + ';font-size:12px;text-align:right">Views</td><td style="padding:0 0 4px 12px;color:' + mut + ';font-size:12px;text-align:right;white-space:nowrap">Avg time</td></tr>' +
      list.slice(0, n).map(function (pg) {
        return '<tr><td style="' + cell + ';padding-right:10px">' + esc(short(pg.title)) + '</td><td style="' + cell + ';text-align:right"><b>' + pg.n + '</b></td>' +
          '<td style="' + cell + ';padding-left:12px;text-align:right;white-space:nowrap;color:' + mut + '">' + mins(pg.timed ? pg.secs / pg.timed : 0) + '</td></tr>';
      }).join('') + '</table>';
  };
  var taps = function (x) { return (x.tapN.WhatsApp || 0) + (x.tapN.Phone || 0) + (x.tapN.Email || 0); };
  var tile = function (n, what, was) {
    return '<td style="width:50%;padding:12px 14px;border:1px solid ' + line + ';vertical-align:top;background:#ffffff"><div style="font:700 28px/1.1 Arial,sans-serif;color:' + ink + '">' + n + '</div>' +
      '<div style="font-size:13px;color:' + ink + ';margin-top:3px">' + what + '</div>' + (p ? '<div style="font-size:12px;color:' + mut + ';margin-top:2px">' + was + ' the ' + kind + ' before</div>' : '') + '</td>';
  };

  var all = Object.keys(s.pages).map(function (k) { return s.pages[k]; }).sort(function (a, b) { return b.n - a.n || b.secs - a.secs; });
  var product = all.filter(function (x) { return /^(items\/(?!index)|galvanizing\.html|wire-drawing\.html|reinplast\.html|pultrusion\.html)/.test(x.page); });
  var models = {}, calcPages = 0, articles = [], other = {};
  all.forEach(function (x) {
    if (/^v\//.test(x.page)) models[short(x.title)] = x.n;
    else if (/^(calculator\.html|calculators)/.test(x.page)) calcPages += x.n;
    else if (/^blog\/(?!index)/.test(x.page)) articles.push(x);
    else if (product.indexOf(x) < 0) other[short(x.page === 'index.html' ? 'Home page' : x.title)] = x.n;
  });
  var firms = Object.keys(s.firms).sort(function (a, b) { return s.firms[b].n - s.firms[a].n; });
  var hot = Object.keys(s.visitors).map(function (k) { return s.visitors[k]; })
    .filter(function (v) { return v.n >= 4 || v.secs >= 300 || (v.visit >= 2 && v.n >= 2); })
    .sort(function (a, b) { return (b.secs + 60 * b.n) - (a.secs + 60 * a.n); }).slice(0, 6);
  var quick = all.filter(function (x) { return x.n >= 5 && x.timed >= 3 && x.secs / x.timed < 15; }).slice(0, 3);
  var devTotal = Object.keys(s.devices).reduce(function (n, k) { return n + s.devices[k]; }, 0);
  var url = ''; try { url = book_().getUrl(); } catch (e) {}
  var waLast = ''; try { waLast = PropertiesService.getScriptProperties().getProperty('WA_LAST') || ''; } catch (e) {}

  var lead = function (l) {
    var when = ''; try { when = Utilities.formatDate(l.at, 'Asia/Kolkata', 'EEE d MMM, HH:mm'); } catch (e) {}
    var msg = String(l.message || '').replace(/\s+/g, ' ');
    return '<div style="border-left:4px solid ' + amber + ';background:#fff8ea;padding:10px 12px;margin:8px 0">' +
      '<b>' + esc(l.name || 'No name given') + '</b>' + (l.company ? ' · ' + esc(l.company) : '') + '<br>' +
      (l.product ? esc(l.product) + '<br>' : '') + [l.contact, l.email].filter(Boolean).map(esc).join(' · ') + '<br>' +
      grey(esc([when, l.source, l.place || l.where].filter(Boolean).join(' · '))) +
      (msg ? '<div style="margin-top:6px;font-size:13px">' + esc(msg.slice(0, 220)) + (msg.length > 220 ? ' ...' : '') + '</div>' : '') + '</div>';
  };
  var top = product[0] ? short(product[0].title) : '';
  var said = [s.leads.length ? count_(s.leads.length, 'enquiry', 'enquiries') + ' to answer' : 'no enquiries'];
  if (firms.length) said.push(count_(firms.length, 'company network', 'company networks') + ' looked around');
  if (top) said.push('most interest in ' + top);

  var html = '<div style="font:14px/1.5 Arial,sans-serif;color:' + ink + ';max-width:640px;margin:0 auto">' +
    '<div style="background:' + navy + ';color:#ffffff;padding:16px 18px;border-radius:10px 10px 0 0"><div style="font-size:12px;letter-spacing:.06em;text-transform:uppercase;opacity:.85">SHIVAS website report</div>' +
    '<div style="font:700 20px/1.3 Arial,sans-serif;margin-top:2px">' + esc(label) + '</div></div>' +
    '<div style="border:1px solid ' + line + ';border-top:0;padding:14px 18px 18px;border-radius:0 0 10px 10px">' +
    '<p style="font-size:15px;margin:0 0 12px">' + (kind === 'day' ? 'Yesterday' : 'This week') + ': ' + esc(said.join(', ')) + '.</p>' +
    '<table role="presentation" style="border-collapse:collapse;width:100%"><tr>' +
    tile(s.leads.length, 'enquiries', p ? p.leads.length : 0) + tile(s.visits, 'visits', p ? p.visits : 0) + '</tr><tr>' +
    tile(taps(s), 'WhatsApp, phone and email taps', p ? taps(p) : 0) + tile(s.calcs.length, 'calculator uses', p ? p.calcs.length : 0) + '</tr></table>';

  if (!s.views && !s.leads.length) {
    html += none('No visits were recorded ' + per + '.');
  } else {
    html += h2('Follow up first', 'Enquiries also reached you by email the moment they were sent.') +
      (s.leads.length ? s.leads.map(lead).join('') : none('No enquiries ' + per + '.')) +
      '<p style="margin:16px 0 4px"><b>Companies that looked at the site</b> ' + grey('office networks, named from their internet address') + '</p>' +
      (firms.length ? '<ul style="margin:0;padding-left:18px">' + firms.slice(0, 10).map(function (k) {
        var f = s.firms[k];
        return '<li style="margin:0 0 8px"><b>' + esc(k) + '</b>' + (f.where ? ' · ' + esc(f.where) : '') + '<br>' + grey(count_(f.n, 'page', 'pages') + (f.secs ? ', ' + mins(f.secs) : '') + ': ' + esc(f.pages.slice(0, 6).map(short).join(' · '))) + '</li>';
      }).join('') + '</ul>' : none('None identified. Most people browse on mobile data or home broadband, which cannot be named.')) +
      (hot.length ? '<p style="margin:16px 0 4px"><b>Most interested visitors</b> ' + grey('visitors who pressed OK; a name appears only if they send an enquiry') + '</p><ul style="margin:0;padding-left:18px">' + hot.map(function (v) {
        return '<li style="margin:0 0 8px"><b>' + esc(v.where || 'Place unknown') + '</b>' + (v.org ? ' · ' + esc(v.org) + (v.net ? ' (' + esc(v.net) + ')' : '') : '') + '<br>' +
          grey((v.visit > 1 ? 'visit ' + v.visit : 'first visit') + ' · ' + count_(v.n, 'page', 'pages') + (v.secs ? ', ' + mins(v.secs) : '') + (v.ref ? ' · ' + (/^Direct/.test(v.ref) ? 'came directly' : 'came from ' + esc(v.ref)) : '') + ' · ' + esc(v.id)) +
          '<br>' + esc(v.pages.slice(0, 8).map(short).join(' · ')) + '</li>';
      }).join('') + '</ul>' : '') +
      (taps(s) ? '<p style="margin:16px 0 4px"><b>WhatsApp, phone and email taps</b> ' + grey('the conversation itself is in WhatsApp, your phone or your inbox') + '</p><p style="margin:0">' +
        ['WhatsApp', 'Phone', 'Email'].filter(function (k) { return s.tapN[k]; }).map(function (k) { return esc(k) + ' <b>' + s.tapN[k] + '</b>'; }).join(' · ') + '<br>' +
        grey('tapped on: ' + esc(keys(s.taps.reduce(function (o, x) { inc_(o, short(x.page)); return o; }, {})).slice(0, 6).join(' · '))) + '</p>' : '');

    html += h2('What people looked at') +
      '<p style="margin:10px 0 4px"><b>Products and company pages</b></p>' + pageTable(product, 10) +
      '<p style="margin:18px 0 4px"><b>Calculators</b> ' + grey(count_(calcPages, 'calculator page view', 'calculator page views') + ', ' + count_(s.calcs.length, 'use', 'uses') + ' (a visitor changed the inputs and read the result)') + '</p>' +
      bars(s.calcN, 8) +
      (s.calcs.length ? '<p style="margin:12px 0 4px;font-size:13px;color:' + mut + '">What visitors entered, newest first</p><ul style="margin:0;padding-left:18px;font-size:13px">' +
        s.calcs.slice(-8).reverse().map(function (x) { return '<li style="margin:0 0 6px"><b>' + esc(x.name) + '</b>: ' + esc(x.text) + (x.where ? '<br>' + grey(esc(x.where)) : '') + '</li>'; }).join('') + '</ul>' : '') +
      '<p style="margin:18px 0 4px"><b>3D models opened</b></p>' + bars(models, 8) +
      '<p style="margin:18px 0 4px"><b>Articles read</b></p>' + pageTable(articles, 5) +
      '<p style="margin:18px 0 4px"><b>Other pages</b></p>' + bars(other, 6);

    html += h2('Where visitors came from', 'Counted once per visit.') + bars(s.sources, 8) +
      '<p style="margin:18px 0 4px"><b>Countries</b> ' + grey('from the location of visitors who pressed OK, otherwise from the time zone of their device') + '</p>' + bars(s.countries, 8) +
      '<p style="margin:14px 0 0"><b>Devices</b>: ' + (devTotal ? keys(s.devices).map(function (k) { return esc(k) + ' ' + Math.round(100 * s.devices[k] / devTotal) + ' %'; }).join(' · ') : 'none') + '</p>';

    if (quick.length) html += h2('Worth improving', 'Pages that many people leave within a few seconds.') + '<ul style="margin:0;padding-left:18px">' +
      quick.map(function (x) { return '<li>' + esc(short(x.title)) + ': ' + count_(x.n, 'view', 'views') + ', ' + mins(x.secs / x.timed) + ' on average</li>'; }).join('') + '</ul>';
  }

  html += '<div style="margin-top:28px;padding:14px 16px;background:' + soft + ';border-radius:8px;font-size:13px;line-height:1.55">' +
    (url ? '<a href="' + url + '" style="color:' + navy + ';font-weight:700">Open the visitor log (Google Sheet)</a> ' + grey('every visit, page and enquiry, row by row') + '<br>' : '') +
    '<b>Your own visits</b>: open <a href="' + SITE + '?staff=1" style="color:' + navy + '">' + SITE.replace(/^https:\/\//, '') + '?staff=1</a> once on each of your phones and computers, and they are not counted.<br>' +
    '<b>More or fewer emails</b>: Apps Script, Project settings, Script properties. DAILY_REPORT = on adds a report every morning, VISIT_ALERTS = on an email for every visit, and REPORT_TO sends this report to more addresses (separated by commas).' +
    (waOn_() && waLast ? '<br><b>WhatsApp</b>: the last message that did not go through, ' + esc(waLast) + '. Run testWhatsApp in Apps Script to see why.' : '') +
    '</div></div></div>';
  return html;
}

function day_(offset) { return Utilities.formatDate(new Date(Date.now() + offset * 864e5), 'Asia/Kolkata', 'yyyy-MM-dd'); }
function send_(s, p, label, kind, test) {
  var nf = Object.keys(s.firms).length;
  var subject = (test ? 'Test: ' : '') + 'SHIVAS website, ' + label + ': ' + count_(s.leads.length, 'enquiry', 'enquiries') + ', ' + count_(s.visits, 'visit', 'visits') + (nf ? ', ' + count_(nf, 'company', 'companies') : '');
  MailApp.sendEmail({ to: recipients_(), subject: subject, htmlBody: report_(s, p, label, kind), name: 'SHIVAS website' });
}
// the last 7 days and the 7 before them; 'shift' 0 is Monday's report (last Monday to Sunday), 1 includes today
function weekly_(shift, test) {
  var to = day_(shift), from = day_(shift - 7), before = day_(shift - 14), data = load_(before);
  var s = summary_(data, from, to), p = summary_(data, before, from), span = nice_(from) + ' to ' + nice_(day_(shift - 1));
  if (test || on_('WEEKLY_EMAIL', true)) send_(s, p, (test ? 'Last 7 days, ' : 'Week of ') + span, 'week', test);
  try { waWeekly_(s, p, span + (test ? ' (test)' : '')); } catch (err) { waNote_(err.message); }
}

// every Monday at 8:30: the week before
function weeklyDigest() { weekly_(0, false); }

// every morning at 8:00: tidies old rows; a WhatsApp summary of yesterday (WA_DAILY) and, only if DAILY_REPORT is on, an email
function dailyDigest() {
  try {
    var y = day_(-1), mail = on_('DAILY_REPORT', DAILY_REPORT), wa = waOn_() && on_('WA_DAILY', true);
    if (mail || wa) {
      var data = load_(day_(-2)), s = summary_(data, y, day_(0));
      if (mail && (s.views || s.leads.length)) send_(s, summary_(data, day_(-2), y), nice_(y), 'day', false);
      if (wa) { try { waDaily_(s, Utilities.formatDate(ist_(y), 'Asia/Kolkata', 'EEE d MMM')); } catch (err) { waNote_(err.message); } }
    }
  } finally { tidy_(); cleanup(); }
}

// run by hand (choose it in the function list, press Run): the weekly report for the last 7 days, today included
function sendTestWeekly() { weekly_(1, true); }
function sendTestReport() { sendTestWeekly(); }

// visit rows older than KEEP_DAYS are deleted (enquiries in Leads are kept)
function cleanup() {
  var sh = book_().getSheetByName('Visits'), last = sh.getLastRow(); if (last < 3) return;
  var cut = new Date(Date.now() - KEEP_DAYS * 864e5), t = sh.getRange(2, 1, last - 1, 1).getValues(), n = 0;
  while (n < t.length && new Date(t[n][0]) < cut) n++;
  if (n) sh.deleteRows(2, Math.min(n, last - 2));
}

// ---------------- WhatsApp (Version 5): messages to the owner's own WhatsApp ----------------
// Sent through WhatsApp's official Cloud API (Meta), so an enquiry goes from SHIVAS's Sheet to SHIVAS's WhatsApp and to
// nobody else. Set up once (README.txt, "WhatsApp"): put these in Project settings > Script properties, never in this
// file (it is public on the website): WA_TOKEN (the access token), WA_PHONE_ID (the sender's phone number ID) and
// WA_WABA_ID (the WhatsApp Business Account ID); then run setupWhatsApp. WA_TO (script property) changes the numbers.
// Switches (script properties, on or off): WA_LEADS, WA_COMPANIES, WA_DAILY and WA_WEEKLY are on; WA_VISITS is off.
// A message that does not go through never stops a visit or an enquiry being written; the last problem is kept in
// WA_LAST and shown at the foot of the Monday email.
var WA_TO = '919818610744';                     // +91 98186 10744, the owner (24 Nov 2026); several: comma-separated
var WA_VERSION = 'v26.0';                       // Graph API version (script property WA_VERSION overrides)
var WA_LANG = 'en';
var WA_VISITS_PER_DAY = 25;
// The message formats (Meta calls them templates and reviews each once). Meta's rules: no {{n}} at the very start or
// end, enough words around each {{n}}, and the values themselves have no line breaks (waText_ removes them).
var WA_TEMPLATES = {
  shivas_enquiry: { text: 'New enquiry from the SHIVAS website.\n\nName: {{1}}\nPhone: {{2}}\nCompany: {{3}}\nPlace: {{4}}\nProduct: {{5}}\nMessage: {{6}}\nLooked at: {{7}}\n\nPlease call or WhatsApp them soon. The full enquiry is also in your email and in the Leads tab of the visitor log.',
    example: ['Ramesh Kumar', '+91 98765 43210', 'Example Steel Pvt Ltd', 'Pune, India', 'Galvanizing plant', 'We need a galvanizing plant for 800 t a month, please call', 'Zinc kettle, Galvanizing plant calculator'] },
  shivas_company: { text: 'A company network is looking at the SHIVAS website.\n\nCompany network: {{1}}\nPlace: {{2}}\nPage: {{3}}\n\nThis name comes from their office internet connection, not from a person. If they send an enquiry, their number will come to this chat.',
    example: ['Example Steel Pvt Ltd', 'Ludhiana, India', 'Zinc kettle'] },
  shivas_visit: { text: 'Someone opened the SHIVAS website.\n\nFirst page: {{1}}\nCame from: {{2}}\nDevice: {{3}}\nPlace: {{4}}\n\nA visit has no name or number. If they send an enquiry, their number will come to this chat.',
    example: ['Zinc kettle', 'Google search', 'Phone, Android', 'Pune, India'] },
  shivas_daily: { text: 'SHIVAS website, yesterday ({{1}}).\n\nVisits: {{2}}\nEnquiries: {{3}}\nWhatsApp, phone and email taps: {{4}}\nCalculator uses: {{5}}\nCompanies: {{6}}\nMost viewed: {{7}}\n\nEach enquiry also came to this chat when it was sent. The full report comes by email every Monday.',
    example: ['Mon 23 Nov', '12', '1: Ramesh Kumar, Example Steel Pvt Ltd', '3 (WhatsApp 2, phone 1)', '2: Galvanizing plant calculator, Wire drawing', 'Example Steel Pvt Ltd (Ludhiana)', 'Zinc kettle (4), Galvanizing furnace (2)'] },
  shivas_weekly: { text: 'SHIVAS website, week of {{1}}.\n\nVisits: {{2}}, the week before: {{3}}\nEnquiries: {{4}}\nCompanies: {{5}}\nMost viewed: {{6}}\nCalculators: {{7}}\n\nThe full report with every enquiry, company and page is in your email. Tap the button to open the visitor log.',
    example: ['16 Nov to 22 Nov', '41', '29', '3: Ramesh Kumar, Example Steel Pvt Ltd; Sample buyer', 'Example Steel Pvt Ltd (Ludhiana)', 'Zinc kettle (9), Galvanizing furnace (5)', 'Galvanizing plant calculator 4, Wire drawing 2'], button: 'Open the visitor log' }
};
function waProps_() {
  var p = PropertiesService.getScriptProperties();
  return { token: p.getProperty('WA_TOKEN'), phone: p.getProperty('WA_PHONE_ID'), waba: p.getProperty('WA_WABA_ID'), to: p.getProperty('WA_TO') || WA_TO, v: p.getProperty('WA_VERSION') || WA_VERSION };
}
function waOn_() { var w = waProps_(); return !!(w.token && w.phone); }
// a value for a {{n}}: one line, not empty, not too long
function waText_(v, max) {
  var s = String(v === null || v === undefined ? '' : v).replace(/^'/, '').replace(/[\r\n\t]+/g, ' · ').replace(/\s{4,}/g, '   ').trim();
  if (s.length > max) s = s.slice(0, max - 3).trim() + '...';
  return s || '-';
}
function waNote_(what) { try { PropertiesService.getScriptProperties().setProperty('WA_LAST', Utilities.formatDate(new Date(), 'Asia/Kolkata', 'd MMM HH:mm') + ': ' + String(what).slice(0, 300)); } catch (e) {} }
// one message in a given format to every WA_TO number; returns what Meta answered
function waSend_(name, values) {
  var w = waProps_(); if (!w.token || !w.phone) return 'WhatsApp is not set up (script properties WA_TOKEN and WA_PHONE_ID).';
  var out = [];
  String(w.to).split(/[,;]+/).map(function (x) { x = x.replace(/\D/g, ''); return /^[6-9]\d{9}$/.test(x) ? '91' + x : x; }).filter(function (x) { return x.length >= 11; }).forEach(function (to) {   // +91 98186 10744, 919818610744 or 9818610744
    var body = { messaging_product: 'whatsapp', to: to, type: 'template', template: { name: name, language: { code: WA_LANG },
      components: [{ type: 'body', parameters: values.map(function (x) { return { type: 'text', text: x }; }) }] } };
    try {
      var r = UrlFetchApp.fetch('https://graph.facebook.com/' + w.v + '/' + w.phone + '/messages', { method: 'post', contentType: 'application/json',
        headers: { Authorization: 'Bearer ' + w.token }, payload: JSON.stringify(body), muteHttpExceptions: true });
      var code = r.getResponseCode(), txt = r.getContentText();
      if (code >= 300) waNote_(name + ' to ' + to + ': ' + txt.slice(0, 250));
      out.push(to + ': ' + (code < 300 ? 'sent' : 'not sent, ' + code + ' ' + txt.slice(0, 250)));
    } catch (err) { waNote_(name + ': ' + err.message); out.push(to + ': not sent, ' + err.message); }
  });
  return out.join('\n');
}
// every enquiry, at once: who, the number to call, and what they looked at first
function waLead_(d) {
  if (!waOn_() || !on_('WA_LEADS', true)) return;
  var seen = String(d.seen || '').split('\n').map(function (x) { return x.replace(/^\d+ \w+ \d\d:\d\d\s+/, '').trim(); }).filter(Boolean);
  seen = seen.filter(function (x, i) { return seen.lastIndexOf(x) === i; }).slice(-6);
  waSend_('shivas_enquiry', [waText_(d.name, 60), waText_([d.contact, d.email].filter(Boolean).join(' · '), 70), waText_(d.company, 60),
    waText_(d.place || [d.city, d.region, d.country].filter(Boolean).join(', '), 60), waText_(d.product || d.source, 80), waText_(d.message, 250), waText_(seen.join(', '), 160)]);
}
// a company network (an office connection that names its company) looking at the site: once a day per company
function waCompany_(d) {
  if (!waOn_() || !on_('WA_COMPANIES', true) || d.nettype !== 'Company network' || !d.org) return;
  var p = PropertiesService.getScriptProperties(), key = 'WC_' + day_(0) + '_' + String(d.org).replace(/\W+/g, '_').slice(0, 60);
  if (p.getProperty(key)) return;
  p.setProperty(key, '1');
  waSend_('shivas_company', [waText_(d.org, 80), waText_([d.city, d.region, d.country].filter(Boolean).join(', ') || 'not known', 60), waText_(d.title || d.page, 90)]);
}
// a message for every visit: off unless the script property WA_VISITS is on (a visit has no name or number)
function waVisit_(d) {
  if (!waOn_() || !on_('WA_VISITS', false)) return;
  var p = PropertiesService.getScriptProperties(), key = 'WV_' + day_(0), n = +(p.getProperty(key) || 0);
  if (n >= WA_VISITS_PER_DAY) return;
  p.setProperty(key, String(n + 1));
  var place = [d.city, d.country].filter(Boolean).join(', ') || (TZC[d.tz] ? TZC[d.tz] + ' (from the time zone)' : 'not known');
  waSend_('shivas_visit', [waText_(d.title || d.page, 90), waText_(source_(d.ref, d.utm), 60), waText_([d.device, d.model, d.os].filter(Boolean).join(', '), 60), waText_(place, 60)]);
}
// the short lines both summaries use
function waSum_(s) {
  var total = (s.tapN.WhatsApp || 0) + (s.tapN.Phone || 0) + (s.tapN.Email || 0);
  var calcs = Object.keys(s.calcN).sort(function (a, b) { return s.calcN[b] - s.calcN[a]; });
  var firms = Object.keys(s.firms).sort(function (a, b) { return s.firms[b].n - s.firms[a].n; });
  var prod = Object.keys(s.pages).map(function (k) { return s.pages[k]; })
    .filter(function (x) { return /^(items\/(?!index)|galvanizing\.html|wire-drawing\.html|reinplast\.html|pultrusion\.html)/.test(x.page); })
    .sort(function (a, b) { return b.n - a.n; });
  return {
    leads: waText_(s.leads.length ? s.leads.length + ': ' + s.leads.map(function (l) { return [l.name, l.company].filter(Boolean).join(', ') || 'no name'; }).join('; ') : 'none', 220),
    taps: waText_(total ? total + ' (' + ['WhatsApp', 'Phone', 'Email'].filter(function (k) { return s.tapN[k]; }).map(function (k) { return (k === 'WhatsApp' ? k : k.toLowerCase()) + ' ' + s.tapN[k]; }).join(', ') + ')' : 'none', 80),
    calcs: waText_(s.calcs.length ? s.calcs.length + ': ' + calcs.slice(0, 3).join(', ') : 'none', 140),
    calcN: waText_(calcs.length ? calcs.slice(0, 4).map(function (k) { return k + ' ' + s.calcN[k]; }).join(', ') : 'none', 160),
    firms: waText_(firms.length ? firms.slice(0, 5).map(function (k) { var w = String(s.firms[k].where || '').split(',')[0]; return k + (w ? ' (' + w + ')' : ''); }).join('; ') : 'none identified', 220),
    top: waText_(prod.length ? prod.slice(0, 3).map(function (x) { return x.title + ' (' + x.n + ')'; }).join(', ') : 'no product pages', 160)
  };
}
// every morning (WA_DAILY): yesterday in seven lines, only when something happened
function waDaily_(s, label) {
  if (!waOn_() || !on_('WA_DAILY', true) || (!s.views && !s.leads.length)) return;
  var w = waSum_(s);
  waSend_('shivas_daily', [waText_(label, 30), waText_(s.visits, 20), w.leads, w.taps, w.calcs, w.firms, w.top]);
}
// every Monday (WA_WEEKLY): the week against the week before, with a button that opens the Sheet
function waWeekly_(s, p, label) {
  if (!waOn_() || !on_('WA_WEEKLY', true)) return;
  var w = waSum_(s);
  waSend_('shivas_weekly', [waText_(label, 40), waText_(s.visits, 20), waText_(p.visits, 20), w.leads, w.firms, w.top, w.calcN]);
}
// old once-a-day markers (WC_ companies, WV_ visit count) are removed every morning
function tidy_() {
  try {
    var p = PropertiesService.getScriptProperties(), today = day_(0);
    p.getKeys().forEach(function (k) { if (/^(WC|WV)_\d{4}-\d\d-\d\d/.test(k) && k.slice(3, 13) !== today) p.deleteProperty(k); });
  } catch (e) {}
}

// Run by hand once WA_TOKEN, WA_PHONE_ID and WA_WABA_ID are in the script properties. It asks Meta to approve the five
// message formats (usually done within minutes). Run it again until every line says APPROVED; then it sends a test
// enquiry to WA_TO. The Execution log shows every step.
function setupWhatsApp() {
  var w = waProps_();
  if (!w.token || !w.phone || !w.waba) throw new Error('First add the script properties WA_TOKEN, WA_PHONE_ID and WA_WABA_ID (README.txt, "WhatsApp").');
  var base = 'https://graph.facebook.com/' + w.v + '/' + w.waba + '/message_templates', H = { Authorization: 'Bearer ' + w.token }, lines = [], url = book_().getUrl();
  Object.keys(WA_TEMPLATES).forEach(function (name) {
    var t = WA_TEMPLATES[name], have = null;
    var got = JSON.parse(UrlFetchApp.fetch(base + '?name=' + name + '&fields=name,status,language,rejected_reason', { headers: H, muteHttpExceptions: true }).getContentText() || '{}');
    if (got.error) { lines.push(name + ': ' + (got.error.error_user_msg || got.error.message)); return; }
    (got.data || []).forEach(function (x) { if (x.name === name && x.language === WA_LANG) have = x; });
    if (have) { lines.push(name + ': ' + have.status + (have.rejected_reason && have.rejected_reason !== 'NONE' ? ' (' + have.rejected_reason + ')' : '')); return; }
    var parts = [{ type: 'BODY', text: t.text, example: { body_text: [t.example] } }];
    if (t.button) parts.push({ type: 'BUTTONS', buttons: [{ type: 'URL', text: t.button, url: url }] });
    var r = JSON.parse(UrlFetchApp.fetch(base, { method: 'post', contentType: 'application/json', headers: H, muteHttpExceptions: true,
      payload: JSON.stringify({ name: name, language: WA_LANG, category: 'UTILITY', components: parts }) }).getContentText() || '{}');
    lines.push(name + ': ' + (r.error ? 'not created, ' + (r.error.error_user_msg || r.error.message) : (r.status || 'PENDING') + ' (sent to Meta for review)'));
  });
  if (lines.every(function (l) { return /: APPROVED$/.test(l); })) {
    lines.push('All five approved. Test enquiry to ' + w.to + ':\n' + waSend_('shivas_enquiry', ['TEST from setupWhatsApp', '+91 00000 00000', 'SHIVAS', 'Ghaziabad, India', 'Test message', 'If this arrived, WhatsApp messages from the visitor log work.', 'nothing, this is a test']));
  } else {
    lines.push('Meta is still reviewing some formats (or one was refused: the reason is shown). Run setupWhatsApp again in a few minutes.');
  }
  console.log(lines.join('\n'));
  return lines.join('\n');
}
// Run by hand: sends yesterday's summary to WhatsApp now (even on a quiet day) and shows what Meta answered.
function testWhatsApp() {
  var y = day_(-1), data = load_(day_(-2)), s = summary_(data, y, day_(0)), w = waSum_(s);
  var a = waSend_('shivas_daily', [waText_(nice_(y) + ' (test)', 30), waText_(s.visits, 20), w.leads, w.taps, w.calcs, w.firms, w.top]);
  console.log(a);
  return a;
}

// ---------------- run once ----------------
function setup() {
  var book = book_();
  PropertiesService.getScriptProperties().setProperty('SHEET', book.getId());
  [['Visits', VISIT_COLS], ['Leads', LEAD_COLS]].forEach(function (x) {
    var sh = book.getSheetByName(x[0]) || book.insertSheet(x[0]);
    sh.getRange(1, 1, 1, x[1].length).setValues([x[1].map(function (c) { return c[1]; })]).setFontWeight('bold').setBackground('#1F4E79').setFontColor('#ffffff');
    sh.setFrozenRows(1);
    sh.getRange('A:A').setNumberFormat('dd mmm yyyy hh:mm');
  });
  book.getSheetByName('Visits').hideColumns(col_(VISIT_COLS, 'pv'));
  // Companies tab: every office network seen, newest first
  var cs = book.getSheetByName('Companies') || book.insertSheet('Companies');
  var L = function (k) { var n = col_(VISIT_COLS, k), s = ''; while (n) { var m = (n - 1) % 26; s = String.fromCharCode(65 + m) + s; n = (n - 1 - m) / 26; } return s; };
  cs.getRange('A1').setFormula('=IFERROR(QUERY(Visits!A:' + L('pv') + ',"select ' + L('org') + ', ' + L('city') + ', ' + L('country') + ', count(' + L('page') + '), max(A) where ' + L('nettype') + " = 'Company network' and " + L('type') + " = 'view' group by " + L('org') + ', ' + L('city') + ', ' + L('country') + ' order by max(A) desc label ' + L('org') + " 'Company network', " + L('city') + " 'City', " + L('country') + " 'Country', count(" + L('page') + ") 'Page views', max(A) 'Last visit'\",1),\"No company visits yet\")");
  // Pages, Daily and Viewers tabs: live summaries of the Visits tab
  var tab = function (name, formula) { var t = book.getSheetByName(name) || book.insertSheet(name); t.getRange('A1').setFormula(formula); t.setFrozenRows(1); return t; };
  var V = 'Visits!A:' + L('pv'), q = function (sel) { return '=IFERROR(QUERY(' + V + ',"' + sel + '",1),"No page views yet")'; };
  tab('Pages', q('select ' + L('title') + ', ' + L('page') + ', count(' + L('type') + '), avg(' + L('secs') + '), max(A) where ' + L('type') + " = 'view' group by " + L('title') + ', ' + L('page') + ' order by count(' + L('type') + ') desc label ' + L('title') + " 'Page', " + L('page') + " 'Address', count(" + L('type') + ") 'Views', avg(" + L('secs') + ") 'Avg seconds', max(A) 'Last view'"));
  tab('Daily', q('select toDate(A), count(' + L('type') + ') where ' + L('type') + " = 'view' group by toDate(A) order by toDate(A) desc label toDate(A) 'Day', count(" + L('type') + ") 'Page views'")).getRange('A:A').setNumberFormat('ddd dd mmm yyyy');
  tab('Viewers', q('select ' + L('visitor') + ', max(A), count(' + L('type') + '), ' + L('org') + ', ' + L('city') + ', ' + L('country') + ', ' + L('device') + ' where ' + L('type') + " = 'view' and " + L('visitor') + " <> '' group by " + L('visitor') + ', ' + L('org') + ', ' + L('city') + ', ' + L('country') + ', ' + L('device') + ' order by max(A) desc label ' + L('visitor') + " 'Visitor', max(A) 'Last seen', count(" + L('type') + ") 'Page views', " + L('org') + " 'Network / company', " + L('city') + " 'City', " + L('country') + " 'Country', " + L('device') + " 'Device'"));
  var old = book.getSheetByName('Sheet1'); if (old && old.getLastRow() === 0 && book.getSheets().length > 1) book.deleteSheet(old);
  ScriptApp.getProjectTriggers().forEach(function (t) { if (/^(dailyDigest|weeklyDigest)$/.test(t.getHandlerFunction())) ScriptApp.deleteTrigger(t); });
  ScriptApp.newTrigger('dailyDigest').timeBased().atHour(8).everyDays(1).inTimezone('Asia/Kolkata').create();
  ScriptApp.newTrigger('weeklyDigest').timeBased().onWeekDay(ScriptApp.WeekDay.MONDAY).atHour(8).nearMinute(30).inTimezone('Asia/Kolkata').create();
  MailApp.getRemainingDailyQuota();   // asks for the email permission now, not on the first enquiry
}
