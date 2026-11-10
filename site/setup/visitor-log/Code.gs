/**
 * SHIVAS website visitor log — Google Apps Script for a Google Sheet.
 * Receives what the website sends (assets/track.js) and writes it to two tabs:
 *   Visits  – one row per page view: page, device, browser, country, city, network / company, time on page …
 *   Leads   – every enquiry form and "ask our engineer" request, with what that visitor looked at before.
 * Also: an email for every lead at once, and a summary of yesterday's visitors every morning at 8:00 (India time).
 * Set up: see README.txt in this folder. Run setup() once, then Deploy → New deployment → Web app.
 */

// ---------------- settings ----------------
var ALERT_TECH = { to: 'info@shivastechnology.com', cc: 'shivastechnology@gmail.com' };   // galvanizing and wire drawing
var ALERT_REIN = { to: 'info@shivasasia.com', cc: 'shivasasia@gmail.com' };               // SHIVAS Reinplast
var DIGEST_TO = 'info@shivastechnology.com';                                              // morning summary
var KEEP_DAYS = 730;                                                                      // visit rows older than this are deleted (privacy notice says 24 months)

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
function doGet() { return ContentService.createTextOutput('SHIVAS visitor log is running.'); }

function doPost(e) {
  var lock = LockService.getScriptLock();
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
    if (d.type === 'time' || d.type === 'update') { update_(visits, d); return reply('ok'); }
    if (d.type === 'lead') {
      d.seen = history_(visits, d.visitor);
      book.getSheetByName('Leads').appendRow(row_(LEAD_COLS, d));
      d.detail = d.source + ': ' + [d.name, d.company, d.contact].filter(Boolean).join(' · ');
      alert_(d);
    }
    visits.appendRow(row_(VISIT_COLS, d));
    return reply('ok');
  } finally { try { lock.releaseLock(); } catch (err) {} }
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
  return id ? SpreadsheetApp.openById(id) : SpreadsheetApp.getActiveSpreadsheet();
}
function row_(cols, d) {   // text from the web is never run as a formula (+91… stays text too)
  return cols.map(function (c) { var v = d[c[0]]; if (v === undefined || v === null) return ''; return typeof v === 'string' && /^[=+\-@]/.test(v) ? "'" + v : v; });
}
function col_(cols, key) { for (var i = 0; i < cols.length; i++) if (cols[i][0] === key) return i + 1; return 0; }

// time on page and the visitor's OK arrive after the page view: fill them into that row
function update_(sh, d) {
  var last = sh.getLastRow(); if (last < 2 || !d.pv) return;
  var from = Math.max(2, last - 799), pvCol = col_(VISIT_COLS, 'pv');
  var pvs = sh.getRange(from, pvCol, last - from + 1, 1).getValues();
  for (var i = pvs.length - 1; i >= 0; i--) {
    if (pvs[i][0] !== d.pv) continue;
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
    if (r[cV] !== visitor) return;
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
  MailApp.sendEmail({ to: who.to, cc: who.cc, subject: 'Website enquiry: ' + [d.name, d.company].filter(Boolean).join(' · ') + ' — ' + (d.product || d.source), htmlBody: html, name: 'SHIVAS website' });
}
function esc(s) { return String(s).replace(/[&<>]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;' }[c]; }); }

// ---------------- every morning: yesterday's visitors ----------------
function dailyDigest() {
  var sh = book_().getSheetByName('Visits'), last = sh.getLastRow(); if (last < 2) return;
  var tz = 'Asia/Kolkata', now = new Date(), today = Utilities.formatDate(now, tz, 'yyyy-MM-dd');
  var y = Utilities.formatDate(new Date(now.getTime() - 864e5), tz, 'yyyy-MM-dd');
  var from = Math.max(2, last - 19999), rows = sh.getRange(from, 1, last - from + 1, VISIT_COLS.length).getValues();
  var c = {}; VISIT_COLS.forEach(function (x, i) { c[x[0]] = i; });
  var views = 0, people = {}, anon = 0, countries = {}, devices = {}, firms = {}, leads = [], calcs = [], clicks = [], pages = {};
  rows.forEach(function (r) {
    if (Utilities.formatDate(new Date(r[c.at]), tz, 'yyyy-MM-dd') !== y) return;
    var t = r[c.type];
    if (t === 'view') {
      views++; if (r[c.visitor]) people[r[c.visitor]] = 1; else anon++;
      var co = r[c.country] || (r[c.tz] ? 'Time zone ' + r[c.tz] : 'Unknown'); countries[co] = (countries[co] || 0) + 1;
      devices[r[c.device] || 'Unknown'] = (devices[r[c.device] || 'Unknown'] || 0) + 1;
      pages[r[c.title] || r[c.page]] = (pages[r[c.title] || r[c.page]] || 0) + 1;
      if (r[c.nettype] === 'Company network') {
        var f = firms[r[c.org]] = firms[r[c.org]] || { n: 0, secs: 0, where: [r[c.city], r[c.country]].filter(Boolean).join(', '), pages: {} };
        f.n++; f.secs += +r[c.secs] || 0; f.pages[r[c.title] || r[c.page]] = 1;
      }
    } else if (t === 'lead') leads.push(r[c.detail]);
    else if (t === 'calc') calcs.push(String(r[c.detail]).split('\n')[0] + (r[c.org] ? ' — ' + r[c.org] : '') + (r[c.city] ? ', ' + r[c.city] : ''));
    else if (t === 'click' && /^(WhatsApp|Email|Phone)/.test(r[c.detail])) clicks.push(r[c.detail] + (r[c.org] ? ' — ' + r[c.org] : '') + (r[c.city] ? ', ' + r[c.city] : ''));
  });
  if (!views && !leads.length) return;
  var top = function (o, n) { return Object.keys(o).sort(function (a, b) { return o[b] - o[a]; }).slice(0, n).map(function (k) { return esc(k) + ' <b>' + o[k] + '</b>'; }).join(' · '); };
  var firmList = Object.keys(firms).sort(function (a, b) { return firms[b].n - firms[a].n; }).slice(0, 40).map(function (k) {
    var f = firms[k]; return '<li><b>' + esc(k) + '</b> · ' + esc(f.where) + ' · ' + f.n + ' pages, ' + Math.round(f.secs / 60) + ' min<br><span style="color:#566778">' + esc(Object.keys(f.pages).slice(0, 8).join(' · ')) + '</span></li>';
  }).join('');
  var li = function (a) { return a.length ? '<ul>' + a.slice(0, 40).map(function (x) { return '<li>' + esc(x) + '</li>'; }).join('') + '</ul>' : '<p style="color:#566778">None</p>'; };
  var html = '<div style="font:14px/1.5 Arial,sans-serif;color:#13202c">' +
    '<p style="font-size:16px"><b>SHIVAS website, ' + y + '</b></p>' +
    '<p>' + views + ' page views · ' + Object.keys(people).length + ' visitors who said OK · ' + anon + ' views from visitors who did not</p>' +
    '<p><b>Enquiries</b></p>' + li(leads) +
    '<p><b>Companies</b> (visits from office networks; home and mobile connections cannot be named)</p>' + (firmList ? '<ol>' + firmList + '</ol>' : '<p style="color:#566778">None identified</p>') +
    '<p><b>WhatsApp, email and phone taps</b></p>' + li(clicks) +
    '<p><b>Calculators used</b></p>' + li(calcs) +
    '<p><b>Countries</b><br>' + top(countries, 12) + '</p><p><b>Devices</b><br>' + top(devices, 5) + '</p><p><b>Most viewed</b><br>' + top(pages, 12) + '</p>' +
    '<p style="color:#566778">Every row is in the Visits tab of the visitor log.</p></div>';
  MailApp.sendEmail({ to: DIGEST_TO, subject: 'SHIVAS website ' + y + ': ' + views + ' views · ' + Object.keys(firms).length + ' companies · ' + leads.length + ' enquiries', htmlBody: html, name: 'SHIVAS website' });
  cleanup();
}

// visit rows older than KEEP_DAYS are deleted (enquiries in Leads are kept)
function cleanup() {
  var sh = book_().getSheetByName('Visits'), last = sh.getLastRow(); if (last < 3) return;
  var cut = new Date(Date.now() - KEEP_DAYS * 864e5), t = sh.getRange(2, 1, last - 1, 1).getValues(), n = 0;
  while (n < t.length && new Date(t[n][0]) < cut) n++;
  if (n) sh.deleteRows(2, Math.min(n, last - 2));
}

// ---------------- run once ----------------
function setup() {
  var book = SpreadsheetApp.getActiveSpreadsheet();
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
  var old = book.getSheetByName('Sheet1'); if (old && old.getLastRow() === 0 && book.getSheets().length > 1) book.deleteSheet(old);
  ScriptApp.getProjectTriggers().forEach(function (t) { if (t.getHandlerFunction() === 'dailyDigest') ScriptApp.deleteTrigger(t); });
  ScriptApp.newTrigger('dailyDigest').timeBased().atHour(8).everyDays(1).inTimezone('Asia/Kolkata').create();
  MailApp.getRemainingDailyQuota();   // asks for the email permission now, not on the first enquiry
}
